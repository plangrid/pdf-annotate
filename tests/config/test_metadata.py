from datetime import datetime
from unittest import TestCase

from pdf_annotate.config.metadata import Flags
from pdf_annotate.config.metadata import Metadata
from pdf_annotate.config.metadata import serialize_value


class TestMetadata(TestCase):

    def test_defaults(self):
        m = Metadata()
        assert isinstance(m.metadata['CreationDate'], datetime)
        assert isinstance(m.metadata['M'], datetime)
        assert m.metadata['F'] == 4
        assert isinstance(m.metadata['NM'], str)

    def test_specified(self):
        creation = datetime(2016, 1, 1)
        modified = datetime(2018, 1, 1)
        flags = Flags.Print | Flags.ReadOnly | Flags.Locked
        m = Metadata(
            creation_date=creation,
            modified_date=modified,
            name='Bailey',
            flags=flags,
        )
        assert m.metadata['CreationDate'] == creation
        assert m.metadata['M'] == modified
        assert m.metadata['NM'] == 'Bailey'
        assert m.metadata['F'] == flags

    def test_extra_kwargs(self):
        m = Metadata(Subj='rectangle')
        assert m.metadata['Subj'] == 'rectangle'

    def test_serialize(self):
        d = datetime(2016, 1, 27, 9, 23, 2)
        s = serialize_value(d)
        assert s == "D:20160127092302+00'00"
