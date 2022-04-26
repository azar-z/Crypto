import enum

SOURCE_CURRENCIES = (
    ('BTC', 'Bitcoin'),
    ('ETH', 'Ethereum'),
)
DEST_CURRENCIES = (
    ('USDT', 'Tether'),
)
ALL_CURRENCIES = DEST_CURRENCIES + SOURCE_CURRENCIES


class AccountOrderStatus(enum.Enum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'
    DONE = 'done'

