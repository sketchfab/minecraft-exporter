import zipfile
import sys
import tempfile
import datetime
import os

def create_zip_file(directory, position):

    if os.path.exists(directory) == False:
        print "directory %s does not exist" % directory

    tmpdir = tempfile.mkdtemp()
    date = datetime.datetime.utcnow()
    name = "minecraft-%d-%d-%d.zip" % (date.year, date.month, date.day)
    filename = "%s/%s" % (tmpdir, name)
    print "write file to %s" % filename
    zip = zipfile.ZipFile(filename, 'w')

    for dirpath,dirs,files in os.walk(directory):
        for f in files:
            fn = os.path.join(dirpath, f)
            print fn
            zip.write(fn)
    zip.close()
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s api-key world-directory world-position' % sys.argv[0])
    create_zip_file(sys.argv[1])
