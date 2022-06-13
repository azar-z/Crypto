'''
    def get_token(self, email, password):
        pass  # throw user

    @staticmethod
    def get_currency_symbol(currency):
        if currency == 'IRR':
            return 'TMN'
        else:
            return currency

    @staticmethod
    def get_raw_orderbook(market_symbol, is_bids):
        cache_key = 'wallex_orderbook_' + market_symbol
        response = cache.get(cache_key)
        order_book_type = 'ask'
        if is_bids:
            order_book_type = 'bid'
        return response['result'][order_book_type]

    @staticmethod
    def get_raw_trades(market_symbol, is_sell):
        cache_key = 'wallex_trades_' + market_symbol
        response = cache.get(cache_key)
        all_trades = response['result']['latestTrades']
        specific_type_trades = []
        for trade in all_trades:
            if trade['isBuyOrder'] != is_sell:
                specific_type_trades.append(trade)
        return specific_type_trades

    @staticmethod
    def get_price_from_raw_order(raw_order):
        return Decimal(raw_order['price'])

    @staticmethod
    def get_size_from_raw_order(raw_order):
        return float(raw_order['quantity'])

    @staticmethod
    def get_price_from_raw_trade(raw_trade):
        return Decimal(raw_trade['price'])

    @staticmethod
    def get_size_from_raw_trade(raw_trade):
        return float(raw_trade['quantity'])

    @staticmethod
    def get_time_from_raw_trade(raw_trade):
        zulu_time = raw_trade['timestamp']
        return datetime.datetime.strptime(zulu_time, '%Y-%m-%dT%H:%M:%S.%fZ')

    def has_authentication_information(self):
        url = "https://api.wallex.ir/v1/account/profile"
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        response = requests.get(url, headers=headers).json()
        return response['success']

    def get_authentication_headers(self):
        if not self.has_authentication_information():
            self.raise_authentication_expired_exception()
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        return headers

    def new_order(self, source, dest, amount, price, is_sell):
        side = 'sell' if is_sell else 'buy'
        market_symbol = self.get_market_symbol(source, dest)
        if source == 'IRR':
            price = price / 10
        data = json.dumps({
            "price": str(price),
            "quantity": str(amount),
            "side": side,
            "symbol": market_symbol,
            "type": "limit",
        })
        headers = self.get_authentication_headers().update({
            'Content-Type': 'application/json',
        })
        url = "https://api.wallex.ir/v1/account/orders"
        response = requests.post(url, headers=headers, data=data)
        response = response.json()
        if response['success']:
            return response['result']['clientOrderId']
        return ""

    def get_balance(self, currency):
        url = "https://api.wallex.ir/v1/account/balances"
        response = requests.get(url, headers=self.get_authentication_headers(), data="")
        response = response.json()
        if response['success']:
            response = response['result']['balances'][self.get_currency_symbol(currency)]
            total = float(response['value'])
            locked = float(response['locked'])
            balance = total - locked
            if currency == 'IRR':
                balance = balance * 10
            return balance
        return ""

    def get_balance_of_all_currencies(self):
        cache_key = 'wallex_balance_' + str(self.id)
        if cache_key not in cache:
            url = "https://api.wallex.ir/v1/account/balances"
            response = requests.get(url, headers=self.get_authentication_headers(), data="")
            response = response.json()
            cache.set(cache_key, response, timeout=300)
        else:
            response = cache.get(cache_key)
        if response['success']:
            balance_of_all = []
            for currency_tuple in ALL_CURRENCIES:
                currency = currency_tuple[0]
                response = response['result']['balances'][self.get_currency_symbol(currency)]
                total = float(response['value'])
                locked = float(response['locked'])
                balance = total - locked
                if currency == 'IRR':
                    balance = balance * 10
                if balance > 0.0:
                    balance_of_all.append((currency, balance))
            return balance_of_all
        return ""

    @classmethod
    def get_market_info(cls, source, dest):
        market_symbol = cls.get_market_symbol(source, dest)
        cache_key = 'wallex_market'
        response = cache.get(cache_key)
        response = response['result']['symbols'][market_symbol]['stats']
        return {
            'bestSell': round(float(response['24h_highPrice']), 2),
            'bestBuy': round(float(response['24h_lowPrice']), 2),
        }

    def get_order_status(self, order_id):
        return AccountOrderStatus.CANCELLED
'''