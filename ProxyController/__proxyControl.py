from threading import Thread as _Thread
from typing import Callable as _Callable
from typing import Tuple as _Tuple
from winreg import HKEY_CURRENT_USER as _HKCU
from winreg import KEY_ALL_ACCESS as _KAA
from winreg import REG_DWORD as _RDWs
from winreg import REG_SZ as _RSZ
from winreg import CloseKey as _CloseKey
from winreg import OpenKey as _OpenKey
from winreg import QueryValueEx as _QueryValueEx
from winreg import SetValueEx as _SetValueEx

from win32api import REG_NOTIFY_CHANGE_LAST_SET as _REG_NOTIFY_CHANGE_LAST_SET
from win32api import RegNotifyChangeKeyValue as _RegNotifyChangeKeyValue

_proxyKey: str = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
_proxyHostVar: str = 'ProxyServer'
_proxyBypassVar: str = 'ProxyOverride'
_proxyEnabledVar: str = 'ProxyEnable'

_proxyWatchStateCallback: _Callable[[bool], None] | None = None
_watching = False

_proxyStateWatchThread: _Thread | None = None


def setProxy(host: str, port: int, bypass: str | None = None) -> None:
    hostStr = f'{host}:{port}'
    with _OpenKey(_HKCU, _proxyKey, 0, _KAA) as key:
        _SetValueEx(key, _proxyHostVar, 0, _RSZ, hostStr)
        _SetValueEx(key, _proxyBypassVar, 0, _RSZ, bypass or '')
        _CloseKey(key)


def queryCurrentProxy() -> _Tuple[str, int, str]:
    with _OpenKey(_HKCU, _proxyKey) as key:
        hostStr, _ = _QueryValueEx(key, _proxyHostVar)
        bypass, _ = _QueryValueEx(key, _proxyBypassVar)
        _CloseKey(key)
    host, port = hostStr.split(':')
    return host, int(port), bypass


def queryProxyState() -> bool:
    with _OpenKey(_HKCU, _proxyKey) as key:
        state, _ = _QueryValueEx(key, _proxyEnabledVar)
    return int(state) != 0


def setProxyState(state: bool) -> None:
    with _OpenKey(_HKCU, _proxyKey, 0, _KAA) as key:
        _SetValueEx(key, _proxyEnabledVar, 0, _RDWs, int(state))
        _CloseKey(key)


def toggleProxyState() -> None:
    with _OpenKey(_HKCU, _proxyKey, 0, _KAA) as key:
        state, _ = _QueryValueEx(key, _proxyEnabledVar)
        _SetValueEx(key, _proxyEnabledVar, 0, _RDWs, int(not bool(state)))
        _CloseKey(key)


def setProxyStateWatchCallback(callback: _Callable[[bool], None]) -> None:
    global _proxyWatchStateCallback
    _proxyWatchStateCallback = callback


def startWatchingProxyState() -> bool:
    if _watching or not _proxyWatchStateCallback:
        return False
    global _proxyStateWatchThread
    _proxyStateWatchThread = _Thread(target=_watchProxyStateThread)
    _proxyStateWatchThread.start()
    return True


def stopWatchingProxyState() -> None:
    global _watching
    _watching = False
    if _proxyStateWatchThread:
        _proxyStateWatchThread._stop()


def _watchProxyStateThread():
    global _watching
    _watching = True
    with _OpenKey(_HKCU, _proxyKey) as key:
        while _watching:
            _RegNotifyChangeKeyValue(key, False, _REG_NOTIFY_CHANGE_LAST_SET,
                                     None, False)
            if _proxyWatchStateCallback:
                _proxyWatchStateCallback(queryProxyState())
    _watching = False


# test
if __name__ == '__main__':
    with _OpenKey(_HKCU, _proxyKey) as key:
        host, _ = _QueryValueEx(key, _proxyHostVar)
        bypass, _ = _QueryValueEx(key, _proxyBypassVar)
        _CloseKey(key)
    print(queryProxyState(), " <- should be proxy state")
    print(queryCurrentProxy(), " <- should be proxy host, port, bypass")
    setProxyState(False)
    print("set to off")
    print(queryProxyState(), " <- should be a different proxy state")
    toggleProxyState()
    print("toggle")
    print(queryProxyState(), " <- should be a different proxy state")
    toggleProxyState()
    print("toggle")
    print(queryProxyState(), " <- should be a different proxy state")

    oldHost, oldPort, oldBypass = queryCurrentProxy()
    setProxy('0.0.0.0', 0, 'localhost')
    print("set to test values")
    print(queryCurrentProxy(), " <- should be \'0.0.0.0\', 0, \'localhost\'")
    setProxy(oldHost, oldPort, oldBypass)
    print("set back to old values")
    print(queryCurrentProxy(), " <- should be old values")
