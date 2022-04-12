CELERY_BEAT_SCHEDULE = {
    'cache-orderbook-nobitex': {
        'task': 'user.tasks.nobitex.cache_orderbook_task',
        'schedule': 5.0,
        'options': {
            'expires': 3.0,
        },
    },
    'cache-trades-nobitex': {
        'task': 'user.tasks.nobitex.cache_trades_task',
        'schedule': 10.0,
        'options': {
            'expires': 5.0,
        },
    },
    'cache-market-info-nobitex': {
        'task': 'user.tasks.nobitex.cache_market_info_task',
        'schedule': 30.0,
        'options': {
            'expires': 15.0,
        },
    },
    'cache-orderbook-exir': {
        'task': 'user.tasks.exir.cache_orderbook_task',
        'schedule': 5.0,
        'options': {
            'expires': 3.0,
        },
    },
    'cache-trades-exir': {
        'task': 'user.tasks.exir.cache_trades_task',
        'schedule': 10.0,
        'options': {
            'expires': 5.0,
        },
    },
    'cache-orderbook-wallex': {
        'task': 'user.tasks.wallex.cache_orderbook_task',
        'schedule': 5.0,
        'options': {
            'expires': 3.0,
        },
    },
    'cache-trades-wallex': {
        'task': 'user.tasks.wallex.cache_trades_task',
        'schedule': 10.0,
        'options': {
            'expires': 5.0,
        },
    },
    'cache-market-info-wallex': {
        'task': 'user.tasks.wallex.cache_market_info_task',
        'schedule': 30.0,
        'options': {
            'expires': 15.0,
        },
    },
}
