ORDERBOOK_UPDATE_RATE = 10.0
TRADES_UPDATE_RATE = 30.0
MARKET_UPDATE_RATE = 120.0


ORDER_UPDATE_STATUS_RATE = 60.0

UPDATE_GOLDEN_TRADES_RATE = 100.0

EXPORT_DATA_RATE = 100.0

CELERY_BEAT_SCHEDULE = {

    ################################## market update tasks ###############################

    'cache-orderbook-nobitex': {
        'task': 'user.tasks.nobitex.cache_orderbook_task',
        'schedule': ORDERBOOK_UPDATE_RATE,
        'options': {
            'expires': ORDERBOOK_UPDATE_RATE / 2,
        },
    },
    'cache-trades-nobitex': {
        'task': 'user.tasks.nobitex.cache_trades_task',
        'schedule': TRADES_UPDATE_RATE,
        'options': {
            'expires': TRADES_UPDATE_RATE / 2,
        },
    },
    'cache-market-info-nobitex': {
        'task': 'user.tasks.nobitex.cache_market_info_task',
        'schedule': MARKET_UPDATE_RATE,
        'options': {
            'expires': MARKET_UPDATE_RATE / 2,
        },
    },
    'cache-orderbook-exir': {
        'task': 'user.tasks.exir.cache_orderbook_task',
        'schedule': ORDERBOOK_UPDATE_RATE,
        'options': {
            'expires': ORDERBOOK_UPDATE_RATE / 2,
        },
    },
    'cache-trades-exir': {
        'task': 'user.tasks.exir.cache_trades_task',
        'schedule': TRADES_UPDATE_RATE,
        'options': {
            'expires': TRADES_UPDATE_RATE / 2,
        },
    },
    'cache-orderbook-wallex': {
        'task': 'user.tasks.wallex.cache_orderbook_task',
        'schedule': ORDERBOOK_UPDATE_RATE,
        'options': {
            'expires': ORDERBOOK_UPDATE_RATE / 2,
        },
    },
    'cache-trades-wallex': {
        'task': 'user.tasks.wallex.cache_trades_task',
        'schedule': TRADES_UPDATE_RATE,
        'options': {
            'expires': TRADES_UPDATE_RATE / 2,
        },
    },
    'cache-market-info-wallex': {
        'task': 'user.tasks.wallex.cache_market_info_task',
        'schedule': MARKET_UPDATE_RATE,
        'options': {
            'expires': MARKET_UPDATE_RATE / 2,
        },
    },

    ################################## order update status tasks###############################

    'order_update_status': {
        'task': 'trade.tasks.order_update_status_task',
        'schedule': ORDER_UPDATE_STATUS_RATE,
        'options': {
            'expires': ORDER_UPDATE_STATUS_RATE / 2,
        },
    },

    ################################## golden trade task ###############################

    'update_golden_trades': {
        'task': 'trade.tasks.update_golden_trades_task',
        'schedule': UPDATE_GOLDEN_TRADES_RATE,
        'options': {
            'expires': UPDATE_GOLDEN_TRADES_RATE / 2,
        },
    },

    ################################## export data ###############################

    'export_user_data_task': {
        'task': 'data.tasks.export_user_data_task',
        'schedule': EXPORT_DATA_RATE,
        'options': {
            'expires': EXPORT_DATA_RATE / 2,
        },
    },

    'download_data_from_binance': {
        'task': 'data.tasks.download_data_from_binance',
        'schedule': EXPORT_DATA_RATE,
        'options': {
            'expires': EXPORT_DATA_RATE / 2,
        },
    },
}
