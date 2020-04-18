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

    def get_all_floats(self):
        self.cursor.execute('select weapon, name, min_float, max_float from floats')
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        floats = []
        for cur_float in res:
            floats.append({
                'weapon': cur_float[0],
                'name': cur_float[1],
                'min_float': cur_float[2],
                'max_float': cur_float[3]
            })
        return floats

    def insert_offer(self, weapon, name, quality, stat_trak, offer_type, price):
        self.cursor.execute('insert into offers(weapon, name, quality, stat_trak, offer_type, price) '
                            'values(%s, %s, %s, %s, %s, %s)', (weapon, name, quality, stat_trak, offer_type, price))
        self.connection.commit()

    def insert_item_nameid(self, weapon, name, quality, stat_trak, nameid):
        self.cursor.execute('insert into item_nameids(weapon, name, quality, stat_trak, nameid) '
                            'values(%s, %s, %s, %s, %s)', (weapon, name, quality, stat_trak, nameid))
        self.connection.commit()

    def get_item_nameid(self, weapon, name, quality, stat_trak):
        self.cursor.execute('select * from item_nameids where weapon=%s and name=%s and quality=%s and stat_trak=%s',
                            (weapon, name, quality, stat_trak))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        else:
            return res[0][5]

    def get_skins_without_id(self):
        self.cursor.execute('select s.weapon, s.name, s.rarity, s.collection, s.quality, s.stat_trak, s.url '
                            'from skins as s left join item_nameids as i on '
                            's.weapon=i.weapon and s.name=i.name and s.quality=i.quality and s.stat_trak=i.stat_trak '
                            'where i.nameid is null order by s.collection')
        res = self.cursor.fetchall()
        skins = []
        for cur_skin in res:
            skins.append({
                'weapon': cur_skin[0],
                'name': cur_skin[1],
                'rarity': cur_skin[2],
                'collection': cur_skin[3],
                'quality': cur_skin[4],
                'stat_trak': bool(cur_skin[5]),
                'url': cur_skin[6]
            })
        return skins

    def get_skins_by_offer_timestamp(self):
        """Returns all skins ordered by the timestamp of the last offer"""
        self.cursor.execute('select distinct s.weapon, s.name, s.rarity, s.collection, s.quality, s.stat_trak, s.url '
                            'from skins as s left join offers as o on '
                            's.weapon = o.weapon and s.name = o.name and s.quality = o.quality and '
                            's.stat_trak = o.stat_trak order by o.timestamp asc')
        res = self.cursor.fetchall()
        skins = []
        for cur_skin in res:
            skins.append({
                'weapon': cur_skin[0],
                'name': cur_skin[1],
                'rarity': cur_skin[2],
                'collection': cur_skin[3],
                'quality': cur_skin[4],
                'stat_trak': bool(cur_skin[5]),
                'url': cur_skin[6]
            })
        return skins

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
        self.cursor.execute('select distinct collection from skins')
        res = self.cursor.fetchall()
        collections = []
        for cur_collection in res:
            collections.append(cur_collection[0])
        return collections

    def get_offers(self, weapon, name, quality, stat_trak):
        # first get highest buy price
        self.cursor.execute('select price from offers '
                            'where offer_type="buy" and weapon=%s and name=%s and quality=%s and stat_trak=%s',
                            (weapon, name, quality, stat_trak))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        highest_buy_order = res[0][0]

        # now get the sales offers
        self.cursor.execute('select price from offers '
                            'where offer_type="sell" and weapon=%s and name=%s and quality=%s and stat_trak=%s',
                            (weapon, name, quality, stat_trak))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        lowest_sell_orders = [round(float(i[0]), 2) for i in list(res)]
        return {
            'highest_buy_order': round(float(highest_buy_order), 2),
            'lowest_sell_orders': lowest_sell_orders
        }

    def get_all_buy_offers(self):
        self.cursor.execute('select weapon, name, quality, stat_trak, price from offers where offer_type="buy"')
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        offers = []
        for cur_offer in res:
            offers.append({
                'weapon': cur_offer[0],
                'name': cur_offer[1],
                'quality': cur_offer[2],
                'stat_trak': cur_offer[3],
                'price': round(float(cur_offer[4]), 2)
            })
        return offers

    def get_all_sell_offers(self):
        self.cursor.execute('select weapon, name, quality, stat_trak, price from offers where offer_type="sell"')
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        offers = []
        for cur_offer in res:
            offers.append({
                'weapon': cur_offer[0],
                'name': cur_offer[1],
                'quality': cur_offer[2],
                'stat_trak': cur_offer[3],
                'price': round(float(cur_offer[4]), 2)
            })
        return offers

    def get_rarities_by_collection(self):
        self.cursor.execute('select distinct collection, rarity from skins')
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        rarities = []
        for cur_rarity in res:
            rarities.append({
                'collection': cur_rarity[0],
                'rarity': cur_rarity[1]
            })
        return rarities

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

    def get_skins_in_collection_by_rarity_by_stat_trak(self, collection, rarity, stat_trak):
        self.cursor.execute('select * from skins where collection=%s and rarity=%s and stat_trak=%s', (collection, rarity, stat_trak))
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

    def get_skins_by_rarity_by_stat_trak(self, rarity, stat_trak):
        self.cursor.execute('select * from skins where rarity=%s and stat_trak=%s', (rarity, stat_trak))
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

    def get_all_skins(self):
        self.cursor.execute('select * from skins')
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

    def get_distinct_skin_names(self):
        self.cursor.execute('select distinct weapon, name, rarity, collection from skins')
        res = self.cursor.fetchall()
        skins = []
        for cur_skin in res:
            skins.append({
                'weapon': cur_skin[0],
                'name': cur_skin[1],
                'rarity': cur_skin[2],
                'collection': cur_skin[3],
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
    # skindb.insert_skin(weapon='testweapon', name='aname', rarity='very rare', collection='the cool collection',
    #                    quality='Factory New', stat_trak=False, url='https:hihihi.de')
    # print(skindb.get_skin(weapon='testweapon', name='aname', quality='Factory New', stat_trak=False))
    # skindb.delete_skin(weapon='testweapon', name='aname', quality='Factory New', stat_trak=False)
    # print(skindb.get_all_collections())
    # print(skindb.get_skins_in_collection('The Prisma 2 Collection'))
    # skindb.insert_float(weapon='FloatWeapon', name='FloatName', min_float=0.1, max_float=0.9)
    # print(skindb.get_float(weapon='FloatWeapon', name='FloatName'))
    # skindb.delete_float(weapon='FloatWeapon', name='FloatName')
    # print(skindb.get_skins_without_id()[0])
    print(skindb.get_offers(weapon='AK-47', name='Fire Serpent', quality='Factory New', stat_trak=False))
    print(skindb.get_distinct_skin_names())
