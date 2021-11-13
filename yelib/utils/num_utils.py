# encoding: utf-8

def int_bytes(v, length=4):
    return v.to_bytes(length=length, byteorder='big', signed=True)


def bytes_int(v):
    return int.from_bytes(v, byteorder='big', signed=True)
