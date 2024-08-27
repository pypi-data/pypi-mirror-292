import ctypes
import sys
from math import log2

import argon2

from decentnet.consensus.blockchain_params import BlockchainParams
from decentnet.modules.pow.difficulty import Difficulty

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
    return bytes(buffer)


def compute_pow(n_bits, hash_t, nonce):
    _bits = len(hash_t.value) * 8 - n_bits

    value = hash_t.value_as_int()

    current_value = value

    while log2(hash_t.value_as_int()) >= _bits:
        current_value %= sys.maxsize
        current_value += 1
        nonce += 1
        hash_t.recompute(
            int_to_bytes(current_value))

    return nonce


def hash_func(data: bytes, diff: Difficulty):
    return argon2.hash_password_raw(data, BlockchainParams.default_salt, diff.t_cost,
                                    diff.m_cost,
                                    diff.p_cost, diff.hash_len_chars)
