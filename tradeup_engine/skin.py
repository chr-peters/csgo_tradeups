"""This class is used to model a skin object"""


class Skin(object):
    __slots__ = [
        'weapon',
        'name',
        'rarity',
        'collection',
        'quality',
        'stat_trak',
        'url'
    ]

    def __init__(self, weapon, name, rarity, collection, quality, stat_trak, url):
        self.weapon = weapon
        self.name = name
        self.rarity = rarity
        self.collection = collection
        self.quality = quality
        self.stat_trak = stat_trak
        self.url = url

    def __str__(self):
        return '{{weapon: {}, name: {}, rarity: {}, collection: {}, quality: {}, stat_trak: {}, ' \
               'url: {}}}'.format(self.weapon, self.name, self.rarity,
                                  self.collection, self.quality,
                                  self.stat_trak, self.url)

    def __repr__(self):
        return self.__str__()


class SkinOffer:
    __slots__ = [
        'skin',
        'price'
    ]

    def __init__(self, skin, price):
        self.skin = skin
        self.price = price

    def __str__(self):
        return 'Price: {}, Skin: {}'.format(self.price, self.skin)

    def __repr__(self):
        return self.__str__()