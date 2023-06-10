from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import random
from BotConf import MONGO_LINK
from datetime import datetime, timedelta


class BongoMongo:
    def __init__(self) -> None:
        super().__init__()
        self.client = MongoClient(MONGO_LINK)
        self.db = self.client['gfooy_dis']

    def get_wisdom(self):
        collection = self.db['words of wisdom']
        document = collection.aggregate([{'$sample': {'size': 1}}])
        if document:
            return document.next()['wisdom']
        else:
            return 'error please contact dev'

    def add_wisdom(self, wisdom):
        collection = self.db['words of wisdom']
        document = {'wisdom': wisdom}
        res = collection.insert_one(document)
        return res.acknowledged

    def add_user(self, user):
        collection = self.db['users']
        try:
            admin = user.__class__.__name__ == 'Gfooy'
            doc = {
                'name': user.get_name(),
                'uid': user.get_id(),
                'nicknames': user.get_nicknames(),
                'replies': user.get_replies(),
                'group': user.get_group(),
                'admin': admin,
                'reasons': user.get_reasons()
            }
            res = collection.insert_one(doc)
            if res.acknowledged:
                return 'user created successfully'
            else:
                return 'there was an error creating your user'

        except DuplicateKeyError:
            return "Duplicate key error: user already in the system."

    def get_user(self, uid):
        collection = self.db['users']
        doc = collection.find_one({'uid': str(uid)})
        if doc:
            return doc
        return None

    def get_users(self):
        collection = self.db['users']
        return collection.find()

    def add_nickname(self, uid, nickname):
        user = self.get_user(uid)
        if user:

            update = {'$push': {'nicknames': nickname}}
            _filter = {'uid': uid}
            collection = self.db['users']
            res = collection.update_one(_filter, update)
            return res.matched_count > 0
        else:
            return False

    def add_reply(self, uid, reply):
        user = self.get_user(uid)
        if user:
            update = {'$push': {'replies': reply}}
            _filter = {'uid': uid}
            collection = self.db['users']
            res = collection.update_one(_filter, update)
            return res.matched_count > 0
        else:
            return False

    def is_admin(self, uid):
        user = self.get_user(uid)
        if user:
            return user['admin']
        return False

    def mentioned(self, uid):
        user = self.get_user(str(uid))
        if user:

            return f'{self.get_nickname(user)} {self.get_reply(user)}'

        else:
            return 'I have been summoned'

    @staticmethod
    def get_nickname(user):
        if user:
            nicknames = user['nicknames']
            return random.choice(nicknames)
        return ''

    @staticmethod
    def get_reply(user):
        if user:
            replies = user['replies']
            return random.choice(replies)
        return ''

    @staticmethod
    def get_reason(user):
        if user:
            reasons = user['reasons']
            return random.choice(reasons)
        return ''

    def add_reason(self, uid, reason):
        user = self.get_user(uid)
        if user:
            update = {'$push': {'reasons': reason}}
            _filter = {'uid': uid}
            collection = self.db['users']
            res = collection.update_one(_filter, update)
            return res.matched_count > 0
        else:
            return False

    def get_triggers(self):
        collection = self.db['triggers']
        return collection.distinct('trigger')

    def get_trigger_reply(self, trigger):
        collection = self.db['triggers']
        return collection.find_one({'trigger': trigger})['reply']

    def add_trigger(self, trigger: str, reply: str):
        collection = self.db['triggers']
        document = {'trigger': trigger.upper(),
                    'reply': reply}
        res = collection.insert_one(document)
        return res.acknowledged

    def add_message(self, uid, message_text, channel_id, send_time):
        user = self.get_user(uid)
        collection = self.db['users']
        if user:
            message = {
                'text': message_text,
                'channel_id': channel_id,
                'send_time': send_time,
                'sent': False
            }
            res = collection.update_one(
                {'uid': uid},
                {'$push': {'messages': message}}
            )

            return res.matched_count > 0
        else:
            return False
