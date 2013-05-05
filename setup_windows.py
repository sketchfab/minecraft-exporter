from distutils.core import setup
import py2exe

setup(
    console=['minecraft2sketchfab.py'],
    options= {
        'py2exe': {
            'includes': ['sip', 'PyQt4', 'poster' ]
            }
        }
    )
