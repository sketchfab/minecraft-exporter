import re
import os
import sys
import json
import minecraft


def list_worlds():
    for i, world in enumerate(minecraft.getWorlds()):
        name, path = world
        print(" - %s" % (name))

        for j, dimension in enumerate(minecraft.getDimensions(world)):
            dimension_name, dimension_id = dimension
            print("     %s (%s)" % (dimension_id, dimension_name))


def main(options):
    if options.list is True:
        list_worlds()
        return

    if not options.world is None:
        if options.token is None:
            print("Missing sketchfab api token. You can find it on your dashboard : https://sketchfab.com/dashboard")
            return
        token = options.token

        world = minecraft.getWorldByName(options.world)
        if world is None:
            print("Can't find world %s" % (options.world))
            return

        dimension = minecraft.getDimensionById(world, int(options.dimension))
        if dimension is None:
            print("Can't find dimension %s in world %s" % (options.dimension, options.world))
            return

        area = minecraft.getDefaultArea(world)

        title = options.world
        if not options.title is None:
            title = options.title

        if not options.area is None:
            m = re.match("(\d+),(\d+),(\d+),(\d+)", options.area)
            if not m:
                print("Invalid area")
                return
            area[0][0] = int(m.group(1))
            area[1][0] = int(m.group(2))
            area[0][2] = int(m.group(3))
            area[1][2] = int(m.group(4))

        if not options.height is None:
            m = re.match("(\d+),(\d+)", options.height)
            if not m:
                print("Invalid height")
                return
            area[0][1] = int(m.group(1))
            area[1][1] = int(m.group(2))

        params = {
            "area": {
                "x": [area[0][0], area[1][0]],
                "y": [area[0][1], area[1][1]],
                "z": [area[0][2], area[1][2]],
            },
            "dimension": dimension[0]
        }
        filename, dirname = minecraft.create_zip_file(world[1], params)
        print(filename)

        state, contents = minecraft.uploadURLLIB2(
            filename=filename,
            api_key=token,
            description="Minecraft %s" % (world[0]),
            model_name=title,
            tags="minecraft")
        print(contents)
        data = json.loads(contents)
        success = data['success']

        if state is False:
            sys.exit("There was an HTTP error : %s" % (data["error"]))

        result = data['result']

        if success is False:
            sys.exit("Error while uploading : %s" % (json.dumps(result)))

        print("Model uploaded, available at %s." % ("%s/show/%s" % (minecraft.sketchfab_url, result["id"])))
