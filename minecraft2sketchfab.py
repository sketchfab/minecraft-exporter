import os, sys
currentScriptPath = os.getcwd()
if currentScriptPath.find(".app") != -1:
    sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python2.7', 'lib-dynload')] + sys.path

# We will be using things from the qt and sys modules
from PyQt4 import QtCore
from PyQt4 import QtGui
import sys

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
