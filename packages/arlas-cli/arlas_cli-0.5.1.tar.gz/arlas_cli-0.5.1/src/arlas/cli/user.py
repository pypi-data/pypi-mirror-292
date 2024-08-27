import typer
from prettytable import PrettyTable

from arlas.cli.service import Service
from arlas.cli.variables import variables

user = typer.Typer()


@user.command(help="Create user", name="add")
def add(email: str = typer.Argument(help="User's email")):
    config = variables["arlas"]
    print(Service.create_user(config, email).get("id"))


@user.command(help="Delete user", name="delete")
def delete(id: str = typer.Argument(help="User's identifier")):
    config = variables["arlas"]
    print(Service.delete_user(config, id).get("message"))


@user.command(help="Activate user account", name="activate")
def activate(id: str = typer.Argument(help="User's identifier")):
    config = variables["arlas"]
    print(Service.activate(config, id).get("message"))


@user.command(help="Deactivate user account", name="deactivate")
def deactivate(id: str = typer.Argument(help="User's identifier")):
    config = variables["arlas"]
    print(Service.deactivate(config, id).get("message"))

