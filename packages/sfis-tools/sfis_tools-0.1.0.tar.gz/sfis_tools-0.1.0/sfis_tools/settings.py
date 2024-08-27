import dbm

from pathlib import Path

from platformdirs import user_config_dir

from sfis_tools.info import APP_NAME


def _user_config_file(filename: str) -> str:
    config_dir = Path(user_config_dir(APP_NAME))
    config_dir.mkdir(exist_ok=True)
    return str(Path(user_config_dir(APP_NAME)) / filename)


def _get_user_setting(setting: str) -> str | None:
    db_path = _user_config_file("settings_v1")
    with dbm.open(db_path, "c") as db:
        value = db.get(setting)
        if value is None:
            return None
        return value.decode()


def _set_user_setting(setting: str, value: str | None) -> str | None:
    db_path = _user_config_file("settings_v1")
    with dbm.open(db_path, "c") as db:
        if value is None:
            if setting in db:
                del db[setting]
        else:
            db[setting] = value.encode()


class Settings:

    def __init__(self):
        pass

    @property
    def current_tenant(self) -> str | None:
        return _get_user_setting("tenant_id")

    @current_tenant.setter
    def current_tenant(self, tenant_id: str):
        _set_user_setting("tenant_id", tenant_id)

    @property
    def current_project(self) -> str | None:
        return _get_user_setting("project_id")

    @current_project.setter
    def current_project(self, tenant_id: str):
        _set_user_setting("project_id", tenant_id)

    @property
    def backend(self) -> str | None:
        return _get_user_setting("backend")

    @backend.setter
    def backend(self, tenant_id: str | None):
        _set_user_setting("backend", tenant_id)
