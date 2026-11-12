from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db
import os
import requests

# Variable para Slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def notificar_slack(texto: str):
    if SLACK_WEBHOOK_URL:
        try:
            requests.post(SLACK_WEBHOOK_URL, json={"text": texto}, timeout=3)
        except Exception as e:
            print("Error enviando a Slack:", e)

# Crea las tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API GameVault - Colección de Videojuegos",
    version="1.0.0",
    description="Backend con 4 tablas: games, platforms, genres y sales"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ENDPOINTS DE PLATAFORMAS
# ==========================================
@app.get("/api/v1/platforms", response_model=List[schemas.PlatformResponse], tags=["Platforms"])
def list_platforms(db: Session = Depends(get_db)):
    return db.query(models.Platform).all()

@app.post("/api/v1/platforms", response_model=schemas.PlatformResponse, status_code=status.HTTP_201_CREATED, tags=["Platforms"])
def create_platform(platform: schemas.PlatformCreate, db: Session = Depends(get_db)):
    nuevo = models.Platform(**platform.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ==========================================
# ENDPOINTS DE GÉNEROS
# ==========================================
@app.get("/api/v1/genres", response_model=List[schemas.GenreResponse], tags=["Genres"])
def list_genres(db: Session = Depends(get_db)):
    return db.query(models.Genre).all()

@app.post("/api/v1/genres", response_model=schemas.GenreResponse, status_code=status.HTTP_201_CREATED, tags=["Genres"])
def create_genre(genre: schemas.GenreCreate, db: Session = Depends(get_db)):
    nuevo = models.Genre(**genre.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ==========================================
# ENDPOINTS DE JUEGOS
# ==========================================
@app.get("/api/v1/games", response_model=List[schemas.GameResponse], tags=["Games"])
def list_games(db: Session = Depends(get_db)):
    return db.query(models.Game).all()

@app.post("/api/v1/games", response_model=schemas.GameResponse, status_code=status.HTTP_201_CREATED, tags=["Games"])
def create_game(game: schemas.GameCreate, db: Session = Depends(get_db)):
    plataforma = db.query(models.Platform).filter(models.Platform.id == game.platform_id).first()
    if not plataforma:
        raise HTTPException(status_code=400, detail=f"La plataforma con ID {game.platform_id} no existe")
    
    genero = db.query(models.Genre).filter(models.Genre.id == game.genre_id).first()
    if not genero:
        raise HTTPException(status_code=400, detail=f"El género con ID {game.genre_id} no existe")

    nuevo = models.Game(**game.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    
    notificar_slack(f"🎮 Nuevo juego agregado: *{nuevo.title}* (${nuevo.price})")
    
    return nuevo

# ==========================================
# ENDPOINT DE VENTAS (CHECKOUT)
# ==========================================
@app.post("/api/v1/checkout/{game_id}", response_model=schemas.SaleResponse, tags=["Ventas"])
def procesar_compra(game_id: int, db: Session = Depends(get_db)):
    # 1. Buscar el juego
    juego = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not juego:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    # 2. Validar Stock (Lógica de negocio real)
    if juego.stock <= 0:
        raise HTTPException(status_code=400, detail="No hay stock disponible de este juego")
    
    # 3. Restar el stock
    juego.stock -= 1
    db.commit()
    db.refresh(juego)
    
    # 4. Registrar la venta
    nueva_venta = models.Sale(game_id=juego.id, quantity=1, total=juego.price)
    db.add(nueva_venta)
    db.commit()
    db.refresh(nueva_venta)
    
    # 5. Notificar a Slack
    notificar_slack(f"💰 ¡Nueva venta realizada! Juego: *{juego.title}* por ${juego.price}. Quedan {juego.stock} en stock.")
    
    return nueva_venta