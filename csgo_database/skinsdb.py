import pymysql


class SkinDB:

    def __init__(self):
        self.connection = pymysql.connect(host='localhost', user='root', passwd='root', db='csgo')
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def insert_skin(self, weapon, name, rarity, collection, quality, stat_trak, url):
        self.cursor.execute('insert into skins(weapon, name, rarity, collection, quality, stat_trak, url) '
                            'values(%s, %s, %s, %s, %s, %s, %s)',
                            (weapon, name, rarity, collection, quality, stat_trak, url))
        self.connection.commit()

    def insert_float(self, weapon, name, min_float, max_float):
        self.cursor.execute('insert into floats(weapon, name, min_float, max_float) values(%s, %s, %s, %s)',
                            (weapon, name, min_float, max_float))
        self.connection.commit()

    def get_float(self, weapon, name):
        self.cursor.execute('select * from floats where weapon=%s and name=%s', (weapon, name))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        else:
            return {
                'weapon': res[0][1],
                'name': res[0][2],
                'min_float': res[0][3],
                'max_float': res[0][4]
            }

    def insert_offer(self, weapon, name, quality, stat_trak, offer_type, price):
        self.cursor.execute('insert into offers(weapon, name, quality, stat_trak, offer_type, price) '
                            'values(%s, %s, %s, %s, %s, %s)', (weapon, name, quality, stat_trak, offer_type, price))
        self.connection.commit()

    def delete_offers(self, weapon, name, quality, stat_trak):
        self.cursor.execute('delete from offers where weapon=%s and name=%s and quality=%s and stat_trak=%s',
                            (weapon, name, quality, stat_trak))

    def get_skin(self, weapon, name, quality, stat_trak):
        self.cursor.execute('select * from skins where weapon=%s and name=%s and quality=%s and stat_trak=%s',
                            (weapon, name, quality, stat_trak))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        else:
            return {
                'weapon': res[0][1],
                'name': res[0][2],
                'rarity': res[0][3],
                'collection': res[0][4],
                'quality': res[0][5],
                'stat_trak': bool(res[0][6]),
                'url': res[0][7]
            }

    def get_all_collections(self):
        """Returns a list of all collections in the game ordered ascending by timestamp of last price check."""
        query = 'select collection, max(offers.timestamp) as max_timestamp ' \
                'from skins left join offers on skins.weapon = offers.weapon and skins.name = offers.name ' \
                'group by skins.collection ' \
                'order by max_timestamp asc'
        self.cursor.execute(query)
        res = self.cursor.fetchall()
        collections = []
        for cur_collection in res:
            collections.append(cur_collection[0])
        return collections

    def get_skins_in_collection(self, collection):
        self.cursor.execute('select * from skins where collection=%s', [collection])
        res = self.cursor.fetchall()
        skins = []
        for cur_skin in res:
            skins.append({
                'weapon': cur_skin[1],
                'name': cur_skin[2],
                'rarity': cur_skin[3],
                'collection': cur_skin[4],
                'quality': cur_skin[5],
                'stat_trak': bool(cur_skin[6]),
                'url': cur_skin[7]
            })
        return skins

    def delete_skin(self, weapon, name, quality, stat_trak):
        self.cursor.execute('delete from skins where weapon=%s and name=%s and quality=%s and stat_trak=%s',
                            (weapon, name, quality, stat_trak))
        self.connection.commit()

    def delete_float(self, weapon, name):
        self.cursor.execute('delete from floats where weapon=%s and name=%s', (weapon, name))
        self.connection.commit()


if __name__ == '__main__':
    skindb = SkinDB()
    skindb.insert_skin(weapon='testweapon', name='aname', rarity='very rare', collection='the cool collection',
                       quality='Factory New', stat_trak=False, url='https:hihihi.de')
    print(skindb.get_skin(weapon='testweapon', name='aname', quality='Factory New', stat_trak=False))
    skindb.delete_skin(weapon='testweapon', name='aname', quality='Factory New', stat_trak=False)
    print(skindb.get_all_collections())
    print(skindb.get_skins_in_collection('The Prisma 2 Collection'))
    skindb.insert_float(weapon='FloatWeapon', name='FloatName', min_float=0.1, max_float=0.9)
    print(skindb.get_float(weapon='FloatWeapon', name='FloatName'))
    skindb.delete_float(weapon='FloatWeapon', name='FloatName')
