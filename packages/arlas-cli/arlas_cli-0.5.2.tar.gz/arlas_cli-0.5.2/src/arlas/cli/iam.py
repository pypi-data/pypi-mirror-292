
import typer

from arlas.cli.variables import variables

iam = typer.Typer()


@iam.callback()
def configuration(config: str = typer.Option(help="Name of the ARLAS configuration to use from your configuration file ({}).".format(variables["configuration_file"]))):
    variables["arlas"] = config
