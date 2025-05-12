from fastapi import FastAPI

from . import users_controller, files_controller
from . import reports_controller


class AppRouters:
    def __init__(self):
        self.app = None
        self.api_prefix = '/api'

    def start_router(self, app: FastAPI):
        self.app = app
        self.__include_routes()

    def __include_routes(self):
        self.app.include_router(router=users_controller.router, prefix=self.api_prefix, tags=['Users'])
        self.app.include_router(router=reports_controller.router, prefix=self.api_prefix, tags=['Reports'])
        self.app.include_router(router=files_controller.router, prefix=self.api_prefix, tags=['Files'])


app_routers = AppRouters()
