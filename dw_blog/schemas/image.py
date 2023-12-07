from enum import Enum


class ImageType(str, Enum):
    GIF = "image/gif"
    BMP = "image/bmp"
    JPEG = "image/jpeg"
    JPG = "image/jpg"
    PNG = "image/png"
    SVG = "image/svg+xml"
    TIFF = "image/tiff"
    WEBP = "image/webp"
