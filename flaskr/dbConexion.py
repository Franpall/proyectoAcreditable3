import mysql.connector
from mysql.connector import Error
from flaskr.models import Usuario, Producto, ProductoAuxiliar, ProductoEditar
import bcrypt
import os

def crear_conexion():
    try:
        conn = mysql.connector.connect(
            host='localhost',       
            user='root',     
            password='', 
            database='franpalstore'    
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error al conectarse a la base de datos: {e}")
        return None

# Area de productos
# def obtener_producto_por_id(id_producto):
#     conn = crear_conexion()
#     if conn is None:
#         print("No se pudo establecer la conexión a la base de datos.")
#         return None
#     cursor = conn.cursor()
#     cursor.execute('SELECT id, marca, modelo, descripcion, id_categoria, imagen, precio, stock FROM producto WHERE id = %s', (id_producto,))
#     producto = cursor.fetchone()
#     conn.close()
#     if producto:
#         return ProductoEditar(producto[0], producto[1], producto[2], producto[3], producto[4], producto[5], producto[6], producto[7])
#     else:
#         return None

# def actualizar_producto(id_producto, marca, modelo, stock, precio, categoria, descripcion, imagen):
#     conn = crear_conexion()
#     cursor = conn.cursor()
#     cursor.execute(
#         'UPDATE producto SET marca = %s, modelo = %s, stock = %s, precio = %s, id_categoria = %s, descripcion = %s, imagen = %s WHERE id = %s',
#         (marca, modelo, stock, precio, obtener_id_categoria(categoria), descripcion, imagen, id_producto)
#     )
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return True

# Area de productos Admin
def agregar_producto(marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO producto (marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
        (marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True

def mostrar_productos_admin():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, marca, modelo, imagen, precio, stock FROM producto')
    productos = cursor.fetchall()
    productosModel = list()
    for producto in productos:
        productosModel.append(Producto(producto[0], producto[1], producto[2], producto[3], producto[4], producto[5]))
    conn.close()
    return productosModel

# Area de productos Index
def mostrar_productos():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT marca, modelo, imagen, precio FROM producto WHERE recomendado = 0')
    productos = cursor.fetchall()
    productosModel = list()
    for producto in productos:
        productosModel.append(ProductoAuxiliar(producto[0], producto[1], producto[2], producto[3]))
    conn.close()
    return productosModel

def mostrar_productos_recomendados():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT marca, modelo, imagen, precio FROM producto WHERE recomendado = 1')
    productos = cursor.fetchall()
    productosModel = list()
    for producto in productos:
        productosModel.append(ProductoAuxiliar(producto[0], producto[1], producto[2], producto[3]))
    conn.close()
    return productosModel

# Eliminar Productos
def eliminar_producto(id_producto):
    conn = crear_conexion()
    cursor = conn.cursor()

    # Obtener la imagen antes de eliminar la categoría
    cursor.execute("SELECT imagen FROM producto WHERE id = %s", (id_producto,))
    filename = cursor.fetchone()
    
    if filename:
        filepath = os.path.join(os.path.dirname(__file__), 'static', 'uploads', filename[0])
        try:
            os.remove(filepath)
        except FileNotFoundError:
            print("No se encontró el archivo")

    cursor.execute("DELETE FROM producto WHERE id = %s", (id_producto,))
    conn.commit()

    cursor.close()
    conn.close()
    return True


# Area de categorias

def verCategorias():
    conexion = crear_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre FROM categoria")
    categorias = cursor.fetchall()
    categoriasSTR = list()
    for categoria in categorias:
        categoriasSTR.append(categoria[0])
    conexion.close()
    return categoriasSTR

def obtener_id_categoria(nombre_categoria):
    conexion = crear_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM categoria WHERE nombre = %s", (nombre_categoria,))
    id_categoria = cursor.fetchone()
    conexion.close()
    return id_categoria[0]

# Area de crear Categorias
def obtener_categorias():
    conn = crear_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categoria")
    categorias = cursor.fetchall()
    cursor.close()
    conn.close()
    return categorias

def agregar_categoria(nombre, imagen):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categoria (nombre, imagen) VALUES (%s, %s)", (nombre, imagen))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def eliminar_categoria(id_categoria):
    conn = crear_conexion()
    cursor = conn.cursor()

    # Obtener la imagen antes de eliminar la categoría
    cursor.execute("SELECT imagen FROM categoria WHERE id = %s", (id_categoria,))
    filename = cursor.fetchone()
    
    if filename:
        filepath = os.path.join(os.path.dirname(__file__), 'static', 'uploads', filename[0])
        try:
            os.remove(filepath)
        except FileNotFoundError:
            print("No se encontró el archivo")

    cursor.execute("DELETE FROM categoria WHERE id = %s", (id_categoria,))
    conn.commit()

    cursor.close()
    conn.close()
    return True


# Area de Login
def iniciar_sesion(usuario, contraseña):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT contraseña FROM usuario WHERE usuario= %s', (usuario,))
    hash = cursor.fetchone()
    if hash:
        hash, = hash
        if verificarHash(contraseña, hash):
            cursor.execute('SELECT rol FROM usuario WHERE usuario= %s', (usuario,))
            resultado = cursor.fetchone()
            resultado, = resultado
            conn.close()
            return resultado
    else:
        return False

# Funciones de encriptacion
    
def crearHash(contraseña_usuario):
    salt = bcrypt.gensalt()
    contraseña_hash = bcrypt.hashpw(contraseña_usuario.encode('utf-8'), salt)
    return contraseña_hash

def verificarHash(contraseña_usuario, contraseña_hash):
    if bcrypt.checkpw(contraseña_usuario.encode('utf-8'), contraseña_hash):
        return True
    else:
        return False

# Area de Registro

def registrar_cliente(usuario, correo, contraseña, rol):
    conn = crear_conexion()
    cursor = conn.cursor()

    # Verificar si el usuario ya existe
    cursor.execute("SELECT usuario FROM usuario WHERE usuario = %s", (usuario,))
    resultado_usuario = cursor.fetchone()

    # Verificar si el correo ya existe
    cursor.execute("SELECT correo FROM usuario WHERE correo = %s", (correo,))
    resultado_correo = cursor.fetchone()

    if resultado_usuario or resultado_correo:
        conn.close()
        return False
    contraseña_encriptada = crearHash(contraseña)
    cursor.execute(
        'INSERT INTO usuario (usuario, correo, contraseña, rol) VALUES (%s, %s, %s, %s)',
        (usuario, correo, contraseña_encriptada, rol)
    )
    conn.commit()
    conn.close()

    return True

# Area de clientes

def mostrar_clientes():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, correo FROM usuario WHERE rol = 'cliente'")
    clientes = cursor.fetchall()
    usuarios = list()
    for cliente in clientes:
        usuarios.append(Usuario(cliente[0],cliente[1],cliente[2]))
    conn.close()
    return usuarios

def contarClientes():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(id) FROM usuario WHERE rol = 'cliente';")
    resultado = cursor.fetchone()
    clientesLen = resultado[0]
    conn.close()
    return clientesLen

# Area de administradores

def mostrar_admins():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, correo FROM usuario WHERE rol = 'admin'")
    admins = cursor.fetchall()
    usuarios = list()
    for admin in admins:
        usuarios.append(Usuario(admin[0],admin[1],admin[2]))
    conn.close()
    return usuarios

def eliminar_admin(id):
    conn = crear_conexion()
    print(id)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return "Eliminado con exito"
