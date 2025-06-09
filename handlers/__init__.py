# handlers/__init__.py
from .user import register_user_handlers
from .admin import register_admin_handlers
from .marketing import register_marketing_handlers
from .payment import register_payment_handlers

__all__ = [
    'register_user_handlers',
    'register_admin_handlers',
    'register_marketing_handlers',
    'register_payment_handlers'
]