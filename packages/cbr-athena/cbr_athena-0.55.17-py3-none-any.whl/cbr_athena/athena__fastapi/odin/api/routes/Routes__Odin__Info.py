from cbr_athena.athena__fastapi.odin.FastApi_Header_Auth import route_with_auth
from cbr_athena.athena__fastapi.odin.api.Odin__EC2      import Odin__EC2
from cbr_athena.athena__fastapi.routes.Fast_API_Route   import Fast_API__Routes
from cbr_athena.llms.LLMs_API import LLMs_API
from cbr_athena.utils.Version import Version
from osbot_utils.utils.Status import status_ok, status_error

FAST_API_ROUTES__ODIN__API__CONFIG =  ['/config/config/version']



class Routes__Odin__Info(Fast_API__Routes):
    path_prefix: str = "config"

    def __init__(self):
        super().__init__()

    def add_routes(self):
        @route_with_auth(self.router, 'get', '/config/version', summary="What is the current version of this server")
        def version():
            return Version().version()