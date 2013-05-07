import os, sys
import glob
import json
currentScriptPath = os.getcwd()
if currentScriptPath.find(".app") != -1:
    sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python2.7', 'lib-dynload')] + sys.path

# We will be using things from the qt and sys modules
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtNetwork

import platform
import minecraft

def getDirectoryWorld():
    # on linux I did not tested
    config = ""
    system = platform.platform().lower()
    if system.find('darwin') != -1:
        config = os.path.join(os.environ['HOME'], "Library", "Application Support", "minecraft", "saves") 
    elif system.find('windows') != -1:
        config = os.path.join(os.environ['APPDATA'], ".minecraft", "saves")
    else:
        # CP:
        # to clement, could you test the path is correct 
        config = os.path.join(os.environ['HOME'], ".minecraft", "saves")
    return config

# return a list of world with directory
def getWorlds():
    config = getDirectoryWorld()
    worlds_list = os.listdir(config)
    worlds_final = []
    for a in worlds_list:
        p = os.path.join(config, a)
        if os.path.isdir(p):
            worlds_final.append((a, p))
    return worlds_final

def getDimensions(world):
    name, path = world
    dimensions_list = glob.glob(os.path.join(path, "DIM*"))
    dimensions_final = [("Overworld", 0)]
    default_dimensions = {
        "DIM-1": "The Nether",
        "DIM1": "The End"
    }
    for p in dimensions_list:
        a = os.path.basename(p)
        if a in default_dimensions:
            b = default_dimensions[a]
        else:
            b = a
        a = a[3:]

        if os.path.isdir(p):
            dimensions_final.append((b, int(a)))
    return dimensions_final

# a few thought
# - the api key should be saved to not enter it each time
# - the position should be optional
# - add an about and a link to support
# anything else ?

class Window(QtGui.QWidget):
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)
        self.setWindowTitle('Minecraft2Sketchfab')

        grid = QtGui.QGridLayout()
        grid.addWidget(self.createWorldGroup(), 0, 0, 1, 0)
        grid.addWidget(self.createAreaGroup(), 1, 0, 1, 0)
        grid.addWidget(self.createSketchfabGroup(), 2, 0, 1, 0)

        submit = QtGui.QPushButton("Upload")
        grid.addWidget(submit, 3, 0)
        submit.clicked.connect(self.start_upload)

        about = QtGui.QPushButton("About")
        grid.addWidget(about, 3, 1)
        about.clicked.connect(self.open_about)

        self.setLayout(grid)

    def start_upload(self):
        progress = QtGui.QProgressDialog("Uploading...", "Cancel", 0, 100, self)
        progress.show()

        params = {
            "area": {
                "x": [int(self.editXMin.text()), int(self.editXMax.text())],
                "y": [int(self.editYMin.text()), int(self.editYMax.text())],
                "z": [int(self.editZMin.text()), int(self.editZMax.text())]
            },
            "dimension": self.currentDimension[1]
        }
        filename, dirname = minecraft.create_zip_file(self.currentWorld[1], params)
        print("Zip file : %s" % (filename))
        print("Zip dir : %s" % (dirname))

        self.manager, self.reply = minecraft.upload(
            fileModel = filename,
            title = self.currentWorld[0],
            description = "Minecraft %s" % (self.currentDimension[0]),
            tags = "minecraft test",
            token = str(self.editToken.text()),
            source = "minecraft-plugin"
        )

        def upload_finished():
            if not progress.wasCanceled():
                data = json.loads(str(self.reply.readAll()))
                success = data['success']
                result = data['result']
                if success:
                    id = result["id"]
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://sketchfab.com/show/%s" % (id)))

                    progress.close()
                else:
                    QtGui.QMessageBox.critical(self, "Upload sketchfab error", json.dumps(result))

                print(result)
                progress.close()

        def upload_error():
            progress.cancel()
            data = json.loads(str(self.reply.readAll()))
            progress.close()
            if data and "success" in data and data["success"] == False:
                QtGui.QMessageBox.critical(self, "Upload error", data["error"])
            else:
                QtGui.QMessageBox.critical(self, "Upload network error", self.reply.errorString())
            self.reply = None

        def upload_progress(value, max):
            progress.setValue(value)
            progress.setMaximum(max)

        def download_progress(value, max):
            progress.setValue(value)
            progress.setMaximum(max)
            progress.setLabelText('Downloading result...')

        def upload_canceled():
            self.reply = None

        self.reply.finished.connect(upload_finished)
        self.reply.error.connect(upload_error)
        self.reply.uploadProgress.connect(upload_progress)
        self.reply.downloadProgress.connect(download_progress)
        progress.canceled.connect(upload_canceled)

    def open_about(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://sketchfab.com/faq#minecraft"))

    def createWorldGroup(self):
        groupBox = QtGui.QGroupBox("World")
        grid = QtGui.QGridLayout()

        grid.addWidget(QtGui.QLabel("Dimension"), 1, 0)
        grid.addWidget(self.createComboDimension(), 1, 1)
        grid.addWidget(QtGui.QLabel("World"), 0, 0)
        grid.addWidget(self.createComboWorld(), 0, 1)

        groupBox.setLayout(grid)
        return groupBox

    def createComboWorld(self):
        combo = QtGui.QComboBox()
        combo.currentIndexChanged.connect(self.selectWorld)

        self.modelWorld = QtGui.QStandardItemModel()
        combo.setModel(self.modelWorld)
        for i, world in enumerate(getWorlds()):
            name, path = world
            item = QtGui.QStandardItem(name)
            item.setData(path)
            self.modelWorld.setItem(i, 0, item)
        combo.setCurrentIndex(0)

        return combo

    def selectWorld(self, i):
        name = self.modelWorld.item(i, 0)
        self.currentWorld = (str(name.text()), str(name.data().toPyObject()))

        self.modelDimension.clear()
        for i, world in enumerate(getDimensions(self.currentWorld)):
            name, path = world
            item = QtGui.QStandardItem(name)
            item.setData(path)
            self.modelDimension.setItem(i, 0, item)
        self.comboDimension.setCurrentIndex(0)

    def createComboDimension(self):
        combo = QtGui.QComboBox()
        combo.currentIndexChanged.connect(self.selectDimension)

        self.modelDimension = QtGui.QStandardItemModel()
        combo.setModel(self.modelDimension)

        self.comboDimension = combo
        return combo

    def selectDimension(self, i):
        name = self.modelDimension.item(i, 0)
        self.currentDimension = (str(name.text()), int(name.data().toPyObject()))

    def createAreaGroup(self):
        groupBox = QtGui.QGroupBox("Area limits")
        grid = QtGui.QGridLayout()
        
        self.editXMin = QtGui.QLineEdit("0")
        self.editXMax = QtGui.QLineEdit("128")
        self.editYMin = QtGui.QLineEdit("60")
        self.editYMax = QtGui.QLineEdit("256")
        self.editZMin = QtGui.QLineEdit("0")
        self.editZMax = QtGui.QLineEdit("128")

        grid.addWidget(QtGui.QLabel("x"), 0, 0)
        grid.addWidget(self.editXMin, 0, 1)
        grid.addWidget(self.editXMax, 0, 2)

        grid.addWidget(QtGui.QLabel("y"), 1, 0)
        grid.addWidget(self.editYMin, 1, 1)
        grid.addWidget(self.editYMax, 1, 2)
        
        grid.addWidget(QtGui.QLabel("z"), 2, 0)
        grid.addWidget(self.editZMin, 2, 1)
        grid.addWidget(self.editZMax, 2, 2)

        groupBox.setLayout(grid)

        return groupBox

    def createSketchfabGroup(self):
        groupBox = QtGui.QGroupBox("Sketchfab")
        grid = QtGui.QGridLayout()

        self.editToken = QtGui.QLineEdit("")
        self.editToken.setText("81d8448493734f06a7c4cc4df93b8128");
        grid.addWidget(QtGui.QLabel("Api token"), 0, 0)
        grid.addWidget(self.editToken, 0, 1)

        groupBox.setLayout(grid)
        return groupBox

def main():
    app = QtGui.QApplication(sys.argv)
    w = Window()
    #w.resize(250, 150)
    #w.move(300, 300)

    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
