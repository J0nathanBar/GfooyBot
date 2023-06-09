from GfooyBot import start_bot
from mongobongo import BongoMongo

import inspect
import DawnFrager
from datetime import datetime

start_bot()


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
