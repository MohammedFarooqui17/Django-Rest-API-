from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
# from models import CarCreate, CarUpdate, CarResponse
from database import get_connection
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal
import pymysql



# Database connection function
def get_connection():
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='car'
    )
    return db



# Pydantic models for Car
class CarBase(BaseModel):
    name: str
    descriptions: str
    active: bool = True
    chessinumber: Optional[str] = None
    price: Optional[Decimal] = None

    @validator('price')
    def price_must_be_valid(cls, v, values):
        if values.get('active') and (v is None or v < 50000):
            raise ValueError("Price must be >= 50000 if car is active")
        return v

class CarCreate(CarBase):
    pass

class CarUpdate(CarBase):
    pass

class CarResponse(CarBase):
    id: int



# FastAPI application instance
app = FastAPI()


@app.get("/cars/", response_model=List[CarResponse])
def list_cars():
    db = get_connection()
    cur = db.cursor()
    cur.execute("SELECT * FROM carlist")
    rows = cur.fetchall()
    db.close()

    car_list_data = []
    discount_percentage = Decimal(10)

    for row in rows:
        price = Decimal(row[5])
        discounted_price = price - (price * discount_percentage / Decimal(100))
        car = {
            "id": row[0],
            "name": row[1],
            "descriptions": row[2],
            "active": row[3],
            "chessinumber": row[4],
            "price": price,
            "discounted_price": discounted_price
        }
        car_list_data.append(car)
    
    return car_list_data


@app.post("/cars/", status_code=201)
def create_car(car: CarCreate):
    db = get_connection()
    cur = db.cursor()
    try:
        query = "INSERT INTO carlist (name, descriptions, active, chessinumber, price) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(query, (car.name, car.descriptions, car.active, car.chessinumber, car.price))
        db.commit()
        return {"message": "Car added successfully!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        db.close()


@app.get("/cars/{car_id}/", response_model=CarResponse)
def get_car(car_id: int):
    db = get_connection()
    cur = db.cursor()
    cur.execute("SELECT * FROM carlist WHERE id = %s", (car_id,))
    row = cur.fetchone()
    db.close()

    if not row:
        raise HTTPException(status_code=404, detail="Car not found")

    price = Decimal(row[5])
    discounted_price = price - (price * Decimal(10) / Decimal(100))

    return {
        "id": row[0],
        "name": row[1],
        "descriptions": row[2],
        "active": row[3],
        "chessinumber": row[4],
        "price": price,
        "discounted_price": discounted_price
    }


@app.put("/cars/{car_id}/")
def update_car(car_id: int, car: CarUpdate):
    db = get_connection()
    cur = db.cursor()
    try:
        cur.execute("SELECT * FROM carlist WHERE id = %s", (car_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Car not found")

        query = """
            UPDATE carlist SET name = %s, descriptions = %s, active = %s, chessinumber = %s, price = %s
            WHERE id = %s
        """
        cur.execute(query, (car.name, car.descriptions, car.active, car.chessinumber, car.price, car_id))
        db.commit()
        return {"message": "Car updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        db.close()


@app.delete("/cars/{car_id}/")
def delete_car(car_id: int):
    db = get_connection()
    cur = db.cursor()
    try:
        cur.execute("SELECT * FROM carlist WHERE id = %s", (car_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Car not found")

        cur.execute("DELETE FROM carlist WHERE id = %s", (car_id,))
        db.commit()
        return {"message": "Car deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        db.close()
