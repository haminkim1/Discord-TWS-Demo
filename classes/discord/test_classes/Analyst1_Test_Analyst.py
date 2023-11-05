from classes.discord.Analyst1 import Analyst1
from classes.discord.Options_Contract import Options_Contract
from datetime import datetime
import pytz

class Analyst1_Test_Analyst(Analyst1):
    def __init__(self):
        super().__init__()
        self.server_id="1088950623883513970"
        self.channel_id="1088950623883513973"
        self.name = "Analyst1_Test"
        
    # Splits each Discord chat messages into words in a list. 
    # First word will always be the title: 'open', 'close' or 'update'. 
    def _split_messages_into_words_list(self, message):
        description = message['content']
        self.words_list = description.split()
            

