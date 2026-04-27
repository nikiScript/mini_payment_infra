import uuid
import datetime
import enum
from sqlalchemy import String,  ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Provider(enum.Enum):
    stripe = "stripe_mock"
    paypal = "paypal_mock"
    adyen = "ayden_mock"



class Base(DeclarativeBase):
    pass

class Merchants(Base):
    __tablename__ = "merchants"
    __table_args__ = {"schema": "merchants"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=func.now()
    )

class ApiKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = {"schema": "merchants"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("merchants.merchants.id"))
    key_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=func.now()
    )
