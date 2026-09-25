from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from app.database import Base


class Photo(Base):
    __tablename__ = "photo"

    id = Column(Integer, primary_key=True, index=True)
    produit_id = Column(
        Integer, ForeignKey("produit.id", ondelete="CASCADE"), nullable=False
    )
    url = Column(String, nullable=False)
    ordre = Column(Integer, nullable=False, default=0)
    principale = Column(Boolean, nullable=False, default=False)
