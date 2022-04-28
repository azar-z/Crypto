
'''

    @classmethod
    def get_orderbook(cls, market_symbol, is_bids):
        raw_orders = cls.get_raw_orderbook(market_symbol, is_bids)[:NUMBER_OF_ROWS]
        orders = []
        for raw_order in raw_orders:
            price = round(cls.get_price_from_raw_order(raw_order), 2)
            size = round(cls.get_size_from_raw_order(raw_order), 6)
            total = round(float(price) * size, 2)
            market = cls.__name__
            orders.append({"price": price, "size": size, "total": total, "market": market})
        orders = sorted(orders, key=itemgetter('price'), reverse=True)
        if is_bids:
            return orders[-NUMBER_OF_ROWS:]
        return orders[:NUMBER_OF_ROWS]

    @staticmethod
    def get_orderbook_of_all(source, dest, is_bids):
        orders = []
        for subclass in Account.__subclasses__():
            market_symbol = subclass.get_market_symbol(source, dest)
            orders.extend(subclass.get_orderbook(market_symbol, is_bids))
        orders = sorted(orders, key=itemgetter('price'), reverse=True)
        if is_bids:
            return orders[-NUMBER_OF_ROWS:]
        return orders[:NUMBER_OF_ROWS]

    @classmethod
    def get_trades(cls, market_symbol, is_sell):
        raw_trades = cls.get_raw_trades(market_symbol, is_sell)[:NUMBER_OF_ROWS]
        trades = []
        for raw_trade in raw_trades:
            price = round(cls.get_price_from_raw_trade(raw_trade), 2)
            size = round(cls.get_size_from_raw_trade(raw_trade), 6)
            total = round(float(price) * size, 2)
            market = cls.__name__
            trades.append({"price": price, "size": size, "total": total, "market": market})
        trades = sorted(trades, key=itemgetter('price'), reverse=True)
        if is_sell:
            return trades[-NUMBER_OF_ROWS:]
        return trades[:NUMBER_OF_ROWS]

    @staticmethod
    def get_trades_of_all(source, dest, is_sell):
        trades = []
        for subclass in Account.__subclasses__():
            market_symbol = subclass.get_market_symbol(source, dest)
            trades.extend(subclass.get_trades(market_symbol, is_sell))
        trades = sorted(trades, key=itemgetter('price'), reverse=True)
        if is_sell:
            return trades[-NUMBER_OF_ROWS:]
        return trades[:NUMBER_OF_ROWS]

    @classmethod
    def get_average_market_price(cls, source, dest):
        market_info = cls.get_market_info(source, dest)
        market_lowest_price = market_info['bestBuy']
        market_highest_price = market_info['bestSell']
        average_market_price = (market_highest_price + market_lowest_price) / 2
        return average_market_price

    @staticmethod
    def get_market_info_of_all(dest='USDT'):
        market_info = []
        for currency_tuple in SOURCE_CURRENCIES:
            currency = currency_tuple[0]
            _market_info = {}
            for subclass in Account.__subclasses__():
                subclass_market_info = subclass.get_market_info(currency, dest)
                _market_info.update({
                    subclass.__name__.lower(): subclass_market_info
                })
            market_info.append({'currency': currency, 'info': _market_info})
        return market_info

    @classmethod
    def make_an_account_for_user(cls, user):
        account = cls.objects.create(owner=user)
        account.save()
        return account

    @classmethod
    def get_type(cls):
        return cls.__name__[0].upper()
'''
