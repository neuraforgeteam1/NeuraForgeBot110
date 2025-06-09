from tortoise.expressions import Q
from .models import (
    User, License, Referral, Transaction, Reward, AdminUser
)
from config import Config
from datetime import datetime, timedelta
import logging

config = Config()
logger = logging.getLogger(__name__)

async def get_user_by_telegram_id(telegram_id: int) -> User:
    return await User.get_or_none(telegram_id=telegram_id)

async def create_user(telegram_id: int, full_name: str, username: str = None) -> User:
    user = await User.create(
        telegram_id=telegram_id,
        full_name=full_name,
        username=username
    )
    logger.info(f"User created: {user.telegram_id}")
    return user

async def get_active_license(user_id: int) -> License:
    return await License.filter(
        user_id=user_id,
        is_active=True
    ).first()

async def get_referral_tree(user_id: int, level: int = 3) -> dict:
    tree = {}
    current_user = await User.get(id=user_id)
    tree[user_id] = {
        'user': current_user,
        'level': 0,
        'children': {}
    }
    
    # سطح 1
    level1_refs = await Referral.filter(
        referrer_id=user_id,
        level=1
    ).prefetch_related('referred')
    
    for ref in level1_refs:
        tree[user_id]['children'][ref.referred_id] = {
            'user': ref.referred,
            'level': 1,
            'children': {}
        }
        
        if level > 1:
            # سطح 2
            level2_refs = await Referral.filter(
                referrer_id=ref.referred_id,
                level=1
            ).prefetch_related('referred')
            
            for ref2 in level2_refs:
                tree[user_id]['children'][ref.referred_id]['children'][ref2.referred_id] = {
                    'user': ref2.referred,
                    'level': 2,
                    'children': {}
                }
                
                if level > 2:
                    # سطح 3
                    level3_refs = await Referral.filter(
                        referrer_id=ref2.referred_id,
                        level=1
                    ).prefetch_related('referred')
                    
                    for ref3 in level3_refs:
                        tree[user_id]['children'][ref.referred_id]['children'][ref2.referred_id]['children'][ref3.referred_id] = {
                            'user': ref3.referred,
                            'level': 3,
                            'children': {}
                        }
    
    return tree

async def get_expiring_licenses(days: int = 3) -> list[License]:
    end_date = datetime.utcnow() + timedelta(days=days)
    return await License.filter(
        end_date__lte=end_date,
        is_active=True,
        is_permanent=False
    ).prefetch_related('user')