from unittest import TestCase

from pdf_annotate.util.geometry import identity
from pdf_annotate.util.geometry import matrix_multiply
from pdf_annotate.util.geometry import matrix_inverse
from pdf_annotate.util.geometry import rotate
from pdf_annotate.util.geometry import scale
from pdf_annotate.util.geometry import translate


class TestMatrixMath(TestCase):
    def test_multiply_identity(self):
        matrix = [1, 2, 3, 4, 5, 6]
        ident = identity()

        assert matrix == matrix_multiply(matrix, ident)
        assert matrix == matrix_multiply(ident, matrix)

    def test_translates_add(self):
        T1 = translate(3, 5)
        T2 = translate(2, -1)

        assert translate(5, 4) == matrix_multiply(T1, T2)
        assert translate(5, 4) == matrix_multiply(T2, T1)

    def test_scales_multiply(self):
        S1 = scale(2, 3)
        S2 = scale(5, 2)

        assert scale(10, 6) == matrix_multiply(S1, S2)
        assert scale(10, 6) == matrix_multiply(S2, S1)

    def test_rotations_add(self):
        R1 = rotate(90)
        R2 = rotate(45)

        assert rotate(135) == matrix_multiply(R1, R2)
        assert rotate(135) == matrix_multiply(R2, R1)

    def test_invert_rotation(self):
        assert rotate(-45) == matrix_inverse(rotate(45))
        assert rotate(90) == matrix_inverse(rotate(-90))

        assert identity() == matrix_multiply(rotate(45), rotate(-45))
        assert identity() == matrix_multiply(rotate(-45), rotate(45))

        assert identity() == matrix_multiply(rotate(90), rotate(-90))
        assert identity() == matrix_multiply(rotate(-90), rotate(90))

    def test_invert_scale(self):
        assert scale(2, 4) == matrix_inverse(scale(0.5, 0.25))
        assert scale(0.1, 8) == matrix_inverse(scale(10, 0.125))

        assert identity() == matrix_multiply(scale(2, 4), scale(0.5, 0.25))
        assert identity() == matrix_multiply(scale(0.1, 8), scale(10, 0.125))

    def test_invert_translate(self):
        assert translate(-3, -5) == matrix_inverse(translate(3, 5))
        assert translate(-2, 1) == matrix_inverse(translate(2, -1))

    def test_multiply_is_associative(self):
        R = rotate(45)
        S = scale(3, 2)
        T = translate(5, -1)

        # T*(S*R)
        M1 = matrix_multiply(T, matrix_multiply(S, R))
        # (T*S)*R
        M2 = matrix_multiply(matrix_multiply(T, S), R)

        assert M1 == M2
        assert M1 == matrix_multiply(T, S, R)

    def test_invert_identity(self):
        ident = identity()

        assert ident == matrix_inverse(ident)
