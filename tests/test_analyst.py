# The next 5 line of code is necessary to auto run this test by pressing play. 
# If the codes are not present, Python fails to find the imported modules. 
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from classes.discord.Analyst import Analyst



import unittest

class TestAnalyst(unittest.TestCase):
    def setUp(self):
        self.analyst = Analyst(1,1)
    

    def test_convert_string_to_int_or_float(self):
        self.assertEqual(0, self.analyst._convert_string_to_int_or_float("0"))
        self.assertEqual(0, self.analyst._convert_string_to_int_or_float("0.0"))
        self.assertEqual(0.95, self.analyst._convert_string_to_int_or_float("0.95"))
        self.assertEqual(10, self.analyst._convert_string_to_int_or_float("10"))
        self.assertEqual(10, self.analyst._convert_string_to_int_or_float("10.0"))
        self.assertEqual(10.05, self.analyst._convert_string_to_int_or_float("10.05"))
        self.assertEqual(10.5, self.analyst._convert_string_to_int_or_float("10.5"))
        self.assertEqual(10, self.analyst._convert_string_to_int_or_float("10.0000000000"))
        self.assertEqual(10.5, self.analyst._convert_string_to_int_or_float("10.500000000000"))


    def test_get_right_from_sentence(self):
        self.assertEqual("C", self.analyst._get_right_from_sentence("C"))
        self.assertEqual("P", self.analyst._get_right_from_sentence("P"))
        self.assertEqual("C", self.analyst._get_right_from_sentence("c"))
        self.assertEqual("P", self.analyst._get_right_from_sentence("p"))


    def test_extract_expiry_date(self):
        # Check method returns nothing if invalid date format. 
        self.assertEqual("", self.analyst._extract_expiry_date_YYYYMMDD("0930"))
        self.assertEqual("", self.analyst._extract_expiry_date_YYYYMMDD("09_30"))
        self.assertEqual("", self.analyst._extract_expiry_date_YYYYMMDD("09\\30"))
        self.assertEqual("", self.analyst._extract_expiry_date_YYYYMMDD("f"))

        # Check method does not return the correct date if invalid date format given.
        self.assertNotEqual("20230930", self.analyst._extract_expiry_date_YYYYMMDD("09//30"))

        # Tested on 07/12/2023 all passed. Make sure tested date is AFTER current date. 
        self.assertEqual("20231021", self.analyst._extract_expiry_date_YYYYMMDD("10/21"))
        self.assertEqual("20230930", self.analyst._extract_expiry_date_YYYYMMDD("9/30"))
        self.assertEqual("20230930", self.analyst._extract_expiry_date_YYYYMMDD("09/30"))


        # Tested on 07/12/2023 all passed. Make sure tested date is BEFORE current date. 
        self.assertEqual("20240707", self.analyst._extract_expiry_date_YYYYMMDD("07/07"))
        self.assertEqual("20240707", self.analyst._extract_expiry_date_YYYYMMDD("7/07"))
        self.assertEqual("20240707", self.analyst._extract_expiry_date_YYYYMMDD("7/7"))

        self.assertEqual("20230804", self.analyst._extract_expiry_date_YYYYMMDD("08/04/23"))
        self.assertEqual("20230804", self.analyst._extract_expiry_date_YYYYMMDD("8/4/23"))
        self.assertEqual("20230707", self.analyst._extract_expiry_date_YYYYMMDD("07/07/23"))
        self.assertEqual("20240707", self.analyst._extract_expiry_date_YYYYMMDD("07/07/24"))
        self.assertEqual("20230814", self.analyst._extract_expiry_date_YYYYMMDD("08/14/2023"))
        self.assertEqual("20230804", self.analyst._extract_expiry_date_YYYYMMDD("08/4/2023"))
        self.assertEqual("20230804", self.analyst._extract_expiry_date_YYYYMMDD("8/4/2023"))
        self.assertEqual("20231204", self.analyst._extract_expiry_date_YYYYMMDD("12/4/2023"))



if __name__ == '__main__':
    unittest.main()