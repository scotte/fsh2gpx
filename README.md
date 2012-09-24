fsh2gpx
=======

Python script for converting Raymarine FSH files to OpenCPN compatible GPX files

This script is for converting waypoints, routes, and tracks from Raymarine chartplotters (using the FSH format) into a GPX file suitable for importing into OpenCPN.

Current state of development
----------------------------

* Minimal waypoint and route parsing and GPX export works
* Tracks are not yet supported
* Many attributes have not yet been decoded
* Lots of debug output to stdout
* Code is very rough and not modular
* There are no validity checks, so this could easily get in an endless loop if it decodes a value incorrectly

Routes seem to be encoded twice in FSH files sometimes, and as the format hasn't been fully decoded it may not import correctly into OpenCPN.

If the script doesn't work, please help me improve this by creating a bug on github. Attach your FSH file if you can.

Usage
-----

$ python fsh2gpx.py archive.fsh output.gpx

Supported plotters
------------------

Raymarine chartplotters that save data to flash cards using the RL90 FSH format. C-Series chartplotters are certainly supported, as is probably the RL90. Files written by Raytech Navigator should work as well. The only way to really be sure is try it. If the file isn't called "archive.fsh", then it probably won't work.

Why this project exists
-----------------------

I have a C-Series chartplotter on my sailboat and have a bunch of waypoints, routes, and tracks from a trip to Mexico that I want to retain, as well as import into OpenCPN. Unfortunately, Raymarine chose a proprietary binary format for these chartplotters to save data. The tools available to open FSH files are either not-free or very limited - such as not supporting all FSH data (such as tracks), or by only running on Windows.

I'm decoding the FSH format in a fairly brute-force manner - hours and hours of staring at hexdumps of files with known waypoints and routes and incrementally writing the code to parse them. Because of this, it's very, very easy for this script to break if it gets a value it's not expecting.

Future plans
------------

Once the FSH format has been fully decoded, it would be reasonable to convert this to a GPS Babel filter. Once the project is to this stage, this fsh2gpx python script will be deprecated.

If you are interested in helping out, feel free to dig in!

License
-------
fsh2gpx is distributed as free, open source software under the GNU General Public License 3.0. See LICENSE for the complete license text.

Project website
---------------

https://github.com/scotte/fsh2gpx
