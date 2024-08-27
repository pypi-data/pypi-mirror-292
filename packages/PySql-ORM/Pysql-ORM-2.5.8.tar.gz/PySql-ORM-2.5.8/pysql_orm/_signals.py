# -*- coding: utf-8 -*-
"""
#/*
##; Copyright (c) 2010, Pallets(BSD-3-Clause)
##; All rights reserved.
##; 
##; @@@Origin: https://github.com/pallets/flask/blob/main/src/flask/signals.py
##; 
##; This module is part of SQLAlchemy and is released under
##; the BSD-3-Clause License: https://opensource.org/license/bsd-3-clause
##; details as below:
#*
#* Redistribution and use in source and binary forms, with or without
#* modification, are permitted provided that the following conditions are met:
#*
#* 1. Redistributions of source code must retain the above copyright notice, this
#*    list of conditions and the following disclaimer.
#*
#* 2. Redistributions in binary form must reproduce the above copyright notice,
#*    this list of conditions and the following disclaimer in the documentation
#*    and/or other materials provided with the distribution.
#*
#* 3. Neither the name of the copyright holder nor the names of its
#*    contributors may be used to endorse or promote products derived from
#*    this software without specific prior written permission.
#*
#* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#* DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#* FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#*/
"""

import typing as t

try:
    from blinker import Namespace

    signals_available = True
except ImportError:
    signals_available = False

    class Namespace:  # type: ignore
        def signal(self, name: str, doc: t.Optional[str] = None) -> "_FakeSignal":
            return _FakeSignal(name, doc)

    class _FakeSignal:
        """If blinker is unavailable, create a fake class with the same
        interface that allows sending of signals but will fail with an
        error on anything else.  Instead of doing anything on send, it
        will just ignore the arguments and do nothing instead.
        """

        def __init__(self, name: str, doc: t.Optional[str] = None) -> None:
            self.name = name
            self.__doc__ = doc

        def send(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
            pass

        def _fail(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
            raise RuntimeError(
                "Signalling support is unavailable because the blinker"
                " library is not installed."
            ) from None

        connect = connect_via = connected_to = temporarily_connected_to = _fail
        disconnect = _fail
        has_receivers_for = receivers_for = _fail
        del _fail


# The namespace for code signals.  If you are not Flask code, do
# not put signals in here.  Create your own namespace instead.
_signals = Namespace()

models_committed = _signals.signal('models-committed')
before_models_committed = _signals.signal('before-models-committed')