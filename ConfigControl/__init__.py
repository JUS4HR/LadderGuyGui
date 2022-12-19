from .__proxyConfig import ProxyConfig, configPath as _configPath, getProxyConfigList

def setConfigPath(path: str) -> None:
    global _configPath
    _configPath = path
