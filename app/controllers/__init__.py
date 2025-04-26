from fastapi import FastAPI, Depends

from . import users_controller


class AppRouters:
    def __init__(self):
        self.app = None
        self.api_prefix = '/api'

    def start_router(self, app: FastAPI):
        self.app = app
        self.__include_routes()

    def __include_routes(self):
        self.app.include_router(router=users_controller.router, prefix=self.api_prefix, tags=['Users'])


app_routers = AppRouters()
