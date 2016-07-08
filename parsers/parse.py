import logging
import re

from lxml import html
from models.history import History
from models.session import Session
from object import Object


class Parse:
    ip_place = re.compile('((.+)\s\(((\d{1,3}\.*){1,4}))')
    ip = re.compile('((\d{1,3}\.*){1,4})')
    spac_date = None

    def __init__(self, spac_data):
        self.spac_date = spac_data
        return

    @staticmethod
    def check_auth(json):
        if json['code'] == '00000':
            logging.info("Login ok: [name = " + json['attributes']['name'] + "; id = " + str(json['attributes']['nid']) + "]")
            return True

        logging.fatal("Auth error (code: " + json['code'] + ")")
        return False

    def parse_hist(self, content):
        tree = html.fromstring(content)
        logging.debug("DOM created...")

        tmp = ' '.join(str(x) for x in tree.xpath('//div[contains(@class, "light_blue")]/text()'))
        if "Здесь вы сможете проверить, не заходил ли кто-то чужой под вашим ником!" in tmp:
            logging.error("History protection (admin?)")
            return []

        hist_raw_list = tree.xpath('//div[contains(@class,"list_item")]/span/following-sibling::text()[1]')
        hist_list = []
        logging.debug("List items: " + str(len(hist_raw_list)))

        l = len(hist_raw_list)

        for i in range(0, l, 2):
            device = ""

            logging.debug(str(i) + " // Date raw: " + hist_raw_list[i])
            date = self.spac_date.get_python_time(hist_raw_list[i])
            logging.debug("RawTime: " + str(date))

            logging.debug(str(i + 1) + " // UA raw: " + hist_raw_list[i + 1])
            ua = hist_raw_list[i + 1].strip()
            logging.debug("UA: " + ua)

            if l == i + 3 and l % 2 == 1:
                device = hist_raw_list[i + 2]
                logging.debug("Device: " + device)
                hist_list.append(History(date, ua, device))
                return hist_list

            hist_list.append(History(date, ua, device))

        return hist_list

    def parse_sess(self, content):
        tree = html.fromstring(content)
        logging.debug("DOM created...")

        if 'Текущий сеанс' in tree.xpath('//div[contains(@class,"list_item")]/div/b/text()'):
            logging.error("Session protection (admin?)")
            return []

        sess_raw_list = tree.xpath('//div[contains(@class,"list_item")]/div/span/following-sibling::text()[1]')
        sess_list = []
        logging.debug("List items: " + str(len(sess_raw_list)))

        for i in range(0, len(sess_raw_list), 3):
            date = self.spac_date.get_python_time(sess_raw_list[i])
            logging.debug("RawTime: " + str(date))

            logging.debug("RawIP: " + sess_raw_list[i + 1])
            ip_raw = self.ip_split(sess_raw_list[i + 1])
            ip = ip_raw.ip
            ip_place = ip_raw.ip_place.strip()
            logging.debug("IP: " + ip + "; Place: " + ip_place)

            ua = sess_raw_list[i + 2].strip()
            logging.debug("UA" + ua)

            sess_list.append(Session(date, ua, "", ip, ip_place))

        return sess_list

    def ip_split(self, text):
        result = Object()

        if text.strip() == "":
            result.ip = " "
            result.ip_place = " "
            return result

        result_raw = self.ip_place.search(text)

        if result_raw is not None:
            # place + ip parse
            result.ip_place = result_raw.group(2)
            result.ip = result_raw.group(3)
        else:
            # unknown place
            result.ip = self.ip.search(text).group(1)
            result.ip_place = " "

        return result

    @staticmethod
    def extract_json_user_id(login, json):
        return next((item for item in json['users'] if item['name'] == login), -1)['nid']

    @staticmethod
    def parse_comm_users(content, current_login=None):
        tree = html.fromstring(content)
        logging.debug("DOM created...")

        users_list = tree.xpath('//div[@class="widgets-group"]/div/a[contains(@href, "mysite")]//span[@class="block-item__title m break-word"]/text()[normalize-space()]')

        if current_login:
            users_list.remove(current_login)

        return [user.strip() for user in users_list]
