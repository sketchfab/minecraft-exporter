import os
import sys
currentScriptPath = os.getcwd()
if currentScriptPath.find(".app") != -1:
    sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python2.7', 'lib-dynload')] + sys.path

from optparse import OptionParser


# a few thought
# - texturepack choice (upload texturepack also ?)
# anything else ?



def main():
    parser = OptionParser()
    parser.add_option("-l", "--list", action="store_true", dest="list", help="List your saved minecraft worlds.")
    parser.add_option("-t", "--token", type="string", dest="token", help="Your sketchfab api token. Can be found on your dashboard.")
    parser.add_option("-w", "--world", type="string", dest="world", help="Name of minecraft world to export.")
    parser.add_option("-d", "--dimension", type="string", dest="dimension", default="0", help="Dimension number to export from world. Default is 0 for the overworld.")
    parser.add_option("-n", "--name", type="string", dest="title", help="Sketchfab model title.")
    parser.add_option("-a", "--area", type="string", dest="area", help="Box x, z limit coordinates of world selection. Format : xmin,xmax,zmin,zmax")
    parser.add_option("-y", "--height", type="string", dest="height", help="y coordinates limit. Format : ymin,ymax")
    (options, args) = parser.parse_args()

    gui_enabled = True

    # if arguments passed, switch to cli
    if not options.list is None or not options.world is None:
        gui_enabled = False

    if gui_enabled is True:
        import gui
        try:
            from PyQt4 import QtGui

            app = QtGui.QApplication(sys.argv)
            w = gui.Window()
            w.show()
            w.setFixedSize(w.size())

            sys.exit(app.exec_())
        except:
            print("Failed to initialize QtGui interface. Switching to cli.")

            # if gui failed to start fallback to cli
            gui_enabled = False

    if gui_enabled is False:
        import cli
        cli.main(options)


if __name__ == '__main__':
    main()
