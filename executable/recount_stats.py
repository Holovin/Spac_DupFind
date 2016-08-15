#!/usr/bin/python

import logging

from storage.database import Database


def main():
    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.INFO)

    db = Database()
    if db.recount_stats():
        logging.info("Success.")

    logging.info("--- APP END ---")
    return


if __name__ == "__main__":
    main()
