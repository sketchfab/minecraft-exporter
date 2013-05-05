import os, sys
currentScriptPath = os.getcwd()
if currentScriptPath.find(".app") != -1:
    sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python2.7', 'lib-dynload')] + sys.path

# We will be using things from the qt and sys modules
from PyQt4 import QtCore
from PyQt4 import QtGui

import platform
import minecraft


def getDirectoryWorld():
    # on linux I did not tested
    config = ""
    system = platform.platform().lower()
    if system.find('darwin') != -1:
        config = "%s/Library/Application Support/minecraft/saves/" % os.environ['HOME']
    elif system.find('windows') != -1:
        config = "%s/Roaming/.minecraft/saves/" % os.environ['APPDATA']
    else:
        # CP:
        # to clement, could you test the path is correct 
        config = "%s/.minecraft/saves" % os.environ['HOME']
    return config

# return a list of world with directory
def getWorlds():
    config = getDirectoryWorld()
    worlds_list = os.listdir(config)
    worlds_final = []
    for a in worlds_list:
        p = "%s/%s" % (config, a)
        if os.path.isdir(p):
            worlds_final.append((a, p))
    print worlds_final
    return worlds_final


# the current interface does nothin it's just to have a minimal setup
# that works on a standalone application on osx and windows

# a few thought
# - the api key should be saved to not enter it each time
# - the position should be optional
# - the user should be able to select which world he wants to save ( getWorlds )
# - add an about and a link to support
# anything else ?

def main():
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
