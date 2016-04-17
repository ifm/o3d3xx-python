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

Usage
-----

The library provides all XMLRPC objects as mentioned in the camera's XMLRPC manual. The entry point is the RPC main object which can be created with e.g.

    camera = o3d3xx.Device("192.168.0.69")

RPC calls can be performed e.g. like this

    version_info = camera.getSWVersion()
    
These are the different RPC objects and the possibilites how they can be acquired:

* Session object
    - `session = camera.requestSession()`  
      This is different from the regular RPC call which only
      returns the session ID. The session ID can be
      retrieved from `camera.sessionID`
    - `session = camera.session` (only valid after a 
      `requestSession()` call
* EditMode object
    - `edit = session.startEdit()` which is equivalent to
    - `edit = session.setOperatingMode(1)` (again, this is
      different from the pure RPC call)
    - `edit = session.edit` (only valid after a 
      `startEdit()` call)
* DeviceConfig object
    - `device = edit.device`
* NetworkConfig object
    - `network = edit.network`
* ApplicationConfig object
    - `application = edit.editApplication(1)` (different
      from the pure RPC)
    - `application = edit.application` (only valid after a
      `editApplication()` call)
* ImagerConfig object
    - `imagerConfig = application.imagerConfig`
* Spatial filter configuration object
    - `spatialFilter = application.spatialFilter`
* Temporal filter configuration object
    - `temporalFilter = application.temporalFilter`
