from openai import OpenAI
import openai
from .prompt_template import USER_DESC_PROMPT

PROMPT_TYPE_PYTHON = "python"
PROMPT_TYPE_SUGGESTION = "suggestion"
PROMPT_TYPE_FORMULAR = "formular"
PROMPT_TYPE_OP = "op"

SUPPORT_MODELS = {
    "moonshot-v1-8k": 4096,
    "moonshot-v1-32k": 16384,
    "moonshot-v1-128k": 65536
}

class KimiClient:
    __openai_client: OpenAI = None
    model_name: str = "moonshot-v1-128k"
    __python_prompt_messages: list = []
    __formular_prompt_messages: list = []
    __suggest_prompt_messages: list = []
    __op_prompt_messages: list = []
    __prompt_type_map: dict = {}
    __max_tokens: int = 65536
    __ctx = None
    ready = False

    def __init__(self, ctx):
        self.__ctx = ctx
        self.__python_prompt_messages = []
        self.__formular_prompt_messages = []
        self.__suggest_prompt_messages = []
        self.__op_prompt_messages = []
        self.__max_tokens = 65536
        self.model_name = "moonshot-v1-128k"
        self.__prompt_type_map = {
            PROMPT_TYPE_PYTHON: self.__python_prompt_messages,
            PROMPT_TYPE_FORMULAR: self.__formular_prompt_messages,
            PROMPT_TYPE_SUGGESTION: self.__suggest_prompt_messages,
            PROMPT_TYPE_OP: self.__op_prompt_messages,
        }

    def setup_kimi(self, key):
        self.__openai_client = OpenAI(
            api_key=key,
            base_url="https://api.moonshot.cn/v1",
        )
        self.ready = True

    def only_enqueue_prmpt(self, prompt_type, prompt_content, prompt_role="system") -> list:
        prompt_list = self.__prompt_type_map[prompt_type]
        new_msg = new_message(prompt_role, prompt_content)
        prompt_list.append(new_msg)
        return prompt_list

    def enqueue_prompt(self, prompt_type, prompt_content):
        # TODO control token length

        prompt_list = self.only_enqueue_prmpt(prompt_type, prompt_content, "user")
        # self.debug_sending_prompt(prompt_list)
        try:
            stream = self.__openai_client.chat.completions.create(
                model=self.model_name,
                messages=prompt_list,
                temperature=0.3,
                max_tokens=SUPPORT_MODELS[self.model_name],
                stream=True,
            )

            #self.__ctx.send_msg(completion.choices[0].message.content)
            ai_reply = ""
            # handle openai chunk
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    self.__ctx.send_msg(delta.content)
                    ai_reply += delta.content

            self.__ctx.send_msg("\n")
            reply_msg = new_message("assistant", ai_reply)
            prompt_list.append(reply_msg)

            if prompt_type == PROMPT_TYPE_PYTHON:
                self.__ctx.set_temp_replay(ai_reply)

        except openai.APIConnectionError:
            self.__ctx.send_msg("无法访问kimi服务")
        except openai.BadRequestError:
            self.__ctx.send_msg("请求kimi内容不正确")
        except openai.PermissionDeniedError:
            self.ready = False
            self.__ctx.send_msg("kimi的密钥错误")
        except openai.RateLimitError:
            self.__ctx.send_msg("请求kimi服务过快，达到上限，请稍等再使用")
        except openai.InternalServerError:
            self.__ctx.send_msg("kimi服务暂时不可用")

    def enqueue_user_desc_prompt(self, prompt_content):
        desc_prompt = USER_DESC_PROMPT.format(user_desc=prompt_content)
        for prompt_type in self.__prompt_type_map:
            self.only_enqueue_prmpt(prompt_type, desc_prompt, "user")

    def clear(self):
        self.__openai_client.close()

    def debug_sending_prompt(self, prompt_list):
        debug_info = ""
        for prompt in prompt_list:
            debug_info += ("content : {content}, role : {role}\n"
                           .format(content=prompt['content'], role=prompt['role']))
        self.__ctx.debug_msg(debug_info)


def new_message(role, content):
    return {
        "role": role,
        "content": content,
    }
