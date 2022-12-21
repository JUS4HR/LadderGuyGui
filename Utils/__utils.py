import sys as _sys
from os import path as _osPath
from sys import argv as _argv
from winreg import HKEY_CURRENT_USER as _HKCU
from winreg import OpenKey as _OpenKey
from winreg import QueryValueEx as _QueryValueEx

_themeKey = "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
_taskBarThemeVar = "SystemUsesLightTheme"
_appThemeVar = "AppsUseLightTheme"

def getBundledAssetPath(relativePath: str)-> str:
    """
    Returns the path of a file in the packed assets folder.
    """
    bundleDir = getattr(_sys, '_MEIPASS', _osPath.abspath(_osPath.dirname(_argv[0])))
    return _osPath.abspath(_osPath.join(bundleDir, relativePath))

def getTaskBarThemeIsLight() -> bool:
    """
    Returns whether current taskbar theme is light.
    """
    with _OpenKey(_HKCU, _themeKey) as key:
        state, _ = _QueryValueEx(key, _taskBarThemeVar)
    return int(state) != 0

def getAppThemeIsLight() -> bool:
    """
    Returns whether current app theme is light.
    """
    with _OpenKey(_HKCU, _themeKey) as key:
        state, _ = _QueryValueEx(key, _appThemeVar)
    return int(state) != 0