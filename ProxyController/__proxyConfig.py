from json import dump as _jsonDump
from json import load as _jsonLoad
from os import makedirs as _osMakedirs
from os import path as _osPath
from sys import executable as _sysExecutable
from typing import Dict as _Dict
from typing import List as _List
from typing import Tuple as _Tuple

configPath = ""


def _getConfigPath() -> str:
    global configPath
    if configPath == "":
        configPath = _osPath.join(_osPath.dirname(_sysExecutable),
                                  "conf/proxyConfig.json")
    return configPath


def _addToConfig(name: str, config: _Dict[str,
                                          str]) -> _Tuple[bool, str | None]:
    if not _osPath.exists(_getConfigPath()):
        _osMakedirs(_osPath.dirname(_getConfigPath()), exist_ok=True)
        with open(_getConfigPath(), "w") as f:
            _jsonDump({}, f, indent=4)
    with open(_getConfigPath(), "r") as f:
        data: _Dict[str, _Dict[str, str]] = _jsonLoad(f)
    for oldName, conf in data.items():
        if oldName == name:
            return False, "Name already exists"
        if conf["host"] == config["host"] and conf["port"] == config["port"]:
            return False, "Config already exists"
    data[name] = config
    with open(_getConfigPath(), "w") as f:
        _jsonDump(data, f, indent=4)
    return True, None


def _removeFromConfig(name: str) -> _Tuple[bool, str | None]:
    if not _osPath.exists(_getConfigPath()):
        return False, "config file does not exist"
    with open(_getConfigPath(), "r") as f:
        data: _Dict[str, _Dict[str, str]] = _jsonLoad(f)
    if name not in data:
        return False, "config does not exist"
    del data[name]
    with open(_getConfigPath(), "w") as f:
        _jsonDump(data, f, indent=4)
    return True, None


class ProxyConfig:

    def __init__(self,
                 name: str,
                 host: str | None = None,
                 port: int | None = None,
                 bypass: str | None = None,
                 confDict: _Dict[str, str] | None = None):
        self.__confDict: _Dict[str, str] = {}
        self.__name = name
        if confDict is not None:
            if host or port or bypass:
                raise ValueError("confDict and other args are exclusive")
            self.__confDict = confDict
        else:
            self.__confDict = {
                "host": host or "",
                "port": str(port) or "",
                "bypass": bypass or "",
            }

    def setName(self, name: str) -> None:
        self.__confDict["name"] = name

    def setHost(self, host: str) -> None:
        self.__confDict["host"] = host

    def setPort(self, port: int) -> None:
        self.__confDict["port"] = str(port)

    def setBypass(self, bypass: str) -> None:
        self.__confDict["bypass"] = bypass

    def saveToConf(self) -> _Tuple[bool, str | None]:
        return _addToConfig(self.__name, self.__confDict)

    def removeFromConf(self) -> _Tuple[bool, str | None]:
        return _removeFromConfig(self.__name)

    def getName(self) -> str:
        return self.__name

    def getHost(self) -> str:
        return self.__confDict["host"]

    def getPort(self) -> int:
        return int(self.__confDict["port"])

    def getBypass(self) -> str:
        return self.__confDict["bypass"]


def getProxyConfigList() -> _List[ProxyConfig]:
    if not _osPath.exists(_getConfigPath()):
        return []
    with open(_getConfigPath(), "r") as f:
        data: _Dict[str, _Dict[str, str]] = _jsonLoad(f)
    return [ProxyConfig(name, confDict=conf) for name, conf in data.items()]
