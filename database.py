import logging
import re
from math import floor

import math
from pymongo import MongoClient
from object import Object
from config import Config
from dict_converter import Dict2Obj


class Database:
    HISTORY_KEY = 'hist'
    SESSION_KEY = 'sess'
    USERAGENT_KEY = 'user_agent'
    IP_KEY = 'ip'
    IPPLACE_KEY = 'ip_place'

    client = None
    db = None
    isOperable = False

    position_selector = {
        'key': 'position'
    }

    def __init__(self):
        try:
            keys = {'serverSelectionTimeoutMS': 4000}
            self.client = MongoClient(Config.DB_HOST, Config.DB_PORT)
            self.client.database_names()
            self.db = self.client[Config.DB_NAME]
            logging.info("Connected to mongo... ok")

            self.isOperable = True
        except Exception as e:
            logging.fatal("Connection to mongo failed (" + str(e) + ")")
            self.isOperable = False
        return

    def upsert_user(self, user):
        if not self.isOperable:
            logging.error("Db is not operable!")
            return False

        u = Object()
        u.name = user.name
        u.id = user.id
        u.hist = []
        u.sess = []

        # Find this user [by ID] and get hist + sess to compare
        old_user = self.db[Config.TABLE_NAME].find_one({'id': user.id})

        if old_user:
            old_user = Dict2Obj(old_user)

            # Exist user
            hist_new = user.merge_var(self.HISTORY_KEY, old_user)
            sess_new = user.merge_var(self.SESSION_KEY, old_user)

            u_find = Object()
            u_find.id = user.id

            result = self.db[Config.TABLE_NAME].update_one(filter=u_find.__dict__, update={
                '$set': {
                    'name': u.name,
                },
                '$push': {
                    self.HISTORY_KEY: {
                        '$each': hist_new
                    },
                    self.SESSION_KEY: {
                        '$each': sess_new
                    }
                }

            })

            logging.info("Old user updated (modified count: " + str(result.modified_count) + ")")
            return

        # New user
        u.hist = user.get_var_dict(self.HISTORY_KEY)
        u.sess = user.get_var_dict(self.SESSION_KEY)

        insert_id = self.db[Config.TABLE_NAME].insert_one(u.__dict__).inserted_id
        logging.info("New user inserted with key: " + str(insert_id))

        return

    def find_face(self, login, level=0):
        if not self.isOperable:
            logging.error("Db is not operable!")
            return False

        user = self.db[Config.TABLE_NAME].find_one({
            'name': re.compile(login, re.IGNORECASE)
        })

        if user is None:
            logging.fatal("User not found!")
            return False

        unique_ua = set()
        unique_ip = set()
        unique_ip_place = set()

        for h in user[self.HISTORY_KEY]:
            unique_ua.add(h[self.USERAGENT_KEY])

        for s in user[self.SESSION_KEY]:
            unique_ua.add(s[self.USERAGENT_KEY])
            unique_ip.add(s[self.IP_KEY])
            unique_ip_place.add(s[self.IPPLACE_KEY])

        d = {}

        for ua in unique_ua:
            # rating #
            print(ua)

            rating_match = self.db[Config.TABLE_STAT_NAME].find_one({
                self.USERAGENT_KEY: ua
            })

            print(rating_match)

            if rating_match is None:
                logging.fatal("Need recount rating... Stopping.")
                exit()

            rating = rating_match['rating']

            # sess #
            sess_match_users = self.db[Config.TABLE_NAME].find({
                'name': {
                    '$regex': re.compile('^(?!.*' + login + ').*$', re.IGNORECASE)
                },

                self.SESSION_KEY: {
                    '$elemMatch': {
                        self.USERAGENT_KEY: ua
                    }
                }
            })

            for u in sess_match_users:
                if u['name'] not in d:
                    d[u['name']] = 0

                unique_user_sess_ua = set()
                for sess in u[self.SESSION_KEY]:
                    unique_user_sess_ua.add(sess[self.USERAGENT_KEY])

                for uusu_item in unique_user_sess_ua:
                    if ua == uusu_item:
                        d[u['name']] += rating
                    elif Config.SEARCH_DEC:
                        d[u['name']] -= floor(rating / Config.SEARCH_DEC_DIV)

            # hist #
            hist_match_users = self.db[Config.TABLE_NAME].find({
                'name': {
                    '$regex': re.compile('^(?!.*' + login + ').*$', re.IGNORECASE)
                },

                self.HISTORY_KEY: {
                    '$elemMatch': {
                        self.USERAGENT_KEY: ua
                    }
                }
            })

            for u in hist_match_users:
                if u['name'] not in d:
                    d[u['name']] = 0

                unique_user_hist_ua = set()
                for hist in u[self.HISTORY_KEY]:
                    unique_user_hist_ua.add(hist[self.USERAGENT_KEY])

                for uuhu_item in unique_user_hist_ua:
                    if ua == uuhu_item:
                        d[u['name']] += rating
                    elif Config.SEARCH_DEC:
                        d[u['name']] -= floor(rating / Config.SEARCH_DEC_DIV)

        for ip in unique_ip:
            ip_match_users = self.db[Config.TABLE_NAME].find({
                'name': {
                    '$regex': re.compile('^(?!.*' + login + ').*$', re.IGNORECASE)
                },

                self.SESSION_KEY: {
                    '$elemMatch': {
                        self.IP_KEY: ip
                    }
                }
            })

            for u_ip in ip_match_users:
                if u_ip['name'] not in d:
                    d[u_ip['name']] = 0

                for sess in u_ip[self.SESSION_KEY]:
                    if ip == sess[self.IP_KEY]:
                        d[u_ip['name']] += Config.STAT_IP_WEIGHT

        for ip_place in unique_ip_place:
            ip_place_match_users = self.db[Config.TABLE_NAME].find({
                'name': {
                    '$regex': re.compile('^(?!.*' + login + ').*$', re.IGNORECASE)
                },

                self.SESSION_KEY: {
                    '$elemMatch': {
                        self.IPPLACE_KEY: ip_place
                    }
                }
            })

            for u_ip_place in ip_place_match_users:
                if u_ip_place['name'] not in d:
                    d[u_ip_place['name']] = 0

                for sess in u_ip_place[self.SESSION_KEY]:
                    if ip_place == sess[self.IPPLACE_KEY]:
                        d[u_ip_place['name']] += 0  # ip very valuable!

        return d

    def recount_stats(self):
        rem_result = self.db[Config.TABLE_STAT_NAME].remove({})
        logging.info("Clear old data... [" + str(rem_result) + "]")

        result = self.db[Config.TABLE_NAME].aggregate([{
            '$project': {
                'ua': {
                    '$setUnion': ['$hist.user_agent', '$sess.user_agent']
                },
                '_id': 0
            }
        }, {
            '$unwind': '$ua'
        }, {
            '$group': {
                '_id': '$ua',
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                'count': -1
            }
        }])

        docs = []
        doc_max = -1

        # hack for take 1st record because command_cursor cant move back
        for item in result:
            doc_max = item['count']

            docs.append({
                self.USERAGENT_KEY: str(item['_id']),
                'count': item['count'],
                'rating': 0
            })

            # don't touch #
            break

        for item in result:
            docs.append({
                self.USERAGENT_KEY: str(item['_id']),
                'count': item['count'],
                'rating': int(floor(math.log(doc_max - item['count'], Config.STAT_LOG_BASE)))
            })

        result = self.db[Config.TABLE_STAT_NAME].insert(docs)
        logging.info("Inserted: " + str(len(result)))

        return True
