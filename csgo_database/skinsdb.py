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

    def delete_skin(self, weapon, name):
        self.cursor.execute('delete from skins where weapon=%s and name=%s', (weapon, name))
        self.connection.commit()


if __name__ == '__main__':
    skindb = SkinDB()
    skindb.insert_skin('testweapon', 'aname', 'very rare', 'the cool collection')
    print(skindb.get_skin('testweapon', 'aname'))
    skindb.delete_skin('testweapon', 'aname')
