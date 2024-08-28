import json
import mimetypes
import gzip
import zlib

from typing import Any, Literal
from pathlib import Path


from urllib import request
from urllib.parse import urlunparse

mimetypes.init()


class ApiClient:

    def __init__(
        self,
        tenant: str,
        api_key: str,
        netloc: str,
        scheme: Literal["http", "https"] = "https",
    ):
        self._tenant = tenant
        self._api_key = api_key
        self._netloc = netloc
        self._scheme = scheme

    def list_projects(self) -> list[dict[str, Any]]:
        """List all projects for the active key"""
        url = self._tenant_url("/projects")
        res = self._get(url)
        return res["projects"]

    def project_info(self, project_id: str):
        url = self._project_url(project_id, "/status")
        return self._get(url)

    def ingest_device_file(
        self,
        project_id: str,
        device_id: str,
        file_path: Path,
        tags: dict[str, str] | None = None,
    ):
        url = self._project_url(project_id, "/device/" + device_id + "/ingest_url")
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"

        data = {
            "filename": file_path.name,
            "content_type": content_type,
            "tags": tags or {},
        }

        response = self._post(url, data, {"Content-Encoding": "gzip"})
        upload_url = response["url"]
        headers = response["headers"]

        with open(file_path, "rb") as fp:
            comp_obj = zlib.compressobj(wbits=16 + zlib.MAX_WBITS)

            def chunk():
                while True:
                    data = fp.read(2**20)
                    if not data:
                        yield comp_obj.flush()
                        break
                    yield comp_obj.compress(data)

            req = request.Request(
                upload_url, data=chunk(), method="PUT", headers=headers
            )
            with request.urlopen(req):
                pass

    def _url(self, path: str) -> str:
        return urlunparse((self._scheme, self._netloc, "/v0" + path, None, None, None))

    def _tenant_url(self, path: str) -> str:
        return self._url("/tenant/" + self._tenant + path)

    def _project_url(self, project_id: str, path: str) -> str:
        return self._tenant_url("/project/" + project_id + path)

    def _get(self, url: str) -> dict[str, Any]:
        headers = {
            "Authorization": f"bearer {self._api_key}",
        }
        req = request.Request(url, method="GET", headers=headers)
        with request.urlopen(req) as response:
            return json.loads(response.read())

    def _post(
        self, url: str, data: dict[str, Any], headers: dict[str, str] | None = None
    ):
        if headers is None:
            headers = {}
        headers |= {
            "Content-Type": "application/json",
            "Authorization": f"bearer {self._api_key}",
        }
        req = request.Request(
            url, data=json.dumps(data).encode(), method="POST", headers=headers
        )
        with request.urlopen(req) as response:
            return json.loads(response.read())
