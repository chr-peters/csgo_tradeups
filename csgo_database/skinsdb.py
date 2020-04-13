import pymysql


class SkinDB:

    def __init__(self):
        self.connection = pymysql.connect(host='localhost', user='root', passwd='root', db='csgo')
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def insert_skin(self, weapon, name, rarity, collection):
        self.cursor.execute('insert into skins(weapon, name, rarity, collection) values(%s, %s, %s, %s)',
                            (weapon, name, rarity, collection))
        self.connection.commit()

    def insert_offer(self, weapon, name, quality, stat_trak, offer_type, price):
        self.cursor.execute('insert into offers(weapon, name, quality, stat_trak, offer_type, price) '
                            'values(%s, %s, %s, %s, %s, %s)', (weapon, name, quality, stat_trak, offer_type, price))
        self.connection.commit()

    def delete_offers(self, weapon, name, quality, stat_trak):
        self.cursor.execute('delete from offers where weapon=%s and name=%s and quality=%s and stat_trak=%s',
                            (weapon, name, quality, stat_trak))

    def get_skin(self, weapon, name):
        self.cursor.execute('select * from skins where weapon=%s and name=%s', (weapon, name))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        else:
            return {
                'weapon': res[0][1],
                'name': res[0][2],
                'rarity': res[0][3],
                'collection': res[0][4]
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
                'collection': cur_skin[4]
            })
        return skins

    def delete_skin(self, weapon, name):
        self.cursor.execute('delete from skins where weapon=%s and name=%s', (weapon, name))
        self.connection.commit()


if __name__ == '__main__':
    skindb = SkinDB()
    skindb.insert_skin('testweapon', 'aname', 'very rare', 'the cool collection')
    print(skindb.get_skin('testweapon', 'aname'))
    skindb.delete_skin('testweapon', 'aname')
    print(skindb.get_all_collections())
    print(skindb.get_skins_in_collection('The Prisma 2 Collection'))
