from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Platform(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    company = Column(String, nullable=False)

    games = relationship("Game", back_populates="platform")

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)

    games = relationship("Game", back_populates="genre")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    image_url = Column(String, nullable=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False)

    platform = relationship("Platform", back_populates="games")
    genre = relationship("Genre", back_populates="games")

# --- NUEVA TABLA PARA VENTAS ---
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total = Column(Float, nullable=False)
    
    game = relationship("Game")