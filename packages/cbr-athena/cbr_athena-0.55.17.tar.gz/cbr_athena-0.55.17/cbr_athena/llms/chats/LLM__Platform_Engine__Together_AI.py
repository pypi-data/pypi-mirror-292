from cbr_athena.llms.chats.LLM__Platform_Engine import LLM__Platform_Engine
from cbr_athena.llms.providers.together_ai.LLM__Together_AI import LLM__Together_AI
from cbr_athena.schemas.for_fastapi.LLMs__Chat_Completion import LLMs__Chat_Completion

class LLM__Platform_Engine__Together_AI(LLM__Platform_Engine):
    llm_platform       : str
    llm_provider       : str
    llm_model          : str
    llm_chat_completion: LLMs__Chat_Completion
    llm_together_ai    : LLM__Together_AI

    def execute_request(self):
        with self.llm_together_ai as _:
            _.add_messages__system(self.llm_chat_completion.system_prompts)
            _.add_histories       (self.llm_chat_completion.histories     )
            _.add_message__user   (self.llm_chat_completion.user_prompt   )
            _.set_model           (self.llm_model                         )
            _.set_stream          (self.llm_chat_completion.stream        )
            return _.chat_completion()



