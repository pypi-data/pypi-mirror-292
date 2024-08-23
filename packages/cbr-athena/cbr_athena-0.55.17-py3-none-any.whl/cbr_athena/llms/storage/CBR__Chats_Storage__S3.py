from cbr_athena.aws.s3.S3_DB_Base                           import S3_DB_Base
from cbr_athena.schemas.for_fastapi.LLMs__Chat_Completion   import LLMs__Chat_Completion
from cbr_athena.config.CBR__Config__Athena                  import cbr_config_athena
from cbr_athena.utils._for_osbot.for_osbot_utils            import date_today
from osbot_utils.base_classes.Type_Safe                     import Type_Safe
from osbot_utils.helpers.Local_Caches                       import Local_Caches
from osbot_utils.utils.Dev                                  import pprint
from osbot_utils.utils.Files import path_combine, folder_create, current_temp_folder, path_combine_safe
from osbot_utils.utils.Json                                 import from_json_str
from osbot_utils.utils.Misc                                 import is_guid, random_guid, date_time_now

CACHE_NAME__CHATS_CACHE =  'chats_cache'
#CACHE_NAME__CHATS_CACHE =  'chats_cache/2024-07-16'

class CBR__Chats_Storage__S3(Type_Safe):
    s3_db_base : S3_DB_Base

    def __init__(self):
        super().__init__()

    # todo: use this version instead of the one in CBR__Chats_Storage__Local
    def s3_chat_save(self, chat_id, chat_data):
        if cbr_config_athena.aws_disabled():                # todo: add special flag to capture the chat save
            return False
        try:
            print("---------- Saving CHAT to S3 ---------")
            s3_key     = self.s3_key_for_cache_id(chat_id)
            data       = chat_data
            self.s3_db_base.s3_save_data(data, s3_key)

            print('s3_bucket', self.s3_db_base.s3_bucket())
            print('s3_key'   , s3_key   )
            return s3_key

        except Exception as error:
            pprint(f'error in saving chat to s3: {error}')

    # todo: add support for calculating the self.chat value (which is pointing to the current date
    def s3_key_for_cache_id(self, chat_id):
        pprint(f"Saved chat with id: {chat_id}")
        s3_key = self.chat(chat_id).path_cache_file().replace(current_temp_folder(), '')
        return s3_key[1:]

    def folders__days(self):
        return self.s3_db_base.s3_folder_list(CACHE_NAME__CHATS_CACHE)

    def folder__chat_ids(self, day):
        s3_path = path_combine_safe(CACHE_NAME__CHATS_CACHE, day)
        if s3_path:
            return self.s3_db_base.s3_folder_files(s3_path)