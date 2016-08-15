from helpers.dict_converter import Dict2Obj
from models.history import History


class Session(History):
    ip = ""
    ip_place = ""

    def __init__(self, date, user_agent, device, ip, ip_place):
        super().__init__(date, user_agent, device)
        self.ip = ip
        self.ip_place = ip_place
        return

    def __eq__(self, other):
        other = Dict2Obj(other)

        return self.date == other.date and self.user_agent == other.user_agent and self.ip == other.ip \
               and self.ip_place == other.ip_place and self.device == other.device

    def __hash__(self):
        return hash(self.date) ^ hash(self.user_agent) ^ hash(self.ip) ^ hash(self.ip_place) ^ hash(self.device)