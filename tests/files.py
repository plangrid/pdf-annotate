import os.path


dirname, _ = os.path.split(os.path.abspath(__file__))

SIMPLE = os.path.join(dirname, 'pdfs', 'simple.pdf')
ROTATED_90 = os.path.join(dirname, 'pdfs', 'rotated_90.pdf')
ROTATED_180 = os.path.join(dirname, 'pdfs', 'rotated_180.pdf')
ROTATED_270 = os.path.join(dirname, 'pdfs', 'rotated_270.pdf')

BINARIZED_PNG = os.path.join(dirname, 'images', 'binarized.png')
GRAYSCALE_PNG = os.path.join(dirname, 'images', 'grayscale.png')
RGB_PNG = os.path.join(dirname, 'images', 'rgb.png')
ALPHA_PNG = os.path.join(dirname, 'images', 'rgba.png')

PNG_FILES = [
    BINARIZED_PNG,
    GRAYSCALE_PNG,
    RGB_PNG,
    ALPHA_PNG,
]
