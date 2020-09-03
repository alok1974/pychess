import unittest
import itertools


from pychess.squarer import Square


def get_exception_string(address, error_no):
    if error_no == 1:
        return (
            'Expected address as tuple of length of 2, '
            f'recieved address={address}'
        )
    elif error_no == 2:
        return (
            'x and y should be a number from 0 to 7, '
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
            'where each elements of tuple is a number from 0 to 7 or '
            'it should be a string of the form '
            '\'<alpha><number>\' where <alpha> is one of '
            '\'abcdefgh\' and <number> is from 1 to 8, example '
            '\'a5\', \'h4\' etc.'
        )
    else:
        raise ValueError(f'Unable to handle error_no={error_no}')


class TestSquarer(unittest.TestCase):
    def setUp(self):
        self.x_map = dict(
            [
                (i, 'abcdefgh'[i])
                for i in range(8)
            ]
        )
        self.y_map = dict(
            [
                (i, str(i + 1))
                for i in range(8)
            ]
        )

        self.squares = dict(
            [
                ((x, y), Square((x, y)))
                for (x, y) in itertools.product(range(8), range(8))
            ]
        )

    def test_x(self):
        for (x, y), square in self.squares.items():
            expected_result = x
            self.assertEqual(square.x, expected_result)

    def test_y(self):
        for (x, y), square in self.squares.items():
            expected_result = y
            self.assertEqual(square.y, expected_result)

    def test_x_address(self):
        for (x, y), square in self.squares.items():
            expected_result = self.x_map[x]
            self.assertEqual(square.x_address, expected_result)

    def test_y_address(self):
        for (x, y), square in self.squares.items():
            expected_result = self.y_map[y]
            self.assertEqual(square.y_address, expected_result)

    def test_address(self):
        for (x, y), square in self.squares.items():
            expected_result = f'{self.x_map[x]}{self.y_map[y]}'
            self.assertEqual(square.address, expected_result)

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

    def test_hash(self):
        for (x, y), square in self.squares.items():
            expected_result = 10 * x + y
            self.assertEqual(hash(square), expected_result)

    def test_equals(self):
        s1 = Square((1, 3))
        s2 = Square((1, 3))
        self.assertEqual(s1, s2)
        self.assertFalse(s1 is s2)

    def test_not_equals(self):
        s1 = Square((1, 3))
        s2 = Square((3, 1))

        self.assertNotEqual(s1, s2)

    def test_greater(self):
        s1 = Square('a1')
        s2 = Square('a2')

        self.assertGreater(s2, s1)

    def test_less(self):
        s1 = Square('a1')
        s2 = Square('a2')

        self.assertLess(s1, s2)

    def test_geater_equals(self):
        s1 = Square('a1')
        s2 = Square('a2')

        self.assertGreaterEqual(s2, s1)

    def test_less_equals(self):
        s1 = Square('a1')
        s2 = Square('a2')

        self.assertLess(s1, s2)

    def test_repr(self):
        for (x, y), square in self.squares.items():
            address = f'{self.x_map[x]}{self.y_map[y]}'
            expected_result = f'<Square: {address}>'
            self.assertEqual(repr(square), expected_result)


if __name__ == "__main__":
    unittest.main()
