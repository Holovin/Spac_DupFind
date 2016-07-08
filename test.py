#!/usr/bin/python

import logging
import datetime

from database import Database
from models.user import User
from models.history import History
from models.session import Session
from parsers.downloader import Downloader
from parsers.spac_date import SpacDate
from parsers.parse import Parse


def main():
    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.INFO)

    sd = SpacDate()
    p = Parse(sd)
    d = Downloader(p)
    db = Database()

    ########################################################
    db.recount_stats()

    logging.info("--- APP END ---")
    return


def test_db_upsert(db):
    history = [History(datetime.datetime(2016, 12, 31, 23, 59, 59), "mozillo1"),
               History(datetime.datetime(2015, 11, 30, 22, 58, 59), "mozillo2")]

    session = [Session(datetime.datetime(2016, 12, 31, 23, 59, 59), "mozillo1", "192.0.0.1", "msk")]
    user = User(1, "test_user", history, session)
    db.upsert_user(user)
    return


def test_date_parser(sd):
    logging.debug(sd.get_python_time("вчера в 20:55"))
    logging.debug(sd.get_python_time("в 20:55"))
    logging.debug(sd.get_python_time("10 дек в 10:00"))
    logging.debug(sd.get_python_time("10 дек 2010"))
    return


def test_get_user_id(d, p):
    LOGIN = 'Nickolay'
    ID_CHECK = 1

    d.get_user_id(LOGIN)
    result = p.extract_json_user_id(LOGIN, d.get_data_json())

    assert(result == ID_CHECK)
    return

if __name__ == "__main__":
    main()
