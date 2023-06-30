from typing import Union

from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


import sqlite3

import time

import json


file_db = "./database.db"


app = FastAPI()
app.title = "Simulación de TBK"
app.version = "1.0.7"

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "up"}


#class execute_sale_fake_class(BaseModel):
    monto: int = "100"
    rut: str = "19111222-4" 
    nro_tarjeta: int = 8888999977776666
    fecha_v: str = "05/23"
    cvv: int = 456
#@app.post("/execute_sale_fake")
#def execute_sale_fake(raw_data:execute_sale_fake_class):
    json_data = {"monto":raw_data.monto, "rut":raw_data.rut, "nro_tarjeta":raw_data.nro_tarjeta, "fecha_v":raw_data.fecha_v, "cvv":raw_data.cvv}
    # {"monto":100, "rut":"19111222-4", "nro_tarjeta":8888999977776666, "fecha_v":"05/23", "cvv":456}
    print(json_data)
    # Extraer los datos del JSON
    monto = json_data.get("monto")
    rut = json_data.get("rut")
    n_tarjeta = json_data.get("n_tarjeta")
    fecha_v = json_data.get("fecha_v")
    cvv = json_data.get("cvv")
    # Obtener el timestamp actual
    timestamp = int(time.time())

    return {"status": True, "id_transaction": timestamp}


class execute_sale_class(BaseModel):
    monto: int = "100"
    rut: str = "19111222-4" 
    nro_tarjeta: int = 8888999977776666
    fecha_v: str = "05/23"
    cvv: int = 456
@app.post("/execute_sale")
def execute_sale(raw_data: execute_sale_class):
    # {"monto":100, "rut":"19111222-4", "nro_tarjeta":8888999977776666, "fecha_v":"05/23", "cvv":456}
    
    json_data = {"monto":raw_data.monto, "nro_tarjeta":raw_data.nro_tarjeta, "fecha_v":raw_data.fecha_v, "cvv":raw_data.cvv}
    print(json_data)
    # Extraer los datos del JSON
    monto = json_data.get("monto")
    rut = json_data.get("rut")
    nro_tarjeta = json_data.get("nro_tarjeta")
    fecha_v = json_data.get("fecha_v")
    try:
        if len(fecha_v) != 5:
            return {"status": False, "msg": "fecha_v con formato incorrecto"}
        fecha_ven_mes_tmp = int(fecha_v.split("/")[0])
        fecha_ven_year_tmp = int("20" + fecha_v.split("/")[1])
        if isinstance(fecha_ven_mes_tmp, int) and isinstance(fecha_ven_year_tmp, int):
            fecha_ven_mes = fecha_ven_mes_tmp
            fecha_ven_year = fecha_ven_year_tmp
    except:
        return {"status": False, "msg": "fecha_v con formato incorrecto"}
    cvv = json_data.get("cvv")
    # Obtener el timestamp actual
    timestamp = int(time.time())

    # ¿Tarjeta existe?
    tarjeta = obtener_tarjeta(nro_tarjeta)    
    if {'msg': 'Tarjeta no encontrada'} == tarjeta:
        return {"status": False, "msg": "Tarjeta no encontrada"}
    tarjeta_dict = json.loads(tarjeta)

    # Comprobar datos tarjetas
    tarjeta_base = {"nro_tarjeta": tarjeta_dict.get("nro_tarjeta"), "cvv": tarjeta_dict.get("cvv"), "fecha_ven_mes": tarjeta_dict.get("fecha_ven_mes"), "fecha_ven_year": tarjeta_dict.get("fecha_ven_year")}
    tarjeta_obj  = {"nro_tarjeta": nro_tarjeta, "cvv": cvv, "fecha_ven_mes": fecha_ven_mes, "fecha_ven_year": fecha_ven_year}
    if tarjeta_base != tarjeta_obj:
        return {"status": False, "msg": "Los valores de la tarjeta no coinciden"}

    # Validar saldo
    amount_comparison_exec = amount_comparison({"nro_tarjeta": nro_tarjeta, "monto_a_descontar": monto})
    if not amount_comparison_exec.get("Operacion"):
        print({"status": False, "msg": "Saldo insuficiente"})
        return {"status": False, "msg": "Saldo insuficiente"}

    # Recalcular saldo y update en base
    discount_amount_exec = discount_amount({"nro_tarjeta": nro_tarjeta, "monto_a_descontar": monto})
    if not discount_amount_exec:
        return {"status": False, "msg": "Error en el cobro"}
    print({"status": True, "id_transaction": timestamp})
    return {"status": True, "id_transaction": timestamp}

@app.post("/view_all_card")
def view_all_card():
    # Crear una conexión a la base de datos SQLite
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    # Ejecutar la consulta SELECT
    cursor.execute("SELECT * FROM Tarjeta")
    rows = cursor.fetchall()
    # Crear una lista para almacenar las tarjetas
    tarjetas = []
    # Iterar sobre las filas y crear un diccionario por cada tarjeta
    for row in rows:
        tarjeta = {
            "NumeroDeTarjeta": row[0],
            "CVV": row[1],
            "MesDeVencimiento": row[3],
            "YearDeVencimiento": row[4],
            "Saldo": row[2],
        }
        tarjetas.append(tarjeta)
    # Cerrar la conexión a la base de datos
    conn.close()
    # Devolver la respuesta en formato JSON
    return {"tarjetas": tarjetas}


#@app.get("/view_card/{nro_tarjeta}")
def obtener_tarjeta(nro_tarjeta: int):
    # Crear una conexión a la base de datos SQLite
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    # Ejecutar la consulta SELECT
    cursor.execute("SELECT * FROM Tarjeta WHERE nro_tarjeta = ?", (nro_tarjeta,))
    # Obtener la primera fila de resultados
    result = cursor.fetchone()
    # Cerrar la conexión
    conn.close()
    # Verificar si se encontró la tarjeta
    if result:
        # Crear un diccionario con los nombres de las columnas como claves
        # y los valores de la fila como valores
        columnas = [desc[0] for desc in cursor.description]
        fila_dict = dict(zip(columnas, result))
        # Convertir el diccionario en formato JSON
        fila_json = json.dumps(fila_dict)
        return fila_json
    else:
        return {"msg": "Tarjeta no encontrada"}



@app.put("/discount_amount")
def discount_amount(data: dict):
    # {"nro_tarjeta": 1896892098148735, "monto_a_descontar": 5000}
    # {"Operacion": false}
    # {"Operacion": true, "monto_resultado": 5000}
    # Obtener los valores del JSON
    nro_tarjeta = data.get("nro_tarjeta")
    monto_a_descontar = data.get("monto_a_descontar")
    # Crear una conexión a la base de datos SQLite
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    # Obtener el saldo actual de la tarjeta
    cursor.execute("SELECT saldo FROM Tarjeta WHERE nro_tarjeta=?", (nro_tarjeta,))
    row = cursor.fetchone()
    # Verificar si se encontró la tarjeta
    if row is None:
        conn.close()
        return {"Operacion": False}
    saldo_actual = row[0]
    # Verificar si hay suficiente saldo para el descuento
    if saldo_actual < monto_a_descontar:
        conn.close()
        return {"Operacion": False}
    # Calcular el nuevo saldo después del descuento
    nuevo_saldo = saldo_actual - monto_a_descontar
    # Actualizar el saldo en la base de datos
    cursor.execute("UPDATE Tarjeta SET saldo=? WHERE nro_tarjeta=?", (nuevo_saldo, nro_tarjeta))
    conn.commit()
    # Cerrar la conexión a la base de datos
    conn.close()
    return {"Operacion": True, "monto_resultado": nuevo_saldo}


@app.post("/validate_card/{nro_tarjeta}")
def validate_card(nro_tarjeta: int):
    # Crear una conexión a la base de datos SQLite
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    # Ejecutar la consulta SELECT
    cursor.execute("SELECT * FROM Tarjeta WHERE nro_tarjeta = ?", (nro_tarjeta,))
    # Obtener la primera fila de resultados
    result = cursor.fetchone()
    # Cerrar la conexión
    conn.close()
    # Verificar si se encontró la tarjeta
    if result:
        return {"message": "Tarjeta encontrada"}
    else:
        return {"message": "Tarjeta no encontrada"}


@app.post("/amount_comparison")
def amount_comparison(data: dict):
    # {"nro_tarjeta": 1896892098148735, "monto_a_descontar": 5000}
    # {"Operacion": false, "saldo": insuficiente, "monto_resultado": 5000}
    # {"Operacion": true, "saldo": suficiente, "monto_resultado": 5000}
    nro_tarjeta = data.get("nro_tarjeta")
    monto_a_descontar = data.get("monto_a_descontar")
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute("SELECT saldo FROM Tarjeta WHERE nro_tarjeta = ?", (nro_tarjeta,))
    saldo = cursor.fetchone()
    if saldo is None:
        conn.close()
        return {"Operacion": False, "mensaje": "Tarjeta no encontrada"}
    saldo = saldo[0]
    resultado = saldo - monto_a_descontar
    if resultado < 0:
        conn.close()
        return {"Operacion": False, "saldo": "insuficiente", "monto_resultado": resultado}
    cursor.execute("UPDATE Tarjeta SET saldo = ? WHERE nro_tarjeta = ?", (resultado, nro_tarjeta))
    conn.commit()
    conn.close()
    return {"Operacion": True, "saldo": "ok", "monto_resultado": resultado}







