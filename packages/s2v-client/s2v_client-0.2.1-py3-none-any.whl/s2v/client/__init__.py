import abc
import datetime
import enum
import io
import os
import pathlib
import shutil
import sys
import tempfile
import zipfile
from collections.abc import Callable
from typing import IO, Any, Literal

import click
import google.auth
import httpx
from google.auth import credentials, impersonated_credentials
from google.auth.transport import requests

from s2v.version import version


def _google_auth(
    source_credentials: credentials.Credentials, audience: str
) -> Callable[[httpx.Request], httpx.Request]:
    id_token_credentials = impersonated_credentials.IDTokenCredentials(source_credentials, audience, include_email=True)
    transport = requests.Request()

    def authenticate(request: httpx.Request) -> httpx.Request:
        id_token_credentials.before_request(transport, request.method, request.url, request.headers)
        return request

    return authenticate


def _zip_directory_contents(dir: pathlib.PurePath, target: IO[bytes]) -> None:
    """
    Creates a ZIP archive of the given directory's contents, recursively.

    :param dir: the directory to search for contents to be zipped
    :param target: a target IO to write the ZIP archive to
    """

    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_LZMA) as zip_file:
        for directory_name, _, files in os.walk(dir):
            directory = pathlib.PurePath(directory_name)
            zip_file.write(directory, directory.relative_to(dir))
            for file_name in files:
                file = directory / file_name
                zip_file.write(file, file.relative_to(dir))


class AuthMode(str, enum.Enum):
    NONE = "none"
    GOOGLE = "google"


class S2VError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class ValidationResult(abc.ABC):
    @abc.abstractmethod
    def __bool__(self) -> bool: ...


class ValidationSuccess(ValidationResult):
    def __bool__(self) -> Literal[True]:
        return True


class ValidationFailure(ValidationResult):
    def __init__(self, details: list[str]) -> None:
        self.details = details

    def __bool__(self) -> Literal[False]:
        return False

    def __str__(self) -> str:
        return "\n".join(self.details)


class S2VClient:
    def __init__(self, client: httpx.Client):
        self._httpx_client = client

    @classmethod
    def create(cls, base_url: str | httpx.URL, auth_mode: AuthMode = AuthMode.GOOGLE) -> "S2VClient":
        auth: Callable[[httpx.Request], httpx.Request] | None
        match auth_mode:
            case AuthMode.GOOGLE:
                adc, _ = google.auth.default()
                auth = _google_auth(adc, str(base_url))
            case _:
                auth = None

        headers = {"User-Agent": f"s2v-client/{version}"}
        timeout = httpx.Timeout(timeout=datetime.timedelta(minutes=1).total_seconds())
        return cls(httpx.Client(base_url=base_url, auth=auth, headers=headers, timeout=timeout))

    def validate(self, input_dir: pathlib.PurePath) -> ValidationResult:
        with tempfile.TemporaryFile(suffix=".zip") as zip_file:
            _zip_directory_contents(input_dir, zip_file)
            zip_file.seek(0)

            response = self._httpx_client.post(
                "/v1/validate",
                content=zip_file,
                headers={"Accept": "text/plain", "Accept-Encoding": "gzip", "Content-Type": "application/zip"},
            )

        match response.status_code:
            case httpx.codes.OK:
                return ValidationSuccess()
            case httpx.codes.UNPROCESSABLE_ENTITY:
                return ValidationFailure(response.text.splitlines())
            case _:
                response.raise_for_status()
                # This is unreachable, because raise_for_status() will already raise an error.
                # However, we need to convince the type checker that no return statement is missing.
                raise Exception()

    def generate(self, input_dir: pathlib.PurePath, output_dir: pathlib.PurePath) -> None:
        with tempfile.TemporaryFile(suffix=".zip") as request_data:
            _zip_directory_contents(input_dir, request_data)
            request_data.seek(0)

            response = self._httpx_client.post(
                "/v1/generate",
                content=request_data,
                headers={"Accept": "application/zip", "Content-Type": "application/zip"},
            )

            match response.status_code:
                case httpx.codes.UNPROCESSABLE_ENTITY:
                    raise S2VError(response.text)
                case _:
                    response.raise_for_status()

            content_type = response.headers["content-type"]
            assert (
                content_type == "application/zip"
            ), f"Expected response Content-Type of 'application/zip', got: '{content_type}'"

        with zipfile.ZipFile(io.BytesIO(response.content), "r") as response_zip:
            response_zip.extractall(output_dir)


class _URLParamType(click.ParamType):
    name = "URL"

    def convert(self, value: Any, param: click.Parameter | None, ctx: click.Context | None) -> httpx.URL:
        try:
            return httpx.URL(value)
        except (TypeError, httpx.InvalidURL) as err:
            self.fail(f"{value!r} is not a valid {self.name}: {err}", param, ctx)


@click.group(name="s2v", help=f"Stream2Vault CLI {version}")
def cli() -> None:
    pass


input_dir_opt = click.option(
    "-i",
    "--input",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.PurePath),
    required=True,
    help="Path to the input directory",
)
output_dir_opt = click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=False, writable=True, path_type=pathlib.PurePath),
    required=True,
    help="Path to the output directory",
)
url_opt = click.option(
    "-u",
    "--url",
    type=_URLParamType(),
    required=True,
    help="URL of the S2V server to connect to",
)
auth_mode_opt = click.option(
    "--auth-mode",
    type=click.Choice(list(AuthMode), case_sensitive=False),
    default=AuthMode.GOOGLE,
    show_default=True,
    help="How to authenticate to the server",
)


@cli.command("validate", help="Validate vault model")
@input_dir_opt
@url_opt
@auth_mode_opt
def validate(input: pathlib.PurePath, url: httpx.URL, auth_mode: AuthMode) -> None:
    client = S2VClient.create(url, auth_mode)
    try:
        results = client.validate(input)
        print(results)
    except S2VError as err:
        print(f"ERROR: {err}", file=sys.stderr)
    except BaseException as err:
        print(err, file=sys.stderr)


@cli.command("generate", help="Generate deployment artifacts for vault model")
@input_dir_opt
@output_dir_opt
@url_opt
@auth_mode_opt
def generate(input: pathlib.PurePath, output: pathlib.PurePath, url: httpx.URL, auth_mode: AuthMode) -> None:
    client = S2VClient.create(url, auth_mode)
    try:
        client.generate(input, output)
    except S2VError as err:
        print(f"ERROR: {err}", file=sys.stderr)
    except BaseException as err:
        print(err, file=sys.stderr)


def main() -> None:
    terminal_size = shutil.get_terminal_size()
    cli(auto_envvar_prefix="S2V", max_content_width=terminal_size.columns)
