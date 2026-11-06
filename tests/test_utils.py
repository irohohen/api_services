import unittest
from api_services.utils import parse_currency_value

class TestParseCurrencyValue(unittest.TestCase):
    def test_european_format_with_thousands(self):
        self.assertEqual(parse_currency_value("36.123,45"), 36123.45)
        self.assertEqual(parse_currency_value("1.234,56"), 1234.56)

    def test_simple_comma_decimal(self):
        self.assertEqual(parse_currency_value("36,50"), 36.50)
        self.assertEqual(parse_currency_value("1004,96"), 1004.96)

    def test_standard_dot_decimal(self):
        self.assertEqual(parse_currency_value("36.50"), 36.50)
        self.assertEqual(parse_currency_value("1234.56"), 1234.56)

    def test_anglo_format(self):
        self.assertEqual(parse_currency_value("1,234.56"), 1234.56)

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            parse_currency_value("")
        with self.assertRaises(ValueError):
            parse_currency_value("abc")

if __name__ == "__main__":
    unittest.main()
