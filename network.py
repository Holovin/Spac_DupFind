import logging

import requests

from config import Config
from helpers.message import Msg
from parsers.json_api import JsonApi


class Network:
    # api methods
    URI_API_AUTH = 'http://spaces.ru/api/auth/'
    URI_API_SEARCH = 'http://spaces.ru/neoapi/users/'

    # raw html-parse methods
    URI_RAW_USER_HIST = 'http://spaces.ru/mysite/loghist/?name='
    URI_RAW_USER_SESS = 'http://spaces.ru/mysite/sessions_list/?name='
    URI_RAW_USER_BLOGS = 'http://spaces.ru/diary/'
    URI_RAW_COMM_USERS = 'http://spaces.ru/comm/users/'
    URI_RAW_COMM_FORUM = 'http://spaces.ru/forums/'

    session = None
    last_answer = ""

    def __init__(self):
        self.clean()
        return

    def _get_cookie_value(self, name):
        return self.session.cookies.get(name)

    def get_data(self):
        return self.last_answer.text

    def get_data_json(self):
        return self.last_answer.json()

    def get_session_sid(self):
        return self._get_cookie_value('sid')

    def get_session_ck(self):
        # last 4 digit of sid
        return self.get_session_sid()[-4:]

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
                logging.warning("Redirect to: " + self.last_answer.url)

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

        return JsonApi.json_check_success(self.get_data_json(), 'login')

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

    def get_comm_user_remove(self, comm_id, user_id):
        logging.debug("Removing user [user_id = " + str(user_id) + "; comm_id = " + str(comm_id) + "]")

        if self.do_get(self.URI_RAW_COMM_USERS + '?CK=' + self.get_session_ck() + '&Comm=' + str(
                comm_id) + '&Delete=' + str(user_id)) is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def get_comm_forum_page(self, forum_id, page):
        logging.debug("Get forum page [forum_id = " + str(forum_id) + "]")

        if self.do_get(self.URI_RAW_COMM_FORUM + '?f=' + str(forum_id) + '&tp=' + str(page)) is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def get_comm_forum_theme_remove(self, theme_id):
        logging.debug("Remove theme [theme_id = " + str(theme_id) + "]")

        if self.do_get(self.URI_RAW_COMM_FORUM + '?CK=' + self.get_session_ck() + '&dt=' + str(
                theme_id) + '&sure=1') is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def get_comm_forum_theme_move(self, theme_id, forum_id):
        logging.debug("Move theme [theme_id = " + str(theme_id) + "; forum_id = " + str(forum_id) + "]")

        if self.do_get(self.URI_RAW_COMM_FORUM + '?CK=' + self.get_session_ck() + '&f=' + str(
                forum_id) + '&move=' + str(theme_id)) is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def get_comm_forum_theme_close(self, theme_id):
        logging.debug("Close theme [theme_id = " + str(theme_id) + "]")

        if self.do_get(self.URI_RAW_COMM_FORUM + '?CK=' + self.get_session_ck() + '&ct=' + str(
                theme_id)) is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def get_comm_forum_theme_open(self, theme_id):
        logging.debug("Open theme [theme_id = " + str(theme_id) + "]")

        if self.do_get(self.URI_RAW_COMM_FORUM + '?CK=' + self.get_session_ck() + '&ot=' + str(
                theme_id)) is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def get_user_blogs_page(self, login, page):
        logging.debug("User blogs page [login = " + str(login) + "; page = " + "]")

        if self.do_get(self.URI_RAW_USER_BLOGS + 'view/?name=' + login + '&P=' + str(page)) is not Msg.success_ok:
            return Msg.fatal_http

        return True

    def post_user_blogs_access_change(self, blog_id, access_value, password=""):
        logging.debug("User blog access change...")

        data = {
            'M_' + blog_id + '_9': access_value,
            'cfms': 'Сохранить',
            'pass_' + blog_id + '_9': password,
            'CK': self.get_session_ck()
        }

        if self.do_post(self.URI_RAW_USER_BLOGS + 'editaccess/?id=' + blog_id, data=data) is not Msg.success_ok:
            return Msg.fatal_http

        return True