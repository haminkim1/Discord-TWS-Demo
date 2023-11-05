# The next 5 line of code is necessary to auto run this test by pressing play. 
# If the codes are not present, Python fails to find the imported modules. 
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from classes.discord.Unit_test_analyst import Unit_test_analyst
from auth.discord.auth_header import headers


import unittest

class TestAnalyst(unittest.TestCase):
    def setUp(self):
        self.ta = Unit_test_analyst()

    def test_server_id(self):
        self.assertEqual('1088950623883513970', self.ta.server_id)

    def test_channel_id(self):
        self.assertEqual("1125693280429027359", self.ta.channel_id)

    def test_get_discord_messages_from_channel(self):
        self.ta.num_difference = 5
        self.ta.get_discord_messages_from_channel(headers)
        message_data = ["1", "2", "3", "4", "5"]
        for i in range(5):
            self.assertEqual(message_data[i], self.ta.message_data[i]["content"])

    # Checks whether replied message also counts as part of a message
    def test_get_discord_messages_from_channel_replied(self):
        self.ta.num_difference = 5
        self.ta.channel_id = "1125709259171168257"
        self.ta.get_discord_messages_from_channel(headers)
        message_data = ["1", "2", "3", "4", "5"]
        for i in range(5):
            self.assertEqual(message_data[i], self.ta.message_data[i]["content"])

if __name__ == '__main__':
    unittest.main()