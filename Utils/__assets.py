from os import path as _osPath

_iconPath = "icon"
_iconFileMapping = {
    False: {
        True: "ladderIntactDark.ico",
        False: "ladderBrokenDark.ico",
    },
    True: {
        True: "ladderIntactLight.ico",
        False: "ladderBrokenLight.ico",
    }
}

def getIconPath(proxyOn: bool, themeLight: bool) -> str:
    """
    Returns the path of the icon to use for the system tray icon.
    """
    return _osPath.join(_iconPath, _iconFileMapping[themeLight][proxyOn])