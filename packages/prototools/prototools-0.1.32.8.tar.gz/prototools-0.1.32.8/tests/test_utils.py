import io
from textwrap import dedent
from unittest import main, TestCase
from unittest.mock import patch

import prototools.utils as utils


class Test(TestCase):

    def test_language(self):
        f = utils._("y", "es")
        self.assertEqual(f, "s")
        f = utils._("took", "es")
        self.assertEqual(f, "tardó")

    def test_RangeDict(self):
        """Test RangeDict class"""
        rd = utils.RangeDict(
            {
                (1, 2): 'a',
                (3, 4): 'b',
                (5, 6): 'c',
            }
        )
        self.assertEqual(rd[1], 'a')
        self.assertEqual(rd[2], 'a')
        self.assertEqual(rd[3], 'b')
        self.assertEqual(rd[4], 'b')
        self.assertEqual(rd[5], 'c')
        self.assertEqual(rd[6], 'c')
        with self.assertRaises(KeyError):
            rd[7]
        self.assertEqual(rd[(1, 2)], 'a')
        self.assertEqual(rd[(3, 4)], 'b')
        self.assertEqual(rd[(5, 6)], 'c')

    def test_strip_ansi(self):
        self.assertEqual(
            utils.strip_ansi("\x1b[1m\x1b[31mHello\x1b[0m"), "Hello",
        )
        self.assertEqual(
            utils.strip_ansi(
                "\x1b[1m\x1b[31mHello\x1b[0m\x1b[1m\x1b[31mWorld\x1b[0m",
            ),
            "HelloWorld",
        )

    def test_strip_ansi_width(self):
        s = "\x1b[1m\x1b[31mHello\x1b[0m\x1b[1m\x1b[31mWorld\x1b[0m"
        self.assertEqual(utils.strip_ansi_width(s), 26)

    def test_strip_string(self):
        self.assertEqual(utils.strip_string("Hello", strip=None), "Hello")
        self.assertEqual(utils.strip_string("/Hello", strip="/"), "Hello")
        self.assertEqual(utils.strip_string("Hello/", strip="/"), "Hello")
        self.assertEqual(utils.strip_string("/Hello/", strip="/"), "Hello")
        self.assertEqual(utils.strip_string("Hello", strip="o"), "Hell")
        self.assertEqual(utils.strip_string("Hello", strip="H"), "ello")

    def test_chunker(self):
        self.assertEqual(
            list(utils.chunker(list(range(10)), 3)),
            [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]],
        )
        self.assertEqual(
            list(utils.chunker(list(range(10)), 4)),
            [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]],
        )
        self.assertEqual(
            list(utils.chunker(list(range(10)), 5)),
            [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]],
        )

    def test_pairs(self):
        self.assertEqual(
            list(utils.pairs(list(range(8)))),
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)],
        )
    
    def test_tail(self):
        self.assertEqual(
            list(utils.tail(3, "ABCDEFG")), ["E", "F", "G"]
        )

    def test_flatten(self):
        self.assertEqual(
            list(utils.flatten([[0, 1], [2, 3]])),
            [0, 1, 2, 3],
        )

    def test_grouper(self):
        self.assertEqual(
            list(utils.grouper('ABCDEFG', 3, 'x')),
            [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x')],
        )

    def test_partition(self):
        is_even = lambda x: x % 2
        even, odd = utils.partition(is_even, list(range(10)))
        self.assertEqual(list(even), [0, 2, 4, 6, 8])
        self.assertEqual(list(odd), [1, 3, 5, 7, 9])
        lesser, greater = utils.partition(lambda x: x > 5, range(10))
        self.assertEqual(list(lesser), [0, 1, 2, 3, 4, 5])
        self.assertEqual(list(greater), [6, 7, 8, 9])

    @patch('builtins.input', return_value='n')
    def test_main_loop(self, mock_input):
        def func(): 
            return None

        utils.main_loop(func)

    @patch('builtins.input', return_value='y')
    def test_ask_to_finish(self, mock_input):
        self.assertEqual(utils.ask_to_finish(), True)

    @patch('sys.stdout', new_callable=io.StringIO)
    def assert_stdout(self, expected, mock_stdout, function=None, args=None):
        if function:
            function(*args)
        self.assertEqual(mock_stdout.getvalue(), expected)

    def test_text_align(self):
        expected = "═══════════════ Test\n"
        self.assert_stdout(
            expected,
            function=utils.text_align, args=("Test", 20, "double", "right"),
        )

    def test_time_functions(self):
        def f(s):
            return range(10)
        
        def g(s):
            return range(100)
        
        fs = {"f": f, "g": g}
        self.assertEqual(
            utils.time_functions(fs, args="", globals=locals()),
            None,
        )

    def test_create_f(self):
        t = utils.create_f("fs", "x", "return x+2")
        self.assertEqual(t(1), 3)
        r = utils.create_f("gs", "x y", "return x*y")
        self.assertEqual(r(2, 3), 6)


    def test_compose(self):
        f = lambda x: x - 2
        g = lambda x: x + 2
        h = lambda x: x * 3
        i = lambda x: x - 2
        self.assertEqual(utils.compose(f, g, h, i)(2), 4)
        self.assertEqual(utils.compose(f, g, h, i)(4), 10)
        self.assertEqual(utils.compose(f, g, h, i)(3), 7)


if __name__ == '__main__':
    main()