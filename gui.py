from PyQt4 import QtCore
from PyQt4 import QtGui
import minecraft
import json


class MessageBoxHtml(QtGui.QDialog):
    def __init__(self, title, html, parent=None):
        super(MessageBoxHtml, self).__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        mainLayout = QtGui.QVBoxLayout()

        label = QtGui.QLabel()
        label.setText(html)
        label.setTextFormat(QtCore.Qt.RichText)
        label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        label.setOpenExternalLinks(True)

        mainLayout.addWidget(label)

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton("Close", QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.close)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)


class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle('Minecraft2Sketchfab')
        self.settings = QtCore.QSettings("Sketchfab", "Minecraft2Sketchfab")

        areaGroup = self.createAreaGroup()
        worldGroup = self.createWorldGroup()
        sketchfabGroup = self.createSketchfabGroup()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(worldGroup)
        mainLayout.addWidget(areaGroup)
        mainLayout.addWidget(sketchfabGroup)

        buttonBox = QtGui.QDialogButtonBox()

        buttonBox.addButton("About", QtGui.QDialogButtonBox.HelpRole)
        buttonBox.helpRequested.connect(self.open_about)

        buttonBox.addButton("Upload", QtGui.QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.start_upload)

        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)

    def start_upload(self):
        # get area
        minx = int(self.editXMin.text())
        maxx = int(self.editXMax.text())
        miny = max(0, int(self.editYMin.text()))
        maxy = min(255, int(self.editYMax.text()))
        minz = int(self.editZMin.text())
        maxz = int(self.editZMax.text())

        self.editYMin.setText(str(miny))
        self.editYMax.setText(str(maxy))

        if (maxx-minx)*(maxz-minz) > minecraft.max_size[0] * minecraft.max_size[1]:
            QtGui.QMessageBox.information(self, "Area limits", "The exporter's area size is limited to %sx%s.\nPlease specify a smaller x and/or z range.")
            return

        progress = QtGui.QProgressDialog("Uploading...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Sketchfab upload")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()
        self.settings.setValue("account/token", self.editToken.text())

        params = {
            "area": {
                "x": [minx, maxx],
                "y": [miny, maxy],
                "z": [minz, maxz]
            },
            "dimension": self.currentDimension[1]
        }
        filename, dirname = minecraft.create_zip_file(self.currentWorld[1], params)
        print(filename)

        token = str(self.editToken.text())
        if not token:
            QtGui.QMessageBox.information(self, "Sketchfab token", "You need to specify your sketchfab api token.\nIt can be found on your dashboard.")
            return

        self.manager, self.reply = minecraft.upload(
            fileModel=filename,
            title=self.currentWorld[0],
            description="Minecraft %s" % (self.currentDimension[0]),
            tags="minecraft",
            token=token
        )

        def upload_finished():
            if not progress.wasCanceled():
                http_response = self.reply.readAll()
                print(http_response)
                data = json.loads(str(http_response))
                success = data['success']
                result = data['result']
                if success:
                    id = result["id"]
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl("%s/show/%s" % (minecraft.sketchfab_url, id)))
                else:
                    QtGui.QMessageBox.critical(self, "Upload sketchfab error", json.dumps(result))

                print(result)
                progress.close()

        def upload_error():
            progress.cancel()
            rawData = str(self.reply.readAll())
            print(rawData)
            if rawData:
                try:
                    data = json.loads(rawData)
                    if data and "success" in data and not data["success"]:
                        QtGui.QMessageBox.critical(self, "Upload error", data["error"])
                        return
                except:
                    pass
            QtGui.QMessageBox.critical(self, "Upload network error", self.reply.errorString())
            progress.close()
            self.reply = None

        def upload_progress(value, max):
            progress.setValue(value)
            progress.setMaximum(max + 1)
            if value == max:
                progress.setLabelText('Processing...')

        def upload_canceled():
            self.reply = None

        def ssl_errors(err_list):
            for err in err_list:
                print(err.errorString())
            self.reply.ignoreSslErrors()

        self.reply.finished.connect(upload_finished)
        self.reply.error.connect(upload_error)
        self.reply.uploadProgress.connect(upload_progress)
        self.reply.sslErrors.connect(ssl_errors)

        progress.canceled.connect(upload_canceled)

    def open_about(self):
        self.about = MessageBoxHtml(
            "About",
            "<h1>Minecraft2Sketchfab</h1>"
            "Export your minecraft worlds to <a href='https://sketchfab.com'>Sketchfab</a>. <a href='https://sketchfab.com/faq#contact'>Contact us</a>.<br/>"
            "Texture pack is <a href='http://www.minecraftforum.net/topic/626805-3264128256v13214615-minecraft-enhanced-updated-3-14-huge-15-update/'>Minecraft enhanced 64x64</a>.<br/>"
        )
        self.about.show()
        self.about.setFixedSize(self.about.size())

    def open_areaHelp(self):
        self.about = MessageBoxHtml(
            "Help",
            "<h1>Area limits</h1>"
            "<p>"
            "A minecraft world is huge."
            "You wouldn't want to export your whole world as a unique model.<br>"
            "You must select export limits by giving a box coordinates convering the area you want.<br>"
            "Coordinates are the two opposite coordinates of that box.<br>"
            "You can get your in game coordinates using the Minecraft debug screen (Press F3 while in game).<br>"
            "</p>"
            "<p>"
            "Default coordinates center the player inside a %dx%d box. On server maps, it is center around the spawn.<br>"
            "On flat worlds, as the surface level is way lower you will need to use 0 rather than 64.<br>"
            "</p>" % (minecraft.max_size[0], minecraft.max_size[1])
        )
        self.about.show()
        self.about.setFixedSize(self.about.size())

    def open_tokenHelp(self):
        self.about = MessageBoxHtml(
            "Help",
            "<h1>Api token</h1>"
            "<p>"
            "For an application to use sketchfab, the application needs a way to authentificate your user.<br>"
            "A private random generated 32 alpha-numerical characters token is used so you don't have to give your password to any application.<br>"
            "You can find this token directly on your <a href='https://sketchfab.com/dashboard/recent'>dashboard</a> under the profile section."
            "</p>"
        )
        self.about.show()
        self.about.setFixedSize(self.about.size())

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
        for i, world in enumerate(minecraft.getWorlds()):
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
        for i, dimension in enumerate(minecraft.getDimensions(self.currentWorld)):
            name, path = dimension
            item = QtGui.QStandardItem(name)
            item.setData(path)
            self.modelDimension.setItem(i, 0, item)
        self.comboDimension.setCurrentIndex(0)

        area = minecraft.getDefaultArea(self.currentWorld)
        self.editXMin.setText(str(area[0][0]))
        self.editXMax.setText(str(area[1][0]))
        self.editYMin.setText(str(area[0][1]))
        self.editYMax.setText(str(area[1][1]))
        self.editZMin.setText(str(area[0][2]))
        self.editZMax.setText(str(area[1][2]))

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

        def coordEdit(default):
            lineEdit = QtGui.QLineEdit(default)
            lineEdit.setValidator(QtGui.QIntValidator())
            return lineEdit

        self.editXMin = coordEdit("0")
        self.editXMax = coordEdit("128")
        self.editYMin = coordEdit("60")
        self.editYMax = coordEdit("256")
        self.editZMin = coordEdit("0")
        self.editZMax = coordEdit("128")

        labelX = QtGui.QLabel("x<sup>longitude <a href='#'>?</a></sup>")
        labelX.linkActivated.connect(self.open_areaHelp)
        grid.addWidget(labelX, 0, 0)
        grid.addWidget(self.editXMin, 0, 1)
        grid.addWidget(self.editXMax, 0, 2)

        labelY = QtGui.QLabel("y<sup>altitude <a href='#'>?</a></sup>")
        labelY.linkActivated.connect(self.open_areaHelp)
        grid.addWidget(labelY, 1, 0)
        grid.addWidget(self.editYMin, 1, 1)
        grid.addWidget(self.editYMax, 1, 2)

        labelZ = QtGui.QLabel("z<sup>latitude <a href='#'>?</a></sup>")
        labelZ.linkActivated.connect(self.open_areaHelp)
        grid.addWidget(labelZ, 2, 0)
        grid.addWidget(self.editZMin, 2, 1)
        grid.addWidget(self.editZMax, 2, 2)

        groupBox.setLayout(grid)

        return groupBox

    def createSketchfabGroup(self):
        groupBox = QtGui.QGroupBox("Sketchfab")
        grid = QtGui.QGridLayout()

        labelToken = QtGui.QLabel("Api token<sup><a href='#'>?</a></sup>")
        labelToken.linkActivated.connect(self.open_tokenHelp)
        grid.addWidget(labelToken, 0, 0, 1, 1)

        self.editToken = QtGui.QLineEdit(str(self.settings.value("account/token").toString()))
        grid.addWidget(self.editToken, 0, 1, 1, 8)

        groupBox.setLayout(grid)
        return groupBox
