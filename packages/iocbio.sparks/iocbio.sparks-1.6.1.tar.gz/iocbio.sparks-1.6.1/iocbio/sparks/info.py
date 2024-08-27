# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#
from PySide6.QtCore import Signal, QObject
import PySide6.QtCore as QC

infoHub = None


class Info(QObject):
    sigInfo = Signal(str)
    sigWarning = Signal(str)
    sigError = Signal(str, str, str)  # header, short message, long message

    # internal signal, don't use it outside
    _sig = Signal(int, dict)

    def __init__(self):
        QObject.__init__(self)

        self._sig.connect(self.onUpdate, QC.Qt.QueuedConnection)

    def info(self, message):
        self._sig.emit(0, {"message": message})

    def warning(self, message):
        self._sig.emit(1, {"message": message})

    def error(self, header, short, message):
        self._sig.emit(-1, {"header": header, "short": short, "message": message})

    def onUpdate(self, t, m):
        if t == 0:
            self.sigInfo.emit(m["message"])
        elif t == 1:
            self.sigWarning.emit(m["message"])
        elif t == -1:
            self.sigError.emit(m["header"], m["short"], m["message"])
        # print(m)


def info(message):
    infoHub.info(message)


def warning(message):
    infoHub.warning(message)


def error(header, short, message):
    infoHub.error(header, short, message)
