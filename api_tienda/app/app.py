from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Producto, Cliente, Carrito, ProductoCarrito, Compra
from flask_cors import CORS, cross_origin
from logging import exception
import requests
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Conten-Type'
app.url_map.strict_slashes = False
app.config['DEBUG'] = False
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

Migrate(app, db)

@app.route('/')
def index():
    return 'Bienvenido'

#Productos--------------------


#Solicitar todos los productos 
@app.route('/productos', methods=['GET'])
def getProductos():
    user = Producto.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200

#Agregar producto
@app.route('/productos', methods=['POST'])
def addProductos():
    user = Producto()
    user.id_producto = request.json.get('id_producto')
    user.nombre = request.json.get('nombre')
    user.valor_venta = request.json.get('valor_venta')
    user.stock = request.json.get('stock')
    Producto.save(user)

    return jsonify(user.serialize()),200

#Solicitar un producto
@app.route('/productos/<id_producto>', methods=['GET'])
def getProducto(id_producto):
    user = Producto.query.get(id_producto)
    return jsonify(user.serialize()),200
   

#Eliminar un producto 
@app.route('/productos/<id_producto>', methods=['DELETE'])
def deleteProducto(id_producto):
    user = Producto.query.get(id_producto)
    Producto.delete(user)
    return jsonify(user.serialize()),200


#Actualizar un producto 
@app.route('/productos/<id_producto>', methods=['PUT'])
def updateProducto(id_producto):
    user = Producto.query.get(id_producto)

    user.id_producto = request.json.get('id_producto')
    user.valor_venta = request.json.get('valor_venta')
    user.stock = request.json.get('stock')

    Producto.update(user)

    return jsonify(user.serialize()),200

#Clientes--------------------

#Solicitar todos los clientes 
@app.route('/clientes', methods=['GET'])
def getClientes():
    user = Cliente.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200

#Agregar Cliente
@app.route('/clientes', methods=['POST'])
def addCliente():
    def validar_rut(rut):
        rut = rut.replace(".", "").replace("-", "").lower()
        if not rut[:-1].isdigit():
            return False
        verificador = rut[-1]
        cuerpo = rut[:-1]
        suma = 0
        multiplicador = 2
        for digito in reversed(cuerpo):
            suma += int(digito) * multiplicador
            multiplicador = multiplicador + 1 if multiplicador < 7 else 2
        resto = suma % 11
        digito_verificador = str(11 - resto) if resto != 1 else 'k'
        return digito_verificador == verificador

    try:
        rut = request.json.get('rut')
        tarjeta = request.json.get('tarjeta')

        if not rut or not tarjeta:
            error_message = {'error': 'Campos incompletos'}
            return jsonify(error_message), 400

        if not validar_rut(rut):
            error_message = {'error': 'Rut inválido'}
            return jsonify(error_message), 400

        if len(tarjeta) != 16 or not tarjeta.isdigit():
            error_message = {'error': 'Tarjeta inválida'}
            return jsonify(error_message), 400

        existing_rut = Cliente.query.filter_by(rut=rut).first()
        if existing_rut:
            error_message = {'error': 'Rut ya ingresado'}
            return jsonify(error_message), 409

        existing_tarjeta = Cliente.query.filter_by(tarjeta=tarjeta).first()
        if existing_tarjeta:
            error_message = {'error': 'Tarjeta ya registrada'}
            return jsonify(error_message), 409

        user = Cliente()
        user.rut = rut
        user.tarjeta = tarjeta
        Cliente.save(user)

        return jsonify(user.serialize()), 200

    except Exception as e:
        error_message = {'error': 'Ocurrió un error en el servidor'}
        return jsonify(error_message), 500
    
#Eliminar un cliente
@app.route('/clientes/<rut>', methods=['DELETE'])
def deleteCliente(rut):
    try:
        existing_cliente = Cliente.query.get(rut)
        if not existing_cliente:
            error_message = {'error': 'Cliente no encontrado'}
            return jsonify(error_message), 404

        Cliente.delete(existing_cliente)
        return jsonify({'message': 'Cliente eliminado correctamente'}), 200

    except Exception as e:
        error_message = {'error': 'Ocurrió un error en el servidor'}
        return jsonify(error_message), 500

#Solicitar un cliente
@app.route('/clientes/<rut>', methods=['GET'])
def getCliente(rut):
    user = Cliente.query.get(rut)
    
    if user is None:
        error_message = {'error': 'Rut no encontrado'}
        return jsonify(error_message), 404
    
    return jsonify(user.serialize()), 200

#Carrito--------------------

#Solicitar los carritos 
@app.route('/carritos', methods=['GET'])
def getCarritos():
    user = Carrito.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200

#Agregar Carritos
@app.route('/carritos', methods=['POST'])
def addCarrito():
    user = Carrito()
    user.id_carrito = request.json.get('id_carrito')
    user.rut = request.json.get('rut')
    user.total = request.json.get('total')
    Carrito.save(user)

    return jsonify(user.serialize()),200

#Eliminar Carrito
@app.route('/carritos/<id_carrito>', methods=['DELETE'])
def deleteCarrito(id_carrito):
    user = Carrito.query.get(id_carrito)
    Carrito.delete(user)
    return jsonify(user.serialize()),200

#ProductoCarrito--------------------


#Agregar Producto a Carrito 
@app.route('/productocarrito', methods=['POST'])
def addProductoCarrito():
    try:
        id_producto = request.json.get('id_producto')
        id_carrito = request.json.get('id_carrito')
        cantidad = request.json.get('cantidad')

        if not id_producto or not id_carrito:
            return jsonify({'mensaje': 'Campos requeridos no proporcionados'}), 400

        if cantidad is None:
            return jsonify({'mensaje': 'Error de sintaxis. El campo "cantidad" no ha sido proporcionado'}), 400

        producto = Producto.query.get(id_producto)

        if not producto:
            return jsonify({'mensaje': 'Error al incorporar producto. Producto no encontrado'}), 400

        precio_producto = producto.valor_venta
        stock_producto = producto.stock

        if cantidad > stock_producto:
            return jsonify({'mensaje': 'Excedió límite de stock'}), 400

        subtotal = precio_producto * cantidad

        carrito = Carrito.query.get(id_carrito)
        total_carrito = carrito.total

        nuevo_total_carrito = total_carrito + subtotal
        carrito.total = nuevo_total_carrito
        db.session.commit()

        user = ProductoCarrito(id_producto=id_producto, id_carrito=id_carrito, cantidad=cantidad)
        db.session.add(user)
        db.session.commit()

        return jsonify(user.serialize()), 200

    except ValueError as e:
        return jsonify({'mensaje': str(e)}), 500
    except Exception:
        return jsonify({'mensaje': 'Error del sistema'}), 500

#Solicitar todos los ProductoCarrito 
@app.route('/productocarrito', methods=['GET'])
def getProductoCarritos():
    user = ProductoCarrito.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200


#Eliminar producto del carrito
@app.route('/productocarrito/<id_producto>/<id_carrito>', methods=['DELETE'])
def deleteProductoCarrito(id_producto, id_carrito):
    try:
        user = ProductoCarrito.query.filter_by(id_producto=id_producto, id_carrito=id_carrito).first()

        if not user:
            error_message = {'error': 'Producto o carrito no encontrado'}
            return jsonify(error_message), 404

        cantidad = user.cantidad
        precio_producto = Producto.query.filter_by(id_producto=id_producto).first().valor_venta
        if not precio_producto:
            error_message = {'error': 'Producto no encontrado'}
            return jsonify(error_message), 404

        subtotal = precio_producto * cantidad

        carrito = Carrito.query.get(id_carrito)
        if not carrito:
            error_message = {'error': 'Carrito no encontrado'}
            return jsonify(error_message), 404

        total_carrito = carrito.total

        nuevo_total_carrito = total_carrito - subtotal
        carrito.total = nuevo_total_carrito

        db.session.delete(user)
        db.session.commit()

        return jsonify(user.serialize()), 200

    except Exception as e:
        error_message = {'error': 'Ocurrió un error en el servidor'}
        return jsonify(error_message), 500


#Compra--------

#Agregar Compra
@app.route('/compra', methods=['POST'])
def createCompra():
    carrito_id = request.json['id_carrito']
    carrito = Carrito.query.get(carrito_id)

    n_tarjeta = request.json['n_tarjeta']
    fecha_v = request.json['fecha_v']
    cvv = request.json['cvv']

    payload = {
        "monto": carrito.total,
        "nro_tarjeta": n_tarjeta,
        "fecha_v": fecha_v,
        "cvv": cvv
        # "rut": "11123123-1"
    }

    # Realizar la solicitud a la API externa
    api_url = "http://tbkemu/execute_sale"

    response = requests.post(api_url, json=payload)
    print(response)
    print(response.json())
   
    # Procesar la respuesta de la API externa
    if response.status_code == 200:
        response_data = response.json()
        print("------")
        print(response_data['status'])
        print(type(response_data['status']))

        if response_data['status']:
            print(response_data)
            # Si el status es True, guardar la id_transaccion en la tabla compra
            print("------")
            print(type(carrito.total))
            print(carrito.total)
            print("------")

            compra = Compra(id_carrito=carrito_id, total=carrito.total, transaccion=response_data['id_transaction'])
            db.session.add(compra)
            db.session.commit()

            # Descuento del campo stock en la tabla producto
            productos_carrito = ProductoCarrito.query.filter_by(id_carrito=carrito_id).all()
            for producto_carrito in productos_carrito:
                producto = Producto.query.get(producto_carrito.id_producto)
                cantidad = producto_carrito.cantidad
                producto.stock -= cantidad
                db.session.commit()

            ProductoCarrito.query.filter_by(id_carrito=carrito_id).delete()
            Carrito.query.filter_by(id_carrito=carrito_id).delete()
            db.session.commit()

            return jsonify({"message": "Compra creada exitosamente."}), 200
        else:
            response_data = response.json()
            mensaje = response_data.get("msg")
            return jsonify({"message": mensaje}), 500

    else:
        return jsonify({"message": "Error en la solicitud a la API externa."}), response.status_code

#Lista de compras    
@app.route('/compras', methods=['GET'])
def getCompras():
    user = Compra.query.all()
    user = list(map(lambda x: x.serialize(), user))
    return jsonify(user),200

#Tarjetas--------------------

#Lista de todas las tarjetas 
@app.route('/tarjetas', methods=['GET'])
def getTarjetas():
    # Realizar la solicitud POST a la API de FastAPI
    api_url = "http://tbkemu/view_all_card"
    response = requests.post(api_url)
    
    # Procesar la respuesta de la API de FastAPI
    if response.status_code == 200:
        response_data = response.json()
        return jsonify(response_data), 200
    
    return jsonify({"error": "No se pudo obtener la lista de tarjetas"}), 500



if __name__ == '__main__':
    app.run(debug=True, port=4000)