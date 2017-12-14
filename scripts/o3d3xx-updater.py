'''
Copyright (c) 2017 Phil Puetzstueck

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import requests
import o3d3xx
import os.path
import time
import threading
import sys
import json

class SWUpdate :

    def __init__(self, hostname='192.168.0.69', filename=None):
        if not hostname:
            self.hostname = "192.168.0.69"
        else:
            self.hostname=hostname
        self.xml_rpc = o3d3xx.Device(self.hostname)
        self.filename = filename

    def __enter__(self):
        return self

    def __exit__(self,exc_type, exc_value, traceback):
        pass


    def check_filename(self, filename):
        while not filename or not os.path.exists(filename):
            filename = input("Input file not Found. Please enter filepath: ")
        return filename

    def upload(self,filename):
        # the camera doesnt respong, so the post never returns, this is a quite hackish (hopefully temp.) solution:
        filename = self.check_filename(filename)
        payload = open(filename, 'rb').read()
        header = {'Content-Type':'application/octet-stream','X_FILENAME': filename}
        url = 'http://{}:8080/handle_post_request'.format(self.hostname)
        print('Uploading update file: ' + filename + ' to ' + url )

        def post():
            requests.post(url,headers=header,data=payload)
        thread = threading.Thread(target = post)
        thread.daemon = True
        thread.start()

        finished = False

        while not finished:
            isOk, res = self.status()
            if isOk and res["Msg"] != "":
                print("\n"+res["Msg"])
            if not isOk:
                raise requests.exceptions.HTTPError("Something went wrong during Uploading/Installation")
            if res["Error"] != "0":
                print(json.dumps(res, indent = 4))
                raise requests.exceptions.HTTPError("Error occured during Installation")
            finished = res["Status"] == "3"
            time.sleep(0.5)
        print("Finished Install")

    def status(self):
        url = 'http://{}:8080/getstatus.json'.format(self.hostname)
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            return True,r.json()
        else:
            return False,{}

    def install_swu(self, filename):
        self.upload(filename)
        self.reboot()

    def reboot(self):
        print("Rebooting to productive mode...")
        requests.post("http://"+self.hostname+":8080/reboot_to_live")

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", help="specify input SWU file and install update")
    p.add_argument("-H", "--host", help="specify host ip")
    args = p.parse_args()
    if len(sys.argv) == 1:
        p.print_help()
    else:
        s = SWUpdate(args.host)
        if args.input:
            s.install_swu(os.path.expanduser(args.input))
        else:
            s.install_swu("")
