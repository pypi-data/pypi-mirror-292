import dbm
import gzip
import json
import mimetypes

from functools import cache
from typing import Generator, NoReturn
from pathlib import Path

from dataclasses import dataclass, asdict

from urllib import request

from typing_extensions import Annotated

import typer
import keyring

from rich import print
from rich.text import Text

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
            typer.Exit(code=1)
        project_id = projects[selected_nr]["id"]

    print(f"Setting active project to [bold]{project_id}[/bold]")
    settings.current_project = project_id


@app.command()
def status(ctx: typer.Context):
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
    backend = settings.backend
    if backend:
        print(f"backend: [bold]{settings.backend}[/bold]")


@app.command()
def upload(device_id: str):
    api_client = _get_api_client()
    path = Path("doc8183.pdf")
    api_client.ingest_device_file(settings.current_project, device_id, path)
