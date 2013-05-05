    *** Windows
    ** dependancies
    * python2.7
    * pyqt4
    * easy_install https://pypi.python.org/pypi/setuptools
    * easy_install pip
    * pip install urllib2
    ** fix windows bullshit dll
    * get the dll runtime http://stackoverflow.com/questions/323424/py2exe-fails-to-generate-an-executable
    * install the dll into your Python2.7/Dlls directory
    
    ** install poster:
    * download https://pypi.python.org/packages/source/p/poster/poster-0.8.1.tar.gz#md5=2db12704538781fbaa7e63f1505d6fc8
    * python setup.py install_lib
    ** run the command to build the package
    * python.exe ./setup_windows.py py2exe # will generate a minecraft2sketchfab.exe in dist
    

    *** OSX
    ** dependancies
    * setuptools
    * py2app
    * pyqtx http://sourceforge.net/projects/pyqtx/
    ** run the command to build the package
    * ./build.sh #to create a standalone application

