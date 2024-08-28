import dbm
import gzip
import json
import mimetypes

from functools import cache
from typing import Generator, NoReturn, cast
from pathlib import Path
from urllib.error import HTTPError


from dataclasses import dataclass, asdict

from urllib import request

from typing_extensions import Annotated

import click
import typer
import keyring

from rich import print
from rich.progress import track

from sfis_tools.settings import Settings
from sfis_tools.info import APP_NAME
from sfis_tools.api_client import ApiClient

mimetypes.init()


class State:
    """The internal App state"""

    tenant_id: str


app = typer.Typer(name=APP_NAME)


@dataclass
class TenantInfo:
    id: str
    name: str | None

    def __eq__(self, value: object) -> bool:
        if isinstance(value, TenantInfo):
            return self.id == value.id
        return self.id == value


def _add_tenant(tenant: TenantInfo):
    db_path = _user_config_file("tenants_v1")
    with dbm.open(db_path, "c") as db:
        db[tenant.id] = json.dumps(asdict(tenant))


def list_tenants() -> Generator[TenantInfo, None, None]:
    db_path = _user_config_file("tenants_v1")
    with dbm.open(db_path, "c") as db:
        for tenant_id in db.keys():
            data = json.loads(db[tenant_id])
            yield TenantInfo(**data)


def get_current_tenant() -> TenantInfo | None:
    return _get_user_setting("tenant")


class Tenant:
    pass


settings = Settings()


@cache
def _get_api_client() -> ApiClient:
    current_tenant = settings.current_tenant
    api_key = keyring.get_password(APP_NAME, f"{current_tenant}:API-KEY")
    backend = settings.backend
    scheme = "https"
    if backend is None:
        backend = "localhost:8080"
        scheme = "http"
    return ApiClient(current_tenant, api_key, backend, scheme)


@app.command()
def init(
    tenant_id: str,
    api_key: Annotated[str, typer.Option(prompt=True, hide_input=True)],
    backend: str | None = None,
):
    print(
        f"API keys can be found here: [bold]https://{backend}/{tenant_id}/_api_keys[/bold]"
    )
    settings.current_tenant = tenant_id
    if backend:
        settings.backend = backend
    else:
        settings.backend = backend
    keyring.set_password(APP_NAME, f"{tenant_id}:API-KEY", api_key)


@app.command()
def project(project_id: str | None = None):
    if not project_id:
        api_client = _get_api_client()
        projects = api_client.list_projects()
        for i, project in enumerate(projects):
            print(f"[bold]{i}[/bold]: {project['id']} ({project['name']})")
        selected = typer.prompt(f"Select project [0-{len(projects)-1}]")

        try:
            selected_nr = int(selected)
        except ValueError:
            selected_nr = None

        if selected_nr is None or selected_nr < 0 or selected_nr >= len(projects):
            print(f"Invalid project id ({selected}), aborting.")
            raise typer.Exit(code=1)
        project_id = projects[selected_nr]["id"]

    print(f"Setting active project to [bold]{project_id}[/bold]")
    settings.current_project = project_id


@app.command()
def status():
    backend = settings.backend
    current_tenant = settings.current_tenant
    api_key = keyring.get_password(APP_NAME, f"{current_tenant}:API-KEY")
    if not current_tenant or not api_key:
        print("Not initialized, please run:")
        print("[bold]sfis_tools init TENANT_ID[/bold]")
        raise typer.Exit(code=1)

    current_project = settings.current_project
    if not current_project:
        print("No project specified, please run:")
        print("[bold]sfis_tools project [PROJECT_ID][/bold]")
        raise typer.Exit(code=1)

    print(f"tenant: [bold]{current_tenant}[/bold]")
    print(f"project: [bold]{current_project}[/bold]")
    if backend:
        print(f"backend: [bold]{settings.backend}[/bold]")

    api_client = _get_api_client()
    try:
        info = api_client.project_info(current_project)
        print("api key: [green bold]valid[/green bold]")
        if info["success"]:
            print("project status: [green bold]valid[/green bold]")
        else:
            print(f"project status: [red bold]{info['error']}[/red bold]")

    except HTTPError as err:
        if err.code == 401:
            print("api key: [red bold]invalid[/red bold]")


@app.command()
def tags(
    tag: Annotated[
        list[click.Tuple] | None, typer.Option(click_type=click.Tuple([str, str]))
    ] = None
):
    print(tag)


@app.command()
def upload(
    device_id: str,
    file_path: Path,
    attachment: list[Path] | None = None,
    tag: Annotated[
        list[click.Tuple] | None, typer.Option(click_type=click.Tuple([str, str]))
    ] = None,
):
    tags = dict()
    if tag:
        tags |= dict(cast(list[tuple[str, str]], tag))
    tags["_original_size"] = str(file_path.stat().st_size)

    api_client = _get_api_client()
    api_client.ingest_device_file(
        settings.current_project, device_id, file_path, tags=tags
    )

# def log(
#     log_path: Path,
#     attachment: list[Path] | None = None,
#     tag: Annotated[
#         list[click.Tuple] | None, typer.Option(click_type=click.Tuple([str, str]))
#     ] = None,
# ):
#     if not log_path.exists():

#     # put logs in projects/<project>/<station>/<month>/device_timestamp>.csv
#     # metadata: device_id, station_id, tenant_id, project_id
