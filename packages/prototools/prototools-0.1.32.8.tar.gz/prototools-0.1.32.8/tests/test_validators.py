import datetime
import time
from unittest import main, TestCase

import prototools.validators as v


class Test(TestCase):

    def test_err_str(self):
        self.assertEqual(v.MAX_ERROR, 50)
        self.assertEqual(v._err_str("abc"), "abc")
        self.assertEqual(v._err_str("x"*51), "x"*50+"...")

    def test_validate_parameters(self):
        g = v._GenericValidate(blank=True, strip=None)
        self.assertEqual(g._validate_parameters(), None)

        g.blank = None
        with self.assertRaises(v.ValidatorsException):
            g._validate_parameters()

    def test_prevalidation(self):
        g = v._GenericValidate(blank=False, strip=None)
        g.value = ""
        with self.assertRaises(v.ValidatorsException) as msg:
            g._prevalidation()
        self.assertEqual("Blank values are not allowed", str(msg.exception))

    def test_validate_number_parameters(self):
        with self.assertRaises(v.ValidatorsException) as msg:
            v._GenericValidate(min="invalid")._validate_numbers_parameters()
        self.assertEqual(
            "'min' argument must be int, float, or None", str(msg.exception)
        )
        with self.assertRaises(v.ValidatorsException) as msg:
            v._GenericValidate(max="invalid")._validate_numbers_parameters()
        self.assertEqual(
            "'max' argument must be int, float, or None", str(msg.exception)
        )
        with self.assertRaises(v.ValidatorsException) as msg:
            v._GenericValidate(lt="invalid")._validate_numbers_parameters()
        self.assertEqual(
            "'lt' argument must be int, float, or None", str(msg.exception)
        )
        with self.assertRaises(v.ValidatorsException) as msg:
            v._GenericValidate(gt="invalid")._validate_numbers_parameters()
        self.assertEqual(
            "'gt' argument must be int, float, or None", str(msg.exception)
        )

    def test_validate_choices_parameters(self):
        with self.assertRaises(v.ValidatorsException) as msg:
            v._GenericValidate(choices=42)._validate_choices_parameters()
        self.assertEqual(
            "'choices' argument must be a sequence", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v._GenericValidate(
                choices=[], blank=False)._validate_choices_parameters()
        self.assertEqual(
            "'choices' must have at least two items if 'blank' is False",
            str(msg.exception)
            )
        with self.assertRaises(v.ValidatorsException) as msg:
            v._GenericValidate(
                choices=[], blank=True)._validate_choices_parameters()
        self.assertEqual(
            "'choices' must have at least one item", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v._GenericValidate(
                choices=["dog", "dog"], blank=False
            )._validate_choices_parameters()
        self.assertEqual("Duplicates entries in 'choices'", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v._GenericValidate(
                choices=["dog", "Dog"], blank=False
            )._validate_choices_parameters()
        self.assertEqual("Duplicate case-sensitive entries in 'choices'",
        str(msg.exception))

    def test_validate_str(self):
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_str(value="", blank=None)
        self.assertEqual("'blank' argument must be a bool", str(msg.exception))

    def test_validate_number(self):
        self.assertEqual(v.validate_number("69"), 69)
        self.assertEqual(v.validate_number("3.14"), 3.14)
        self.assertEqual(v.validate_number(69), 69)
        self.assertEqual(v.validate_number(3.14), 3.14)
        self.assertEqual(v.validate_number("", blank=True), "")
        self.assertEqual(v.validate_number("x69x", blank=True, strip="x"), 69)
        self.assertEqual(v.validate_number("", blank=True, n_type="num"), "")

        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_number("abc")
        self.assertEqual("abc is not a number", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_number("")
        self.assertEqual("Blank values are not allowed", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_number(" ", blank=True, strip=False, n_type="num")
        self.assertEqual("  is not a number", str(msg.exception))

    def test_validate_int(self):
        self.assertEqual(v.validate_int("69"), 69)
        self.assertEqual(v.validate_int(69), 69)

        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_int("abc")
        self.assertEqual("abc is not an integer", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_int("")
        self.assertEqual("Blank values are not allowed", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_int(" ", blank=True, strip=False)
        self.assertEqual("  is not an integer", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_int("3.14")
        self.assertEqual("3.14 is not an integer", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_int(3.14)
        self.assertEqual("3.14 is not an integer", str(msg.exception))

    def test_validate_float(self):
        self.assertEqual(v.validate_float("3.14"), 3.14)
        self.assertEqual(v.validate_float(3.14), 3.14)

        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_float("abc")
        self.assertEqual("abc is not a float", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_float("")
        self.assertEqual("Blank values are not allowed", str(msg.exception))
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_float(" ", blank=True, strip=False)
        self.assertEqual("  is not a float", str(msg.exception))

    def test_validate_choices(self):
        choices = ["69", "cat", "dog"]
        long_choices = [str(i) for i in range(27)]

        self.assertTrue(v.validate_choice("69", ("69", "cat", "dog")))
        self.assertTrue(v.validate_choice("69", choices))

        self.assertTrue(v.validate_choice("a", choices, letters=True))
        self.assertTrue(v.validate_choice("A", choices, letters=True))
        self.assertTrue(v.validate_choice("c", choices, letters=True))
        self.assertTrue(v.validate_choice("C", choices, letters=True))
        self.assertTrue(v.validate_choice("cat", choices, letters=True))
        self.assertTrue(v.validate_choice("CAT", choices, letters=True))

        self.assertTrue(v.validate_choice(
            "a", choices, letters=True, sensitive=True)
        )
        self.assertTrue(v.validate_choice(
            "A", choices, letters=True, sensitive=True)
        )
        self.assertTrue(v.validate_choice(
            "cat", choices, letters=True, sensitive=True)
        )

        self.assertTrue(v.validate_choice("1", choices, numbers=True))
        self.assertTrue(v.validate_choice("3", choices, numbers=True))

        with self.assertRaises(v.ValidatorsException):
            v.validate_choice("z", choices, numbers=True)
        with self.assertRaises(v.ValidatorsException):
            v.validate_choice("9", choices, numbers=True)
        with self.assertRaises(v.ValidatorsException):
            v.validate_choice("0", choices, numbers=True)
        with self.assertRaises(v.ValidatorsException):
            v.validate_choice("42", choices, letters=True, numbers=True)
        with self.assertRaises(v.ValidatorsException):
            v.validate_choice("a", long_choices, letters=True)
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_choice("XXX", choices)
        self.assertEqual("XXX is not a valid choice", str(msg.exception))

    def test_validate_yes_no(self):
        self.assertTrue(v.validate_yes_no(("yes")))
        self.assertTrue(v.validate_yes_no(("y")))
        self.assertTrue(v.validate_yes_no(("no")))
        self.assertTrue(v.validate_yes_no(("n")))
        self.assertTrue(v.validate_yes_no(("YES")))
        self.assertTrue(v.validate_yes_no(("Y")))
        self.assertTrue(v.validate_yes_no(("NO")))
        self.assertTrue(v.validate_yes_no(("N")))
        self.assertTrue(v.validate_yes_no("si", yes_value="si"))
        self.assertTrue(v.validate_yes_no("Si", yes_value="si"))
        self.assertTrue(v.validate_yes_no("n", yes_value="si", no_value="no"))
        self.assertTrue(v.validate_yes_no("yes", sensitive=True))
        self.assertTrue(v.validate_yes_no("y", sensitive=True))
        self.assertTrue(v.validate_yes_no("no", sensitive=True))
        self.assertTrue(v.validate_yes_no("n", sensitive=True))

        with self.assertRaises(v.ValidatorsException):
            v.validate_yes_no("YES", sensitive=True)
        with self.assertRaises(v.ValidatorsException):
            v.validate_yes_no("Y", sensitive=True)
        with self.assertRaises(v.ValidatorsException):
            v.validate_yes_no("NO", sensitive=True)
        with self.assertRaises(v.ValidatorsException):
            v.validate_yes_no("N", sensitive=True)

    def test_validate_bool(self):
        self.assertEqual(v.validate_bool("True"), True)
        self.assertEqual(v.validate_bool("T", true_value="T"), True)
        self.assertEqual(v.validate_bool("t", true_value="t"), True)
        self.assertEqual(v.validate_bool("True"), True)
        self.assertEqual(v.validate_bool("False"), False)
        self.assertEqual(v.validate_bool("F", false_value="F"), False)
        self.assertEqual(v.validate_bool("f", false_value="f"), False)

        with self.assertRaises(v.ValidatorsException):
            v.validate_bool("TRUE", sensitive=True)
        with self.assertRaises(v.ValidatorsException):
            v.validate_bool("FALSE", sensitive=True)

    def test_validate_date(self):
        self.assertTrue(v.validate_date("2014/08/01"))
        self.assertTrue(v.validate_date("2020/09/24"))
        self.assertTrue(v.validate_date("1/1/2020"))
        self.assertEqual(
            v.validate_date("2021/11/10"), datetime.date(2021, 11, 10)
        )
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_date("2018-1-1")
        self.assertEqual("2018-1-1 is not a valid date", str(msg.exception))

    def test_validate_time(self):
        self.assertEqual(v.validate_time("12:00"), datetime.time(12, 0))
        self.assertEqual(v.validate_time("12:00:00"), datetime.time(12, 0))
        self.assertEqual(v.validate_time("4:00"), datetime.time(4, 0))
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_time("8:61:00")
        self.assertEqual("8:61:00 is not a valid time", str(msg.exception))

    def test_validate_datetime(self):
        self.assertEqual(
            v.validate_datetime("2014/08/01 12:00"),
            datetime.datetime(2014, 8, 1, 12, 0),
        )
        self.assertEqual(
            v.validate_datetime("2014/08/01 12:00:00"),
            datetime.datetime(2014, 8, 1, 12, 0),
        )
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_datetime("2014/08/01 12:61:00")
        self.assertEqual(
            "2014/08/01 12:61:00 is not a valid date and time",
            str(msg.exception),
        )

    def test_validate_email(self):
        self.assertEqual(
            v.validate_email("john@doe.com"),
            "john@doe.com",
        )
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_email("john@doe")
        self.assertEqual(
            "john@doe is not a valid email address",
            str(msg.exception),
        )

    def test_validate_url(self):
        self.assertEqual(
            v.validate_url("ayudaenpython.com"),
            "ayudaenpython.com",
        )
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_url("ayudaenpython")
        self.assertEqual(
            "ayudaenpython is not a valid URL.",
            str(msg.exception),
        )

    def test_language(self):
        g = v._GenericValidate(blank=False, strip=None, lang="es")
        g.value = ""
        with self.assertRaises(v.ValidatorsException) as msg:
            g._prevalidation()
        self.assertEqual(
            "No se permiten valores en blanco", str(msg.exception)
        )
        with self.assertRaises(v.ValidatorsException) as msg:
            v.validate_number("abc", lang="es")
        self.assertEqual("abc no es un número", str(msg.exception))


if __name__ == "__main__":
    main()