import io
import sys
from contextlib import contextmanager
from unittest import main, TestCase
from unittest.mock import patch

import prototools.inputs as proto
import prototools.validators as v


@contextmanager
def replace_stdin(target):
    original = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = original


class Test(TestCase):

    def test_str_input(self):
        with replace_stdin(io.StringIO("abc")):
            proto.str_input()

    def test_int_input(self):
        with replace_stdin(io.StringIO("69")):
            proto.int_input()
        with replace_stdin(io.StringIO(" 2")):
            proto.int_input()
        with replace_stdin(io.StringIO("1 ")):
            proto.int_input()
        with replace_stdin(io.StringIO("1")), \
            self.assertRaises(EOFError) as msg:
            proto.int_input(min="abc")
        self.assertEqual("EOF when reading a line", str(msg.exception))
    
    def test_float_input(self):
        with replace_stdin(io.StringIO("3.14")):
            proto.float_input()

    def test_yes_no_input(self):
        with replace_stdin(io.StringIO("y")):
            proto.yes_no_input()
        with replace_stdin(io.StringIO("1")), \
            self.assertRaises(EOFError) as msg:
            proto.yes_no_input(yes_value="")
        self.assertEqual("EOF when reading a line", str(msg.exception))

    def test_bool_input(self):
        with replace_stdin(io.StringIO("True")):
            proto.bool_input()
        with replace_stdin(io.StringIO("1")), \
            self.assertRaises(EOFError) as msg:
            proto.bool_input(true_value="")
        self.assertEqual("EOF when reading a line", str(msg.exception))

    def test_choice_input(self):
        with replace_stdin(io.StringIO("a")):
            proto.choice_input(["a", "b", "c"])
        with replace_stdin(io.StringIO("b")):
            proto.choice_input(["a", "b", "c"])
        with replace_stdin(io.StringIO("c")):
            proto.choice_input(["a", "b", "c"])

    def test_menu_input(self):
        with replace_stdin(io.StringIO("1")):
            proto.menu_input(["x", "y", "z"], numbers=True)
        with replace_stdin(io.StringIO("x")):
            proto.menu_input(["x", "y", "z"], numbers=True)
        with replace_stdin(io.StringIO("x")), \
            self.assertRaises(v.ValidatorsException) as msg:
            proto.menu_input(choices="")
        self.assertEqual(
            "'choices' must have at least two items if 'blank' is False",
            str(msg.exception)
        )

    @patch("prototools.inputs.str_input", return_value=1)
    def test_mock_int_input(self, mock_input):
        response = mock_input()
        self.assertEqual(response, 1)

    @patch("prototools.inputs.int_input", return_value=1)
    def test_mock_yes_no_input(self, mock_input):
        response = proto.int_input()
        self.assertEqual(response, 1)

    @patch("prototools.inputs.float_input", return_value=3.14)
    def test_mock_yes_no_input(self, mock_input):
        response = proto.float_input()
        self.assertEqual(response, 3.14)

    @patch("prototools.inputs.yes_no_input", return_value="yes")
    def test_mock_yes_no_input(self, mock_input):
        response = proto.yes_no_input()
        self.assertEqual(response, "yes")

    @patch("prototools.inputs.bool_input", return_value=True)
    def test_mock_bool_input(self, mock_input):
        response = proto.bool_input()
        self.assertEqual(response, True)

    @patch("prototools.inputs.date_input", return_value="1/1/2021")
    def test_mock_date_input(self, mock_input):
        response = proto.date_input()
        self.assertEqual(response, "1/1/2021")


if __name__ == "__main__":
    main()