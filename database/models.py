from tortoise.models import Model
from tortoise import fields
import uuid
from datetime import datetime

class TimestampMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class User(Model, TimestampMixin):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)
    full_name = fields.CharField(max_length=255)
    username = fields.CharField(max_length=32, null=True)
    language = fields.CharField(max_length=2, default="fa")
    balance = fields.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_marketer = fields.BooleanField(default=False)
    referral_code = fields.CharField(max_length=12, unique=True, null=True)
    is_blocked = fields.BooleanField(default=False)
    device_id = fields.CharField(max_length=255, null=True)
    total_spent = fields.DecimalField(max_digits=12, decimal_places=2, default=0)

class AdminUser(Model, TimestampMixin):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)
    username = fields.CharField(max_length=32)
    role = fields.CharField(max_length=20, default="admin")  # superadmin, admin
    is_active = fields.BooleanField(default=True)
    two_factor_enabled = fields.BooleanField(default=False)
    last_login = fields.DatetimeField(null=True)

class License(Model, TimestampMixin):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="licenses")
    license_key = fields.CharField(max_length=32, unique=True)
    plan_type = fields.CharField(max_length=20)  # 1m, 3m, 6m, 1y, 3y, permanent
    start_date = fields.DatetimeField(default=datetime.utcnow)
    end_date = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)
    is_permanent = fields.BooleanField(default=False)
    device_id = fields.CharField(max_length=255, null=True)
    activation_count = fields.IntField(default=0)
    max_activations = fields.IntField(default=3)
    created_by_admin: fields.ForeignKeyRelation[AdminUser] = fields.ForeignKeyField(
        "models.AdminUser", null=True, related_name="licenses_created")

class Referral(Model, TimestampMixin):
    referrer: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="referrals_made")
    referred: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="referrals_received")
    level = fields.IntField(default=1)
    commission_earned = fields.DecimalField(max_digits=12, decimal_places=2, default=0)

class Transaction(Model, TimestampMixin):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="transactions")
    amount = fields.DecimalField(max_digits=12, decimal_places=2)
    currency = fields.CharField(max_length=10, default="USDT")
    description = fields.TextField()
    is_completed = fields.BooleanField(default=False)
    is_commission = fields.BooleanField(default=False)
    trx_id = fields.CharField(max_length=100, null=True)
    admin_approved = fields.BooleanField(default=False)
    approved_by: fields.ForeignKeyRelation[AdminUser] = fields.ForeignKeyField(
        "models.AdminUser", null=True, related_name="transactions_approved")

class Reward(Model, TimestampMixin):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="rewards")
    points = fields.IntField(default=0)
    is_claimed = fields.BooleanField(default=False)
    is_claimable = fields.BooleanField(default=False)
    reward_type = fields.CharField(max_length=20, null=True)  # license, cash, module
    claimed_at = fields.DatetimeField(null=True)