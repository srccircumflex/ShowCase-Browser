from __future__ import annotations

import marshal
import pickle
import socket
from queue import Queue
from sys import stderr
from traceback import print_exception
from types import FunctionType
from typing import Callable, Any

from PyQt6.QtCore import QObject, pyqtSignal

try:
    from showcase import Showcase
except ImportError:
    pass


EOT = b"\x04"
PICKLE_PROTOCOL = 4
PICKLE_HEADER = b"\x80"
MARSHAL_VERSION = 4
MARSHAL_HEADER = b"\xE3"


class ServerSide(QObject):

    pipesig = pyqtSignal()

    def __init__(self, i_pipe: Queue[bytes], o_pipe: Queue[bytes], addr: tuple[str, int]):
        QObject.__init__(self)
        self.i_pipe = i_pipe
        self.o_pipe = o_pipe
        self.address = addr

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.address)
        self.socket.listen(1)

    def run(self):
        while True:
            conn, addr = self.socket.accept()
            data = b''
            with conn:
                while True:
                    d = conn.recv(1024)
                    data += d
                    if not d:
                        break
                    if d.endswith(EOT):
                        data = data[:-1]
                        break

                # send to the main thread for execution
                self.pipesig.emit()
                self.i_pipe.put(data)

                # from the main thread
                conn.sendall(self.o_pipe.get())


class Client:

    def __init__(self, server_addr: tuple[str, int]):
        self.server_addr = server_addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def com(self, exec: bytes | Callable[[Showcase, dict], Any] | object) -> dict:
        """
        Send an executable byte-string, object or function to the ``showcase``.

        Strings are executed via ``exec``, the ``showcase`` object can be accessed
        via the globals (`showcase` or `sc`). The response dict is created from the locals.

        Objects and functions are called and receive the storefront object as the
        first parameter and the response dict as the second parameter.

        Returns the response dict.
        """
        with self.socket:
            self.socket.connect(self.server_addr)
            msg = "[??]"
            if not isinstance(exec, bytes):
                try:
                    if (t := type(exec)) == FunctionType:
                        msg = f"{marshal} (version={MARSHAL_VERSION})"
                        exec = marshal.dumps(exec.__code__, MARSHAL_VERSION)
                    else:
                        msg = f"{pickle} (protocol={PICKLE_PROTOCOL})"
                        exec = pickle.dumps(exec, PICKLE_PROTOCOL)
                except Exception as e:
                    print_exception(e)
                    stderr.flush()
                    print(f"\nThe above error occurred when picking {exec} which has the type {t}.\nObjects of type {t} are picked with {msg} for the transaction.\n", file=stderr)
                    exit(1)
            self.socket.sendall(exec + EOT)
            exec = b""
            while d := self.socket.recv(1024):
                exec += d
            if exec:
                return pickle.loads(exec)
            else:
                return dict()

    def com_back(self):
        return self.com(b"sc.back()")

    def com_forward(self):
        return self.com(b"sc.forward()")

    def com_reload(self):
        return self.com(b"sc.reload()")

    def com_home(self):
        return self.com(b"sc.home()")

    def com_load(
            self,
            url: str,
            tab_index: int = None,
            tab_append: bool = None,
    ):
        if tab_append:
            return self.com(b"sc.tab_add(%r)" % url)
        elif tab_index is not None:
            return self.com(b"sc.tab_change(%d); sc.load(%r)" % (tab_index, url))
        else:
            return self.com(b"sc.load(%r)" % url)

    def com_stop_load(self):
        return self.com(b"sc.stop_load()")

    def com_quit(self):
        return self.com(b"sc.quit()")

    def com_tab_change(self, index: int):
        return self.com(b"sc.tab_change(%d)" % index)

    def com_tab_close(self, index: int):
        if index == -1:
            index = b"None"
        return self.com(b"sc.tab_close(%s)" % index)

    def com_ping(self):
        try:
            return self.com(b"pong = 1")
        except ConnectionError:
            return False
