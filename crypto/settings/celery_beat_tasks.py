ORDERBOOK_UPDATE_RATE = 5.0
TRADES_UPDATE_RATE = 10.0
MARKET_UPDATE_RATE = 30.0


ORDER_DONE_UPDATE_RATE = 60.0
CHECK_LIMIT_UPDATE_RATE = 300.0
MOVE_DONE_UPDATE_RATE = 300.0

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

    ################################## order update tasks ###############################

    'os_to_od': {
        'task': 'trade.tasks.order_os_to_od_task',
        'schedule': ORDER_DONE_UPDATE_RATE,
        'options': {
            'expires': ORDER_DONE_UPDATE_RATE / 2,
        },
    },

    'od_to_l_to_next_step_os': {
        'task': 'trade.tasks.order_od_to_l_to_next_step_os_task',
        'schedule': CHECK_LIMIT_UPDATE_RATE,
        'options': {
            'expires': CHECK_LIMIT_UPDATE_RATE / 2,
        },
    },

    'tos_to_td_to_next_step_os': {
        'task': 'trade.tasks.order_tos_to_td_to_next_step_os_task',
        'schedule': MOVE_DONE_UPDATE_RATE,
        'options': {
            'expires': MOVE_DONE_UPDATE_RATE / 2,
        },
    },
}
