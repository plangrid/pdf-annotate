# pdf-annotate
A pure-python library to add annotations to PDFs.

## About
pdf-annotate is a simple library to add PDF annotations to PDFs. Under the hood
it uses the powerful and unopinionated `pdfrw` library to parse the PDF to
figure out where to place the annotations.

## Usage
```python
from pdf_annotate import PdfAnnotator, Location, Appearance
a = PdfAnnotator('a.pdf')
a.add_annotation(
    'square',
    Location(x1=50, y1=50, x2=100, y2=100, page=0),
    Appearance(stroke_color=(1, 0, 0), stroke_width=5),
)
a.write('b.pdf')  # or use overwrite=True if you feel lucky
```
