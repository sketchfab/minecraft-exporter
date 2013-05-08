import zipfile
import sys
import tempfile
import datetime
import os
import json
import shutil

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

from PyQt4 import QtNetwork, QtCore

sketchfab_url = "https://dev2.sketchfab.com"


def create_zip_file(directory, position):
    if position is None:
        position = {
            "area": {
                "x": [-64, 64],
                "y": [60, 256],
                "z": [-64, 64]
            },
            "dimension": 0
        }

    if not os.path.exists(directory):
        print "directory %s does not exist" % directory
        return None

    # remove the
    if directory.endswith('/') or directory.endswith('\\'):
        directory = directory[:len(directory)-1]

    dirname = os.path.basename(directory)

    tmpdir = tempfile.mkdtemp()

    archive_dir = os.path.join(tmpdir, dirname)
    # copy directory
    shutil.copytree(directory, archive_dir)

    # add export_obj.json into directory
    f = open("%s/%s/%s" % (tmpdir, dirname, "export.mc2obj"), 'wb')
    print(position)
    f.write(json.dumps(position))
    f.close()

    date = datetime.datetime.utcnow()
    name = "minecraft-%d-%d-%d.zip" % (date.year, date.month, date.day)
    filename = "%s/%s" % (tmpdir, name)
    print filename

    print "archive %s to file to %s" % (archive_dir, filename)

    # change dir to make a zip
    path = os.getcwd()
    os.chdir(tmpdir)
    zip = zipfile.ZipFile(filename, 'w')

    for dirpath, dirs, files in os.walk(dirname):
        for f in files:
            fn = os.path.join(dirpath, f)
            print fn
            zip.write(fn)
    zip.close()

    # restore path
    os.chdir(path)
    return (filename, dirname)


def upload(fileModel, token, description, title, tags="minecraft"):
    def part_parameter(key, value):
        part = QtNetwork.QHttpPart()
        part.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader, "form-data; name=\"%s\"" % (key))
        part.setBody(value)
        return part

    source = "minecraft-plugin"
    multiPart = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.FormDataType)
    multiPart.append(part_parameter("title", title))
    multiPart.append(part_parameter("description", description))
    multiPart.append(part_parameter("tags", tags))
    multiPart.append(part_parameter("token", token))
    multiPart.append(part_parameter("source", source))

    modelPart = QtNetwork.QHttpPart()
    modelPart.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/octet-stream")
    modelPart.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader, "form-data; name=\"fileModel\"; filename=\"%s\"" % (fileModel))
    file = QtCore.QFile(fileModel)
    file.open(QtCore.QIODevice.ReadOnly)
    modelPart.setBodyDevice(file)
    file.setParent(multiPart)
    multiPart.append(modelPart)

    url = QtCore.QUrl("%s/v1/models" % (sketchfab_url))

    request = QtNetwork.QNetworkRequest(url)

    manager = QtNetwork.QNetworkAccessManager()
    reply = manager.post(request, multiPart)
    multiPart.setParent(reply)

    return (manager, reply)


def uploadURLLIB2(filename, api_key, description, model_name, tags="minecraft"):
    register_openers()
    url = "%s/v1/models" % (sketchfab_url)
    print filename
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
        print response.info()
        contents = response.read()
        result = True
    except urllib2.HTTPError, error:
        contents = error.read()
        result = False
    print contents
    return result


def process_and_upload(directory, position, api_key):
    result = create_zip_file(directory, position)
    if result is None:
        return False

    filename, model_name = result
    if not uploadURLLIB2(filename, api_key, "", model_name):
        print "error while uploading file"
        return False
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('Usage: %s api-key world-directory world-position' % sys.argv[0])
    position = None
    if len(sys.argv) > 3:
        position = sys.argv[3]

    api_key = sys.argv[1]
    directory = sys.argv[2]

    process_and_upload(directory, position, api_key)
