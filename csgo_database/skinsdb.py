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

    def delete_skin(self, weapon, name):
        self.cursor.execute('delete from skins where weapon=%s and name=%s', (weapon, name))
        self.connection.commit()


if __name__ == '__main__':
    skindb = SkinDB()
    skindb.insert_skin('testweapon', 'aname', 'very rare', 'the cool collection')
    skindb.delete_skin('testweapon', 'aname')
