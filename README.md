o3d3xx-python
=============

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

with your device's IP address to create an example application and

    $ python image_viewer.py 192.168.0.69

to view the image data coming from the camera (requires matplotlib)

Usage
-----
### RPC client
The library provides all XMLRPC objects as mentioned in the camera's XMLRPC
manual. The entry point is the RPC main object which can be created with e.g.

    camera = o3d3xx.Device("192.168.0.69")

RPC calls can be performed e.g. like this

    version_info = camera.getSWVersion()
    
These are the different RPC objects and the possibilites how they can be
acquired:

* Session object
    - `session = camera.requestSession()`  
      This is different from the regular RPC call which only returns the
      session ID. The session ID can be retrieved from `camera.sessionID`
    - `session = camera.session` (only valid after a `requestSession()` call)
* EditMode object
    - `edit = session.startEdit()` which is equivalent to
    - `edit = session.setOperatingMode(1)` (again, this is different from the
      pure RPC call)
    - `edit = session.edit` (only valid after a  `startEdit()` call)
* DeviceConfig object
    - `device = edit.device`
* NetworkConfig object
    - `network = edit.network`
* ApplicationConfig object
    - `application = edit.editApplication(1)` (different from the pure RPC)
    - `application = edit.application` (only valid after a `editApplication()`
      call)
* ImagerConfig object
    - `imagerConfig = application.imagerConfig`
* Spatial filter configuration object
    - `spatialFilter = application.spatialFilter`
* Temporal filter configuration object
    - `temporalFilter = application.temporalFilter`

### PCIC client
The library currently provides two basic clients:

* A simple PCIC V3 client
    - Create it with `pcic = o3d3xx.PCICV3Client("192.168.0.69", 50010)`
      providing the device's address and PCIC port.
    - Send PCIC commands with e.g. `answer = pcic.sendCommand("G?")`. All
      asnychronous PCIC messages are discarded while waiting for the answer
      to the command.
    - Read back the next PCIC for a particular ticket number. This can be used
      to read asynchronously sent results (ticket number "0000"):  
      `answer = pcic.readAnswer("0000")`
    - Read back any answer coming from the device:  
      `ticket, answer = pcic.readNextAnswer()`
* A PCIC client for asynchronous image retrieval
    - Create it with `pcic = o3d3xx.ImageClient("192.168.0.69", 50010)`.
    - It configures a PCIC connection to receive all image types.
    - Read back the next result (a dictionary containing all the images)
      with `result = pcic.readNextFrame()`

Links
-----
O3D3xx related libraries for other programming languages:

* C++: [libo3d3xx](https://github.com/lovepark/libo3d3xx)
* Ruby: [ruby-o3d3xx](https://github.com/ifm/ruby-o3d3xx)

Contributing
------------
o3d3xx-python is available at
[Github](https://github.com/ifm/o3d3xx-python)
