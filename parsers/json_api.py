import logging


class JsonApi:
    @staticmethod
    def json_extract_user_id(login, json):
        if JsonApi.json_check_success(json, 'search'):
            return next((item for item in json['users'] if item['name'] == login), -1)['nid']

        return False

    @staticmethod
    def json_check_success(json, method='login'):
        if json['code'] == '00000':
            if method == 'login':
                logging.info("Login ok: [name = " + json['attributes']['name'] + "; id = " + str(
                    json['attributes']['nid']) + "]")
            return True

        logging.fatal("Json parse error (code: " + json['code'] + ")")
        return False
