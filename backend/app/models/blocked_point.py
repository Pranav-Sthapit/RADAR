
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class BlockedPoint(Base):
    __tablename__ = "blocked_points"

    __table_args__ = (
        UniqueConstraint("node_id", name="uq_blocked_points_node_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Node ID from your OSMnx / NetworkX graph
    node_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
