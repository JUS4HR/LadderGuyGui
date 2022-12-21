**Ladder Guy Gui**    
===
**Description**
---
A tray application that allows you to manage windows system proxy settings.    

**Features**
---
* Show whether system proxy is enabled or disabled.
* Toggle system proxy settings by double clicking the tray icon.
* Create and switch between multiple proxy profiles.
* Auto start with windows **and** shortcut to open windows proxy settings page.

Windows only because it uses win32api.

**WIP**
---
- [x] ~~Add a shortcut to open windows proxy settings page.~~
- [x] ~~Auto start with windows.~~
- [ ] Match menu and popup window theme with current windows theme.

**Usage**
---
* Install modules: `pip install -r requirements.txt`
* Build to exe file: `pyinstaller main.spec`
* ~~Or you can grab the latest release [here](https://github.com/jus4hr/LadderGuyGui/releases).~~ The exe file was too large to upload (36MB) for some reason, so build it yourself.
