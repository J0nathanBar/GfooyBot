from abc import ABC, abstractmethod
import random


# bot
# botpass
class User:
    def __init__(self, _id, replies, nicknames, group, name, reasons):
        self._group = group
        self._id = _id
        self._replies = replies
        self._nicknames = nicknames
        self._name = name
        self._reasons = reasons

    def get_id(self):
        return self._id

    def get_replies(self):
        return self._replies

    def get_nicknames(self):
        return self._nicknames

    def get_group(self):
        return self._group

    def set_group(self, group):
        self._group = group

    def get_name(self):
        return self._name

    def get_reasons(self):
        return self._reasons

    def __str__(self) -> str:
        return f'name: {self._name} uid: {self._id} group: {self._group} nicknames: {self._nicknames}  replies:{self._replies}'


class DawnFrager(User):

    def __init__(self, _id, replies, nicknames):
        super().__init__(_id=_id, replies=replies, nicknames=nicknames, group='DawnFrager')

    @abstractmethod
    def frager_was_mentioned(self):
        pass

    def bot_was_mentioned(self):
        return random.choice(self._nicknames) + ' ' + random.choice(self._replies)

    @abstractmethod
    def satisfy(self):
        pass


class Kolb(DawnFrager):

    def __init__(self, _id='380709847093739530', replies=['I lube you', 'you are seggsy'],
                 nicknames=['kold', 'Kold', 'Kolb', 'kolb', 'my future husband', 'Kristian Kold', 'kolbbbbbbbbbbbb']):
        super().__init__(_id, replies, nicknames)

    def frager_was_mentioned(self):
        pass

    def satisfy(self):
        pass


class Tom(DawnFrager):
    def __init__(self, _id='175323481674612741', replies=[''],
                 nicknames=['Tom', 'tom', 'tomatom', 'Matamoto', 'Toom', 'Tommmn']):
        super().__init__(_id, replies, nicknames)

    def frager_was_mentioned(self):
        pass

    def satisfy(self):
        pass


class Gfooy(DawnFrager):
    def __init__(self, _id='411532993421770752', replies=['what you fucktard'], nicknames=['kneebrow']):
        super().__init__(_id, replies, nicknames)

    def frager_was_mentioned(self):
        pass

    def satisfy(self):
        pass


class Zbaby(DawnFrager):
    def __init__(self, _id='593939090190368789',
                 replies=['I love you', 'Ramadan Kareem', 'Udrub Udrub', 'Fauda', 'When you gettin deported',
                          'Amazigh rizz', '*Oui Oui Baguette Sounds*'],
                 nicknames=['Zayd', 'Zbaby', 'Zbubu', 'Zbabe', 'Zayb', 'Sharmoot', 'My benzona', 'boi', 'Hmar',
                            'Zayyyyyyyyyyyyyyyd', 'Zdayyyyyyyyyyyyyy']):
        super().__init__(_id, replies, nicknames)

    def frager_was_mentioned(self):
        pass

    def satisfy(self):
        pass


class Maja(DawnFrager):
    def __init__(self, _id='371700469992521728', replies=[':clown:'],
                 nicknames=['maja', 'Maja', 'womanoid', 'femoid', 'femanoid']):
        super().__init__(_id, replies, nicknames)

    def frager_was_mentioned(self):
        pass

    def satisfy(self):
        return ':palm_tree:'


class Anna(DawnFrager):
    def __init__(self, _id='440719158691233794', replies=['**BAN ANNA**'],
                 nicknames=['Annaaaaaa', 'annaaaaaaaaaaa', 'banananaaaaaaaaa', 'womanoid', 'femoid', 'femanoid']):
        super().__init__(_id, replies, nicknames)

    def frager_was_mentioned(self):
        pass

    def satisfy(self):
        pass


class Flmae(DawnFrager):
    def __init__(self, _id='193831319699062784',
                 nicknames=['Flame', 'Flmae', 'Flmaemae', 'Thomas', 'flmaeeeeeeeeeeeeeeeee'],
                 replies=['I blame you', '#blameflame', 'flame is gayme', 'when you getting  ajob?']):
        super().__init__(_id, replies, nicknames)

    def frager_was_mentioned(self):
        pass

    def satisfy(self):
        pass


class Val(DawnFrager):
    def __init__(self, _id='249590325813706752', replies=[''],
                 nicknames=['vallllllllllll', 'Val', 'Oh glorious viking']):
        super().__init__(_id, replies, nicknames)

    def frager_was_mentioned(self):
        pass

    def satisfy(self):
        pass
