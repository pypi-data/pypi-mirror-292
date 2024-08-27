from functools import wraps
from typing import Literal

from fastapi import Depends, Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.responses import JSONResponse

from cbr_athena.athena__fastapi.CBR__Session_Auth   import cbr_session_auth
from osbot_fast_api.api.Fast_API_Routes             import Fast_API_Routes
from osbot_utils.helpers.Print_Table import Print_Table
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Status import status_error

ROUTES_PATHS__SERVER_REQUESTS = ['/request-data', '/requests-ids', '/requests-data']
ROUTE_PATH__SERVER_REQUESTS   = 'requests'

api_key_header      = APIKeyHeader(name="Authorization", auto_error=False)
LITERAL_RETURN_TYPE = Literal['dict', 'table', 'list']

class Routes__Server__Requests(Fast_API_Routes):

    tag : str = ROUTE_PATH__SERVER_REQUESTS

    def request_data(self,  request: Request = None, request_id: str='', request_index: int=-1,return_type: LITERAL_RETURN_TYPE  = 'json'):
        http_events  = request.state.http_events
        requests_data = http_events.requests_data
        if not request_id and request_index > -1:
            if len(http_events.requests_order) > request_index:
                request_id = http_events.requests_order[request_index]
            else:
                return status_error(f"no request found with index: {request_index}")
        request_data = requests_data.get(request_id)
        if request_data:
            return self.request_data__to_return_type(request_data, return_type)
        else:
            return status_error(f"no request found with id: {request_id}")

    def request_data__to_return_type(self, request_data, return_type:LITERAL_RETURN_TYPE):
        if return_type == 'table':
            data = []
            for key, value in request_data.json().items():
                if type(value) in [list, dict]:
                    value = value.__str__()
                data.append(dict(key=key, value=value))

            print_table = Print_Table()
            print_table.add_data(data)
            print_table.max_cell_size = 50
            print_table.map_texts()
            title   = 'Request Data'
            return dict(headers = print_table.headers ,
                        rows    = print_table.rows    ,
                        title   = title   )
        return request_data

    def requests_ids(self, request: Request,  return_type: LITERAL_RETURN_TYPE  = 'json'):
        requests_ids = []
        if request:
            http_events  = request.state.http_events
            requests_ids = http_events.requests_order

        return self.requests_id__to_return_type(requests_ids, return_type)

    def requests_id__to_return_type(self, requests_ids, return_type:LITERAL_RETURN_TYPE):
        if return_type == 'table':
            headers = ['#', 'Request ID']
            rows    = ( [index + 1, request_id] for index, request_id in enumerate(requests_ids))
            title   = 'Requests Ids (ordered)'
            return dict(headers =  headers,
                        rows    =  rows   ,
                        title   = title   )
        return requests_ids


    def requests_data(self, request: Request = None, return_type:LITERAL_RETURN_TYPE='json'):
        if request:
            try:
                http_events   = request.state.http_events
                requests_data = http_events.requests_data

                return self.requests_data__to_return_type(requests_data, return_type)
            except Exception as error:
                return status_error(f"Error in requests_data: {error}")
        return {}

    def requests_data__to_return_type(self, requests_data, return_type:LITERAL_RETURN_TYPE):
        if return_type == 'table':
            values = [request_data.json() for request_id, request_data in requests_data.items()]
            for index, value in enumerate(values):
                value['#'] = index + 1
            print_table = Print_Table()
            print_table.add_data(values)
            print_table.max_cell_size = 50
            print_table.map_texts()
            title = 'Request Data'

            return dict(headers = print_table.headers,
                        rows    = print_table.rows   ,
                        title   = title              )
        return requests_data

    def setup_routes(self):
        self.add_route_get(self.request_data )
        self.add_route_get(self.requests_ids )
        self.add_route_get(self.requests_data)
        return self