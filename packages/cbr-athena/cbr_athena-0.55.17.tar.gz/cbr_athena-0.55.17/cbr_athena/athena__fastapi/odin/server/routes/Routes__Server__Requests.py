from functools import wraps

from fastapi import Depends, Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.responses import JSONResponse

from cbr_athena.athena__fastapi.CBR__Session_Auth   import cbr_session_auth
from osbot_fast_api.api.Fast_API_Routes             import Fast_API_Routes
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Status import status_error

ROUTES_PATHS__SERVER_REQUESTS = ['/request-data', '/requests-ids', '/requests-data']
ROUTE_PATH__SERVER_REQUESTS   = 'requests'

api_key_header   = APIKeyHeader(name="Authorization", auto_error=False)



class Routes__Server__Requests(Fast_API_Routes):

    tag : str = ROUTE_PATH__SERVER_REQUESTS

    def request_data(self, request_id: str, request: Request = None):
        http_events  = request.state.http_events
        requests_data = http_events.requests_data
        request_data = requests_data.get(request_id)
        if request_data:
            return request_data
        else:
            return status_error(f"no request found with id: {request_id}")

    def requests_ids(self, request: Request):

        if request:
            http_events  = request.state.http_events
            requests_ids = http_events.requests_order
            return requests_ids
        return []

    # def requests_ids(self, request: Request = None, session_data: str = Depends(cbr_session_auth.admins_only)):
    #     if request:
    #         http_events  = request.state.http_events
    #         requests_ids = http_events.requests_order
    #         return requests_ids
    #     return []

    def requests_data(self, request: Request = None):
        if request:
            try:
                http_events   = request.state.http_events
                requests_data = http_events.requests_data
                return requests_data
            except Exception as error:
                return status_error(f"Error in requests_data: {error}")
        return {}

    def setup_routes(self):
        self.add_route_get(self.request_data )
        self.add_route_get(self.requests_ids )
        self.add_route_get(self.requests_data)
        return self