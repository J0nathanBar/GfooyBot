from GfooyBot import start_bot
from mongobongo import BongoMongo
from pymongo import MongoClient

import inspect
import DawnFrager
from abc import ABC, abstractmethod




start_bot()
#
# client = MongoClient('mongodb+srv://bot:botpass@gfooybot.mneifac.mongodb.net/')
# db = client['gfooy_dis']
# collection = db['users']
#
# collection.create_index("uid", unique=True)

#


def inject_fragers():
    mongo = BongoMongo()
    classes = inspect.getmembers(DawnFrager, inspect.isclass)
    fragers = []
    for class_name, class_obj in classes:
        if not inspect.isabstract(class_obj) and (class_name != 'ABC' and class_name != 'User'):
            i = class_obj()
            fragers.append(i)
    for frager in fragers:
        mongo.add_user(frager)
