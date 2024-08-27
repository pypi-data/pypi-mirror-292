import json
import mimetypes
import gzip

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

    def ingest_device_file(self, project_id: str, device_id: str, file_path: Path):
        url = self._project_url(project_id, "/device/" + device_id + "/ingest_url")
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"
        data = {
            "filename": str(file_path),
            "content_type": content_type,
            "metadata": {},
        }
        response = self._post(url, data, {"Content-Encoding": "gzip"})
        upload_url = response["url"]

        with open(file_path, "rb") as fp:
            comp = gzip.compress(fp.read())
            req = request.Request(upload_url, data=comp, method="PUT")
            req.add_header("Content-Type", content_type)
            req.add_header("Content-Encoding", "gzip")
            response = request.urlopen(req)
            text = response.read()
            print(text)



    def _url(self, path: str) -> str:
        return urlunparse((self._scheme, self._netloc, "/v0" + path, None, None, None))

    def _tenant_url(self, path: str) -> str:
        return self._url("/tenant/" + self._tenant + path)

    def _project_url(self, project_id: str, path: str) -> str:
        return self._tenant_url("/project/" + project_id + path)

    def _get(self, url: str) -> dict[str, Any]:
        req = request.Request(url, method="GET")
        req.add_header("Authorization", f"bearer {self._api_key}")
        response = request.urlopen(req)
        return json.loads(response.read())

    def _post(self, url: str, data: dict[str, Any], headers: dict[str, str] | None = None):
        req = request.Request(url, data=json.dumps(data).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"bearer {self._api_key}")
        if headers:
            for key, val in headers.items():
                req.add_header(key, val)
        response = request.urlopen(req)
        return json.loads(response.read())
