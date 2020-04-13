"""This script fetches the prices of all skins and stores them in the csgo database."""
from csgo_database.skinsdb import SkinDB
from PriceFetcher import PriceFetcher

skinDB = SkinDB()
priceFetcher = PriceFetcher()

# go by collections to make it easier to search for deals
collections = skinDB.get_all_collections()  # this is an ordered list by timestamp

# start with the newest element because it might not have been finished (move the last element to the front of the list)
collections = [collections[-1]] + collections[0:(len(collections)-1)]

for cur_collection in collections:
    # iterate over each skin in the collection
    cur_skins = skinDB.get_skins_in_collection(cur_collection)
    for cur_skin in cur_skins:
        # iterate over each possible quality
        for cur_quality in ['Factory New', 'Minimal Wear', 'Field-Tested', 'Well-Worn', 'Battle-Scarred']:
            # stat trak or not
            for stat_trak in [False, True]:
                offers = priceFetcher.fetch_prices(weapon=cur_skin['weapon'],
                                                   name=cur_skin['name'],
                                                   quality=cur_quality,
                                                   stat_trak=stat_trak)

                # delete the old offers
                skinDB.delete_offers(cur_skin['weapon'], cur_skin['name'], cur_quality, stat_trak)

                if offers is None:
                    continue

                print('Successfully retrieved offers for skin {}, quality: {}, stat trak: {}'.format(cur_skin,
                                                                                                     cur_quality,
                                                                                                     stat_trak))
                skinDB.insert_offer(cur_skin['weapon'], cur_skin['name'], cur_quality, stat_trak, 'buy',
                                    offers['highest_buy_order'])
                for cur_sell_order in offers['lowest_sell_orders']:
                    skinDB.insert_offer(cur_skin['weapon'], cur_skin['name'], cur_quality, stat_trak, 'sell',
                                        cur_sell_order)
