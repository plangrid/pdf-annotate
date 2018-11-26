# -*- coding: utf-8 -*-
from unittest import TestCase

from pdf_annotate.annotations.image import Image
from pdf_annotate.config.location import Location
from tests.utils import assert_matrices_equal


class TestImageMethods(TestCase):

    def test_get_ctm(self):
        location = Location(x1=10, y1=20, x2=100, y2=200, page=0)
        assert_matrices_equal(
            Image.get_ctm(0, location),
            [90, 0, 0, 180, 10, 20],
        )
        assert_matrices_equal(
            Image.get_ctm(90, location),
            [0, 180, -90, 0, 100, 20],
        )
        assert_matrices_equal(
            Image.get_ctm(180, location),
            [-90, 0, 0, -180, 100, 200],
        )
        assert_matrices_equal(
            Image.get_ctm(270, location),
            [0, -180, 90, 0, 10, 200],
        )
