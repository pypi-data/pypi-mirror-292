import openpyxl
import os
import pandas as pd
from .prompt_template import INITIAL_PYTHON_PROMPT, INITIAL_FORMULAR_PROMPT, INITIAL_SUGGESTION_PROMPT, INITIAL_OP_PROMPT
import io
import sys

# TODO csv mode

INIT_EXEC_IMPORT = """
import warnings
import openpyxl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

warnings.filterwarnings('ignore')

{ai_code}
"""

class FileFormatError(Exception):
    pass

class Analyzer:
    __excel_file_path: str = ""
    excel_filename: str = ""
    __user_exec_local_namespace: dict = {}
    __user_exec_global_namespace: dict = {}
    __excel_data: pd.DataFrame = {}
    __data_des: str = None
    __data_info: str = None
    ready = False
    __ctx = None
    __workbook = None
    __output_dataframe: pd.DataFrame = None

    def __init__(self, ctx):
        self.__ctx = ctx
        #exec(INIT_EXEC_IMPORT, self.__user_exec_local_namespace,
        #     self.__user_exec_global_namespace)

    def setup_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError
        fn, file_extension = os.path.splitext(file_path)
        if not file_extension == ".xlsx":
            raise FileFormatError("被分析的文件必须是xlsx格式")

        self.__excel_file_path = file_path
        self.excel_filename = fn
        # read excel and set header
        self.__workbook = openpyxl.load_workbook(file_path)
        self.__reset_df()

        df = self.__excel_data
        buffer = io.StringIO()
        df.info(buf=buffer)
        self.__data_info = buffer.getvalue()
        self.__data_des = df.describe().to_string()
        # set exec() local df
        self.ready = True

    def info_str(self) -> str:
        return self.__data_info

    def data_summary(self) -> str:
        return self.__data_des
        # return """
        #     行数：
        #     列数：
        #     列名：
        #     占用内存：
        #     唯一值等...
        # """

    def out_put_data(self, filename):
        if self.__output_dataframe is None or self.__output_dataframe.empty:
            self.__ctx.send_msg("空Dataframe，无输出\n")
            return
        self.__output_dataframe.to_csv(filename, index=False, encoding='utf-8-sig')

    def form_initial_python_prompt(self) -> str:
        return INITIAL_PYTHON_PROMPT.format(
            filename=self.__excel_file_path,
            data_profile=self.__data_des,
        )

    def form_initial_suggestion_prompt(self) -> str:
        return INITIAL_SUGGESTION_PROMPT.format(
            data_profile=self.__data_des,
        )

    def form_initial_formular_prompt(self) -> str:
        return INITIAL_FORMULAR_PROMPT.format(
            data_profile=self.__data_des,
        )

    def form_initial_op_prompt(self) -> str:
        return INITIAL_OP_PROMPT.format(
            data_profile=self.__data_des,
        )

    def exec_python_code(self, code):
        self.__reset_df()
        self.__user_exec_global_namespace["df"] = self.__excel_data
        self.__user_exec_global_namespace["output_df"] = pd.DataFrame()
        output = io.StringIO()
        original_stdout = sys.stdout
        result = ""
        exec_code = INIT_EXEC_IMPORT.format(ai_code=code)
        try:
            sys.stdout = output
            exec(exec_code, self.__user_exec_local_namespace, self.__user_exec_global_namespace)
            result = output.getvalue()
        except Exception as e:
            self.__ctx.code_exec_error(code, e)
        finally:
            sys.stdout = original_stdout
            output.close()
        self.__output_dataframe = self.__user_exec_global_namespace["output_df"]
        self.__ctx.send_msg(f"代码执行结果\n{result}")

    def __reset_df(self):
        active_sheet = self.__workbook.active
        df = pd.DataFrame(active_sheet.values)
        df.columns = df.iloc[0]
        self.__excel_data = df[1:]
        # self.__output_dataframe = pd.DataFrame()

    def clear(self):
        self.__workbook.close()