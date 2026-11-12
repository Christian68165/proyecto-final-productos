from pydantic import BaseModel, ConfigDict
from typing import Optional

# ---------- PLATFORMS ----------
class PlatformBase(BaseModel):
    name: str
    company: str

class PlatformCreate(PlatformBase):
    pass

class PlatformResponse(PlatformBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- GENRES ----------
class GenreBase(BaseModel):
    name: str
    description: Optional[str] = None

class GenreCreate(GenreBase):
    pass

class GenreResponse(GenreBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- GAMES ----------
class GameBase(BaseModel):
    title: str
    price: float
    stock: int
    image_url: Optional[str] = None
    platform_id: int
    genre_id: int

class GameCreate(GameBase):
    pass

class GameResponse(GameBase):
    id: int
    platform: Optional[PlatformResponse] = None
    genre: Optional[GenreResponse] = None
    model_config = ConfigDict(from_attributes=True)

# ---------- SALES (NUEVO) ----------
class SaleCreate(BaseModel):
    game_id: int
    quantity: int = 1

class SaleResponse(BaseModel):
    id: int
    game_id: int
    quantity: int
    total: float
    model_config = ConfigDict(from_attributes=True)