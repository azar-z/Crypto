CELERY_BEAT_SCHEDULE = {
    'cache-orderbook': {
        'task': 'user.tasks.nobitex.cache_orderbook_task',
        'schedule': 5.0,
        'options': {
            'expires': 3.0,
        },
    },
    'cache-trades': {
        'task': 'user.tasks.nobitex.cache_trades_task',
        'schedule': 10.0,
        'options': {
            'expires': 5.0,
        },
    },
}
