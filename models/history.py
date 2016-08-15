import datetime

from helpers.dict_converter import Dict2Obj


class History:
    date = datetime.datetime(1, 1, 1)
    user_agent = ""
    device = ""

    def __init__(self, date, user_agent, device):
        self.date = date
        self.user_agent = user_agent
        self.device = device
        return

    def __eq__(self, other):
        other = Dict2Obj(other)

        return self.date == other.date and self.user_agent == other.user_agent and self.device == other.device

    def __hash__(self):
        return hash(self.date) ^ hash(self.user_agent) ^ hash(self.device)
