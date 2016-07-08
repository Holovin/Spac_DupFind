#!/usr/bin/python

import logging

from database import Database
from models.user import User
from parsers.downloader import Downloader
from parsers.spac_date import SpacDate
from parsers.parse import Parse
from config import Config


def main():
    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.INFO)

    sd = SpacDate()
    p = Parse(sd)
    d = Downloader(p)
    db = Database()

    if not d.auth(Config.USER_NAME, Config.USER_PASSWORD):
        logging.fatal("Auth error...")
        exit()

    logging.info("Init ok... Start parsing... [id = " + str(Config.COMM_ID) + "]")

    users = Config.INSERT_USERS

    for user in users:
        if not d.get_user_id(user):
            logging.error("Get user id error (user = " + user + "). Skipping...")
            return

        u_id = p.extract_json_user_id(user, d.get_data_json())

        if not d.get_user_hist(user):
            logging.error("Get user hist error (user = " + user + "). Skipping...")
            return

        u_hist = p.parse_hist(d.get_data())

        if not d.get_user_sess(user):
            logging.error("Get user sess error (user = " + user + "). Skipping...")
            return

        u_sess = p.parse_sess(d.get_data())

        db_user = User(u_id, user, u_hist, u_sess)
        db.upsert_user(db_user)
        logging.info("User: " + user + ", id: " + str(u_id) + "...")
    return


if __name__ == "__main__":
    main()
