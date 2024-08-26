import ctypes

PyLong_AsByteArray = ctypes.pythonapi._PyLong_AsByteArray
PyLong_AsByteArray.argtypes = [ctypes.py_object,
                               ctypes.POINTER(ctypes.c_uint8),
                               ctypes.c_size_t,
                               ctypes.c_int,
                               ctypes.c_int]


def int_to_bytes(num: int, buffer=None):
    byte_length = num.bit_length() // 8 + 1
    if buffer is None or len(buffer) < byte_length:
        buffer = (ctypes.c_uint8 * byte_length)()
    PyLong_AsByteArray(num, buffer, byte_length, 0, 1)
    return buffer
