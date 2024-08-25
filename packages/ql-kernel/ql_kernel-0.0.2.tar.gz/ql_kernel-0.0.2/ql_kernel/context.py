from openai import OpenAI
from openai import AuthenticationError, APIConnectionError
import re
from .kimi import KimiClient
from .kimi import PROMPT_TYPE_PYTHON, PROMPT_TYPE_FORMULAR, PROMPT_TYPE_SUGGESTION, PROMPT_TYPE_OP
from .prompt_template import USER_PYTHON_PROMPT, USER_FORMULAR_PROMPT, USER_SUGGESTION_PROMPT, USER_OP_PROMPT
from .analyzer import Analyzer
from .debug_info import DEBUG_MODE
from ipykernel.kernelbase import Kernel
from openpyxl.utils.exceptions import InvalidFileException
import os

ERROR_COMMAND_NOT_SINGLE_LINE = "命令格式不正确, 必须为单行。"
ERROR_COMMAND_WRONG_FORMAT = "命令格式不正确。"
ERROR_COMMAND_NOT_SUPPORT = "不被支持的命令。"
ERROR_KIMI_WRONG_KEY = "认证失败，不正确的密钥，请查阅kimi开放平台相关文档。"
ERROR_KIMI_CONN_FAIL = "无法访问kimi服务"
ERROR_KIMI_NO_KEY = "未设置kimi服务密钥"
ERROR_EMPTY_FILE = "未设置要分析的文件"
ERROR_UNEXPECTED_ERROR = "未知错误，请联系清流整合器开发者"
ERROR_INVALID_EXCEL = "不正确的excel文件"
ERROR_INVALID_DATA_FORMAT = "数据格式无法被正确的读取"
ERROR_NOT_READY = "请先设置好kimi密钥和文件再进行分析"
ERROR_NOT_OUTPUT_FILE = "输出时需要指定文件名"
ERROR_INVALID_OUTPUT_FILE = "不是一个正确的文件路径"
ERROR_OUTPUT_FILE_EXIST = "输出指定的文件已经存在"
ERROR_OUTPUT_FILE_NOT_CSV = "输出文件必须是csv格式"
ERROR_PROMPT_EMPTY = "提示词不能为空"
ERROR_CODE_EMPTY = "没有代码可以执行"
ERROR_FILE_UNAVAILABLE = "该文件无法被输出"
ERROR_OUTPUT_DATA = "数据无法被输出成csv"
ERROR_FILE_HAS_SET = "文件已设置，如果想分析新的文件，请关闭本会话"
ERROR_FILE_NOT_FOUND = "文件不存在"

WARNING_NO_DATA_DES = ("强烈先使用##数据说明命令进行数据格式说明，\n"
                       "这能够得到更好的结果\n"
                       "否则AI可能给出错误的结果，或代码无法执行")

TIP_OPENAI_SET = "kimi客户端设置成功"
TIP_FILE_SET = "要分析的文件设置成功"
TIP_MODEL_SET = "模型设置成功"
TIP_READING = "读取中..."
TIP_OUTPUTTING = "输出中..."
TIP_DONE = "完成"
TIP_HELP = """ 帮助信息：
所有的命令都以##开头
（如果一个#会直接回传输出，没有#或者多于2个#会视为python代码直接执行）
支持的命令有：
{cmd_help}
可以通过 help 命令 查看单个命令的说明
"""
TIP_EXECUTING = "执行中..."
TIP_END = "已经结束，可以开启新会话"


class ReplayMsg:
    stream_func: None
    reply_msg: ""

class QLContext:
    __kimi_client: KimiClient = None
    __analyzer: Analyzer = None
    __cmd_map: dict = {}
    __msg_sender: Kernel = None
    __temp_code: str = ""
    __temp_error: str = ""
    __user_data_desc: str = ""

    def __init__(self, sender):
        self.__msg_sender = sender
        self.__analyzer = Analyzer(self)
        self.__kimi_client = KimiClient(self)
        self.__cmd_map = {
            # initial level cmd,
            "设置密钥":
                {"func": self.__set_key,
                 "need_ready": False,
                 "help": "设置调用kimi接口的密钥，请前往kimi开放平台获取"},

            # "设置Model": {"func": self.__set_model, "need_ready": False},
            "读取文件":
                {"func": self.__set_main_file,
                 "need_ready": False,
                 "help": "设置分析文件，必须为excel"},

            "帮助":
                {"func": self.__get_help,
                 "need_ready": False,
                 "help": "获取帮助信息"},

            "结束":
                {"func": self.__go_end,
                 "need_ready": False,
                 "help": "结束本次分析，释放资源"},
            # initial level cmd, need check ready
            "概览":
                {"func": self.__data_desc,
                 "need_ready": True,
                 "help": "输出数据概况"
                 },
            "输出表格":
                {"func": self.__output_data,
                 "need_ready": True,
                 "help": "输出刚刚代码的执行结果到csv文件"
                 },
            # "公式": None,
            "提示代码":
                {"func": self.__python_prompt,
                 "need_ready": True,
                 "help": "提示AI编写可以直接运行的代码"
                 },
            "执行代码":
                {"func": self.__exec_python_code,
                 "need_ready": True,
                 "help": "直接运行AI给出的代码"
                 },
            # "报告错误": None,
            # "总结": None,
            "提示思路":
                {"func": self.__suggestion_prompt,
                 "need_ready": True,
                 "help": "提示AI给出分析建议(无代码)"
                 },
            "提示公式":
                {"func": self.__formular_prompt,
                 "need_ready": True,
                 "help": "提示AI给出可以在excel中计算的公式"
                 },
            "提示操作":
                {"func": self.__op_prompt,
                 "need_ready": True,
                 "help": "提示AI给操作excel的建议，（无代码）"
                 },
            # "提示词": None,
            "数据说明":
                {"func": self.__user_desc,
                 "need_ready": True,
                 "help": "提示AI数据格式，强烈在使用AI给出进一步建议之前，先提示数据说明"
                 },
        }

    def handle_input(self, msg):
        # now, check how many # in the head of msg
        # if two it is cmd, otherwise it is python code
        hashes_count = count_leading_hashes(msg)
        if hashes_count == 2:
            # check if cmd is valid
            trim_msg = str.strip(msg[2:])

            instruction = parse_input(trim_msg)
            if len(instruction["command"]) == 0:
                self.send_tip(ERROR_COMMAND_WRONG_FORMAT)
                return
            else:
                if instruction["command"] not in self.__cmd_map:
                    self.send_tip(ERROR_COMMAND_NOT_SUPPORT)
                    return

                cmd_info = self.__cmd_map[instruction["command"]]
                if cmd_info["need_ready"] and not self.__check_ready():
                    self.send_tip(ERROR_NOT_READY)
                else:
                    cmd_info["func"](instruction["parameters"])
        elif hashes_count == 1:
            self.send_msg(msg)
        else:
            self.__do_exec_python(msg)

    def __exec_python_code(self, args):
        if len(self.__temp_code) == 0:
            self.send_tip(ERROR_CODE_EMPTY)
            return
        self.__analyzer.exec_python_code(self.__temp_code)
        return

    def __do_exec_python(self, msg):
        self.__analyzer.exec_python_code(msg)
        return

    def __set_key(self, arg: str):
        if len(arg) == 0:
            self.send_tip(ERROR_KIMI_NO_KEY)
            return
        try:
            self.__kimi_client.setup_kimi(arg)
        except AuthenticationError:
            self.send_tip(ERROR_KIMI_WRONG_KEY)
        except APIConnectionError as e:
            self.send_tip(ERROR_KIMI_CONN_FAIL, e)
        except Exception as e:
            self.send_tip(ERROR_UNEXPECTED_ERROR, e)
        self.send_tip(TIP_OPENAI_SET)

    def __set_model(self, arg: str):
        if len(arg) == 0:
            self.send_tip(ERROR_KIMI_NO_KEY)
            return
        self.__kimi_client.model_name = arg
        self.send_tip(TIP_MODEL_SET)
        return

    def __set_main_file(self, arg: str):
        if len(arg) == 0:
            self.send_tip(ERROR_EMPTY_FILE)
            return
        if self.__analyzer.ready:
            self.send_tip(ERROR_FILE_HAS_SET)
            return

        try:
            self.send_tip(TIP_READING)
            self.__analyzer.setup_file(arg)
        except InvalidFileException:
            self.send_tip(ERROR_INVALID_EXCEL)
        except AttributeError:
            self.send_tip(ERROR_INVALID_DATA_FORMAT)
        except FileNotFoundError:
            self.send_tip(ERROR_FILE_NOT_FOUND)
        except Exception as e:
            self.send_tip(ERROR_UNEXPECTED_ERROR, e)

        # init kimi system prompt base on file info
        python_system_prompt = self.__analyzer.form_initial_python_prompt()
        self.__kimi_client.only_enqueue_prmpt(PROMPT_TYPE_PYTHON, python_system_prompt)
        formular_system_prompt = self.__analyzer.form_initial_formular_prompt()
        self.__kimi_client.only_enqueue_prmpt(PROMPT_TYPE_FORMULAR, formular_system_prompt)
        suggest_system_prompt = self.__analyzer.form_initial_suggestion_prompt()
        self.__kimi_client.only_enqueue_prmpt(PROMPT_TYPE_SUGGESTION, suggest_system_prompt)
        op_system_prompt = self.__analyzer.form_initial_suggestion_prompt()
        self.__kimi_client.only_enqueue_prmpt(PROMPT_TYPE_OP, op_system_prompt)

        # output base info
        self.send_tip(TIP_DONE)
        info_str = self.__analyzer.info_str()
        self.send_tip(f"基本信息：\n{info_str}")

    def __get_help(self, arg):
        if len(arg) == 0:
            help_all_cmd = ""
            for k in self.__cmd_map:
                help_cmd = self.__cmd_map[k]['help']
                help_all_cmd += f"{k} : {help_cmd}\n"
            help_str = TIP_HELP.format(cmd_help=help_all_cmd)
            self.send_tip(help_str)
            return

        if arg not in self.__cmd_map:
            self.send_tip(ERROR_COMMAND_NOT_SUPPORT)
            return

        help_cmd = self.__cmd_map[arg]["help"]
        self.send_msg(help_cmd)

    def __go_end(self, arg):
        self.__analyzer.clear()
        self.__kimi_client.clear()
        self.__temp_code = ""
        self.__temp_error = ""
        self.__user_data_desc = ""

        self.__analyzer = Analyzer(self)
        self.__kimi_client = KimiClient(self)
        self.send_msg(TIP_END)

    def __data_desc(self, arg):
        info_str = self.__analyzer.data_summary()
        self.send_tip(info_str)

    def __output_data(self, arg):
        if len(arg) == 0:
            self.send_tip(ERROR_NOT_OUTPUT_FILE)
            return
        if os.path.exists(arg):
            self.send_tip(ERROR_OUTPUT_FILE_EXIST)
            return
        _, file_extension = os.path.splitext(arg)
        if not file_extension == ".csv":
            self.send_tip(ERROR_OUTPUT_FILE_NOT_CSV)
            return
        self.send_tip(TIP_OUTPUTTING)
        try:
            self.__analyzer.out_put_data(arg)
        except FileNotFoundError:
            self.send_tip(ERROR_FILE_UNAVAILABLE)
            return
        except ValueError:
            self.send_tip(ERROR_OUTPUT_DATA)
            return
        except Exception as e:
            self.send_tip(ERROR_UNEXPECTED_ERROR, e)
            return
        self.send_tip(TIP_DONE)

    def send_tip(self, des, err=None):
        if err is None:
            stream_content = {'name': 'stdout', 'text': des + "\n"}
            self.__msg_sender.send_response(self.__msg_sender.iopub_socket, 'stream', stream_content)
        else:
            msg = f"{des} Error: {str(err)}"
            stream_content = {'name': 'stdout', 'text': msg + "\n"}
            self.__msg_sender.send_response(self.__msg_sender.iopub_socket, 'stream', stream_content)

    def __check_ready(self) -> bool:
        return self.__kimi_client.ready and self.__analyzer.ready

    def __prompt_python_code(self, arg):
        if len(arg) == 0:
            self.send_tip(ERROR_PROMPT_EMPTY)
            return
        self.__kimi_client.enqueue_prompt(arg, PROMPT_TYPE_PYTHON)

    def __user_desc(self, arg):
        if len(arg) == 0:
            self.send_tip(ERROR_PROMPT_EMPTY)
            return
        self.__user_data_desc = arg
        self.__kimi_client.enqueue_user_desc_prompt(arg)
        self.send_tip(TIP_DONE)

    def send_msg(self, chuck):
        stream_content = {'name': 'stdout', 'text': chuck}
        self.__msg_sender.send_response(self.__msg_sender.iopub_socket, 'stream', stream_content)

    def code_exec_error(self, code, err):
        self.__temp_code = code
        self.__temp_error = str(err)
        stream_content = {'name': 'stdout', 'text': f"代码执行出错\n{self.__temp_error}"}
        self.__msg_sender.send_response(self.__msg_sender.iopub_socket, 'stream', stream_content)

    def debug_msg(self, msg):
        if not DEBUG_MODE:
            return
        stream_content = {'name': 'stdout', 'text': "debug: " + msg + "\n"}
        self.__msg_sender.send_response(self.__msg_sender.iopub_socket, 'stream', stream_content)

    def __python_prompt(self, arg):
        self.__tip_if_no_user_desc()
        self.__temp_code = ""
        fn = self.__analyzer.excel_filename
        prompt = USER_PYTHON_PROMPT.format(user_input=arg, filename=fn)
        self.__kimi_client.enqueue_prompt(PROMPT_TYPE_PYTHON, prompt)

    def __formular_prompt(self, arg):
        self.__tip_if_no_user_desc()
        prompt = USER_FORMULAR_PROMPT.format(user_input=arg)
        self.__kimi_client.enqueue_prompt(PROMPT_TYPE_FORMULAR, prompt)

    def __suggestion_prompt(self, arg):
        self.__tip_if_no_user_desc()
        prompt = USER_SUGGESTION_PROMPT.format(user_input=arg)
        self.__kimi_client.enqueue_prompt(PROMPT_TYPE_SUGGESTION, prompt)

    def __op_prompt(self, arg):
        self.__tip_if_no_user_desc()
        prompt = USER_OP_PROMPT.format(user_input=arg)
        self.__kimi_client.enqueue_prompt(PROMPT_TYPE_OP, prompt)

    def __tip_if_no_user_desc(self):
        if len(self.__user_data_desc) == 0:
            self.send_tip(WARNING_NO_DATA_DES)

    def set_temp_replay(self, msg):
        pattern = r'```python(.*?)```'
        matches = re.search(pattern, msg, re.DOTALL)
        if matches:
            self.__temp_code = matches.group(1).strip()

def count_leading_hashes(s: str):
    return len(s) - len(s.lstrip('#'))

def parse_input(user_input: str) -> dict:
    if len(user_input) == 0:
        return {"command": ""}

    match = re.split(r'\s+', user_input, maxsplit=1)
    if len(match) == 2:
        return {
            "command": match[0].strip(),
            "parameters": match[1].strip()
        }
    elif len(match) == 1:
        return {
            "command": match[0].strip(),
            "parameters": ""
        }
    else:
        return {
            "command": "",
        }