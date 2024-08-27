import json
import os
from os import path
from outerbounds._vendor import click
import requests

from ..utils import metaflowconfig
from ..utils.schema import (
    CommandStatus,
    OuterboundsCommandResponse,
    OuterboundsCommandStatus,
)


@click.group()
def cli(**kwargs):
    pass


@click.group(help="Manage perimeters")
def app(**kwargs):
    pass


@app.command(help="Start an app using a port and a name")
@click.option(
    "-d",
    "--config-dir",
    default=path.expanduser(os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
@click.option(
    "--port",
    required=True,
    help="Port number where you want to start your app",
    type=int,
)
@click.option(
    "--name",
    required=True,
    help="Name of your app",
    type=str,
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
def start(config_dir=None, profile=None, port=-1, name="", output=""):
    start_app_response = OuterboundsCommandResponse()

    validate_workstation_step = CommandStatus(
        "ValidateRunningOnWorkstation",
        OuterboundsCommandStatus.OK,
        "Command is being run on a workstation.",
    )

    list_workstations_step = CommandStatus(
        "ListWorkstations",
        OuterboundsCommandStatus.OK,
        "List of workstations fetched.",
    )

    validate_port_exists = CommandStatus(
        "ValidatePortExists",
        OuterboundsCommandStatus.OK,
        "Port exists on workstation",
    )

    start_app_step = CommandStatus(
        "StartApp",
        OuterboundsCommandStatus.OK,
        f"App {name} started on port {port}!",
    )

    if "WORKSTATION_ID" not in os.environ:
        validate_workstation_step.update(
            OuterboundsCommandStatus.FAIL,
            "All outerbounds app commands can only be run from a workstation.",
            "",
        )
        start_app_response.add_step(validate_workstation_step)
        click.secho(
            "All outerbounds app commands can only be run from a workstation.",
            fg="red",
            err=True,
        )

        if output == "json":
            click.echo(json.dumps(start_app_response.as_dict(), indent=4))
        return

    try:
        try:
            metaflow_token = metaflowconfig.get_metaflow_token_from_config(
                config_dir, profile
            )
            api_url = metaflowconfig.get_sanitized_url_from_config(
                config_dir, profile, "OBP_API_SERVER"
            )

            workstations_response = requests.get(
                f"{api_url}/v1/workstations", headers={"x-api-key": metaflow_token}
            )
            workstations_response.raise_for_status()
            start_app_response.add_step(list_workstations_step)
        except:
            click.secho("Failed to list workstations!", fg="red", err=True)
            list_workstations_step.update(
                OuterboundsCommandStatus.FAIL, "Failed to list workstations!", ""
            )
            start_app_response.add_step(list_workstations_step)
            if output == "json":
                click.echo(json.dumps(start_app_response.as_dict(), indent=4))
            return

        workstations_json = workstations_response.json()["workstations"]
        for workstation in workstations_json:
            if workstation["instance_id"] == os.environ["WORKSTATION_ID"]:
                if "named_ports" in workstation["spec"]:
                    for named_port in workstation["spec"]["named_ports"]:
                        if int(named_port["port"]) == port:
                            start_app_response.add_step(validate_port_exists)
                            if named_port["enabled"] and named_port["name"] == name:
                                click.secho(
                                    f"App {name} started on port {port}!",
                                    fg="green",
                                    err=True,
                                )
                                click.secho(
                                    f"App URL: {api_url.replace('api', 'ui')}/apps/{os.environ['WORKSTATION_ID']}/{name}/",
                                    fg="green",
                                    err=True,
                                )
                                start_app_response.add_step(start_app_step)
                                if output == "json":
                                    click.echo(
                                        json.dumps(
                                            start_app_response.as_dict(), indent=4
                                        )
                                    )
                                return
                            else:
                                try:
                                    response = requests.put(
                                        f"{api_url}/v1/workstations/update/{os.environ['WORKSTATION_ID']}/namedports",
                                        headers={"x-api-key": metaflow_token},
                                        json={
                                            "port": port,
                                            "name": name,
                                            "enabled": True,
                                        },
                                    )

                                    response.raise_for_status()
                                    click.secho(
                                        f"App {name} started on port {port}!",
                                        fg="green",
                                        err=True,
                                    )
                                except:
                                    click.secho(
                                        f"Failed to start app {name} on port {port}!",
                                        fg="red",
                                        err=True,
                                    )
                                    start_app_step.update(
                                        OuterboundsCommandStatus.FAIL,
                                        f"Failed to start app {name} on port {port}!",
                                        "",
                                    )

                                start_app_response.add_step(start_app_step)
                                if output == "json":
                                    click.echo(
                                        json.dumps(
                                            start_app_response.as_dict(), indent=4
                                        )
                                    )
                                return

        click.secho(
            f"Port {port} not found on workstation {os.environ['WORKSTATION_ID']}",
            fg="red",
            err=True,
        )
        validate_port_exists.update(
            OuterboundsCommandStatus.FAIL,
            f"Port {port} not found on workstation {os.environ['WORKSTATION_ID']}",
            "",
        )
        start_app_response.add_step(validate_port_exists)
        if output == "json":
            click.echo(json.dumps(start_app_response.as_dict(), indent=4))
    except Exception as e:
        click.secho(f"Failed to start app {name} on port {port}!", fg="red", err=True)
        start_app_step.update(
            OuterboundsCommandStatus.FAIL,
            f"Failed to start app {name} on port {port}!",
            "",
        )
        start_app_response.add_step(start_app_step)
        if output == "json":
            click.secho(json.dumps(start_app_response.as_dict(), indent=4))


@app.command(help="Stop an app using its port number")
@click.option(
    "-d",
    "--config-dir",
    default=path.expanduser(os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
@click.option(
    "--port",
    required=True,
    help="Port number where you want to start your app.",
    type=int,
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
def stop(config_dir=None, profile=None, port=-1, output=""):
    stop_app_response = OuterboundsCommandResponse()

    validate_workstation_step = CommandStatus(
        "ValidateRunningOnWorkstation",
        OuterboundsCommandStatus.OK,
        "Command is being run on a workstation.",
    )

    list_workstations_step = CommandStatus(
        "ListWorkstations",
        OuterboundsCommandStatus.OK,
        "List of workstations fetched.",
    )

    validate_port_exists = CommandStatus(
        "ValidatePortExists",
        OuterboundsCommandStatus.OK,
        "Port exists on workstation",
    )

    stop_app_step = CommandStatus(
        "StopApp",
        OuterboundsCommandStatus.OK,
        f"App stopped on port {port}!",
    )

    if "WORKSTATION_ID" not in os.environ:
        validate_workstation_step.update(
            OuterboundsCommandStatus.FAIL,
            "All outerbounds app commands can only be run from a workstation.",
            "",
        )
        stop_app_response.add_step(validate_workstation_step)
        click.secho(
            "All outerbounds app commands can only be run from a workstation.",
            fg="red",
            err=True,
        )

        if output == "json":
            click.echo(json.dumps(stop_app_response.as_dict(), indent=4))
        return

    try:
        try:
            metaflow_token = metaflowconfig.get_metaflow_token_from_config(
                config_dir, profile
            )
            api_url = metaflowconfig.get_sanitized_url_from_config(
                config_dir, profile, "OBP_API_SERVER"
            )

            workstations_response = requests.get(
                f"{api_url}/v1/workstations", headers={"x-api-key": metaflow_token}
            )
            workstations_response.raise_for_status()
            stop_app_response.add_step(list_workstations_step)
        except:
            click.secho("Failed to list workstations!", fg="red", err=True)
            list_workstations_step.update(
                OuterboundsCommandStatus.FAIL, "Failed to list workstations!", ""
            )
            stop_app_response.add_step(list_workstations_step)
            if output == "json":
                click.echo(json.dumps(stop_app_response.as_dict(), indent=4))
            return

        workstations_json = workstations_response.json()["workstations"]
        for workstation in workstations_json:
            if workstation["instance_id"] == os.environ["WORKSTATION_ID"]:
                if "named_ports" in workstation["spec"]:
                    for named_port in workstation["spec"]["named_ports"]:
                        if int(named_port["port"]) == port:
                            stop_app_response.add_step(validate_port_exists)
                            if not named_port["enabled"]:
                                click.secho(
                                    f"App stopped on port {port}!", fg="green", err=True
                                )
                                stop_app_response.add_step(stop_app_step)
                                if output == "json":
                                    click.echo(
                                        json.dumps(
                                            stop_app_response.as_dict(), indent=4
                                        )
                                    )
                                return
                            else:
                                try:
                                    response = requests.put(
                                        f"{api_url}/v1/workstations/update/{os.environ['WORKSTATION_ID']}/namedports",
                                        headers={"x-api-key": metaflow_token},
                                        json={
                                            "port": port,
                                            "name": named_port["name"],
                                            "enabled": False,
                                        },
                                    )
                                    response.raise_for_status()
                                    click.secho(
                                        f"App stopped on port {port}!",
                                        fg="green",
                                        err=True,
                                    )
                                except:
                                    click.secho(
                                        f"Failed to stop app on port {port}!",
                                        fg="red",
                                        err=True,
                                    )
                                    stop_app_step.update(
                                        OuterboundsCommandStatus.FAIL,
                                        f"Failed to stop app on port {port}!",
                                        "",
                                    )

                                stop_app_response.add_step(stop_app_step)
                                if output == "json":
                                    click.echo(
                                        json.dumps(
                                            stop_app_response.as_dict(), indent=4
                                        )
                                    )
                                return

        click.secho(
            f"Port {port} not found on workstation {os.environ['WORKSTATION_ID']}",
            fg="red",
            err=True,
        )
        validate_port_exists.update(
            OuterboundsCommandStatus.FAIL,
            f"Port {port} not found on workstation {os.environ['WORKSTATION_ID']}",
            "",
        )
        stop_app_response.add_step(validate_port_exists)
        if output == "json":
            click.echo(json.dumps(stop_app_response.as_dict(), indent=4))
    except Exception as e:
        click.secho(f"Failed to stop app on port {port}!", fg="red", err=True)
        stop_app_step.update(
            OuterboundsCommandStatus.FAIL, f"Failed to stop on port {port}!", ""
        )
        stop_app_response.add_step(stop_app_step)
        if output == "json":
            click.echo(json.dumps(stop_app_response.as_dict(), indent=4))


@app.command(help="Stop an app using its port number")
@click.option(
    "-d",
    "--config-dir",
    default=path.expanduser(os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
def list(config_dir=None, profile=None, output=""):
    list_app_response = OuterboundsCommandResponse()

    validate_workstation_step = CommandStatus(
        "ValidateRunningOnWorkstation",
        OuterboundsCommandStatus.OK,
        "Command is being run on a workstation.",
    )

    list_workstations_step = CommandStatus(
        "ListWorkstations",
        OuterboundsCommandStatus.OK,
        "List of workstations fetched.",
    )

    if "WORKSTATION_ID" not in os.environ:
        validate_workstation_step.update(
            OuterboundsCommandStatus.FAIL,
            "All outerbounds app commands can only be run from a workstation.",
            "",
        )
        list_app_response.add_step(validate_workstation_step)
        click.secho(
            "All outerbounds app commands can only be run from a workstation.",
            fg="red",
            err=True,
        )

        if output == "json":
            click.echo(json.dumps(list_app_response.as_dict(), indent=4))
        return

    try:
        try:
            metaflow_token = metaflowconfig.get_metaflow_token_from_config(
                config_dir, profile
            )
            api_url = metaflowconfig.get_sanitized_url_from_config(
                config_dir, profile, "OBP_API_SERVER"
            )

            workstations_response = requests.get(
                f"{api_url}/v1/workstations", headers={"x-api-key": metaflow_token}
            )
            workstations_response.raise_for_status()
            list_app_response.add_step(list_workstations_step)
        except:
            click.secho("Failed to list workstations!", fg="red", err=True)
            list_workstations_step.update(
                OuterboundsCommandStatus.FAIL, "Failed to list workstations!", ""
            )
            list_app_response.add_step(list_workstations_step)
            if output == "json":
                click.echo(json.dumps(list_app_response.as_dict(), indent=4))
            return

        workstations_json = workstations_response.json()["workstations"]
        for workstation in workstations_json:
            if workstation["instance_id"] == os.environ["WORKSTATION_ID"]:
                if "named_ports" in workstation["spec"]:
                    for named_port in workstation["spec"]["named_ports"]:
                        if named_port["enabled"]:
                            click.secho(
                                f"App Name: {named_port['name']}", fg="green", err=True
                            )
                            click.secho(
                                f"App Port on Workstation: {named_port['port']}",
                                fg="green",
                                err=True,
                            )
                            click.secho(f"App Status: Deployed", fg="green", err=True)
                            click.secho(
                                f"App URL: {api_url.replace('api', 'ui')}/apps/{os.environ['WORKSTATION_ID']}/{named_port['name']}/",
                                fg="green",
                                err=True,
                            )
                        else:
                            click.secho(
                                f"App Port on Workstation: {named_port['port']}",
                                fg="yellow",
                                err=True,
                            )
                            click.secho(
                                f"App Status: Not Deployed", fg="yellow", err=True
                            )

                        click.echo("\n", err=True)
    except Exception as e:
        click.secho(f"Failed to list apps!", fg="red", err=True)
        if output == "json":
            click.echo(json.dumps(list_app_response.as_dict(), indent=4))


cli.add_command(app, name="app")
