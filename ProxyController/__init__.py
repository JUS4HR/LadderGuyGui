from typing import List as _List
from typing import Tuple as _Tuple

from .__proxyConfig import ProxyConfig
from .__proxyConfig import configPath as _configPath
from .__proxyConfig import getProxyConfigList as _getProxyConfigList
from .__proxyControl import queryCurrentProxy as queryCurrentProxy
from .__proxyControl import queryProxyState as queryProxyState
from .__proxyControl import setProxy as setProxy
from .__proxyControl import \
    setProxyStateWatchCallback as setProxyStateWatchCallback
from .__proxyControl import startWatchingProxyState as startWatchingProxyState
from .__proxyControl import stopWatchingProxyState as stopWatchingProxyState
from .__proxyControl import toggleProxyState as toggleProxyState

_defaultPass = [
    "192.168.x.x",
    "<local>",
]

_configList: _List[ProxyConfig] = []


def _getDefaultPass() -> str:
    """Used to prevent modification of the default bypass list

    Returns:
        str: A string containing the default bypass list, separated by semicolons
    """
    return ";".join(_defaultPass)


def reloadConfigList() -> None:
    """Reloads the config list from the config file

    Returns:
        bool: True if the config list was reloaded, False if the config file does not exist
    """
    global _configList
    _configList = _getProxyConfigList()


def setConfigPath(path: str) -> None:
    """Sets where to find the proxy config file.

    Args:
        path (str): The path to the proxy config file. Config name should be "proxyConfig.json"
    """
    global _configPath
    _configPath = path


def getConfigList() -> _Tuple[_List[ProxyConfig], int | None]:
    """Get a list of ProxyConfig objects and the index of the current config.

    Returns:
        _Tuple[_List[ProxyConfig], int | None]: A tuple containing a list of
        ProxyConfig objects and the index of the current config. If the current
        config is not in the list, the index will be None. 
    """
    reloadConfigList()
    host, port, _ = queryCurrentProxy()
    for i, config in enumerate(_configList):
        if config.getHost() == host and config.getPort(
        ) == port:  # bypass is not checked
            return _configList, i
    return _configList, None


def createNewConfigFromCurrent(name: str = "New Config") -> None:
    """Creates a new config from the current proxy settings.
    """
    origName = name
    i: int = 0
    host, port, bypass = queryCurrentProxy()
    while True:
        newConfig = ProxyConfig(name, host, port, bypass)
        if newConfig.saveToConf()[0]:
            break
        i += 1
        name = origName + f" ({i})"


def renameConfig(oldName: str, newName: str) -> _Tuple[bool, str | None]:
    """Renames a config.

    Args:
        oldName (str): The name of the config to rename
        newName (str): The new name of the config

    Returns:
        _Tuple[bool, str | None]: A tuple containing a boolean indicating whether
        the operation was successful and a string containing an error message if
        the operation was not successful.
    """
    newConf: ProxyConfig | None = None
    for config in _configList:
        if config.getName() == oldName:
            newConf = ProxyConfig(newName, config.getHost(), config.getPort(),
                                  config.getBypass())
            if not config.removeFromConf()[0]:
                return False, "failed to remove old config"
            break
    if newConf is None:
        return False, "config does not exist"
    return newConf.saveToConf()


def deleteConfig(name: str) -> _Tuple[bool, str | None]:
    """Deletes a config.

    Args:
        name (str): The name of the config to delete

    Returns:
        _Tuple[bool, str | None]: A tuple containing a boolean indicating whether
        the operation was successful and a string containing an error message if
        the operation was not successful.
    """
    for config in _configList:
        if config.getName() == name:
            return config.removeFromConf()
    return False, "config does not exist"
