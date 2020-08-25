import unittest


from pychess import util, constant as c


class TestUtil(unittest.TestCase):
    def setUp(self):
        self.dirs = c.Direction

    def tearDown(self):
        pass

    def test_get_move_direction(self):
        src = (3, 3)
        pairs = {
            (src, (1, 1)): c.Direction.sw,
            (src, (3, 1)): c.Direction.s,
            (src, (4, 1)): c.Direction.se,
            (src, (6, 3)): c.Direction.e,
            (src, (6, 5)): c.Direction.ne,
            (src, (3, 6)): c.Direction.n,
            (src, (1, 5)): c.Direction.nw,
            (src, (1, 3)): c.Direction.w,
        }

        expected_results = [d for d in pairs.values()]
        results = list(
                map(
                    lambda p: util.get_move_direction(*p),
                    pairs.keys(),
                )
        )
        self.assertEqual(results, expected_results)


if __name__ == '__main__':
    unittest.main()
