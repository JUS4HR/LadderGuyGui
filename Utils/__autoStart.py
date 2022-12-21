from os import environ as _osEnviron
from os import mkdir as _osMkdir
from os import path as _osPath
from os import remove as _osRemove
from sys import executable as _executable

from win32com.client import Dispatch as _dispatch


def setStartup(input: bool = True) -> None:
    # 快捷方式路径 C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
    path = _osPath.join(_osEnviron['APPDATA'], 'Microsoft', 'Windows',
                        'Start Menu', 'Programs', 'Startup')
    fileName = 'LadderGuyGui.lnk'
    if input:
        if not _osPath.exists(path):
            _osMkdir(path)
        # with open(_osPath.join(path, fileName), 'w') as f:
        #     f.write('[InternetShortcut]\n')
        #     f.write('URL=file:///' + sys.executable + '\n')
        #     f.write('IconIndex=0\n')
        #     f.write('IconFile=' + sys.executable + '\n')
        #     f.write('HotKey=0\n')
        #     f.write('Description=LadderGuy\n')
        fullPath = _osPath.join(path, fileName)
        # icon = _osPath.split(_osPath.realpath(sys.executable))[0] + r"\ico\ladderIntactDark.ico"
        shell = _dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(fullPath)
        shortcut.Targetpath = _executable
        # shortcut.IconLocation = icon
        shortcut.save()
    else:
        if _osPath.exists(_osPath.join(path, fileName)):
            _osRemove(_osPath.join(path, fileName))
    return getStartup()


def getStartup() -> bool:
    path = _osPath.join(_osEnviron['APPDATA'], 'Microsoft', 'Windows',
                        'Start Menu', 'Programs', 'Startup')
    fileName = 'LadderGuyGui.lnk'
    return _osPath.exists(_osPath.join(path, fileName))