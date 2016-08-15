from enum import Enum


class Msg(Enum):
    success_ok = 1
    err_http = 2
    fatal_http = 3
    err_parse = 4
    fatal_parse = 5

