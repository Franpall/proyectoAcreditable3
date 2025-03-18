import mysql.connector
from mysql.connector import Error
from flaskr.models import ElementoCarrito, Producto, ProductoAuxiliar, ProductoEditar, Usuario
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
    

# <-- Area de categorias -->

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
    return id_categoria[0] if id_categoria else None

# Area de crear Categorias
def obtener_categorias():
    conn = crear_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categoria")
    categorias = cursor.fetchall()
    cursor.close()
    conn.close()
    return categorias

# Area de crear Categorias
def obtener_categoria_especifica(id):
    conn = crear_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, imagen FROM categoria WHERE id = %s", (id,))
    categoria = cursor.fetchone()
    cursor.close()
    conn.close()
    return categoria

def agregar_categoria(nombre, imagen):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categoria (nombre, imagen) VALUES (%s, %s)", (nombre, imagen))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def actualizar_categoria(id_categoria, nombre, imagen):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE categoria SET nombre = %s, imagen = %s WHERE id = %s',
        (nombre, imagen, id_categoria)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True

def eliminar_categoria(id_categoria):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categoria WHERE id = %s", (id_categoria,))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def contarCategoriasDisponibles():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(id) FROM categoria;")
    resultado = cursor.fetchone()
    productosLen = resultado[0]
    conn.close()
    return productosLen


# <-- Area de productos -->

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

def obtener_producto_por_id(id_producto):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado FROM producto WHERE id = %s', (id_producto,))
    producto = cursor.fetchone()
    conn.close()
    return ProductoEditar(producto[0], producto[1], producto[2], producto[3], producto[4], producto[5], producto[6], producto[7], producto[8])

def actualizar_producto(id_producto, marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE producto SET marca = %s, modelo = %s, descripcion = %s, id_categoria = %s, imagen = %s, precio = %s, stock = %s, recomendado = %s WHERE id = %s',
        (marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado, id_producto)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True

# Area de productos Index
def mostrar_productos():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, marca, modelo, imagen, precio FROM producto')
    productos = cursor.fetchall()
    productosModel = list()
    for producto in productos:
        productosModel.append(ProductoAuxiliar(producto[0], producto[1], producto[2], producto[3], producto[4]))
    conn.close()
    return productosModel

def mostrar_productos_categoria(id_categoria):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, marca, modelo, imagen, precio FROM producto WHERE id_categoria = %s', (id_categoria,))
    productos = cursor.fetchall()
    productosModel = list()
    for producto in productos:
        productosModel.append(ProductoAuxiliar(producto[0], producto[1], producto[2], producto[3], producto[4]))
    conn.close()
    return productosModel

def mostrar_productos_recomendados():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, marca, modelo, imagen, precio FROM producto WHERE recomendado = 1')
    productos = cursor.fetchall()
    productosModel = list()
    for producto in productos:
        productosModel.append(ProductoAuxiliar(producto[0], producto[1], producto[2], producto[3], producto[4]))
    conn.close()
    return productosModel

# Eliminar Productos
def eliminar_producto(id_producto):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM producto WHERE id = %s", (id_producto,))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def contarProductosDisponibles():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(id) FROM producto WHERE stock > 0;")
    resultado = cursor.fetchone()
    productosLen = resultado[0]
    conn.close()
    return productosLen

# Area de carrito
def obtenerElementosCarrito(carritoSession):
    elementos = []
    for elemento in carritoSession:
        producto = obtener_producto_por_id(elemento['producto_id'])
        item = ElementoCarrito(elemento['producto_id'], producto.marca, producto.modelo, producto.precio, elemento['cantidad'])
        elementos.append(item)
    return elementos

def sumarElementos(elementos):
    total = 0.00
    for elemento in elementos:
        try:
            total += float(elemento.precio) * float(elemento.cantidad)
        except ValueError:
            print("error crítico: tipo de dato incorrecto")
    return total

# Area de Login
def iniciar_sesion(usuario, contraseña):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, contraseña, rol FROM usuario WHERE usuario= %s', (usuario,))
    resultado = cursor.fetchone()
    if resultado:
        id_usuario, hash, rol = resultado
        if verificarHash(contraseña, hash):
            conn.close()
            return rol, id_usuario  # Devuelve el rol y el id_usuario
    conn.close()
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

def guardar_venta(id_usuario, carrito, total, metodo_pago):
    conn = crear_conexion()
    cursor = conn.cursor()
    try:
        # Agregar la venta en la tabla venta
        cursor.execute(
            'INSERT INTO venta (id_usuario, fecha, hora, total, metodo_de_pago) VALUES (%s, CURDATE(), CURTIME(), %s, %s)',
            (id_usuario, total, metodo_pago)
        )
        venta_id = cursor.lastrowid  # Obtener el ID de la venta recién insertada

        # Agregar los productos de la venta en la tabla detalle_venta
        for item in carrito:
            producto = obtener_producto_por_id(item['producto_id'])
            cantidad = item['cantidad']
            
            cursor.execute(
                'INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)',
                (venta_id, item['producto_id'], item['cantidad'], producto.precio)
            )
            
            # Restar el stock del producto
            nuevo_stock = producto.stock - int(cantidad)
            if nuevo_stock < 0:
                raise ValueError("No hay suficiente stock para el producto con ID {}".format(item['producto_id']))

            cursor.execute(
                'UPDATE producto SET stock = %s WHERE id = %s',
                (nuevo_stock, item['producto_id'])
            )

        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()
        
def obtener_ventas():
    conn = crear_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, id_usuario, fecha, hora, total, metodo_de_pago FROM venta')
    ventas = cursor.fetchall()
    conn.close()
    return ventas

def obtenerDetallesVenta(id):
    conn = crear_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT marca, modelo, cantidad, precio_unitario FROM detalle_venta INNER JOIN producto ON producto.id = detalle_venta.id_producto WHERE id_venta = %s;', (id,))
    ventas = cursor.fetchall()
    conn.close()
    print(ventas)
    return ventas