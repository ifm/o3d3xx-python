# o3d3xx-python

A Python 2/3 library for ifm efector O3D3xx 3D cameras

Features
--------

* easy XMLRPC interface with integrated session handling
* PCIC V3 client for result data transfer

Prerequisites
-------------

Usage with Python 2 requires the 'future' package

Installation
------------

Install the package with

   $ python setup.py install

Examples
--------

For a quick start, go to the `examples` folder and run

    $ python create_application.py 192.168.0.69

with your device's IP address to create an example
application and

    $ python image_viewer.py 192.168.0.69

to view the image data coming from the camera (requires matplotlib)
