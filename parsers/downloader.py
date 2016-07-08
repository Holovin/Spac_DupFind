import logging
import requests

from config import Config
from message import Msg


class Downloader:
    URI_API_AUTH = "http://spaces.ru/api/auth/"
    URI_API_SEARCH = "http://spaces.ru/neoapi/users/"

    URI_RAW_USER_HIST = "http://spaces.ru/mysite/loghist/?name="
    URI_RAW_USER_SESS = "http://spaces.ru/mysite/sessions_list/?name="
    URI_RAW_COMM_USERS = "http://spaces.ru/comm/users/"

    parser = None
    session = None
    last_answer = ""

    def __init__(self, parser):
        self.parser = parser
        self.clean()
        return

    def get_data(self):
        return self.last_answer.text

    def get_data_json(self):
        return self.last_answer.json()

    def clean(self):
        self.last_answer = None
        self.session = requests.Session()
        logging.info("Downloader init... ok")

        return

    def do_get(self, url):
        logging.debug("Get url: " + url)

        try:
            self.last_answer = self.session.get(url, headers=Config.HEADERS)
            logging.debug("Result url (" + str(self.last_answer.status_code) + " : " + self.last_answer.url + ")")

            if self.last_answer.url.lower() != url.lower():
                logging.warning("Redirect!")

                if 'http://spaces.ru/registration/' in self.last_answer.url.lower():
                    logging.fatal("No auth...")
                    exit()

        except requests.exceptions.RequestException as e:
            logging.fatal("Fatal error [get url]: " + str(e))
            exit()

        logging.debug("Getting url... ok")
        return Msg.success_ok

    def do_post(self, url, data):
        logging.debug("Post url: " + url)

        try:
            self.last_answer = self.session.post(url, headers=Config.HEADERS, data=data)
            logging.debug("Result url (" + str(self.last_answer.status_code) + " : " + self.last_answer.url + ")")

        except requests.exceptions.RequestException as e:
            logging.fatal("Fatal error [post url]: " + str(e))
            exit()

        logging.debug("Posting url... ok")
        return Msg.success_ok

    def auth(self, user_name, user_password):
        data = {
            'method': 'login',
            'login': user_name,
            'password': user_password
        }

        logging.debug("Auth starting...")
        if self.do_post(self.URI_API_AUTH, data=data) is not Msg.success_ok:
            return Msg.fatal_http

        return self.parser.check_auth(self.get_data_json())

    def get_user_hist(self, login):
        logging.debug("Get user history... [login = " + login + "]")

        if self.do_get(self.URI_RAW_USER_HIST + login) is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def get_user_sess(self, login):
        logging.debug("Get user sessions... [login = " + login + "]")

        if self.do_get(self.URI_RAW_USER_SESS + login) is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def get_user_id(self, login):
        logging.debug("Get user id... [login = " + login + "]")

        data = {
            'method': 'search',
            'q': login
        }

        if self.do_post(self.URI_API_SEARCH, data=data) is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def get_comm_users_page(self, comm_id, page):
        logging.debug("Get comm page [comm_id = " + str(comm_id) + "; page = " + str(page) + "]")

        if self.do_get(self.URI_RAW_COMM_USERS + '?Comm=' + str(comm_id) + '&P=' + str(page)) is not Msg.success_ok:
            return Msg.fatal_http

        return True
