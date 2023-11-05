from classes.discord.Analyst3 import Analyst3
from classes.discord.Options_Contract import Options_Contract
from datetime import datetime
import pytz

class Analyst3_Test(Analyst3):
    def __init__(self):
        super().__init__()
        self.server_id = "1088950623883513970"
        self.channel_id = "1088950623883513973"
        self.name = "Analyst3_Test"

