## Windows
to build a .exe file you will need to install all depandancies needed by the program. Here the list of dependancies:
*   Python2.7 # http://www.python.org/getit/
*   Pyqt4 # http://www.riverbankcomputing.com/software/pyqt/download
*   easy_install https://pypi.python.org/pypi/setuptools
*   easy_install pip
*   pip install urllib2

Fix issue with dll for windows error: MSVCP90.dll, a thread talk about it here http://stackoverflow.com/questions/323424/py2exe-fails-to-generate-an-executable

Get the dll and install it in Python2.7/Dlls then py2exe will find it

py2exe is not able to handle .egg format so download https://pypi.python.org/packages/source/p/poster/poster-0.8.1.tar.gz#md5=2db12704538781fbaa7e63f1505d6fc8 and install it python setup.py install_lib

to build the package run:
python.exe ./setup_windows.py py2exe # will generate a minecraft2sketchfab.exe in dist
    

## OSX
It's easier on osx you need to install the following dependancies:
*   setuptools https://pypi.python.org/pypi/setuptools
*   py2app http://wiki.python.org/moin/MacPython/py2app
*   pyqtx http://sourceforge.net/projects/pyqtx/

to build the package run:
./build.sh # to create a standalone application dmg

