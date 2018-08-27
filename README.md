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

### Scaling and rotation
`pdf-annotate` draws annotations as though you were drawing them in a PDF viewer,
meaning it assumes you want to draw on the rotated page. For example an annotation drawn at
(10, 10) on a 90° rotated page will still appear in the bottom left, not the top-left.

It also supports specifying your annotations' coordinates in differently scaled coordinate systems.
If, for example, you know your coordinates are in the system of the PDF rastered at 150 DPI, you
would specify `scale=72.0/150` in the constructor to properly scale your coordinates to PDF user space.

Finally, if all you have is the dimensions of each page in the viewer's coordinate system, you can
specify these. Building on the previous example, if you know the dimensions of page 0, you would use
```python
a = PdfAnnotator('a.pdf')
a.set_page_dimensions((1275, 1650), 0)
```
Note that these are the dimensions of an un-rotated 8.5"x11" page rastered at 150 DPI. If the same page is
rotated 90° or 270°, you would pass in `(1650, 1275)`.
Setting page dimensions specifically overrides document-wide scale and rotation settings.

## Local Development
Tests are run against several supported python versions using `tox`. To get this to
work, you need versioned python executables - e.g. `python3.5` - in your path.

An opinionated setup, which assumes you have certain python versions installed,
and that you use `pyenv`, is provided by `make setup`. After this you can run
`tox` to run tests.

### Manual tests
Fully automated testing is difficult for things that depend on the complexities
of PDF viewers. When making changes, it's good practice to compare the file
`tests/end_to_end/pdfs/end_to_end.pdf`, which is generated during testing,
with `expected.pdf` in the same directory. To ensure rotation is handled correctly,
there is also `end_to_end_rotated_90.pdf` and corresponding expected file.

By default, the file will be the one generated during the last python version's `tox` run.
To check a specific version, use e.g. `tox -e py27`.
