"""
This class provides basic functions representing the logic of tradeups.
It uses the singleton design pattern.
"""
from csgo_database.skinsdb import SkinDB
from tradeup_engine.skin import Skin, SkinOffer

from timeit import default_timer as timer

import numpy as np


class TradeupUtils:
    float_ranges = {
        'Factory New': {
            'min_float': 0,
            'max_float': 0.07
        },
        'Minimal Wear': {
            'min_float': 0.07,
            'max_float': 0.15,
        },
        'Field-Tested': {
            'min_float': 0.15,
            'max_float': 0.38
        },
        'Well-Worn': {
            'min_float': 0.38,
            'max_float': 0.45
        },
        'Battle-Scarred': {
            'min_float': 0.45,
            'max_float': 1
        }
    }

    def __init__(self):
        self.skinDB = SkinDB()

        # build a lookup table for floats alias (weapon, name) -> {min_float, max_float}
        floats = self.skinDB.get_all_floats()
        self.float_lookup_table = {}
        for cur_float in floats:
            self.float_lookup_table[(cur_float['weapon'], cur_float['name'])] = {
                'min_float': cur_float['min_float'],
                'max_float': cur_float['max_float']
            }

        # build a lookup table for skins alias (collection, rarity, stat_trak) -> [Skin, Skin, ...]
        self.skin_lookup_table = {}
        skins = self.skinDB.get_all_skins()
        for cur_skin in skins:
            descriptor_tuple_skins = (cur_skin['collection'], cur_skin['rarity'], cur_skin['stat_trak'])
            if descriptor_tuple_skins not in self.skin_lookup_table.keys():
                self.skin_lookup_table[descriptor_tuple_skins] = []
            self.skin_lookup_table[descriptor_tuple_skins].append(
                Skin(
                    weapon=cur_skin['weapon'],
                    name=cur_skin['name'],
                    rarity=cur_skin['rarity'],
                    collection=cur_skin['collection'],
                    quality=cur_skin['quality'],
                    stat_trak=cur_skin['stat_trak'],
                    url=cur_skin['url']
                )
            )

        # also build a lookup table for all the offers
        # (weapon, name, quality, stat_trak) -> {highest_buy_order, lowest_sell_orders}
        self.offers_lookup_table = {}
        buy_offers = self.skinDB.get_all_buy_offers()
        for cur_offer in buy_offers:
            descriptor_tuple_orders = (cur_offer['weapon'], cur_offer['name'], cur_offer['quality'],
                                       cur_offer['stat_trak'])
            self.offers_lookup_table[descriptor_tuple_orders] = {'highest_buy_order': cur_offer['price'],
                                                                 'lowest_sell_orders': []}
        sell_offers = self.skinDB.get_all_sell_offers()
        for cur_offer in sell_offers:
            descriptor_tuple_orders = (cur_offer['weapon'], cur_offer['name'], cur_offer['quality'],
                                       cur_offer['stat_trak'])
            self.offers_lookup_table[descriptor_tuple_orders]['lowest_sell_orders'].append(cur_offer['price'])

        # build a lookup table that maps collections to it's rarities
        self.collection_rarities_lookup_table = {}
        rarities = self.skinDB.get_rarities_by_collection()
        for cur_rarity in rarities:
            if cur_rarity['collection'] not in self.collection_rarities_lookup_table.keys():
                self.collection_rarities_lookup_table[cur_rarity['collection']] = []
            self.collection_rarities_lookup_table[cur_rarity['collection']].append(cur_rarity['rarity'])

    def get_output_pool(self, inputs):
        """Get the pool of possible outputs for a list of input skinoffer objects."""
        output_pool = []
        # first calculate the average float from the inputs (always assuming the worst case)
        floatsum = 0
        for cur_skin in inputs:
            floatsum += TradeupUtils.float_ranges[cur_skin.skin.quality]['max_float']
        avg_float = floatsum / len(inputs)
        for cur_input in inputs:
            next_rarity = TradeupUtils.get_next_rarity(cur_input.skin.rarity)
            try:
                next_skins = self.skin_lookup_table[(cur_input.skin.collection, next_rarity, cur_input.skin.stat_trak)]
            except KeyError:
                continue
            for cur_next_skin in next_skins:
                floats = self.float_lookup_table[(cur_next_skin.weapon, cur_next_skin.name)]
                target_float = round(floats['min_float'] + (floats['max_float'] - floats['min_float']) * avg_float, 2)
                cur_quality = cur_next_skin.quality
                cur_float_range = TradeupUtils.float_ranges[cur_quality]
                if cur_float_range['min_float'] < target_float <= cur_float_range['max_float']:
                    try:
                        offers = self.offers_lookup_table[(cur_next_skin.weapon, cur_next_skin.name,
                                                           cur_next_skin.quality, cur_next_skin.stat_trak)]
                    except KeyError:
                        print('Attention! No buy offer for skin {}'.format(cur_next_skin))
                        continue
                    output_pool.append(SkinOffer(
                        skin=Skin(
                            weapon=cur_next_skin.weapon,
                            name=cur_next_skin.name,
                            rarity=cur_next_skin.rarity,
                            collection=cur_next_skin.collection,
                            quality=cur_next_skin.quality,
                            stat_trak=cur_next_skin.stat_trak,
                            url=cur_next_skin.url
                        ),
                        price=offers['highest_buy_order']
                    ))

        return output_pool

    @staticmethod
    def get_next_rarity(rarity):
        """Get the next rarity of a skin. For example Classified -> Covert"""
        if rarity == 'Consumer':
            return 'Industrial'
        elif rarity == 'Industrial':
            return 'Mil-Spec'
        elif rarity == 'Mil-Spec':
            return 'Restricted'
        elif rarity == 'Restricted':
            return 'Classified'
        elif rarity == 'Classified':
            return 'Covert'
        return None


if __name__ == '__main__':
    start_time = timer()
    tradeup_utils = TradeupUtils()
    end_time = timer()
    init_time = end_time - start_time
    print('Init time: {}'.format(init_time))
    input_pool = [
        SkinOffer(
            skin=Skin(weapon='Negev', name='Prototype', rarity='Mil-Spec', collection='The Prisma 2 Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.61
        ),
        SkinOffer(
            skin=Skin(weapon='Negev', name='Prototype', rarity='Mil-Spec', collection='The Prisma 2 Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.61
        ),
        SkinOffer(
            skin=Skin(weapon='Negev', name='Prototype', rarity='Mil-Spec', collection='The Prisma 2 Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.61
        ),
        SkinOffer(
            skin=Skin(weapon='Negev', name='Prototype', rarity='Mil-Spec', collection='The Prisma 2 Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.61
        ),
        SkinOffer(
            skin=Skin(weapon='Negev', name='Prototype', rarity='Mil-Spec', collection='The Prisma 2 Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.61
        ),
        SkinOffer(
            skin=Skin(weapon='Negev', name='Prototype', rarity='Mil-Spec', collection='The Prisma 2 Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.61
        ),
        SkinOffer(
            skin=Skin(weapon='Negev', name='Prototype', rarity='Mil-Spec', collection='The Prisma 2 Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.61
        ),
        SkinOffer(
            skin=Skin(weapon='Negev', name='Prototype', rarity='Mil-Spec', collection='The Prisma 2 Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.61
        ),
        SkinOffer(
            skin=Skin(weapon='Sawed-Off', name='Yorick', rarity='Mil-Spec', collection='The Revolver Case Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.73
        ),
        SkinOffer(
            skin=Skin(weapon='Sawed-Off', name='Yorick', rarity='Mil-Spec', collection='The Revolver Case Collection',
                      quality='Factory New', stat_trak=False, url='url'),
            price=0.73
        )
    ]
    num_measurements = 10
    durations = []
    for i in range(num_measurements):
        start_time = timer()
        output_pool = tradeup_utils.get_output_pool(input_pool)
        end_time = timer()
        durations.append(end_time - start_time)

    print('Min: {}'.format(np.min(durations)))
    print('Max: {}'.format(np.max(durations)))
    print('Avg: {}'.format(np.average(durations)))
    print('Std: {}'.format(np.std(durations)))

# Starting benchmark:
# ===================
# Min: 3.2062793999999997
# Max: 3.2355192000000024
# Avg: 3.22164437
# Std: 0.009142503289587012

# Adding float lookup table:
# ==========================
# Min: 3.0490930000000027
# Max: 3.0917428
# Avg: 3.0646301300000003
# Std: 0.011953417122400075

# Adding skin lookup table:
# =========================
# Min: 3.009478699999999
# Max: 3.0406054
# Avg: 3.02297939
# Std: 0.009225167861502714

# Adding offers lookup table:
# ===========================
# Min: 0.0004217999999999722
# Max: 0.00047279999999999545
# Avg: 0.00043023999999999287
# Std: 1.4336540726411114e-05
