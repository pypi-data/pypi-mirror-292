import struct
import zlib
from itertools import chain

from kivy.graphics.texture import Texture


class Gradient(object):

    @staticmethod
    def horizontal(*args):
        texture = Texture.create(size=(len(args), 1), colorfmt='rgba')
        buf = bytes([int(v * 255) for v in chain(*args)])  # flattens

        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        return texture

    @staticmethod
    def vertical(*args):
        texture = Texture.create(size=(1, len(args)), colorfmt='rgba')
        buf = bytes([int(v * 255) for v in chain(*args)])  # flattens
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        return texture


def save_as_png(width, height, pixel_data, filename=None):
    # Prepare PNG header
    png_header = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr = (
            struct.pack(">I", width)
            + struct.pack(">I", height)
            + b'\x08\x06\x00\x00\x00'
    )
    ihdr_crc = struct.pack(
        ">I",
        zlib.crc32(b'IHDR' + ihdr) & 0xffffffff
    )
    ihdr_chunk = (
            struct.pack(">I", len(ihdr))
            + b'IHDR' + ihdr + ihdr_crc
    )

    # IDAT chunk
    # Rearrange the pixels into scanlines
    scanlines = b''.join(
        b'\x00' + pixel_data[4 * i * width: 4 * (i + 1) * width]
        for i in range(height)
    )
    compressed_data = zlib.compress(scanlines)
    idat_crc = struct.pack(
        ">I",
        zlib.crc32(b'IDAT' + compressed_data) & 0xffffffff
    )
    idat_chunk = (
            struct.pack(">I", len(compressed_data))
            + b'IDAT' + compressed_data + idat_crc
    )

    # IEND chunk
    iend_chunk = (
            struct.pack(">I", 0)
            + b'IEND'
            + struct.pack(">I", zlib.crc32(b'IEND') & 0xffffffff)
    )

    image_byte = png_header + ihdr_chunk + idat_chunk + iend_chunk

    # Write all chunks to the file
    if filename:
        with open(filename, 'wb') as f:
            f.write(png_header)
            f.write(ihdr_chunk)
            f.write(idat_chunk)
            f.write(iend_chunk)

    return image_byte
