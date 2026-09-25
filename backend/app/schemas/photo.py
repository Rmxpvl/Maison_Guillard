from pydantic import BaseModel


class PhotoOut(BaseModel):
    id: int
    produit_id: int
    url: str
    ordre: int
    principale: bool

    class Config:
        from_attributes = True
