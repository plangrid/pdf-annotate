# pdf-annotate
A pure-python library to add annotations to PDFs.

[![Build Status](https://travis-ci.com/plangrid/pdf-annotate.svg?branch=master)](https://travis-ci.com/plangrid/pdf-annotate)

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
### Annotation Types
`pdf-annotate` includes most of the basic PDF annotation types, leaving out some
of the more complex interactive types. Contributions for these welcome! Currently supported
annotation types are:

* square
* circle
* line
* polygon
* polyline
* ink
* text
* image

### Appearance
Annotations' appearance is controlled by the `Appearance` class, passed to the
`appearance` argument to `add_annotation`. Not all attributes
on this class apply to all annotations; documentation on this is forthcoming.

### Location
Where an annotation is placed on the PDF is controlled by the `Location` class, passed
to the `location` argument to `add_annotation`. By default these coordinates are in the
PDF's user space scale, which is "points". There are 72 points/inch, so an 8.5"x11" PDF
would have a coordinate system of 612x792. See [scaling and rotation](#scaling-and-rotation) below
for changing the coordinate system.

Annotations that are defined by width/height
(square, circle, text, image) require `x1`, `y1`, `x2`, `y2` attributes, while annotations
that are defined by a list of points (line, polygon, polyline, ink) require a `points` attribute.
All annotations require a `page` attribute, which determines which page of the PDF the
annotations will be placed on.

### Metadata
PDF annotations can contain arbitrary metadata. This is controlled by the `Metadata` class,
passed to the `metadata` argument to `add_annotation`. By default, annotations will contain
default values for creation date, modification date, unique name (just a uuid), and the print flag
set. To leave off any of these, use the `UNSET` singleton. For more context, check out the
[`Metadata`](https://github.com/plangrid/pdf-annotate/blob/a59e1554f6bb912087932d1c0c4f3524524309fa/pdf_annotate/config/metadata.py#L43)
class itself.

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

## Advanced Usage

### Using the Content Stream
`pdf-annotate` also includes an abstraction of the PDF content stream that you can use to
draw arbitrary annotation shapes onto the PDF. To fully take advantage of this feature, we
recommend reading the relevant parts of the [PDF specification](https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf):
(Section 8 - Graphics and Section 12.5.5 - Annotation Appearance Streams).

To use an explicit content stream in an annotation, specify the `appearance_stream`
argument to the `Appearance` object as a `pdf_annotate.graphics.ContentStream` object.
See the [end-to-end tests](https://github.com/plangrid/pdf-annotate/blob/a59e1554f6bb912087932d1c0c4f3524524309fa/tests/end_to_end/test_annotate_pdf.py#L317)
for examples.

## Local Development
Tests are run against several supported python versions using `tox`. To get this to
work, you need versioned python executables - e.g. `python3.6` - in your path.

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
To check a specific version, use e.g. `tox -e py36`.
