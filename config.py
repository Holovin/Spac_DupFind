class Config:
    #####################################
    # comm_users_parse.py settings      #
    COMM_ID = 000                       # comm_id for parse
    START_PAGE = 1                      #
    END_PAGE = 100                      #

    #####################################
    # search.py settings                #
    SEARCH_LOGIN = "user"               # nickname for search
    SEARCH_LEVEL = 10                   #

    STAT_IP_WEIGHT = 1000               # rating value if ip1 == ip2

    SEARCH_DEC = False                  # decrease rating if ua1 != ua2
    SEARCH_DEC_DIV = 100                # if yes -> value for divide original rating

    #####################################
    # recount.py settings               #
    STAT_LOG_BASE = 3                   # log base for rating scale

    #####################################
    # insert_single_user.py settings    #
    INSERT_USERS = ['u1', 'u2']         # list or nicknames of users for manually inserting

    #####################################
    # common settings #
    DB_HOST = "127.0.0.1"
    DB_PORT = 27017
    DB_NAME = "spaces_users"
    TABLE_NAME = "users"
    TABLE_STAT_NAME = "stats"

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:2.0b7) Gecko/20100101 Firefox/4.0b7',
    }

    #####################################
    # secret settings                   #
    USER_NAME = "user"
    USER_PASSWORD = "password"