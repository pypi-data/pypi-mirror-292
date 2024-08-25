from ipykernel.kernelbase import Kernel

from .debug_info import DEBUG_MODE
from .context import QLContext


# def do_execute(self, code, silent, store_history=True, user_expressions=None,
#                    allow_stdin=False):
class QLKernel(Kernel):
    implementation = 'ql-analysis'
    implementation_version = '0.0.1'
    language = 'python'
    language_version = '3'
    language_info = {
        'name': 'Any text',
        'mimetype': 'text/markdown',
        'file_extension': '.md',
    }
    banner = "清流内核，智能分析你的数据"
    __ql_ctx = None

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False, *, cell_meta=None, cell_id=None,):
        if self.__ql_ctx is None:
            self.__ql_ctx = QLContext(self)

        if not silent:
            try:
                self.__ql_ctx.handle_input(code)
            except Exception as e:
                stream_content = {'name': 'stdout', 'text': f"清流内核出现问题，请联系开发者 Error: str{e}"}
                self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

    # def do_debug_request(self, msg):
    #     self.send_debug_info(msg)

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        """DEPRECATED"""
        pass

    def do_clear(self):
        # TODO clear
        pass


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=QLKernel)

