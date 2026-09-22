from sqlalchemy.orm import Session

from app.models.produit import Produit


def get_all(
    db: Session, categorie_id: int | None = None, disponibilite: str | None = None
) -> list[Produit]:
    query = db.query(Produit)
    if categorie_id is not None:
        query = query.filter(Produit.categorie_id == categorie_id)
    if disponibilite is not None:
        query = query.filter(Produit.disponibilite == disponibilite)
    return query.all()


def get_by_id(db: Session, produit_id: int) -> Produit | None:
    return db.query(Produit).filter(Produit.id == produit_id).first()


def create(db: Session, data: dict) -> Produit:
    produit = Produit(**data)
    db.add(produit)
    db.commit()
    db.refresh(produit)
    return produit


def update(db: Session, produit_id: int, data: dict) -> Produit | None:
    produit = get_by_id(db, produit_id)
    if produit is None:
        return None

    for key, value in data.items():
        if value is not None:
            setattr(produit, key, value)

    db.commit()
    db.refresh(produit)
    return produit


def delete(db: Session, produit_id: int) -> bool:
    produit = get_by_id(db, produit_id)
    if produit is None:
        return False

    db.delete(produit)
    db.commit()
    return True
