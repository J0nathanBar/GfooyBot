from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import random


class BongoMongo:
    def __init__(self) -> None:
        super().__init__()
        self.client = MongoClient('mongodb+srv://bot:botpass@gfooybot.mneifac.mongodb.net/')
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
                'admin': admin
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

    def get_nickname(self, user):
        if user:
            nicknames = user['nicknames']
            return random.choice(nicknames)
        return ''

    def get_reply(self, user):
        if user:
            replies = user['replies']
            return random.choice(replies)
        return ''

    def get_reason(self, user):
        if user:
            reasons = user['reasons']
            return random.choice(reasons)
        return ''
