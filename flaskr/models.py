class Usuario:
    def __init__(self, id, nombre, correo):
        self.id = id
        self.nombre = nombre
        self.correo = correo

class Producto:
    def __init__(self, id, marca, modelo, imagen, precio, stock):
        self.id = id
        self.marca = marca
        self.modelo = modelo
        self.imagen = imagen
        self.precio = precio
        self.stock = stock

class ProductoAuxiliar:
    def __init__(self, marca, modelo, imagen, precio):
        self.marca = marca
        self.modelo = modelo
        self.imagen = imagen
        self.precio = precio