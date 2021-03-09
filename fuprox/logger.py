import logging
import sys

# setting the logger
logging.basicConfig(filename="logger.log", level=logging.DEBUG)


class User:
    username = "killer"

    def name(self, username):
        pass

    def getUser(self):
        logging.info("Just Learning logging Code in Python")


print(User.getUser())
