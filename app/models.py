from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Un usuario puede tener muchas propuestas
    proposals = relationship(
        "Proposal",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Proposal(Base):
    __tablename__ = "proposals"
    __table_args__ = (
        # Optimized lookups for owner-scoped listings and aggregations.
        Index("ix_proposals_owner_created", "owner_id", "created_at"),
        Index("ix_proposals_owner_status", "owner_id", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(120), nullable=False)
    platform = Column(String(80), nullable=False)
    project_title = Column(String(180), nullable=False)
    project_link = Column(String(500), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(32), default="Enviada", index=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="proposals")


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
