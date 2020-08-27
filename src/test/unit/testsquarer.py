import unittest


from pychess.squarer import Square


def get_exception_string(address, error_no):
    if error_no == 1:
        return (
            'Expected address as tuple of length of 2, '
            f'recieved address={address}'
        )
    elif error_no == 2:
        return (
            'x and y should be a number from 1 to 8, '
            f'given x={address[0]}, y={address[1]}'
        )
    elif error_no == 3:
        return (
            f'The given address={address} is invalid, '
            'it should be a string of the form '
            '\'<alpha><number>\' where <alpha> is one of '
            '\'abcdefgh\' and <number> is from 1 to 8, example '
            '\'a5\', \'h4\' etc.'
        )
    elif error_no == 4:
        return (
            f'The given address={address} is invalid, '
            'it should either be a tuple like (0, 5) '
            'where each elements of tuple is a number from 1 to 8 or '
            'it should be a string of the form '
            '\'<alpha><number>\' where <alpha> is one of '
            '\'abcdefgh\' and <number> is from 1 to 8, example '
            '\'a5\', \'h4\' etc.'
        )
    else:
        raise ValueError(f'Unable to handle error_no={error_no}')


class TestSquarer(unittest.TestCase):
    def test_eq(self):
        s1 = Square((1, 3))
        s2 = Square((1, 3))
        self.assertEqual(s1, s2)
        self.assertFalse(s1 is s2)

    def test_neq(self):
        s1 = Square((1, 3))
        s2 = Square((3, 1))

        self.assertNotEqual(s1, s2)

    def test_repr(self):
        s = Square((1, 6))
        expected_result = '<Square: b7 (1, 6)>'
        self.assertEqual(repr(s), expected_result)

    def test_address(self):
        s1 = Square((1, 6))
        s2 = Square('b7')
        self.assertEqual(s1, s2)

    def test_parse_adress_1(self):
        address = (1, 2, 3)
        with self.assertRaises(Exception) as context:
            Square(address)

        exc_str = get_exception_string(address=address, error_no=1)
        self.assertTrue(exc_str in str(context.exception))

    def test_parse_adress_2(self):
        address = 1,
        with self.assertRaises(Exception) as context:
            Square(address)

        exc_str = get_exception_string(address=address, error_no=1)
        self.assertTrue(exc_str in str(context.exception))

    def test_parse_adress_3(self):
        address = ('a', 2)
        with self.assertRaises(Exception) as context:
            Square(address)

        exc_str = get_exception_string(address=address, error_no=2)
        self.assertTrue(exc_str in str(context.exception))

    def test_parse_adress_4(self):
        address = ('a4g5a2s#')
        with self.assertRaises(Exception) as context:
            Square(address)

        exc_str = get_exception_string(address=address, error_no=3)
        self.assertTrue(exc_str in str(context.exception))

    def test_parse_adress_5(self):
        address = (23)
        with self.assertRaises(Exception) as context:
            Square(address)

        exc_str = get_exception_string(address=address, error_no=4)
        self.assertTrue(exc_str in str(context.exception))


if __name__ == "__main__":
    unittest.main()
