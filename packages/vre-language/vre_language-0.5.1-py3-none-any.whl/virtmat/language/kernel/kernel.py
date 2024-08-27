"""This module contains a simple version of an IPython kernel
for the virtmat language
"""
from ipykernel.kernelbase import Kernel
from ipykernel.kernelapp import IPKernelApp
from fireworks import LaunchPad
from fireworks.fw_config import LAUNCHPAD_LOC
from virtmat.language.interpreter.session import Session
from virtmat.language.utilities.errors import error_handler
from virtmat.language.utilities.textx import GRAMMAR_LOC

lpad = LaunchPad.from_file(LAUNCHPAD_LOC) if LAUNCHPAD_LOC else LaunchPad()


class VMKernel(Kernel):
    """This is the actual virtmat kernel class, derived from the Kernel
    class in ipykernel.kernelbase
    """
    implementation = 'Virtmat'
    implementation_version = '0.1'
    language = 'virtmat'
    language_version = '0.1'
    language_info = {
        'name': 'virtmat',
        'mimetype': 'text/plain',
        'file_extension': '.vm',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vmlang_session = Session(lpad, grammar_path=GRAMMAR_LOC,
                                      create_new=True, autorun=True)
        self.memory = ['print', 'use']

    banner = "Virtmat Kernel - a tool for material sciences"

    @error_handler
    def get_model_value(self, *args, **kwargs):
        """wrapped and evaluated version of get_model() of the Session class"""
        return getattr(self.vmlang_session.get_model(*args, **kwargs), 'value', '')

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False, *, cell_meta=None, cell_id=None):

        if not any(word in code for word in ('print', 'use', 'to', '=', '#')):
            # ipython-like print statement
            code = f'print({code})'

        output = self.get_model_value(code)
        name_list = self.vmlang_session.model.name_list

        if name_list:
            for name_ in filter(lambda x: x not in self.memory, name_list):
                self.memory.append(name_)

        if not silent:
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}
                }

    def do_complete(self, code, cursor_pos):
        code = code[:cursor_pos]
        default = {'matches': [], 'cursor_start': 0, 'cursor_end': cursor_pos,
                   'metadata': {}, 'status': 'ok'}

        for char in [';', '(', ')', '=', '**', '*', '/', '+', '-']:
            code = code.replace(char, ' ')

        tokens = code.split()
        if not tokens:
            return default

        token = tokens[-1]
        start = cursor_pos - len(token)

        matches = self.memory
        if not matches:
            return default
        matches = [m for m in matches if m.startswith(token)]

        return {'matches': sorted(matches), 'cursor_start': start,
                'cursor_end': cursor_pos, 'metadata': {},
                'status': 'ok'}

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        raise NotImplementedError

    def do_clear(self):
        raise NotImplementedError

    async def do_debug_request(self, msg):
        raise NotImplementedError


if __name__ == '__main__':
    IPKernelApp.launch_instance(kernel_class=VMKernel)
