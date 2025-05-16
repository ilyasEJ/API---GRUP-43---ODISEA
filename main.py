from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
from database import SessionLocal, engine
from schemas import (
    SocioCreate, SocioResponse,
    HotelCreate, HotelResponse,
    HabitacionResponse,
    RestauranteCreate, RestauranteResponse,
    PistaCreate, PistaResponse,
    SpaCreate, SpaResponse,
    ReservaHotelCreate, ReservaHotelResponse,
    ReservaPistaCreate, ReservaPistaResponse,
    ReservaRestauranteCreate, ReservaRestauranteResponse,
    ReservaSpaCreate, ReservaSpaResponse,
    FavoritoCreate, FavoritoResponse,
    ServicioPistaResponse,
    ServicioRestauranteResponse,
    ServicioSpaResponse
)
# Crear la base de datos si no existe
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["http://18.210.82.24"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints de autenticación
@app.post("/buscar_socio/")
def buscar_socio(email: str, contrasenya: str, db: Session = Depends(get_db)):
    socio = db.query(models.Socio).filter(models.Socio.email == email).first()

    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")

    if socio.contrasenya != contrasenya:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {
        "socio_id": int(socio.id),
        "nombre": socio.nombre
    }

@app.post("/socios/", status_code=201)
def crear_socio(socio: SocioCreate, db: Session = Depends(get_db)):
    existing_socio = db.query(models.Socio).filter(models.Socio.email == socio.email).first()
    if existing_socio:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

    db_socio = models.Socio(**socio.dict())
    db.add(db_socio)
    db.commit()
    db.refresh(db_socio)

    return {"message": "Socio creado correctamente", "socio_id": db_socio.id}


from sqlalchemy import text

@app.get("/lugares")
def get_lugares(db: Session = Depends(get_db)):
    query = text("""
        SELECT
            lp.id AS id,
            lp.local_id AS local_id,
            lp.tipo_local AS tipo_establecimiento,
            lp.popularidad AS valoracion
        FROM local_popularidad lp
        ORDER BY lp.popularidad DESC
    """)
    resultados = db.execute(query).fetchall()

    lugares = []

    for row in resultados:
        if row.tipo_establecimiento == "hotel":
            lugar_info = db.query(models.Hotel).filter(models.Hotel.id == row.local_id).first()
        elif row.tipo_establecimiento == "spa":
            lugar_info = db.query(models.Spa).filter(models.Spa.id == row.local_id).first()
        elif row.tipo_establecimiento == "restaurante":
            lugar_info = db.query(models.Restaurante).filter(models.Restaurante.id == row.local_id).first()
        elif row.tipo_establecimiento == "pista":
            lugar_info = db.query(models.Pista).filter(models.Pista.id == row.local_id).first()
        else:
            lugar_info = None

        if lugar_info:
            lugar = {
                "id": lugar_info.id,
                "nombre": lugar_info.nombre,
                "descripcion": lugar_info.descripcion,
                "detalles": lugar_info.detalles,  # AÑADIDO
                "ubicacion": lugar_info.ubicacion,
                "img_url": lugar_info.img_url,
                "valoracion": float(row.valoracion),
                "tipo_establecimiento": row.tipo_establecimiento
            }
            lugares.append(lugar)

    return lugares

@app.get("/socios/{socio_id}", response_model=SocioResponse)
def obtener_socio(socio_id: int, db: Session = Depends(get_db)):
    socio = db.query(models.Socio).filter(models.Socio.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    return socio

@app.delete("/socios/{socio_id}")
def eliminar_socio(socio_id: int, db: Session = Depends(get_db)):
    socio = db.query(models.Socio).filter(models.Socio.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    db.delete(socio)
    db.commit()
    return {"message": "Socio eliminado correctamente"}

# Favoritos
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

@app.get("/favoritos/{socio_id}")
def obtener_favoritos(socio_id: int, db: Session = Depends(get_db)):
    favoritos = db.query(models.Favorito).filter(models.Favorito.socio_id == socio_id).all()

    lugares_favoritos = []

    for fav in favoritos:
        lugar = None
        if fav.tipo == "hotel":
            lugar = db.query(models.Hotel).filter(models.Hotel.id == fav.referencia_id).first()
        elif fav.tipo == "spa":
            lugar = db.query(models.Spa).filter(models.Spa.id == fav.referencia_id).first()
        elif fav.tipo == "restaurante":
            lugar = db.query(models.Restaurante).filter(models.Restaurante.id == fav.referencia_id).first()
        elif fav.tipo == "pista":
            lugar = db.query(models.Pista).filter(models.Pista.id == fav.referencia_id).first()

        if lugar:
            lugar_dict = lugar.__dict__.copy()
            lugar_dict["tipo"] = fav.tipo  # puedes añadir tipo si lo necesitas
            lugares_favoritos.append(lugar_dict)

    return lugares_favoritos

@app.post("/favoritos/")
def agregar_a_favoritos(socio_id: int, tipo_establecimiento: str, referencia_id: int, db: Session = Depends(get_db)):
    # Verificar que el socio existe
    socio = db.query(models.Socio).filter(models.Socio.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")

    # Crear nuevo registro en la tabla favoritos
    nuevo_favorito = models.Favorito(socio_id=socio_id, tipo=tipo_establecimiento, referencia_id=referencia_id)
    db.add(nuevo_favorito)
    db.commit()
    db.refresh(nuevo_favorito)

    return {"message": "Establecimiento agregado a favoritos correctamente", "favorito_id": nuevo_favorito.id}

@app.delete("/favoritos/{socio_id}/{referencia_id}")
def eliminar_favorito(socio_id: int, referencia_id: int, db: Session = Depends(get_db)):
    # Buscar el favorito por socio_id y referencia_id
    favorito = db.query(models.Favorito).filter(
        models.Favorito.socio_id == socio_id,
        models.Favorito.referencia_id == referencia_id
    ).first()

    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")

    # Eliminar el favorito
    db.delete(favorito)
    db.commit()
    return {"message": "Favorito eliminado correctamente"}


# Reservas
@app.get("/reservas_hotel/{socio_id}")
def obtener_reservas_hotel(socio_id: int, db: Session = Depends(get_db)):
    reservas = db.query(models.ReservaHotel).filter(models.ReservaHotel.socio_id == socio_id).all()
    return reservas

@app.get("/reservas_pista/{socio_id}")
def obtener_reservas_pista(socio_id: int, db: Session = Depends(get_db)):
    reservas = db.query(models.ReservaPista).filter(models.ReservaPista.socio_id == socio_id).all()
    return reservas

@app.get("/reservas_restaurante/{socio_id}")
def obtener_reservas_restaurante(socio_id: int, db: Session = Depends(get_db)):
    reservas = db.query(models.ReservaRestaurante).filter(models.ReservaRestaurante.socio_id == socio_id).all()
    return reservas

@app.get("/reservas_spa/{socio_id}")
def obtener_reservas_spa(socio_id: int, db: Session = Depends(get_db)):
    reservas = db.query(models.ReservaSpa).filter(models.ReservaSpa.socio_id == socio_id).all()
    return reservas

# Información básica de lugares
@app.get("/hotel/{hotel_id}", response_model=HotelResponse)
def obtener_hotel_por_id(hotel_id: int, db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")
    
    # Añadir el campo 'tipoEstablecimiento' con el valor "hotel"
    hotel.tipoEstablecimiento = "hotel"
    return hotel

@app.get("/pista/{pista_id}", response_model=PistaResponse)
def obtener_pista_por_id(pista_id: int, db: Session = Depends(get_db)):
    pista = db.query(models.Pista).filter(models.Pista.id == pista_id).first()
    if not pista:
        raise HTTPException(status_code=404, detail="Pista no encontrada")
    
    # Añadir el campo 'tipoEstablecimiento' con el valor "pista"
    pista.tipoEstablecimiento = "pista"
    return pista

@app.get("/restaurante/{restaurante_id}", response_model=RestauranteResponse)
def obtener_restaurante_por_id(restaurante_id: int, db: Session = Depends(get_db)):
    restaurante = db.query(models.Restaurante).filter(models.Restaurante.id == restaurante_id).first()
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    
    # Añadir el campo 'tipoEstablecimiento' con el valor "restaurante"
    restaurante.tipoEstablecimiento = "restaurante"
    return restaurante

@app.get("/spa/{spa_id}", response_model=SpaResponse)
def obtener_spa_por_id(spa_id: int, db: Session = Depends(get_db)):
    spa = db.query(models.Spa).filter(models.Spa.id == spa_id).first()
    if not spa:
        raise HTTPException(status_code=404, detail="Spa no encontrado")
    
    # Añadir el campo 'tipoEstablecimiento' con el valor "spa"
    spa.tipoEstablecimiento = "spa"
    return spa

# Servicios/características específicas de lugares
@app.get("/hotel/{hotel_id}/habitaciones", response_model=List[HabitacionResponse])
def obtener_habitaciones_hotel(hotel_id: int, db: Session = Depends(get_db)):
    habitaciones = db.query(models.Habitacion).filter(models.Habitacion.hotel_id == hotel_id).all()
    if not habitaciones:
        raise HTTPException(status_code=404, detail="No se encontraron habitaciones para este hotel")
    return habitaciones

@app.get("/pista/{pista_id}/servicios", response_model=List[ServicioPistaResponse])
def obtener_servicios_pista(pista_id: int, db: Session = Depends(get_db)):
    servicios = db.query(models.ServicioPistas).filter(models.ServicioPistas.pista_id == pista_id).all()
    if not servicios:
        raise HTTPException(status_code=404, detail="No se encontraron servicios para esta pista")
    return servicios

@app.get("/restaurante/{restaurante_id}/servicios", response_model=List[ServicioRestauranteResponse])
def obtener_servicios_restaurante(restaurante_id: int, db: Session = Depends(get_db)):
    servicios = db.query(models.ServicioRestaurante).filter(models.ServicioRestaurante.restaurante_id == restaurante_id).all()
    if not servicios:
        raise HTTPException(status_code=404, detail="No se encontraron servicios para este restaurante")
    return servicios

@app.get("/spa/{spa_id}/servicios", response_model=List[ServicioSpaResponse])
def obtener_servicios_spa(spa_id: int, db: Session = Depends(get_db)):
    servicios = db.query(models.ServicioSpa).filter(models.ServicioSpa.spa_id == spa_id).all()
    if not servicios:
        raise HTTPException(status_code=404, detail="No se encontraron servicios para este spa")
    return servicios
# Crear reservas
@app.post("/reservas_hotel/", response_model=ReservaHotelResponse)
def crear_reserva_hotel(reserva: ReservaHotelCreate, db: Session = Depends(get_db)):
    db_reserva = models.ReservaHotel(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@app.post("/reservas_pista/", response_model=ReservaPistaResponse)
def crear_reserva_pista(reserva: ReservaPistaCreate, db: Session = Depends(get_db)):
    db_reserva = models.ReservaPista(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@app.post("/reservas_restaurante/", response_model=ReservaRestauranteResponse)
def crear_reserva_restaurante(reserva: ReservaRestauranteCreate, db: Session = Depends(get_db)):
    db_reserva = models.ReservaRestaurante(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@app.post("/reservas_spa/", response_model=ReservaSpaResponse)
def crear_reserva_spa(reserva: ReservaSpaCreate, db: Session = Depends(get_db)):
    db_reserva = models.ReservaSpa(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

# Endpoint para buscar lugares por nombre y categoría
@app.get("/buscar", response_model=List[dict])
def buscar_lugares(query: str, categoria: str, db: Session = Depends(get_db)):
    if categoria == "restaurante":
        resultados = (
            db.query(models.Restaurante)
            .filter(models.Restaurante.nombre.ilike(f"%{query}%"))
            .all()
        )
        return [
            {
                "id": r.id,
                "nombre": r.nombre,
                "ubicacion": r.ubicacion,
                "valoracion": r.valoracion,
                "descripcion": r.descripcion,
                "detalles": r.detalles,  # AÑADIDO
                "img_url": r.img_url,  # AÑADIDO
                "tipo_establecimiento": "restaurante",
            }
            for r in resultados
        ]

    elif categoria == "hotel":
        resultados = (
            db.query(models.Hotel)
            .filter(models.Hotel.nombre.ilike(f"%{query}%"))
            .all()
        )
        return [
            {
                "id": h.id,
                "nombre": h.nombre,
                "ubicacion": h.ubicacion,
                "valoracion": h.valoracion,
                "descripcion": h.descripcion,
                "detalles": h.detalles,  # AÑADIDO
                "img_url": h.img_url,  # AÑADIDO
                "tipo_establecimiento": "hotel",
            }
            for h in resultados
        ]

    elif categoria == "spa":
        resultados = (
            db.query(models.Spa)
            .filter(models.Spa.nombre.ilike(f"%{query}%"))
            .all()
        )
        return [
            {
                "id": s.id,
                "nombre": s.nombre,
                "ubicacion": s.ubicacion,
                "valoracion": s.valoracion,
                "descripcion": s.descripcion,
                "detalles": s.detalles,  # AÑADIDO
                "img_url": s.img_url,  # AÑADIDO
                "tipo_establecimiento": "spa",
            }
            for s in resultados
        ]

    elif categoria == "pista":
        resultados = (
            db.query(models.Pista)
            .filter(models.Pista.nombre.ilike(f"%{query}%"))
            .all()
        )
        return [
            {
                "id": p.id,
                "nombre": p.nombre,
                "ubicacion": p.ubicacion,
                "valoracion": p.valoracion,
                "descripcion": p.descripcion,
                "detalles": p.detalles,  # AÑADIDO
                "img_url": p.img_url,  # AÑADIDO
                "tipo_establecimiento": "pista",
            }
            for p in resultados
        ]

    else:
        raise HTTPException(status_code=400, detail="Categoría no válida")
