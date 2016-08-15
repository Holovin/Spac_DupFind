import logging
import re
from enum import Enum, unique

from lxml import html

from helpers.object import Object
from models.history import History
from models.session import Session


class Parse:
    @unique
    class ForumThemesMode(Enum):
        ALL = 0
        ONLY_OPEN = 1
        ONLY_CLOSED = 2

    @unique
    class BlogAccessMode(Enum):
        ALL = {'int': 0, 'string': 'Доступно всем'}
        ONLY_ME = {'int': 1, 'string': 'Доступно только мне'}
        MY_FRIENDS = {'int': 2, 'string': 'Доступно только друзьям'}
        MY_FRIENDS_DOUBLE = {'int': 3, 'string': 'Доступно друзьям и их друзьям'}
        PASSWORD = {'int': 4, 'string': 'Доступно по паролю'}
        USER_LIST = {'int': 5, 'string': 'Доступно по списку доступа'}

    # regex precompile
    re_ip_place = re.compile('((.+)\s\(((\d{1,3}\.*){1,4}))')
    re_ip = re.compile('((\d{1,3}\.*){1,4})')
    re_delete_id = re.compile('Delete=(\d+)')

    re_theme_move_id = re.compile('move=(\d+)')  # move
    re_theme_ct_id = re.compile('ct=(\d+)')  # close
    re_theme_ot_id = re.compile('ot=(\d+)')  # open

    re_blog_id = re.compile('id=(\d+)')

    spac_date = None

    def __init__(self, spac_data):
        self.spac_date = spac_data
        return

    def xpath_user_history(self, content):
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

    def xpath_user_sessions(self, content):
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
            ip_raw = self.text_ip_split(sess_raw_list[i + 1])
            ip = ip_raw.ip
            ip_place = ip_raw.ip_place.strip()
            logging.debug("IP: " + ip + "; Place: " + ip_place)

            ua = sess_raw_list[i + 2].strip()
            logging.debug("UA" + ua)

            sess_list.append(Session(date, ua, "", ip, ip_place))

        return sess_list

    def text_ip_split(self, text):
        result = Object()

        if text.strip() == "":
            result.ip = " "
            result.ip_place = " "
            return result

        result_raw = self.re_ip_place.search(text)

        if result_raw is not None:
            # place + ip parse
            result.ip_place = result_raw.group(2)
            result.ip = result_raw.group(3)
        else:
            # unknown place
            result.ip = self.re_ip.search(text).group(1)
            result.ip_place = " "

        return result

    @staticmethod
    def xpath_comm_users_page(content, current_login=None):
        tree = html.fromstring(content)
        logging.debug("DOM created...")

        users_list = tree.xpath(
            '//div[@class="widgets-group"]/div/a[contains(@href, "mysite")]//span[@class="block-item__title m break-word"]/text()[normalize-space()]')

        if current_login:
            users_list.remove(current_login)

        return [user.strip() for user in users_list]

    @staticmethod
    def xpath_comm_users_page_delete(content):
        tree = html.fromstring(content)
        logging.debug("DOM created...")

        users_list = tree.xpath('//div[@class="widgets-group"]//a[contains(@href, "Delete")]/@href')

        return [user.strip() for user in users_list]

    def text_url_param_delete(self, text):
        result_raw = self.re_delete_id.search(text)

        if result_raw is not None:
            return result_raw.group(1)

        logging.warning("Bad parse: " + text)
        return ""

    @staticmethod
    def text_url_param_theme_id(text, regex):
        result_raw = regex.search(text)

        if result_raw is not None:
            return result_raw.group(1)

        logging.warning("Bad parse: " + text)
        return ""

    def xpath_comm_forum_themes_id(self, content, mode):
        tree = html.fromstring(content)
        logging.debug("DOM created...")

        modes = ['Переместить', 'Закрыть', 'Открыть']
        m_f = [self.re_theme_move_id, self.re_theme_ct_id, self.re_theme_ot_id]

        themes_raw = tree.xpath('//div[@id="main"]//a[contains(text(), "' + modes[mode.value] + '")]/@href')
        themes = []

        for theme in themes_raw:
            theme_raw = self.text_url_param_theme_id(theme, m_f[mode.value])
            themes.append(theme_raw)

        return themes

    def text_url_param_blog_id(self, text):
        result_raw = self.re_blog_id.search(text)

        if result_raw is not None:
            return result_raw.group(1)

        logging.warning("Bad parse: " + text)
        return ""

    def xpath_user_blog_page(self, content, access_level=BlogAccessMode.ALL, invert_access_level=False):
        tree = html.fromstring(content)
        logging.debug("DOM created...")

        flag = ""
        if invert_access_level:
            flag = "not"

        blog_list = tree.xpath(
            '//div[@id="main"]//div[contains(@class, "widgets-group") and .//span[contains(@class, "ico_mode") and (' +
            flag + '(contains(@title, "' + access_level.value['string'] +
            '")))]]//td//a[contains(@href, "/read/")]/@href')

        blogs_id = []
        for blog in blog_list:
            blogs_id.append(self.text_url_param_blog_id(blog))

        return blogs_id
