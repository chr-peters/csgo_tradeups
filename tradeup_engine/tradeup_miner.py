from csgo_database.skinsdb import SkinDB
from tradeup_engine.skin import Skin, SkinOffer
from tradeup_engine.tradeup_deal import TradeupDeal
from tradeup_engine.tradeup_utils import TradeupUtils

from deap import creator
from deap import base
from deap import tools
from deap import algorithms

import random

import numpy as np

import matplotlib.pyplot as plt


class TradeupMiner:

    def __init__(self):
        self.skinDB = SkinDB()
        self.tradeup_utils = TradeupUtils()

    def search_tradeups_by_rarity_by_stat_trak(self, rarity, stat_trak):
        # build the skin pool
        skin_pool = []
        skins = self.skinDB.get_skins_by_rarity_by_stat_trak(rarity, stat_trak)
        for cur_skin in skins:
            # check if the next rarity is part of the current skin's collection
            next_rarity = TradeupUtils.get_next_rarity(rarity)
            if next_rarity not in self.tradeup_utils.collection_rarities_lookup_table[cur_skin['collection']]:
                continue
            offers = self.tradeup_utils.offers_lookup_table[(cur_skin['weapon'], cur_skin['name'],
                                                             cur_skin['quality'], cur_skin['stat_trak'])]
            if offers is None:
                print('Careful! Skin without offers: {}'.format(cur_skin))
                continue
            for cur_buy_price in offers['lowest_sell_orders']:
                skin_pool.append(SkinOffer(
                    skin=Skin(
                        weapon=cur_skin['weapon'],
                        name=cur_skin['name'],
                        rarity=cur_skin['rarity'],
                        collection=cur_skin['collection'],
                        quality=cur_skin['quality'],
                        stat_trak=cur_skin['stat_trak'],
                        url=cur_skin['url']
                    ),
                    price=cur_buy_price
                ))

        return self.search_tradeups(skin_pool)

    def search_tradeups_for_collection_by_rarity_by_stat_trak(self, collection, rarity, stat_trak):
        # build the skin pool
        skin_pool = []
        skins = self.skinDB.get_skins_in_collection_by_rarity_by_stat_trak(collection, rarity, stat_trak)
        for cur_skin in skins:
            # check if the next rarity is part of the current skin's collection
            next_rarity = TradeupUtils.get_next_rarity(rarity)
            if next_rarity not in self.tradeup_utils.collection_rarities_lookup_table[cur_skin['collection']]:
                continue
            offers = self.tradeup_utils.offers_lookup_table[(cur_skin['weapon'], cur_skin['name'],
                                                             cur_skin['quality'], cur_skin['stat_trak'])]
            if offers is None:
                print('Careful! Skin without offers: {}'.format(cur_skin))
                continue
            for cur_buy_price in offers['lowest_sell_orders']:
                skin_pool.append(SkinOffer(
                    skin=Skin(
                        weapon=cur_skin['weapon'],
                        name=cur_skin['name'],
                        rarity=cur_skin['rarity'],
                        collection=cur_skin['collection'],
                        quality=cur_skin['quality'],
                        stat_trak=cur_skin['stat_trak'],
                        url=cur_skin['url']
                    ),
                    price=cur_buy_price
                ))

        if len(skin_pool) == 0:
            return None
        return self.search_tradeups(skin_pool)

    def search_tradeups(self, skin_pool):
        """Uses inputs from the skin_pool to search for profitable tradeups using a genetic algorithm."""

        creator.create('FitnessMax', base.Fitness, weights=(1.0,))
        creator.create('Individual', list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()
        toolbox.register('generate_attribute', random.randint, 0, len(skin_pool)-1)
        toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.generate_attribute, 10)
        toolbox.register('population', tools.initRepeat, list, toolbox.individual)

        def eval_tradeup(individual):
            inputs = []
            for cur_index in individual:
                inputs.append(skin_pool[cur_index])
            tradeup_deal = TradeupDeal(inputs=inputs, output_pool=self.tradeup_utils.get_output_pool(inputs))
            return tradeup_deal.get_roi(),

        toolbox.register('evaluate', eval_tradeup)
        toolbox.register('mate', tools.cxTwoPoint)
        toolbox.register('mutate', tools.mutUniformInt, low=0, up=len(skin_pool)-1, indpb=0.05)
        toolbox.register('select', tools.selTournament, tournsize=3)
        # toolbox.register('select', tools.selNSGA2)
        # toolbox.register('select', tools.selAutomaticEpsilonLexicase)

        pop = toolbox.population(n=300)
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)

        pop, log = algorithms.eaSimple(population=pop, toolbox=toolbox, cxpb=0.5, mutpb=0.2, ngen=300,
                                       stats=stats, halloffame=hof, verbose=False)

        max_values = []
        for cur_generation in log:
            max_values.append(cur_generation['avg'])

        # plt.plot(max_values)
        # plt.show()

        # generate the tradeup deal from the best individual
        inputs = []
        for cur_index in hof[0]:
            inputs.append(skin_pool[cur_index])
        output_pool = self.tradeup_utils.get_output_pool(inputs)

        return TradeupDeal(inputs, output_pool)

    def mine_tradeups_by_collection(self, rarity, stat_trak):
        collections = self.skinDB.get_all_collections()
        best_deal = None
        for cur_collection in collections:
            print('Current collection: {}'.format(cur_collection))
            deal = self.search_tradeups_for_collection_by_rarity_by_stat_trak(collection=cur_collection,
                                                                              rarity=rarity, stat_trak=stat_trak)
            if deal is None:
                print('No deal found.')
                continue
            print('Current ROI: {}'.format(deal.get_roi()))
            if best_deal is None or deal.get_roi() > best_deal.get_roi():
                best_deal = deal
        return best_deal


if __name__ == '__main__':
    tradeup_miner = TradeupMiner()

    # tradeup_deal = tradeup_miner.search_tradeups_for_collection_by_rarity_by_stat_trak(
    #     collection='The Wildfire Collection', rarity='Restricted', stat_trak=False
    # )

    # tradeup_deal = tradeup_miner.search_tradeups_by_rarity_by_stat_trak('Restricted', True)
    tradeup_deal = tradeup_miner.mine_tradeups_by_collection(rarity='Mil-Spec', stat_trak=False)

    print('Inputs:')
    print('=======')
    for cur_tuple in tradeup_deal.inputs:
        print(cur_tuple)

    print('Outputs:')
    print('========')
    for cur_tuple in tradeup_deal.outputs:
        print(cur_tuple)

    print('Cost: {}'.format(tradeup_deal.get_cost()))
    print('Min Profit: {}'.format(tradeup_deal.get_min_profit()))
    print('Max Profit: {}'.format(tradeup_deal.get_max_profit()))
    print('Average Profit: {}'.format(tradeup_deal.get_average_profit()))
    print('ROI: {}'.format(tradeup_deal.get_roi()))
