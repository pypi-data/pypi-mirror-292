import typer
from pathlib import Path
from python_on_whales import DockerClient

app = typer.Typer()


def get_docker_client(compose_file: str = None) -> DockerClient:
    if compose_file:
        compose_path = Path(compose_file).expanduser().resolve()
        return DockerClient(client_type="docker", compose_files=[str(compose_path)])
    else:
        return DockerClient(client_type="docker")

def complete_services(ctx: typer.Context, args: list[str], incomplete: str):
    try:
        compose_file = ctx.params.get("compose_file")
        docker = get_docker_client(compose_file)
        services = docker.compose.config().services.keys()
        return [service for service in services if service.startswith(incomplete)]
    except Exception:
        return []


@app.command(name="start")
def start_docker_containers(
    services: list[str] = typer.Argument(None, autocompletion=complete_services),
    compose_file: str = typer.Option(None, "--file", "-f"),
):
    """
    Start docker containers with docker-compose file.
    """
    try:
        docker = get_docker_client(compose_file)
        compose_args = {"detach": True}
        if services:
            docker.compose.up(services, **compose_args)
            typer.echo(f"Docker services {', '.join(services)} started successfully.")
        else:
            docker.compose.up(**compose_args)
            typer.echo("Docker containers started successfully.")
    except Exception as e:
        typer.echo(f"Error starting docker containers: {e}", err=True)


@app.command(name="stop")
def stop_docker_containers(
    services: list[str] = typer.Argument(None, autocompletion=complete_services),
    compose_file: str = typer.Option(None, "--file", "-f"),
):
    """
    Stop docker containers with docker-compose file.
    """
    try:
        docker = get_docker_client(compose_file)
        if services:
            docker.compose.stop(services)
            typer.echo(f"Docker services {', '.join(services)} stopped successfully.")
        else:
            docker.compose.stop()
            typer.echo("Docker containers stopped successfully.")
    except Exception as e:
        typer.echo(f"Error stopping docker containers: {e}", err=True)


if __name__ == "__main__":
    app()
