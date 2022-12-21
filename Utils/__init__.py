from . import __assets as _assets
from . import __utils as _utils
from .__utils import getBundledAssetPath
from .__autoStart import setStartup, getStartup


def getIconPath(proxyOn: bool) -> str:
    """
    Returns the bundled path of the icon to use for the system tray icon.
    """
    return getBundledAssetPath(
        _assets.getIconPath(proxyOn, not _utils.getTaskBarThemeIsLight())) # if taskbar theme is light, icon theme should be dark
