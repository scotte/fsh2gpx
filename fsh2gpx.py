import struct
import time
import sys
from elementtree.SimpleXMLWriter import XMLWriter

#    Python script for converting Raymarine FSH files to
#    OpenCPN compatible GPX files
#
#    https://github.com/scotte/fsh2gpx
#
#    Copyright (C) 2012 - L. Scott Emmons
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

class Waypoint:
    def __init__(self):
        self.time = 0
        self.name = ""
        self.lat = 0.0
        self.lon = 0.0
        self.sym = ""
        self.type = ""

class Route:
    def __init__(self):
       self.name = ""
       self.waypoints = []

RL90_HEADER="RL90 FLASH FILE"
FLOB_HEADER="RAYFLOB1"

def rewind(len):
    global pos
    pos -= len

def forward(len):
    global pos
    pos += len

def getBytes(len):
    global pos
    result = data[pos:pos+len]
    pos+=len
    return result

def getAsByte():
    global pos
    result, = struct.unpack("B", getBytes(1))
    return result

def getAsShort():
    global pos
    result, = struct.unpack("<h", getBytes(2))
    return result

def getAsUShort():
    global pos
    result, = struct.unpack("<H", getBytes(2))
    return result

def getAsInt():
    global pos
    result, = struct.unpack("<i", getBytes(4))
    return result

def getAsUInt():
    global pos
    result, = struct.unpack("<I", getBytes(4))
    return result

def getAsULong():
    global pos
    result, = struct.unpack("<Q", getBytes(8))
    return result

def getAsFloat():
    global pos
    result, = struct.unpack("<f", getBytes(4))
    return result

def getAsDouble():
    global pos
    result, = struct.unpack("<d", getBytes(8))
    return result

def getZeroes(len):
    global pos
    for i in range (pos, pos+len):
        val = getAsByte()
        if val:
            print "ERROR - expecting 0, got %s at %d - %s" % (hex(val), (pos-1), hex(pos-1))

def readRL90hdr():
    # RL90 header
    rl90hdr = getBytes(len(RL90_HEADER))
    print rl90hdr
    getZeroes(1)
    getAsShort() # 0x10
    getZeroes(4)
    getAsShort() # 0x01
    getAsShort() # 0x01
    getAsShort() # 0x01

def readFLOBhdr():
    # FLOB header
    flobhdr = getBytes(len(FLOB_HEADER))
    print flobhdr
    getAsShort() # 0x01
    getAsShort() # 0x01
    getAsUShort() # 0xfc ff

def readGUID():
    guid4=getAsUShort()
    guid3=getAsUShort()
    guid2=getAsUShort()
    guid1=getAsUShort()
    return ("%d-%d-%d-%d") % (guid1, guid2, guid3, guid4)

def readBlockHeader():
    size = getAsUShort()
    guid = readGUID()
    type = getAsUShort()
    unknown = getAsUShort()
    return size, guid, type, unknown

def readCoord():
    return float(getAsInt())/1E7

def readTime():
    val=getAsULong()
    return int(val/1E10)

def printAsUShort():
    val=getAsUShort()
    print "Unknown short %s (%d)" % (hex(val), val)

def readWaypoint():
    global w
    lat = readCoord()
    lon = readCoord()
    timestamp = readTime()
    print "LAT: %f" % lat
    print "LON: %f" % lon
    print time.ctime(timestamp)
    getZeroes(12) # Maybe 4 ints?
    val=getAsByte()
    print hex(val) # 06 or 02 (symbol?)
    printAsUShort()
    printAsUShort()
    printAsUShort()
    printAsUShort()
    printAsUShort()
    printAsUShort()
    getZeroes(1)
    namelen=getAsShort()
    getZeroes(4)
    name=getBytes(namelen)
    print "NAME: %d [%s]" % (namelen, name)
    waypoint = Waypoint()
    waypoint.name=name
    waypoint.time=timestamp
    waypoint.lat=lat
    waypoint.lon=lon
    waypoint.sym="circle"
    waypoint.type="wpt"
    print "---"
    return waypoint

def readRouteWaypoint():
    wpt = readWaypoint()
    wpt.type="rtept"
    wpt.sym="diamond"
    return wpt

def readRoute(type):
    route = Route()

    if type == 0x21:
        getZeroes(2)

    namecount=getAsShort()
    guidcount=getAsShort()

    if type == 0x21:
        printAsUShort()

    name=getBytes(namecount)
    print "NAME: %s" % name
    route.name=name

    print "Looping %d GUIDs" % guidcount
    for i in range(0, guidcount):
        print "GUID: %s" % readGUID()

    if type == 0x22:
        print "Looping %d waypoints" % guidcount
        for i in range(0, guidcount):
            route.waypoints.append(readRouteWaypoint())

    if type == 0x21:
        print time.ctime(readTime())
        print time.ctime(readTime())
        print "pos at %s" % hex(pos)
        weird=getAsUInt()
        print "Weird is %s (%d)" % (hex(weird), weird)
        getBytes(26) # What is this? the 0xcc crap
        getZeroes(10)
        # This is a variable length block that I haven't figured out.
        # It has no size, and the length is not an even interval of the
        # number of waypoints. The only marker is that the 'weird' int
        # value shows up again at the end in the case that it's non-zero.
        if weird > 0:
            getBytes(4) # Sometimes, the weird value is in there twice
            while True:
                check=getAsUInt()
                if check == weird:
                    break
                rewind(2) # Not always a 4 byte boundary
        print "pos at %s" % hex(pos)
        guidcount=getAsShort()
        getZeroes(2)
        print "GUID COUNT %d" % guidcount
        print "Looping %d GUIDs+waypoints" % guidcount
        for i in range(0, guidcount):
            print "GUID: %s" % readGUID()
            route.waypoints.append(readRouteWaypoint())

    print "---"
    return route

def writeWaypoint(wpt):
    global w
    w.start(wpt.type, lat=str(wpt.lat), lon=str(wpt.lon))
    w.element("time", time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(wpt.time)))
    w.element("name", wpt.name)
    w.element("sym", wpt.sym)
    w.element("type", "WPT")
    w.start("extensions")
    w.element("opencpn:viz", "1")
    w.element("opencpn:viz_name", "1")
    w.end()
    w.end()

def writeRoute(rte):
    global w
    w.start("rte")
    w.element("name", rte.name)
    w.start("extensions")
    w.element("opencpn:viz", "1")
    w.end()
    for wpt in rte.waypoints:
        writeWaypoint(wpt)
    w.end()

if len(sys.argv) !=3:
    print "Usage: python %s <FSHinput> <GPXoutput>" % sys.argv[0]
    sys.exit(1)

print "Input:%s, output:%s" % (sys.argv[1], sys.argv[2])

data = open(sys.argv[1], "rb").read()
pos = 0

gpxfile = open(sys.argv[2], "w")
w = XMLWriter(gpxfile,"utf-8")
rootattrs=dict()
rootattrs["version"]="1.1"
rootattrs["creator"]="fsh2gpx"
rootattrs["xmlns:xsi"]="http://www.w3.org/2001/XMLSchema-instance"
rootattrs["xmlns"]="http://www.topografix.com/GPX/1/1"
rootattrs["xmlns:gpxx"]="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
rootattrs["xsi:schemaLocation"]="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
rootattrs["xmlns:opencpn"]="http://www.opencpn.org"
gpx = w.start("gpx", rootattrs)

print "Read %d bytes " % len(data)

readRL90hdr()
readFLOBhdr()

done = False
block = 1
waypoints = 0
routes = 0
while not done and pos < len(data):
    print "=== parse block %d" % block
    (entrysize, guid, type, unknown) = readBlockHeader()
    print "ENTRY SIZE %d" % entrysize
    print "POSS TYPE %s" % hex(type)
    print "GUID %s" % guid

    if type == 0x01:
        print "Waypoint"
        writeWaypoint(readWaypoint())
        waypoints+=1
    elif type == 0x21 or type == 0x22:
        print "Route"
        writeRoute(readRoute(type))
        routes+=1
    elif entrysize == 0xffff:
        print "End of output reached"
        done = True
    else:
        print "Skipping unknown type %s" % hex(type)

    # Pad byte, usually 0xcd
    if pos % 2 != 0:
        getAsByte()

    print "==="
    print "pos is %d - %s" % (pos, hex(pos))
    block+=1

print "Read %d waypoints and %d routes" % (waypoints, routes)

w.close(gpx)
