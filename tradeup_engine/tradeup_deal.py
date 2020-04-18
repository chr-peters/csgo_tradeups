from tradeup_engine.tradeup_utils import TradeupUtils
from tradeup_engine.skin import Skin, SkinOffer


class TradeupDeal:

    tax = 0.15  # steam tax for csgo items

    __slots__ = [
        'inputs',
        'outputs'  # a list of tuples: (SkinOffer, probability)
    ]

    def __init__(self, inputs, output_pool):
        self.inputs = inputs
        skin_amounts = []
        for cur_output in output_pool:
            found = False
            for output_tuple in skin_amounts:
                if output_tuple[0].skin.weapon == cur_output.skin.weapon and \
                        output_tuple[0].skin.name == cur_output.skin.name:
                    found = True
                    output_tuple[1] += 1
            if not found:
                skin_amounts.append([cur_output, 1])
        # convert sums to probabilities
        self.outputs = []
        for cur_output in skin_amounts:
            self.outputs.append((cur_output[0], cur_output[1] / len(output_pool)))

    def get_cost(self):
        cost = 0
        for cur_offer in self.inputs:
            cost += cur_offer.price
        return round(cost, 2)

    def get_min_profit(self):
        if len(self.outputs) == 0:
            return float('-inf')
        cost = self.get_cost()
        min_profit = float("inf")
        for cur_offer in self.outputs:
            cur_profit = cur_offer[0].price / (1 + TradeupDeal.tax) - cost
            if cur_profit < min_profit:
                min_profit = cur_profit
        return round(min_profit, 2)

    def get_max_profit(self):
        if len(self.outputs) == 0:
            return float('-inf')
        cost = self.get_cost()
        max_profit = float("-inf")
        for cur_offer in self.outputs:
            cur_profit = cur_offer[0].price / (1 + TradeupDeal.tax) - cost
            if cur_profit > max_profit:
                max_profit = cur_profit
        return round(max_profit, 2)

    def get_average_profit(self):
        if len(self.outputs) == 0:
            return float('-inf')
        cost = self.get_cost()
        average_profit = 0
        for cur_offer in self.outputs:
            average_profit += cur_offer[1] * (cur_offer[0].price / (1 + TradeupDeal.tax) - cost)
        return round(average_profit, 2)

    def get_roi(self):
        cost = self.get_cost()
        average_profit = self.get_average_profit()
        roi = average_profit / cost
        return round(roi, 2)


if __name__ == '__main__':
    tradeup_utils = TradeupUtils()
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
    output_pool = tradeup_utils.get_output_pool(input_pool)
    tradeup_deal = TradeupDeal(inputs=input_pool, output_pool=output_pool)
    for cur_tuple in tradeup_deal.outputs:
        print(cur_tuple)

    print('Cost: {}'.format(tradeup_deal.get_cost()))
    print('Min Profit: {}'.format(tradeup_deal.get_min_profit()))
    print('Max Profit: {}'.format(tradeup_deal.get_max_profit()))
    print('Average Profit: {}'.format(tradeup_deal.get_average_profit()))
    print('ROI: {}'.format(tradeup_deal.get_roi()))
