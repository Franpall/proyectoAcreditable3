import mysql.connector
from mysql.connector import Error

def crear_conexion():
    try:
        conn = mysql.connector.connect(
            host='localhost',       
            user='root',     
            password='', 
            database='franpalbd'    
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error al conectarse a la base de datos: {e}")
        return None

def agregar_producto(marca, modelo, descripción, imagen, precio, stock, oferta):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO productos (marca, modelo, descripcion, imagen, precio, stock, oferta) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (marca, modelo, descripción, imagen, precio, stock, oferta)
    )
    conn.commit()
    cursor.close()
    conn.close()

#agregar_producto("Lenovo", "IdeaPad", "LAPTOP LENOVO 14 CELERON N4020 4GB", "#", 150, 10, 0)

def mostrar_productos():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    conn.close()
    return productos

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

# Area de Login
def iniciar_sesionBD(usuario, contraseña):
    conn = sqlite3.connect('flaskr/KibaStore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT rol FROM cuentas WHERE usuario=? AND contraseña=?', (usuario, contraseña))
    resultado = cursor.fetchone()
    if resultado:
        resultado, = resultado
        return resultado

# Area de Registro
def registrar_cliente(usuario, contraseña, rol):
    conn = sqlite3.connect('flaskr/KibaStore.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO cuentas (usuario, contraseña, rol) VALUES (?, ?, ?)',
        (usuario, contraseña, rol)
        #el rol = 1 es cliente y rol = 2 es admin
    )
    conn.commit()
    conn.close()"""