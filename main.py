from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Catálogo de Productos",
    version="1.0.0",
    description="Servicio Backend conectado a PostgreSQL en Supabase"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/products", response_model=List[schemas.ProductResponse], tags=["Productos"])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.post("/api/v1/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Productos"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    nuevo_producto = models.Product(**product.model_dump())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto