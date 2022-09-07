import importlib
import os
import re
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(default_response_class=ORJSONResponse)

app.add_middleware(GZipMiddleware, minimum_size=1000)
origins = ['http://0.0.0.0:8080', 'http://0.0.0.0', 'http://0.0.0.0:8080/', 'http://localhost:8080', 'http://localhost',
           'http://localhost:8080/', 'http://127.0.0.1:8080', 'http://127.0.0.1', 'http://127.0.0.1:8080/']
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   allow_credentials=True)


class APIServiceRequest:
    def __init__(self):
        self.service_info = {}

    def name(self, name: str):
        self.service_info['name'] = name

    def port(self, port: int):
        self.service_info['port'] = port

    def websocket(self):
        self.service_info['websocket'] = True

    def add_packages(self, package: str):
        if 'packages' in self.service_info:
            packages = self.service_info['packages']
        else:
            packages = []
            self.service_info['packages'] = packages
        packages.append(package)

    def skip_auth(self):
        self.service_info['skip_auth'] = True


class APIService:
    def __init__(self, request: APIServiceRequest):
        self.request = request

    def start(self):
        self.load_api_module()
        service_info = self.request.service_info
        port = service_info['port'] if 'port' in service_info else 8181
        uvicorn.run(app, host="0.0.0.0", port=port)

    def load_api_module(self):
        service_info = self.request.service_info
        if 'packages' not in service_info:
            return
        packages = service_info['packages']
        for p in packages:
            m = importlib.import_module(p)
            curr_path = os.path.dirname(m.__file__)
            files = list(Path(curr_path).rglob("*.*"))
            for f in files:
                module = f.name
                search = re.finditer('__', f.as_posix())
                instances = [[m.start(), m.end()] for m in search]
                if len(instances) > 0:
                    continue
                module = re.sub("^\.", "", module.replace('/', '.'))
                index = module.find('.py')
                importlib.import_module(f"{p}.{module[:index]}")
