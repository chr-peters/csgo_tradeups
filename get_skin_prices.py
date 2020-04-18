"""This script fetches the prices of all skins and stores them in the csgo database."""
from csgo_database.skinsdb import SkinDB
from PriceFetcher import PriceFetcher

skinDB = SkinDB()
priceFetcher = PriceFetcher()

cur_skins = skinDB.get_skins_by_offer_timestamp()
for cur_skin in cur_skins:
    cur_nameid = skinDB.get_item_nameid(weapon=cur_skin['weapon'], name=cur_skin['name'],
                                        quality=cur_skin['quality'], stat_trak=cur_skin['stat_trak'])

    if cur_nameid is None:
        continue

    print(cur_skin)
    offers = priceFetcher.fetch_prices(cur_nameid)

    if offers is None:
        continue

    # delete the old offers
    skinDB.delete_offers(cur_skin['weapon'], cur_skin['name'], cur_skin['quality'], cur_skin['stat_trak'])

    skinDB.insert_offer(cur_skin['weapon'], cur_skin['name'], cur_skin['quality'], cur_skin['stat_trak'], 'buy',
                        offers['highest_buy_order'])
    for cur_sell_order in offers['lowest_sell_orders']:
        skinDB.insert_offer(cur_skin['weapon'], cur_skin['name'], cur_skin['quality'], cur_skin['stat_trak'], 'sell',
                            cur_sell_order)

    print('Successfully retrieved offers for skin {} {}, quality: {}, stat trak: {}'.format(cur_skin['weapon'],
                                                                                            cur_skin['name'],
                                                                                            cur_skin['quality'],
                                                                                            cur_skin['stat_trak']))
