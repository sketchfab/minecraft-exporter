import zipfile
import sys
import tempfile
import datetime
import os
import json
import shutil
import glob
import platform
import nbt

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

sketchfab_url = "https://api.sketchfab.com"
max_size = [512, 512]


def getDirectoryWorld():
    # on linux I did not tested
    config = ""
    system = platform.platform().lower()
    if system.find('darwin') != -1:
        config = os.path.join(os.environ['HOME'], "Library", "Application Support", "minecraft", "saves")
    elif system.find('windows') != -1:
        config = os.path.join(os.environ['APPDATA'], ".minecraft", "saves")
    else:
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


def getWorldByName(name):
    config = getDirectoryWorld()
    p = os.path.join(config, name)
    if os.path.isdir(p):
        return (name, p)
    return None


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


def getDimensionById(world, dimension_id):
    world_name, world_path = world

    if dimension_id == 0:
        dimension_name = "region"
    else:
        dimension_name = "DIM%d" % (dimension_id)
    dimension_path = os.path.join(world_path, dimension_name)
    if os.path.isdir(dimension_path):
        return (dimension_id, dimension_path)
    return None


def getPosition(world):
    name, path = world

    nbtfile = nbt.NBTFile(os.path.join(path, "level.dat"), "rb")
    data = nbtfile["Data"]
    player = data["Player"]
    if player:
        nbtpos = player["Pos"]
        pos = (int(nbtpos[0].value), int(nbtpos[1].value), int(nbtpos[2].value))
    else:
        pos = (data["SpawnX"].value, data["SpawnY"].value, data["SpawnZ"].value)
    return pos


def getDefaultArea(world):
    pos = getPosition(world)

    xmin = pos[0] - 128
    xmax = pos[0] + 128

    ymax = 255
    if pos[1] > 60:
        ymin = 60
    else:
        ymin = 0

    zmin = pos[2] - 128
    zmax = pos[2] + 128

    return [[xmin, ymin, zmin], [xmax, ymax, zmax]]


def create_zip_file(directory, position):
    if position == None:
        position = { 
            "area": {
                "x": [-64, 64],
                "y": [60, 255],
                "z": [-64, 64]
                },
            "dimension": 0
        }

    if os.path.exists(directory) == False:
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
    f = open("%s/%s/%s" % (tmpdir, dirname, "export_obj.json"), 'wb')
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

    for dirpath,dirs,files in os.walk(dirname):
        for f in files:
            fn = os.path.join(dirpath, f)
            print fn
            zip.write(fn)
    zip.close()

    # restore path
    os.chdir(path)
    return (filename, dirname)

def upload(fileModel, token, description, title, tags="minecraft"):
    from PyQt4 import QtNetwork, QtCore

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

    filename = os.path.basename(fileModel)
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

def uploadURLLIB2(filename, api_key, description, model_name, tags = "minecraft"):
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
    contents = ""
    try:
        response = urllib2.urlopen(request)
        print response.info()
        contents = response.read()
        return (True, contents)
    except urllib2.HTTPError, error:
        contents = error.read()
        return (False, contents)

def process_and_upload(directory, position, api_key):
    result = create_zip_file(directory, position)
    if result == None:
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
        position = sys.argv[3];

    api_key = sys.argv[1]
    directory = sys.argv[2]
            
    process_and_upload(directory, position, api_key)
