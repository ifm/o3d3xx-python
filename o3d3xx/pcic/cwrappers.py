import ctypes as ct


class ExtrinsicCalibration(ct.Structure):
    _fields_ = [("transX", ct.c_float),
                ("transY", ct.c_float),
                ("transZ", ct.c_float),
                ("rotX", ct.c_float),
                ("rotY", ct.c_float),
                ("rotZ", ct.c_float)]

    def __str__(self):
        return "{}: {{{}}}".format(self.__class__.__name__,", "
                .join(["{}: {}".format(field[0],getattr(self,field[0])) for field in self._fields_]))

class IntrinsicCalibration(ct.Structure):
    _fields_ = [("fx", ct.c_float),
                ("fy", ct.c_float),
                ("mx", ct.c_float),
                ("my", ct.c_float),
                ("alpha", ct.c_float),
                ("k1", ct.c_float),
                ("k2", ct.c_float),
                ("k5", ct.c_float),
                ("k3", ct.c_float),
                ("k4", ct.c_float),
                ("internalTransRot", ExtrinsicCalibration)]

    def __str__(self):
        return "{}: {{{}}}".format(self.__class__.__name__,", "
                .join(["{}: {}".format(field[0], getattr(self, field[0])) for field in self._fields_]))
