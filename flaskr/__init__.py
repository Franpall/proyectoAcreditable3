from flask import Flask, render_template, redirect, url_for, request, session, send_file
from flaskr.dbConexion import *
import os
from datetime import timedelta
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)

# Aspectos de seguridad y almacenamiento temporal
app.secret_key = "XDV2025"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Creación de carpeta para subir las imagenes
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

# Crear carpeta uploads si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Inicio
@app.route('/')
def index():
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    categorias = obtener_categorias()
    productos = mostrar_productos()
    productos_recomendados = mostrar_productos_recomendados()

    return render_template('index.html', productos=productos, productos_recomendados=productos_recomendados, sesion=session.get('sesion_iniciada', False), 
        categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK, modoAdmin=session.get('sesion_admin', False)
    )

# Manejador de errores global para errores de base de datos
@app.errorhandler(MySQLError)
def handle_database_error(e):
    return render_template('error.html', error="502")

# Capturar error 404 para mostrar html personalizado
@app.errorhandler(404)
def errorURL(e):
    return render_template('error.html', error="404")

@app.route('/login')
def iniciarSesion():
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    return render_template('auth/login.html', notificacion=notificacion, actionError=actionError, actionOK=actionOK)

@app.route('/register')
def registrarse():
    return render_template('auth/register.html')

@app.route('/carrito')
def verCarrito():
    notificacion = request.args.get('notificacion', False)  # Capturar notificación
    actionError = request.args.get('actionError', False)    # Capturar actionError
    actionOK = request.args.get('actionOK', False)
    
    carritoActual = session.get('carrito', False)
    if carritoActual:
        elementos=obtenerElementosCarrito(carritoActual)
        total = sumarElementos(elementos)
        return render_template('carrito.html', sesion=session.get('sesion_iniciada', False), elementos=elementos, total=total, notificacion=notificacion, actionOK=actionOK, actionError=actionError)
    else:
        return render_template('carrito.html', sesion=session.get('sesion_iniciada', False), notificacion=notificacion, actionError=actionError, actionOK=actionOK)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.ico') # Evitar llamar un icono en vez del id_categoria

@app.route('/verProducto/<int:id>')
def verProducto(id):
    notificacion = request.args.get('notificacion', False)
    actionOK = request.args.get('actionOK', False)
    actionError = request.args.get('actionError', False)
    producto = obtener_producto_por_id(id)
    return render_template('producto.html', sesion=session.get('sesion_iniciada', False), producto = producto, notificacion=notificacion, actionOK=actionOK, actionError=actionError, modoAdmin=session.get('sesion_admin', False))

@app.route('/<string:categoria>')
def verProductosCategoria(categoria):
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    
    id_categoria = obtener_id_categoria(categoria)
    
    if id_categoria is None:  # Si la categoría no existe
        return render_template('error.html', error="404")
    
    categoriaSeleccionada = obtener_categoria_especifica(id_categoria)
    
    return render_template('categoria.html', productos=mostrar_productos_categoria(id_categoria), sesion=session.get('sesion_iniciada', False), notificacion=notificacion, actionError=actionError, actionOK=actionOK, categoria = categoriaSeleccionada, modoAdmin=session.get('sesion_admin', False)
        )

@app.route('/misCompras')
def verMisCompras():
    compras = obtenerComprasRealizadas(session.get('id_usuario'))
    return render_template('compras.html', sesion=session.get('sesion_iniciada', False), compras=compras)

@app.route('/detallesCompra/<int:id>')
def verDetallesCompra(id):
    compras = obtenerComprasRealizadas(session.get('id_usuario'))
    detallesCompra = obtenerDetallesVenta(id)
    total = obtenerTotal(id)
    return render_template('compras.html', sesion=session.get('sesion_iniciada', False), detallesCompra=detallesCompra, total=total, compras=compras)

# Rutas para administradores

@app.route('/dashboard')
def adminDashboard():
    clientes = contarClientes()
    productos_disponibles = contarProductosDisponibles()
    categorias_disponibles = contarCategoriasDisponibles()
    ventas_totales = contarVentasTotales()
    ingresos_totales = sumarVentasTotales()
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    if session.get('sesion_admin', False):
        return render_template('admin/dashboard.html', clientes=clientes, productos_disponibles=productos_disponibles, categorias_disponibles=categorias_disponibles, notificacion=notificacion, actionError=actionError, actionOK=actionOK, ventas_totales=ventas_totales, ingresos_totales=ingresos_totales)
    else:
        return render_template('error.html', error="401")

@app.route('/productos')
def adminProductos():
    categorias = verCategorias()
    productos = mostrar_productos_admin()
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    if session.get('sesion_admin', False):
        return render_template('admin/productos.html', productos=productos, categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK, sesion=session.get('sesion_admin', False))
    else:
        return render_template('error.html', error="401")

@app.route('/clientes')
def adminClientes():
    usuarios = mostrar_clientes()
    if session.get('sesion_admin', False):
        return render_template('admin/clientes.html', clientes=usuarios, sesion=session.get('sesion_admin', False))
    else:
        return render_template('error.html', error="401")

@app.route('/admins')
def adminAdmins():
    usuarios = mostrar_admins()
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    if session.get('sesion_admin', False):
        return render_template('admin/admins.html', admins=usuarios, notificacion=notificacion, actionError=actionError, actionOK=actionOK, sesion=session.get('sesion_admin', False))
    else:
        return render_template('error.html', error="401")

@app.route('/ventas')
def adminVentas():
    if session.get('sesion_admin', False):
        ventas = obtener_ventas()
        return render_template('admin/ventas.html', ventas=ventas, sesion=session.get('sesion_admin', False))
    else:
        return render_template('error.html', error="401")

@app.route('/exportarVentasPDF', methods=['GET', 'POST'])
def exportarVentasPDF():
    if request.method == 'POST':
        # Renderizar la plantilla HTML con los datos de ventas
        rendered = render_template('admin/reporteVentasPDF.html', ventas = obtener_ventas(), total_ingresos = sumarVentasTotales())

        # Crear el objeto PDF
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(rendered, dest=pdf_file)

        # Verificar si hubo errores en la generación del PDF
        if pisa_status.err:
            return "Error al generar el PDF"

        pdf_file.seek(0)

        # Devolver el PDF como respuesta
        return send_file(pdf_file, download_name='REPORTE DE VENTAS.pdf', as_attachment=True)
    return render_template('admin/reporteVentasPDF.html', ventas=obtener_ventas(), total_ingresos=sumarVentasTotales())

@app.route('/detallesVenta/<int:id>')
def verDetallesVenta(id):
    if session.get('sesion_admin', False):
        detallesVenta = obtenerDetallesVenta(id)
        total = obtenerTotal(id)
        return render_template('admin/verDetallesVenta.html', sesion=session.get('sesion_admin', False), detallesVenta=detallesVenta, total=total)
    else:
        return render_template('error.html', error="401")

# <-- Area de categorias -->

# Agregar categorias
@app.route('/categorias', methods=['GET', 'POST'])
def adminCategorias():
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)

    if request.method == 'POST':
        nombre = request.form['nombre']
        imagen = request.files['imagen']

        if imagen:
            filename = imagen.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(filepath)
            agregar_categoria(nombre, filename)
            return redirect(url_for('adminCategorias', actionOK=True, notificacion="Categoría Registrada con Éxito"))
    
    categorias = obtener_categorias()
    if session.get('sesion_admin', False):
        return render_template('admin/categorias.html', categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK, sesion=session.get('sesion_admin', False))
    else:
        return render_template('error.html', error="401")

# Editar categorias
@app.route('/editarCategoria/<int:id_categoria>')
def editarCategoriaView(id_categoria):
    categoria = obtener_categoria_especifica(id_categoria)
    return render_template('admin/editarCategoria.html', categoria=categoria, sesion=session.get('sesion_admin', False))

@app.route('/subirActualizacionC/<int:id_categoria>', methods=['GET', 'POST'])
def editarCategoriaSend(id_categoria):
    if request.method == 'POST':
        nombre = request.form['nombre']
        imagen = request.files['imagen']

        categoria_actual = obtener_categoria_especifica(id_categoria)

        filename = categoria_actual['imagen']
        
        if imagen and imagen.filename != '':
            # Eliminar la imagen anterior
            if categoria_actual['imagen']:
                try:
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], categoria_actual['imagen'])
                    os.remove(filepath)
                except FileNotFoundError:
                    print("No se encontró la imagen anterior")
                
            filename = imagen.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(filepath)
        actualizar_categoria(id_categoria, nombre, filename)
        return redirect(url_for('adminCategorias', actionOK=True, notificacion="Categoría Actualizada con Éxito"))

# Eliminar Categorias
@app.route('/delete_categoria/<int:id_categoria>')
def eliminarCategoria(id_categoria):
    
    categoria = obtener_categoria_especifica(id_categoria)
    productos = mostrar_productos_categoria(id_categoria)
    
    # Eliminar imagen de categoria
    if categoria['imagen']:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], categoria['imagen'])
            os.remove(filepath)
        except FileNotFoundError:
            print("Imagen de categoría no encontrada")
    
    # Eliminar imagenes de los productos
    for producto in productos:
        if producto.imagen:
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], producto.imagen)
                os.remove(filepath)
            except FileNotFoundError:
                print(f"Imagen de producto {producto.id} no encontrada")
    
    eliminar_categoria(id_categoria)

    return redirect(url_for('adminCategorias', actionOK=True, notificacion="Se Eliminó la Categoría"))


# <-- Área de productos -->

# Registro de productos
@app.route('/registrarProductos', methods=('GET', 'POST'))
def registrarProductos():
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        imagen = request.files['imagen']
        precio = request.form['precio']
        stock = request.form['stock']
        try:
            recomendado = request.form['recomendado']
        except KeyError:
            recomendado = 0

        if recomendado:
            recomendado = 1

        id_categoria = obtener_id_categoria(categoria)

        if imagen:
            filename = imagen.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(filepath)
            agregar_producto(marca, modelo, descripcion, id_categoria, filename, precio, stock, recomendado)
            return redirect(url_for('adminProductos', actionOK=True, notificacion="Producto Registrado con Éxito"))
        
    return render_template('admin/productos.html', notificacion=notificacion, actionError=actionError, actionOK=actionOK, sesion=session.get('sesion_admin', False))

# Editar productos
@app.route('/editarProducto/<int:id_producto>')
def editarProductoView(id_producto):
    producto = obtener_producto_por_id(id_producto)
    categorias = obtener_categorias()
    return render_template('admin/editarProducto.html', producto=producto, categorias=categorias, sesion=session.get('sesion_admin', False))

@app.route('/subirActualizacion/<int:id_producto>', methods=['GET', 'POST'])
def editarProductoSend(id_producto):
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        stock = request.form['stock']
        precio = request.form['precio']
        categoria = request.form['categoria']
        imagen = request.files['imagen']
        descripcion = request.form['descripcion']
        try:
            recomendado = request.form['recomendado']
        except KeyError:
            recomendado = 0

        if recomendado:
            recomendado = 1

        id_categoria = obtener_id_categoria(categoria)
        producto_actual = obtener_producto_por_id(id_producto)
        filename = producto_actual.imagen
        
        if imagen and imagen.filename != '':
            # Eliminar la imagen anterior
            if producto_actual.imagen:
                try:
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], producto_actual.imagen)
                    os.remove(filepath)
                except FileNotFoundError:
                    print("No se encontró la imagen anterior")
        
        if imagen:
            filename = imagen.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(filepath)
        actualizar_producto(id_producto, marca, modelo, descripcion, id_categoria, filename, precio, stock, recomendado)
        return redirect(url_for('adminProductos', actionOK=True, notificacion="Producto Actualizado con Éxito"))

# Eliminar Productos
@app.route('/delete_producto/<int:id_producto>')
def eliminarProducto(id_producto):
    
    producto = obtener_producto_por_id(id_producto)
    
    if producto and producto.imagen:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], producto.imagen)
            os.remove(filepath)
        except FileNotFoundError:
            print("Imagen de producto no encontrada")
    
    eliminar_producto(id_producto)

    return redirect(url_for('adminProductos', actionOK=True, notificacion="Se Eliminó el Producto"))


# <-- Área de Carrito -->

def manejar_carrito():
    # Obtén el ID del producto y la cantidad desde el formulario
    if request.method == 'POST':
        producto_id = request.form.get('producto_id')
        cantidad = request.form.get('cantidad')
        next_url = request.form.get('next', 'index')  # Si no hay "next", redirige a 'index'

    if obtener_producto_por_id(producto_id).stock < int(cantidad):
        return redirect(f"{next_url}?actionError=True&notificacion=No contamos con stock disponible")

    if session.get('sesion_iniciada', False):
        # Guarda los datos en la sesión para uso temporal
        if 'carrito' not in session:
            session['carrito'] = []
        count = 0
        existente = False
        for i in session['carrito']:
            if i['producto_id'] == producto_id:
                session['carrito'].append({'producto_id': producto_id, 'cantidad': int(i['cantidad']) + int(cantidad)})
                del session['carrito'][count]
                existente = True
                session.modified = True
                break
            count += 1
        if not existente:
            session['carrito'].append({'producto_id': producto_id, 'cantidad': int(cantidad)})
            session.modified = True

        return redirect(f"{next_url}?actionOK=True&notificacion=Producto añadido al carrito")
    else:
        if session.get('sesion_admin', False):
            return redirect(f"{next_url}?actionError=True&notificacion=El admin no puede realizar compras")
        else:
            return redirect(url_for('iniciarSesion', actionError=True, notificacion="Inicia Sesión para usar el Carrito"))

# Ruta para HTML 1 (index)
@app.route('/addItemIndex', methods=['POST'])
def agregarAlCarritoIndex():
    return manejar_carrito()  # Redirige a 'index'

# Ruta para HTML 2 (categoria)
@app.route('/addItemCategoria', methods=['POST'])
def agregarAlCarritoCategoria():
    return manejar_carrito()  # Redirige categoria'

# Ruta para HTML 3 (producto)
@app.route('/addItemProducto', methods=['POST'])
def agregarAlCarritoProducto():
    return manejar_carrito()  # Redirige a 'verProducto'

# Eliminar elementos del carrito
@app.route('/removeItem/<int:index>')
def eliminarDelCarrito(index):
    if 'carrito' in session:
        # Verificar que el índice exista en la lista
        if 0 <= index < len(session['carrito']):
            del session['carrito'][index]
            
            session.modified = True
    return redirect(url_for('verCarrito'))

@app.route('/actualizarCantidad/<int:index>', methods=['POST'])
def actualizarCantidad(index):
    if 'carrito' in session:
        nueva_cantidad = int(request.form['cantidad'])
        if 0 <= index < len(session['carrito']):
            # Actualizar la cantidad en el carrito
            session['carrito'][index]['cantidad'] = nueva_cantidad
            session.modified = True
            return redirect(url_for('verCarrito', actionOK=True, notificacion="Cantidad actualizada correctamente"))
    return redirect(url_for('verCarrito', actionError=True, notificacion="Error al actualizar la cantidad"))


# <-- Área de registros y cuentas -->

# Lógica para el registro de administradores
@app.route('/addAdmin', methods=('GET', 'POST'))
def registerAdmin():
    if request.method == 'POST':
        usuario = request.form['admin_name']
        correo = request.form['admin_email']
        contraseña = request.form['password']

        if not registrar_cliente(usuario, correo, contraseña, 2):
            return redirect(url_for('adminAdmins', actionError=True, notificacion="El Usuario o Correo ya está Registrado"))
        else:
            return redirect(url_for('adminAdmins', actionOK=True, notificacion="Administrador Registrado con Éxito"))


# Lógica para el registro de clientes
@app.route('/registerSolicitud', methods=('GET', 'POST'))
def registerSolicitud():
    if request.method == 'POST':
        usuario = request.form['username']
        correo = request.form['email']
        contraseña = request.form['password']
        confirmar_contraseña = request.form['confirm-password']

        if contraseña != confirmar_contraseña:
            return render_template('auth/register.html', actionError=True, notificacion="La Contraseña Repetida no Coincide")
        
        resultado = registrar_cliente(usuario, correo, contraseña, 1)
        
        if resultado:
            return redirect(url_for('iniciarSesion', actionOK=True, notificacion="Cuenta Creada Con Éxito, ahora Inicia Sesión"))
        else:
            return render_template('auth/register.html', actionError=True, notificacion="El Usuario o Correo ya está Registrado")

# Lógica para eliminar Administradores
@app.route("/delete/<int:id_admin>")
def eliminarAdmin(id_admin):
    eliminar_admin(id_admin)
    return redirect(url_for('adminAdmins', actionOK=True, notificacion="Administrador Eliminado con Éxito"))

# Lógica para iniciar sesión
@app.route('/loginSolicitud', methods=('GET', 'POST'))
def loginSolicitud():
    if request.method == 'POST':
        usuario = request.form['username']
        contraseña = request.form['password']

        resultado = iniciar_sesion(usuario, contraseña)
        if resultado:
            rol, id_usuario = resultado
            if rol == "cliente":
                session['sesion_iniciada'] = True
                session['id_usuario'] = id_usuario  # Guardar el id_usuario en la sesión
                return redirect(url_for('index', actionOK=True, notificacion="Sesión Iniciada con Exito!"))
            elif rol == "admin":
                session['sesion_admin'] = True
                session['id_usuario'] = id_usuario  # Guardar el id_usuario en la sesión
                return redirect(url_for('adminDashboard', actionOK=True, notificacion="Sesión Iniciada con Exito!"))
        else:
            return render_template('auth/login.html', actionError=True, notificacion="Usuario o Contraseña Incorrectos")
    return render_template('auth/login.html')

# Lógica para cerrar sesiones
@app.route('/bye', methods=('GET', 'POST'))
def cerrarSesionSolicitud():
    session['sesion_iniciada'] = False
    session['sesion_admin'] = False
    session.modified = True
    return render_template('auth/login.html', actionOK=True, notificacion="Sesión Cerrada con Éxito")

@app.route('/realizarCompra', methods=['POST'])
def realizarCompra():
    if not session.get('sesion_iniciada', False):
        return redirect(url_for('iniciarSesion', actionError=True, notificacion="Inicia Sesión para realizar la compra"))

    metodo_pago = request.form['metodo_pago']
    carrito = session.get('carrito', [])
    total = sumarElementos(obtenerElementosCarrito(carrito))
    id_usuario = session.get('id_usuario')  # Obtener el id_usuario de la sesión

    if not carrito:
        return redirect(url_for('verCarrito', actionError=True, notificacion="El carrito está vacío"))

    # Guardar la venta en la base de datos
    if guardar_venta(id_usuario, carrito, total, metodo_pago):
        session['carrito'] = []  # Vaciar el carrito después de la compra
        return redirect(url_for('verCarrito', actionOK=True, notificacion="Compra realizada con éxito"))
    else:
        return redirect(url_for('verCarrito', actionError=True, notificacion="Error al realizar la compra: Stock insuficiente"))
