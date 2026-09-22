from pydantic import BaseModel


class CategorieCreate(BaseModel):
    nom: str
    slug: str


class CategorieOut(BaseModel):
    id: int
    nom: str
    slug: str

    class Config:
        from_attributes = True
