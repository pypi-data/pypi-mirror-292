# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import os

from bec_qthemes import material_icon
from qtpy.QtDesigner import QDesignerCustomWidgetInterface
from qtpy.QtGui import QGuiApplication, QIcon

import bec_widgets
from bec_widgets.examples.plugin_example_pyside.tictactoe import TicTacToe
from bec_widgets.examples.plugin_example_pyside.tictactoetaskmenu import TicTacToeTaskMenuFactory

DOM_XML = """
<ui language='c++'>
    <widget class='TicTacToe' name='ticTacToe'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>200</width>
                <height>200</height>
            </rect>
        </property>
        <property name='state'>
            <string>-X-XO----</string>
        </property>
    </widget>
</ui>
"""

MODULE_PATH = os.path.dirname(bec_widgets.__file__)


class TicTacToePlugin(QDesignerCustomWidgetInterface):  # pragma: no cover
    def __init__(self):
        super().__init__()
        self._form_editor = None

    def createWidget(self, parent):
        t = TicTacToe(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return "Games"

    def icon(self):
        palette = QGuiApplication.palette()
        pixmap = material_icon("sports_esports", color=palette.text().color(), filled=True)
        return QIcon(pixmap)

    def includeFile(self):
        return "tictactoe"

    def initialize(self, form_editor):
        self._form_editor = form_editor
        manager = form_editor.extensionManager()
        iid = TicTacToeTaskMenuFactory.task_menu_iid()
        manager.registerExtensions(TicTacToeTaskMenuFactory(manager), iid)

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._form_editor is not None

    def name(self):
        return "TicTacToe"

    def toolTip(self):
        return "Tic Tac Toe Example, demonstrating class QDesignerTaskMenuExtension (Python)"

    def whatsThis(self):
        return self.toolTip()
