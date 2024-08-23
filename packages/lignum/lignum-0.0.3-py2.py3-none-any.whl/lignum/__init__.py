import json
import sys
import time
import typing

class Logger:
    def __init__(self, stream:typing.TextIO=sys.stderr):
        self.stream = stream
    def _log(self, message: str, level: str='debug', extra: dict={}):
        self.stream.write(json.dumps({'timestamp': int(time.time()), 'message': message, 'level': level } | extra))
    def debug(self, message: str, extra: dict={}): self._log(message, 'debug', extra)
    def error(self, message: str, extra: dict={}): self._log(message, 'error', extra)
    def fatal(self, message: str, extra: dict={}): self._log(message, 'fatal',  extra)
    def info(self, message: str, extra: dict={}): self._log(message, 'info', extra)
    def warn(self, message: str, extra: dict={}): self._log(message, 'warn', extra)
    def trace(self, message: str, extra: dict={}): self._log(message, 'trace', extra)
