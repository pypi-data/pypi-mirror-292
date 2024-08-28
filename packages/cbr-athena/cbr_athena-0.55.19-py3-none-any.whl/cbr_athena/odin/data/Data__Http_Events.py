from fastapi import Request

from osbot_fast_api.api.Fast_API__Http_Events   import Fast_API__Http_Events
from osbot_fast_api.api.Fast_API__Request_Data  import Fast_API__Request_Data
from osbot_utils.base_classes.Type_Safe         import Type_Safe
from osbot_utils.utils.Dev                      import pprint
from osbot_utils.utils.Misc                     import list_set


class Data__Http_Events(Type_Safe):
    http_events : Fast_API__Http_Events

    def requests_id(self):
        return self.http_events.requests_order

    def requests_data(self):
        requests_data = self.http_events.requests_data
        items = []
        ['fast_api_name', 'messages', 'request_duration', 'request_host_name',
         'request_id', 'request_method', 'request_port', 'request_start_time',
         'request_url', 'response_content_length', 'response_content_type', 'response_end_time',
         'response_status_code', 'thread_id', 'timestamp', 'traces']
        for request_id, request_data  in requests_data.items():
            request_data : Fast_API__Request_Data
            with request_data as _:
                item = dict(method        = _.request_method          ,
                            url           = _.request_url             ,
                            content_type  = _.response_content_type   ,
                            size          = _.response_content_length ,
                            duration      = _.request_duration        ,
                            status_codev  = _.response_status_code    ,
                            messages      = _.messages()              ,
                            host_name     = _.request_host_name       ,
                            traces        = _.traces_count            )
                items.append(item)
        return items

    # def http_events(self):
    #     if
    #     if hasattr(self.request.state, 'http_events'):
    #         return self.request.state.http_events