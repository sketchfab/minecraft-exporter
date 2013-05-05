import zipfile
import sys
import tempfile
import datetime
import os
import json
import shutil

def create_zip_file(directory, position):
    if position == None:
        position = json.dumps( { 
                "area": {
                    "x": [-64, 64],
                    "y": [60, 256],
                    "z": [-64, 64]
                    },
                "dimension": 0
                })

    # should fail if syntax error
    json.loads(position)

    if os.path.exists(directory) == False:
        print "directory %s does not exist" % directory
        return None

    # remove the 
    if directory.endswith('/') or directory.endswith('\\'):
        directory = directory[:len(directory)-1]

    dirname = os.path.basename(directory)

    tmpdir = tempfile.mkdtemp()

    archive_dir = "%s/%s" % (tmpdir, dirname)
    # copy directory
    shutil.copytree(directory, archive_dir)

    # add export_obj.json into directory
    f = open("%s/%s/%s" % (tmpdir, dirname, "export_obj.json"), 'wb')
    f.write(position)
    f.close()
    
    date = datetime.datetime.utcnow()
    name = "minecraft-%d-%d-%d.zip" % (date.year, date.month, date.day)
    filename = "%s/%s" % (tmpdir, name)

    print "archive %s to file to %s" % (archive_dir, filename)

    # change dir to make a zip
    path = os.getcwd()
    os.chdir(tmpdir)
    zip = zipfile.ZipFile(filename, 'w')

    for dirpath,dirs,files in os.walk(dirname):
        for f in files:
            fn = os.path.join(dirpath, f)
            print fn
            zip.write(fn)
    zip.close()

    # restore path
    os.chdir(path)

    return (filename, dirname)


from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2


def upload(filename, model_name, api_key):
    register_openers()
    description="Minecraft world"
    tags="minecraft"
    url="https://api.sketchfab-local.com/v1/models"

    params = {
        'fileModel': open(filename, "rb"),
        'title': model_name,
        'description': description,
        'tags': tags,
        'token': api_key,
        'source': 'minecraft-plugin'
        }

    datagen, headers = multipart_encode(params)
    request = urllib2.Request(url, datagen, headers)
    result = None
    contents = ""
    try:
        response = urllib2.urlopen(request)
        contents = response.read()
        result = True
    except urllib2.HTTPError, error:
        contents = error.read()
        result = False
    print contents
    return result

def process_and_upload(directory, position, api_key):
    result = create_zip_file(directory, position)
    if result == None:
        return False

    filename, model_name = result
    if not upload(filename, model_name):
        print "error while uploading file"
        return False
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('Usage: %s api-key world-directory world-position' % sys.argv[0])
    position = None
    if len(sys.argv) > 3:
        position = sys.argv[3];

    api_key = sys.argv[1]
    directory = sys.argv[2]
            
    process_and_upload(directory, position, api_key)
