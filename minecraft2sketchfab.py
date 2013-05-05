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
    config = "%s/.minecraft/saves" % os.environ['HOME']
    system = platform.platform().lower()
    if system.find('darwin') != -1:
        config = "%s/Library/Application Support/minecraft/saves/" % os.environ['HOME']
    elif system.find('windows') != -1:
        config = "%s/Roaming/.minecraft/saves/" % os.environ['APPDATA']

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
