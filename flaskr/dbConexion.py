import mysql.connector
from mysql.connector import Error as MySQLError
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
    except MySQLError as e:
        print(f"Error al conectarse a la base de datos: {e}")
        raise MySQLError("No se pudo conectar a la base de datos")
    

# <-- Area de categorias -->

def verCategorias():
    try:
        conexion = crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM categoria")
        categorias = cursor.fetchall()
        categoriasSTR = list()
        for categoria in categorias:
            categoriasSTR.append(categoria[0])
        conexion.close()
        return categoriasSTR
    except MySQLError as e:
        print(f"Error en verCategorias: {e}")
        raise

def obtener_id_categoria(nombre_categoria):
    try:
        conexion = crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM categoria WHERE nombre = %s", (nombre_categoria,))
        id_categoria = cursor.fetchone()
        conexion.close()
        return id_categoria[0] if id_categoria else None
    except MySQLError as e:
        print(f"Error en obtener_id_categoria: {e}")
        raise

# Area de crear Categorias
def obtener_categorias():
    try:
        conn = crear_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categoria")
        categorias = cursor.fetchall()
        cursor.close()
        conn.close()
        return categorias
    except MySQLError as e:
        print(f"Error en obtener_categorias: {e}")
        raise

# Area de crear Categorias
def obtener_categoria_especifica(id):
    try:
        conn = crear_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, imagen FROM categoria WHERE id = %s", (id,))
        categoria = cursor.fetchone()
        cursor.close()
        conn.close()
        return categoria
    except MySQLError as e:
        print(f"Error en obtener_categoria_especifica: {e}")
        raise

def agregar_categoria(nombre, imagen):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categoria (nombre, imagen) VALUES (%s, %s)", (nombre, imagen))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except MySQLError as e:
        print(f"Error en agregar_categoria: {e}")
        raise

def actualizar_categoria(id_categoria, nombre, imagen):
    try:
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
    except MySQLError as e:
        print(f"Error en actualizar_categoria: {e}")
        raise

def eliminar_categoria(id_categoria):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categoria WHERE id = %s", (id_categoria,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except MySQLError as e:
        print(f"Error en eliminar_categoria: {e}")
        raise

def contarCategoriasDisponibles():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id) FROM categoria;")
        resultado = cursor.fetchone()
        productosLen = resultado[0]
        conn.close()
        return productosLen
    except MySQLError as e:
        print(f"Error en contarCategoriasDisponibles: {e}")
        raise


# <-- Area de productos -->

# Area de productos Admin
def agregar_producto(marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO producto (marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado, fecha_añadido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE())',
            (marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except MySQLError as e:
        print(f"Error en agregar_producto: {e}")
        raise

def mostrar_productos_admin():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT id, marca, modelo, imagen, precio, stock FROM producto')
        productos = cursor.fetchall()
        productosModel = list()
        for producto in productos:
            productosModel.append(Producto(producto[0], producto[1], producto[2], producto[3], producto[4], producto[5]))
        conn.close()
        return productosModel
    except MySQLError as e:
        print(f"Error en mostrar_productos_admin: {e}")
        raise

def obtener_producto_por_id(id_producto):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT id, marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado FROM producto WHERE id = %s', (id_producto,))
        producto = cursor.fetchone()
        conn.close()
        return ProductoEditar(producto[0], producto[1], producto[2], producto[3], producto[4], producto[5], producto[6], producto[7], producto[8])
    except MySQLError as e:
        print(f"Error en obtener_producto_por_id: {e}")
        raise

def actualizar_producto(id_producto, marca, modelo, descripcion, id_categoria, imagen, precio, stock, recomendado):
    try:
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
    except MySQLError as e:
        print(f"Error en actualizar_producto: {e}")
        raise

# Area de productos Index
def mostrar_productos():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT id, marca, modelo, imagen, precio FROM producto')
        productos = cursor.fetchall()
        productosModel = list()
        for producto in productos:
            productosModel.append(ProductoAuxiliar(producto[0], producto[1], producto[2], producto[3], producto[4]))
        conn.close()
        return productosModel
    except MySQLError as e:
        print(f"Error en mostrar_productos: {e}")
        raise

def mostrar_productos_categoria(id_categoria):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT id, marca, modelo, imagen, precio FROM producto WHERE id_categoria = %s', (id_categoria,))
        productos = cursor.fetchall()
        productosModel = list()
        for producto in productos:
            productosModel.append(ProductoAuxiliar(producto[0], producto[1], producto[2], producto[3], producto[4]))
        conn.close()
        return productosModel
    except MySQLError as e:
        print(f"Error en mostrar_productos_categoria: {e}")
        raise

def mostrar_productos_recomendados():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT id, marca, modelo, imagen, precio FROM producto WHERE recomendado = 1')
        productos = cursor.fetchall()
        productosModel = list()
        for producto in productos:
            productosModel.append(ProductoAuxiliar(producto[0], producto[1], producto[2], producto[3], producto[4]))
        conn.close()
        return productosModel
    except MySQLError as e:
        print(f"Error en mostrar_productos_recomendados: {e}")
        raise

# Eliminar Productos
def eliminar_producto(id_producto):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM producto WHERE id = %s", (id_producto,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except MySQLError as e:
        print(f"Error en eliminar_producto: {e}")
        raise

def contarProductosDisponibles():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id) FROM producto WHERE stock > 0;")
        resultado = cursor.fetchone()
        productosLen = resultado[0]
        conn.close()
        return productosLen
    except MySQLError as e:
        print(f"Error en contarProductosDisponibles: {e}")
        raise

# Area de carrito
def obtenerElementosCarrito(carritoSession):
    try:
        elementos = []
        for elemento in carritoSession:
            producto = obtener_producto_por_id(elemento['producto_id'])
            item = ElementoCarrito(elemento['producto_id'], producto.marca, producto.modelo, producto.precio, elemento['cantidad'], producto.stock)
            elementos.append(item)
        return elementos
    except MySQLError as e:
        print(f"Error en obtenerElementosCarrito: {e}")
        raise

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
    try:
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
    except MySQLError as e:
        print(f"Error en iniciar_sesion: {e}")
        raise

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
    try:
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
            (usuario, correo, contraseña_encriptada, rol))
        
        conn.commit()
        conn.close()

        return True
    except MySQLError as e:
        print(f"Error en registrar_cliente: {e}")
        raise

# area de cuentas

def obtener_cuenta_por_id(id_usuario):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT id, usuario, correo FROM usuario WHERE id = %s', (id_usuario,))
        cuenta = cursor.fetchone()
        conn.close()
        return Usuario(cuenta[0], cuenta[1], cuenta[2])
    except MySQLError as e:
        print(f"Error en obtener_producto_por_id: {e}")
        raise

# Area de clientes

def mostrar_clientes():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, correo FROM usuario WHERE rol = 'cliente'")
        clientes = cursor.fetchall()
        usuarios = list()
        for cliente in clientes:
            usuarios.append(Usuario(cliente[0],cliente[1],cliente[2]))
        conn.close()
        return usuarios
    except MySQLError as e:
        print(f"Error en mostrar_clientes: {e}")
        raise

def contarClientes():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id) FROM usuario WHERE rol = 'cliente';")
        resultado = cursor.fetchone()
        clientesLen = resultado[0]
        conn.close()
        return clientesLen
    except MySQLError as e:
        print(f"Error en contarClientes: {e}")
        raise

# Area de administradores

def mostrar_admins():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, correo FROM usuario WHERE rol = 'admin'")
        admins = cursor.fetchall()
        usuarios = list()
        for admin in admins:
            usuarios.append(Usuario(admin[0],admin[1],admin[2]))
        conn.close()
        return usuarios
    except MySQLError as e:
        print(f"Error en mostrar_admins: {e}")
        raise

def eliminar_admin(id):
    try:
        conn = crear_conexion()
        print(id)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return "Eliminado con exito"
    except MySQLError as e:
        print(f"Error en eliminar_admin: {e}")
        raise

def guardar_venta(id_usuario, carrito, total, metodo_pago):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()

        # Agregar la venta en la tabla venta
        cursor.execute('INSERT INTO venta (id_usuario, fecha, hora, total, metodo_de_pago) VALUES (%s, CURDATE(), CURTIME(), %s, %s)',
        (id_usuario, total, metodo_pago))
        
        venta_id = cursor.lastrowid  # Obtener el ID de la venta recién insertada

        # Agregar los productos de la venta en la tabla detalle_venta
        for item in carrito:
            producto = obtener_producto_por_id(item['producto_id'])
            cantidad = item['cantidad']
            
            cursor.execute(
                'INSERT INTO detalle_venta (id_venta, producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)',
                (venta_id, producto.marca + " " + producto.modelo, item['cantidad'], producto.precio))
                
            # Restar el stock del producto
            nuevo_stock = producto.stock - int(cantidad)
            if nuevo_stock < 0:
                return False

            cursor.execute('UPDATE producto SET stock = %s WHERE id = %s',
                (nuevo_stock, item['producto_id']))

        conn.commit()
        conn.close()
            
        return True
    except MySQLError as e:
        print(f"Error en guardar_venta: {e}")
        raise
        
def obtener_ventas():
    try:
        conn = crear_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT venta.id, usuario, fecha, hora, total, metodo_de_pago FROM venta INNER JOIN usuario ON usuario.id = venta.id_usuario')
        ventas = cursor.fetchall()
        conn.close()
        return ventas
    except MySQLError as e:
        print(f"Error en obtener_ventas: {e}")
        raise

def obtenerDetallesVenta(id):
    try:
        conn = crear_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT producto, cantidad, precio_unitario FROM detalle_venta WHERE id_venta = %s;', (id,))
        ventas = cursor.fetchall()
        conn.close()
        print(ventas)
        return ventas
    except MySQLError as e:
        print(f"Error en obtenerDetallesVenta: {e}")
        raise

def obtenerTotal(id):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT total FROM venta WHERE id = %s', (id,))
        total = cursor.fetchone()
        conn.close()
        return total[0]
    except MySQLError as e:
        print(f"Error en obtenerTotal: {e}")
        raise

def contarVentasTotales():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id) FROM venta;")
        resultado = cursor.fetchone()
        ventasLen = resultado[0]
        conn.close()
        return ventasLen
    except MySQLError as e:
        print(f"Error en contarVentasTotales: {e}")
        raise

def sumarVentasTotales():
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total) FROM venta;")
        resultado = cursor.fetchone()
        ventasTotal = resultado[0]
        conn.close()
        if not ventasTotal:
            return 0
        return ventasTotal
    except MySQLError as e:
        print(f"Error en sumarVentasTotales: {e}")
        raise

# Area de ver Compras realizadas

def obtenerComprasRealizadas(id_usuario):
    try:
        conn = crear_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, fecha, hora, total, metodo_de_pago FROM venta WHERE id_usuario = %s ORDER BY fecha DESC, hora DESC", (id_usuario,))
        resultado = cursor.fetchall()
        conn.close()
        return resultado
    except MySQLError as e:
        print(f"Error en obtenerComprasRealizadas: {e}")
        raise

# Area de generar PDF

def obtener_metodo_pago(id_venta):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT metodo_de_pago FROM venta WHERE id = %s', (id_venta,))
        metodo = cursor.fetchone()
        conn.close()
        return metodo[0] if metodo else "No especificado"
    except MySQLError as e:
        print(f"Error en obtener_metodo_pago: {e}")
        raise
    
def obtener_fecha_compra(id_venta):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT fecha FROM venta WHERE id = %s', (id_venta,))
        fecha = cursor.fetchone()
        conn.close()
        return fecha[0] if fecha else "Fecha no disponible"
    except MySQLError as e:
        print(f"Error en obtener_fecha_compra: {e}")
        raise

def obtenerVentasPDFfecha(fecha_inicio, fecha_fin, metodoDePago):
    try:
        conn = crear_conexion()
        cursor = conn.cursor()

        if not fecha_inicio and not fecha_fin and metodoDePago == "Todos":
            cursor.execute(
                "SELECT venta.id, usuario, fecha, hora, total, metodo_de_pago FROM venta INNER JOIN usuario ON usuario.id = venta.id_usuario"
            )
            ventas = cursor.fetchall()
            cursor.execute("SELECT SUM(total) FROM venta")
            resultado = cursor.fetchone()
            ventasTotal = resultado[0] if resultado and resultado[0] else 0
        elif not fecha_inicio and not fecha_fin:
            cursor.execute(
                "SELECT venta.id, usuario, fecha, hora, total, metodo_de_pago FROM venta INNER JOIN usuario ON usuario.id = venta.id_usuario WHERE metodo_de_pago = %s",
                (metodoDePago,),
            )
            ventas = cursor.fetchall()
            cursor.execute("SELECT SUM(total) FROM venta WHERE metodo_de_pago = %s", (metodoDePago,))
            resultado = cursor.fetchone()
            ventasTotal = resultado[0] if resultado and resultado[0] else 0
        elif metodoDePago == "Todos":
            cursor.execute(
                "SELECT venta.id, usuario, fecha, hora, total, metodo_de_pago FROM venta INNER JOIN usuario ON usuario.id = venta.id_usuario WHERE fecha BETWEEN %s AND %s",
                (fecha_inicio, fecha_fin),
            )
            ventas = cursor.fetchall()
            cursor.execute("SELECT SUM(total) FROM venta WHERE fecha BETWEEN %s AND %s", (fecha_inicio, fecha_fin))
            resultado = cursor.fetchone()
            ventasTotal = resultado[0] if resultado and resultado[0] else 0
        else:
            cursor.execute(
                "SELECT venta.id, usuario, fecha, hora, total, metodo_de_pago FROM venta INNER JOIN usuario ON usuario.id = venta.id_usuario WHERE fecha BETWEEN %s AND %s AND metodo_de_pago = %s",
                (fecha_inicio, fecha_fin, metodoDePago),
            )
            ventas = cursor.fetchall()
            cursor.execute(
                "SELECT SUM(total) FROM venta WHERE fecha BETWEEN %s AND %s AND metodo_de_pago = %s",
                (fecha_inicio, fecha_fin, metodoDePago),
            )
            resultado = cursor.fetchone()
            ventasTotal = resultado[0] if resultado and resultado[0] else 0

        conn.close()
        return ventas, ventasTotal

    except MySQLError as e:
        print(f"Error en obtenerVentasPDFfecha: {e}")
        raise