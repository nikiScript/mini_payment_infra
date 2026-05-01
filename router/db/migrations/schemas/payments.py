import uuid
import datetime
import enum
from typing import List
from sqlalchemy import String, Enum, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Provider(enum.Enum):
    stripe = "stripe"
    paypal = "paypal"
    adyen = "adyen"

class Base(DeclarativeBase):
    pass

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "payments"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "success", "failed", name="transaction_status"),
        nullable=False,
        default="pending"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=func.now(),
    )

class RoutingDecisions(Base):
    __tablename__ = "routing_decisions"
    __table_args__ = {"schema": "payments"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.transactions.id"))
    provider_chosen: Mapped[Provider] = mapped_column(
        Enum(Provider),
        nullable=True,
        name="provider_enum",
    )
    reason: Mapped[str] = mapped_column(String(), nullable=False)
    attempted_providers: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=func.now()
    )

class ProviderStats(Base):
    __tablename__ = "provider_stats"
    __table_args__ = {"schema": "payments"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    provider_name: Mapped[str] = mapped_column(String(), nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, nullable=False)
    avg_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    fee_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        onupdate=func.now(),
        default=func.now()
    )
