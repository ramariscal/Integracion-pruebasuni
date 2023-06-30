from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy() 


class Producto(db.Model):
    __tablename__ = 'Producto' 
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    valor_venta= db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)


    def serialize(self):

        return{
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "valor_venta": self.valor_venta,
            "stock": self.stock,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Carrito(db.Model):
    __tablename__ = 'Carrito' 
    id_carrito = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(10), nullable=False)
    total = db.Column(db.Integer, nullable=False)


    def serialize(self):

        return{
            "id_carrito": self.id_carrito,
            "rut": self.rut,
            "total": self.total,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class ProductoCarrito(db.Model):
    __tablename__ = 'ProductoCarrito' 
    id_carrito = db.Column(db.Integer,  primary_key=True)
    id_producto = db.Column(db.Integer,  primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)


    def serialize(self):

        return{
            "id_carrito": self.id_carrito,
            "id_producto": self.id_producto,
            "cantidad": self.cantidad,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Cliente(db.Model):
    __tablename__ = 'Cliente' 
    rut = db.Column(db.String(10), primary_key=True)
    tarjeta = db.Column(db.Integer, nullable=False)


    def serialize(self):

        return{
            "rut": self.rut,
            "tarjeta": self.tarjeta,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Compra(db.Model):
    __tablename__ = 'Compra' 
    id = db.Column(db.Integer,  primary_key=True)
    id_carrito = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    transaccion = db.Column(db.Integer, nullable=False)


    def serialize(self):

        return{
            "id": self.id,
            "id_carrito": self.id_carrito,
            "total": self.total,
            "transaccion": self.transaccion,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Tarjeta(db.Model):
    __tablename__ = 'Tarjeta' 
    nro_tarjeta = db.Column(db.Integer,  primary_key=True)
    cvv = db.Column(db.Integer, nullable=False)
    saldo = db.Column(db.Integer, nullable=False)
    fecha_ven_dia = db.Column(db.Integer, nullable=False)
    fecha_ven_año = db.Column(db.Integer, nullable=False)


    def serialize(self):

        return{
            "nro_tarjeta": self.nro_tarjeta,
            "cvv": self.cvv,
            "saldo": self.saldo,
            "fecha_ven_dia": self.fecha_ven_dia,
            "fecha_ven_año": self.fecha_ven_año,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
