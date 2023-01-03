from sys import exit as _exit
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import List as _List
from typing import Tuple as _Tuple

import qdarktheme as _qdarktheme
from PyQt6.QtGui import QAction as _QAction
from PyQt6.QtGui import QIcon as _QIcon
from PyQt6.QtGui import QIntValidator as _QIntValidator
from PyQt6.QtWidgets import QApplication as _QApplication
from PyQt6.QtWidgets import QDialog as _QDialog
from PyQt6.QtWidgets import QDialogButtonBox as _QDialogButtonBox
from PyQt6.QtWidgets import QLabel as _QLabel
from PyQt6.QtWidgets import QLineEdit as _QLineEdit
from PyQt6.QtWidgets import QMenu as _QMenu
from PyQt6.QtWidgets import QSystemTrayIcon as _QSystemTrayIcon
from PyQt6.QtWidgets import QVBoxLayout as _QVBoxLayout

# The type of the callback function for the tray icon
TrayCallbackType = _Callable[[], None]
TrayCheckedCallbackType = _Callable[[], bool]
TraySelectListCallbackType = _Callable[[str, int], None]


class TrayAction(_QAction):

    def __init__(self, parent: "TrayMenu", name: str,
                 callback: TrayCallbackType):
        super().__init__(name, parent)
        self.__callback = callback
        self.triggered.connect(self.__callback)


class TrayCheckAction(_QAction):

    def __init__(self,
                 parent: "TrayMenu",
                 name: str,
                 callback: TrayCheckedCallbackType,
                 startChecked: bool = False):
        super().__init__(name, parent)
        self.setCheckable(True)
        self.setChecked(startChecked)
        self.__callback = callback
        self.triggered.connect(self.__innerCallback)

    def __innerCallback(self) -> None:
        self.setChecked(self.__callback())

    # def setChecked(self, checked: bool):
    #     self.setChecked(checked)
    #     self.__callback()


class TraySelectList:

    def __init__(self, parent: "TrayMenu", selectables: _List[str],
                 callback: TraySelectListCallbackType):
        self.__actions: list[_QAction] = []
        self.__innerCallbackList: list[_Callable[[bool, str, int], None]] = []
        self.__callback = callback
        for i, name in enumerate(selectables):
            newCallback = lambda _, name=name, i=i: self.__medCallback(name, i)
            self.__innerCallbackList.append(newCallback)
            newAction = _QAction(name, parent)
            newAction.setCheckable(True)
            newAction.triggered.connect(self.__innerCallbackList[-1])
            self.__actions.append(newAction)
        self.__parent = parent

    def setChecked(self, index: int):
        for i, action in enumerate(self.__actions):
            action.setChecked(i == index)

    def getChecked(self) -> _Tuple[str, int]:
        for i, action in enumerate(self.__actions):
            if action.isChecked():
                return action.text(), i
        return "", -1

    def addAction(self, action: _QAction):
        raise NotImplementedError("Not implemented yet")

    #     self.__actions.append(action)
    #     self.__parent.refreshActionList()

    def __iter__(self):
        return self.__actions.__iter__()

    def __medCallback(self, name: str, i: int):
        self.__callback(name, i)
        for action in self.__actions:
            action.setChecked(False)
        self.__actions[i].setChecked(True)


class TrayMenu(_QMenu):

    def __init__(self, title: str = ""):
        super().__init__(title)
        self.__actionLists: _List[TraySelectList] = []
        self.__topActions: _List[_QAction] = []
        self.__bottomActions: _List[_QAction] = []

    def addTopAction(self, action: TrayAction):
        self.__topActions.append(action)
        self.refreshActionList()

    # TODO: implement this
    def addTopCheckAction(self, action: TrayCheckAction):
        self.__topActions.append(action)
        self.refreshActionList()

    def addBottomAction(self, action: TrayAction):
        self.__bottomActions.append(action)
        self.refreshActionList()

    def addActionList(self, actions: TraySelectList):
        self.__actionLists.append(actions)
        self.refreshActionList()

    def overwriteActionList(self, index: int, actions: TraySelectList):
        self.__actionLists[index] = actions
        self.refreshActionList()

    def clearActionLists(self):
        self.__actionLists.clear()
        self.refreshActionList()

    def refreshActionList(self):  # TODO: Optimize this
        for action in self.actions():
            self.removeAction(action)
        for action in self.__topActions:
            self.addAction(action)
        self.addSeparator()
        for actionList in self.__actionLists:
            for action in actionList:
                self.addAction(action)
            self.addSeparator()
        for action in self.__bottomActions:
            self.addAction(action)


class App:

    def __init__(self, name: str, iconPath: str | None = None):
        self.__app = _QApplication([])
        self.__app.setApplicationName(name)
        self.__app.setApplicationDisplayName(name)
        self.__app.setQuitOnLastWindowClosed(False)
        _qdarktheme.setup_theme("auto")
        _qdarktheme.setup_theme()
        
        self.__tray = _QSystemTrayIcon(self.__app)
        self.__tray.setIcon(_QIcon(iconPath))

    def setIcon(self, iconPath: str):
        self.__tray.setIcon(_QIcon(iconPath))

    def setTooltip(self, tooltip: str):
        self.__tray.setToolTip(tooltip)

    def setTrayMenu(self, menu: TrayMenu):
        self.__tray.setContextMenu(menu)

    def setDoubleClickCallback(self, callback: TrayCallbackType):
        self.__tray.activated.connect(lambda reason: callback(
        ) if reason == _QSystemTrayIcon.ActivationReason.DoubleClick else None)

    def run(self):
        self.__tray.show()
        self.__app.exec()

    def exit(self):
        self.__app.quit()
        _exit(0)


class InputPopup:  # popup window for multiple text edit and confirm or cancel. can use addTextInput() to add text input

    def __init__(self, title: str) -> None:
        self.__textInputs: _Dict[str, _Tuple[_QLabel, _QLineEdit]] = {}
        self.__dialog = _QDialog()
        self.__dialog.setWindowTitle(title)
        self.__dialog.setModal(True)
        self.__dialog.setFixedWidth(400)
        self.__description: str | None = None

    def addDescription(self, description: str) -> None:
        self.__description = description

    def addTextInput(
        self,
        name: str,
        default: str = "",
        isInt: bool = False,
        limit: _Tuple[int, int] = (-1000, 1000)) -> None:
        self.__textInputs[name] = (_QLabel(name), _QLineEdit(default))
        if isInt:
            self.__textInputs[name][1].setValidator(
                _QIntValidator(limit[0], limit[1]))

    def pop(self) -> _Tuple[bool, _Dict[str, str]]:
        self.__layout = _QVBoxLayout()
        if self.__description is not None:
            self.__layout.addWidget(_QLabel(self.__description))
        for name, textInput in self.__textInputs.items():
            self.__layout.addWidget(textInput[0])
            self.__layout.addWidget(textInput[1])
        self.__layout.addStretch()
        self.__buttonBox = _QDialogButtonBox(
            _QDialogButtonBox.StandardButton.Ok
            | _QDialogButtonBox.StandardButton.Cancel)
        self.__buttonBox.accepted.connect(self.__dialog.accept)
        self.__buttonBox.rejected.connect(self.__dialog.reject)
        self.__layout.addWidget(self.__buttonBox)
        self.__dialog.setLayout(self.__layout)
        if self.__dialog.exec() == _QDialog.DialogCode.Accepted:
            return True, {
                name: textInput[1].text()
                for name, textInput in self.__textInputs.items()
            }
        return False, {}


class AlertPopup:

    def __init__(self, title: str, description: str) -> None:
        self.__dialog = _QDialog()
        self.__dialog.setWindowTitle(title)
        self.__dialog.setModal(True)
        self.__dialog.setFixedWidth(400)
        self.__layout = _QVBoxLayout()
        self.__layout.addWidget(_QLabel(description))
        self.__buttonBox = _QDialogButtonBox(
            _QDialogButtonBox.StandardButton.Ok)
        self.__buttonBox.accepted.connect(self.__dialog.accept)
        self.__layout.addWidget(self.__buttonBox)
        self.__dialog.setLayout(self.__layout)

    def pop(self) -> None:
        self.__dialog.exec()
