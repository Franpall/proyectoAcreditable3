import mysql.connector
from mysql.connector import Error
from flaskr.models import Usuario, Producto
import bcrypt

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

"""def agregar_producto(marca, modelo, descripción, imagen, precio, stock, oferta):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO productos (marca, modelo, descripcion, imagen, precio, stock, oferta) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (marca, modelo, descripción, imagen, precio, stock, oferta)
    )
    conn.commit()
    cursor.close()
    conn.close()

agregar_producto("Lenovo", "IdeaPad", "LAPTOP LENOVO 14 CELERON N4020 4GB", "#", 150, 10, 0)"""

def mostrar_productos():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT marca, modelo, imagen, precio FROM producto WHERE recomendado = 0')
    productos = cursor.fetchall()
    productosModel = list()
    for producto in productos:
        productosModel.append(Producto(producto[0], producto[1], producto[2], producto[3]))
    conn.close()
    return productosModel

def mostrar_productos_recomendados():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT marca, modelo, imagen, precio FROM producto WHERE recomendado = 1')
    productos = cursor.fetchall()
    productosModel = list()
    for producto in productos:
        productosModel.append(Producto(producto[0], producto[1], producto[2], producto[3]))
    conn.close()
    return productosModel

"""def mostrar_producto(id_producto):
    conn = sqlite3.connect('flaskr/KibaStore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos WHERE id_producto = ?', (id_producto,))
    producto = cursor.fetchone()
    conn.close()
    return producto

def reducir_stock(id_producto):
    conn = sqlite3.connect('flaskr/KibaStore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT stock FROM productos WHERE id_producto=?', (id_producto,))
    stock = cursor.fetchone()
    if stock[0] > 0:
        cursor.execute('UPDATE productos SET stock = stock - 1 WHERE id_producto = ?', (id_producto,))
        conn.commit()
        conn.close()
        return "Se agregó al Carrito :]"
    else:
        return "Alguien compró antes que tú y se agotó :[ "

"""

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
