from os import startfile
from typing import List, Tuple

import GuiControlelr as gui
import ProxyController as proxy
import Utils as utils

trayMenuTooltipPrefix = "Ladder Guy "

app: gui.qtController.App | None = None
trayMenu: gui.qtController.TrayMenu | None = None

configList: List[proxy.ProxyConfig] = []
confNameList: List[str] = []
activeConfig: Tuple[str, int | None] = ("", None)


def onProxyStateChange(state: bool):
    global app
    if app:
        app.setIcon(utils.getIconPath(state))
        app.setTooltip(trayMenuTooltipPrefix + ("ON" if state else "OFF"))


def onSwitchCommand():
    proxy.toggleProxyState()


def onExitCommand():
    global app
    if app:
        proxy.stopWatchingProxyState()
        app.exit()


def traySelCallback(name: str, i: int):
    global configList
    if i < len(configList) and configList[i].getName() == name:
        proxy.setProxy(configList[i].getHost(), configList[i].getPort(),
                       configList[i].getBypass())


def refreshConfigList() -> None:
    global configList, activeConfig, confNameList
    configList, activeIndex = proxy.getConfigList()
    confNameList = [config.getName() for config in configList]
    activeConfig = (confNameList[activeIndex],
                    activeIndex) if activeIndex is not None else ("", None)


def updateSelList() -> None:
    global trayMenu, confNameList, activeConfig
    if trayMenu:
        newSelList = gui.qtController.TraySelectList(trayMenu, confNameList,
                                                     traySelCallback)
        if activeConfig[1] is not None:
            newSelList.setChecked(activeConfig[1])
        trayMenu.clearActionLists()
        trayMenu.addActionList(newSelList)


def onNewConfig():
    host, port, bypass = proxy.queryCurrentProxy()
    dialog = gui.qtController.InputPopup("New Config")
    dialog.addTextInput("Name", "New Config")
    dialog.addTextInput("Host", host)
    dialog.addTextInput("Port", str(port), isInt=True, limit=(0, 65535))
    dialog.addTextInput("Bypass", bypass)
    result, dict = dialog.pop()
    if result:
        newConfig = proxy.ProxyConfig(dict["Name"], dict["Host"],
                                      int(dict["Port"]), dict["Bypass"])
        print(newConfig.getName(), newConfig.getHost(), newConfig.getPort(),
              newConfig.getBypass())
        succ, reason = newConfig.saveToConf()
        if not succ:
            gui.qtController.AlertPopup(
                "Error", reason
                or "You got error but no reason is given.").pop()
        refreshConfigList()
        updateSelList()


def onDelConfig():
    global configList, activeConfig, trayMenu, confNameList
    if activeConfig[1] is not None and activeConfig[1] < len(
            configList) and configList[
                activeConfig[1]].getName() == activeConfig[0]:
        dialog = gui.qtController.InputPopup("Delete Config")
        dialog.addDescription(
            "Are you sure you want to delete the config \"{}\"?".format(
                activeConfig[0]))
        if dialog.pop()[0]:
            configList[activeConfig[1]].removeFromConf()
            refreshConfigList()
            updateSelList()


def onOpenSettings():
    startfile("ms-settings:network-proxy")


if __name__ == '__main__':
    # init proxy watcher
    proxy.setProxyStateWatchCallback(onProxyStateChange)
    proxy.startWatchingProxyState()

    # init tray icon
    app = gui.qtController.App("Test",
                               utils.getIconPath(proxy.queryProxyState()))
    app.setTooltip(trayMenuTooltipPrefix +
                   ("ON" if proxy.queryProxyState() else "OFF"))
    trayMenu = gui.qtController.TrayMenu("LadderGuy")
    trayMenu.addTopAction(
        gui.qtController.TrayAction(trayMenu, "Toggle", onSwitchCommand))
    trayMenu.addTopAction(
        gui.qtController.TrayAction(trayMenu, "Open Windows Settings",
                                    onOpenSettings))
    trayMenu.addTopCheckAction(
        gui.qtController.TrayCheckAction(
            trayMenu,
            "Auto Start", lambda: utils.setStartup(not utils.getStartup()),
            utils.getStartup())),
    trayMenu.addTopAction(
        gui.qtController.TrayAction(trayMenu, "New Config", onNewConfig))
    trayMenu.addBottomAction(
        gui.qtController.TrayAction(trayMenu, "Delete Selected", onDelConfig))
    trayMenu.addBottomAction(
        gui.qtController.TrayAction(trayMenu, "Exit", onExitCommand))
    app.setDoubleClickCallback(onSwitchCommand)

    # add config list
    refreshConfigList()
    updateSelList()

    # run
    app.setTrayMenu(trayMenu)
    app.run()
