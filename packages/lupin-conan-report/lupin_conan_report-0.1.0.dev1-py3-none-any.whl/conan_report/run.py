import typer

from conan_report.generate_conan_project_report import generate_conan_report
from conan_report.logger_manager import configure_logger
from conan_report.__init__ import __version__

cli = typer.Typer()


def json_file_path_option() -> typer.Option:
    return typer.Option(
        ...,
        "--json-path",
        help="The path to the json file containing the conan project dependencies",
    )


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
    json_file_path: str = json_file_path_option(),
):
    if ctx.invoked_subcommand is None:
        generate_report(json_file_path)


@cli.command()
def generate_report(json_file_path: str = json_file_path_option()):
    typer.echo("Conan report generation started")
    configure_logger()
    generate_conan_report(json_file_path)
    typer.echo("Conan report generation finished")
