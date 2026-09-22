from sqlalchemy import Column, Integer, String

from app.database import Base


class Categorie(Base):
    __tablename__ = "categorie"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
