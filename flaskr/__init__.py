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
        categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK,
        es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False), es_supervisor=session.get('sesion_supervisor', False))

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
    return render_template('producto.html', sesion=session.get('sesion_iniciada', False), producto = producto, notificacion=notificacion, actionOK=actionOK, actionError=actionError,
        es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False), es_supervisor=session.get('sesion_supervisor', False))

@app.route('/<string:categoria>')
def verProductosCategoria(categoria):
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    
    id_categoria = obtener_id_categoria(categoria)
    
    if id_categoria is None:  # Si la categoría no existe
        return render_template('error.html', error="404")
    
    categoriaSeleccionada = obtener_categoria_especifica(id_categoria)
    
    return render_template('categoria.html', productos=mostrar_productos_categoria(id_categoria), sesion=session.get('sesion_iniciada', False), notificacion=notificacion, actionError=actionError, actionOK=actionOK, categoria = categoriaSeleccionada,
        es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False), es_supervisor=session.get('sesion_supervisor', False))

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

@app.route('/miCuenta')
def verMiCuenta():
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    id_usuario = id_usuario=session.get('id_usuario', False)
    usuario = obtener_cuenta_por_id(id_usuario)
    return render_template('miCuenta.html', sesion=session.get('sesion_iniciada', False), usuario = usuario, notificacion=notificacion, actionError=actionError, actionOK=actionOK)

@app.route('/exportarCompraPDF', methods=['POST'])
def exportarCompraPDF():
    if request.method == 'POST':
        usuario = obtener_cuenta_por_id(session.get('id_usuario'))
        id_compra = request.form.get('id_compra')
        detallesCompra = obtenerDetallesVenta(id_compra)
        total = obtenerTotal(id_compra)
        metodo_pago = obtener_metodo_pago(id_compra)
        fecha_compra = obtener_fecha_compra(id_compra)
        
        # Renderizar la plantilla HTML con los datos de ventas
        rendered = render_template('comprobanteDeCompra.html', detallesCompra=detallesCompra, total=total, metodo_pago=metodo_pago, id_compra=id_compra, fecha_compra=fecha_compra, usuario=usuario)
        
        # Crear el objeto PDF
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(rendered, dest=pdf_file)

        # Verificar si hubo errores en la generación del PDF
        if pisa_status.err:
            return redirect(url_for('verMisCompras', actionError=True, notificacion="Error al generar el PDF"))

        pdf_file.seek(0)
        
        # Devolver el PDF como respuesta
        return send_file(pdf_file, download_name=f'COMPROBANTE_COMPRA_{id_compra}.pdf', as_attachment=True)
    return redirect(url_for('verMisCompras'))

# Rutas para administradores

@app.route('/dashboard')
def adminDashboard():
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    
    admin = mostrar_admin_por_id(session.get('id_usuario', False))
    clientes = contarClientes()
    productos_disponibles = contarProductosDisponibles()
    categorias_disponibles = contarCategoriasDisponibles()
    ventas_totales = contarVentasTotales()
    ingresos_totales = sumarVentasTotales()
    
    if session.get('sesion_jefe', False) or session.get('sesion_admin', False) or session.get('sesion_supervisor', False):
        return render_template('admin/dashboard.html', clientes=clientes, admin=admin, productos_disponibles=productos_disponibles, categorias_disponibles=categorias_disponibles, 
            notificacion=notificacion, actionError=actionError, actionOK=actionOK, ventas_totales=ventas_totales, ingresos_totales=ingresos_totales,
            es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False), es_supervisor=session.get('sesion_supervisor', False))
    else:
        return render_template('error.html', error="401")

@app.route('/productos')
def adminProductos():
    admin = mostrar_admin_por_id(session.get('id_usuario', False))
    categorias = verCategorias()
    productos = mostrar_productos_admin()
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    
    if session.get('sesion_jefe', False) or session.get('sesion_admin', False) or session.get('sesion_supervisor', False):
        return render_template('admin/productos.html', admin=admin, productos=productos, categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK,
            es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False), es_supervisor=session.get('sesion_supervisor', False))
    else:
        return render_template('error.html', error="401")

@app.route('/clientes')
def adminClientes():
    admin = mostrar_admin_por_id(session.get('id_usuario', False))
    mostrar_inactivos = request.args.get('mostrar_inactivos', 'false') == 'true'
    usuarios = mostrar_clientes(solo_activos=not mostrar_inactivos)
    
    if session.get('sesion_jefe', False) or session.get('sesion_admin', False) or session.get('sesion_supervisor', False):
        return render_template('admin/clientes.html', admin=admin, clientes=usuarios, mostrar_inactivos=mostrar_inactivos,
        es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False), es_supervisor=session.get('sesion_supervisor', False))
    else:
        return render_template('error.html', error="401")

@app.route('/admins')
def adminAdmins():
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    
    admin = mostrar_admin_por_id(session.get('id_usuario', False))
    usuarios = mostrar_admins()
    
    if session.get('sesion_jefe', False):
        return render_template('admin/admins.html', admin=admin, admins=usuarios, notificacion=notificacion, actionError=actionError, actionOK=actionOK, es_jefe=session.get('sesion_jefe', False))
    else:
        return render_template('error.html', error="401")

@app.route('/supervisores')
def adminSupervisores():
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    
    admin = mostrar_admin_por_id(session.get('id_usuario', False))
    usuarios = mostrar_supervisores()
    
    if session.get('sesion_jefe', False) or session.get('sesion_admin', False):
        return render_template('admin/supervisores.html', admin=admin, supervisores=usuarios, notificacion=notificacion, actionError=actionError, actionOK=actionOK,
            es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False))
    else:
        return render_template('error.html', error="401")

@app.route('/ventas')
def adminVentas():
    admin = mostrar_admin_por_id(session.get('id_usuario', False))
    
    if session.get('sesion_jefe', False) or session.get('sesion_admin', False) or session.get('sesion_supervisor', False):
        ventas = obtener_ventas()
        return render_template('admin/ventas.html', admin=admin, ventas=ventas,
            es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False), es_supervisor=session.get('sesion_supervisor', False))
    else:
        return render_template('error.html', error="401")

@app.route('/exportarVentasPDF', methods=['GET', 'POST'])
def exportarVentasPDF():
    if request.method == 'POST':
        fechaInicio = request.form['desdeInput']
        fechaFin = request.form['hastaInput']
        metodoDePago = request.form['metodoPagoFilter']

        ventas, ventasTotal = obtenerVentasPDFfecha(fechaInicio, fechaFin, metodoDePago)

        rendered = render_template('admin/reporteVentasPDF.html', ventas=ventas, ventasTotal=ventasTotal, desde=fechaInicio, hasta=fechaFin, metodoDePago=metodoDePago)

        # Crear el objeto PDF
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(rendered, dest=pdf_file)

        # Verificar si hubo errores en la generación del PDF
        if pisa_status.err:
            return "Error al generar el PDF"

        pdf_file.seek(0)

        # Devolver el PDF como respuesta
        return send_file(pdf_file, download_name='REPORTE DE VENTAS.pdf', as_attachment=True)
    return render_template('admin/reporteVentasPDF.html')

@app.route('/exportarUsuariosQueCompraronPDF', methods=['GET', 'POST'])
def exportarUsuariosQueCompraronPDF():
    if request.method == 'POST':
        fechaInicio = request.form['desdeInput']
        fechaFin = request.form['hastaInput']

        usuarios = obtenerUsuariosQueCompraronPDFfecha(fechaInicio, fechaFin, "Todos")

        rendered = render_template('admin/reporteUsuariosQueCompraronPDF.html', usuarios=usuarios, desde=fechaInicio, hasta=fechaFin)

        # Crear el objeto PDF
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(rendered, dest=pdf_file)

        # Verificar si hubo errores en la generación del PDF
        if pisa_status.err:
            return "Error al generar el PDF"

        pdf_file.seek(0)

        # Devolver el PDF como respuesta
        return send_file(pdf_file, download_name='REPORTE DE USUARIOS.pdf', as_attachment=True)
    return render_template('admin/reporteVentasPDF.html')

@app.route('/exportarProductosPDF', methods=['GET', 'POST'])
def exportarProductosPDF():
    if request.method == 'POST':
        fechaInicio = request.form['desdeInput']
        fechaFin = request.form['hastaInput']
        nombre_categoria = request.form['categoriaFilter']

        productos = exportarProductosPDFfecha(fechaInicio, fechaFin, nombre_categoria)

        rendered = render_template('admin/reporteProductosPDF.html', productos=productos, desde=fechaInicio, hasta=fechaFin, nombre_categoria=nombre_categoria)

        # Crear el objeto PDF
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(rendered, dest=pdf_file)

        # Verificar si hubo errores en la generación del PDF
        if pisa_status.err:
            return "Error al generar el PDF"

        pdf_file.seek(0)

        # Devolver el PDF como respuesta
        return send_file(pdf_file, download_name='REPORTE DE PRODUCTOS.pdf', as_attachment=True)
    return render_template('admin/reporteProductosPDF.html')

@app.route('/exportarEstadisticasPDF', methods=['POST'])
def exportarEstadisticasPDF():
    if session.get('sesion_jefe', False) or session.get('sesion_admin', False) or session.get('sesion_supervisor', False):
        clientes = contarClientes()
        productos_disponibles = contarProductosDisponibles()
        categorias_disponibles = contarCategoriasDisponibles()
        ventas_totales = contarVentasTotales()
        ingresos_totales = sumarVentasTotales()

        rendered = render_template('admin/reporteEstadisticasPDF.html', clientes=clientes, productos_disponibles=productos_disponibles,
            categorias_disponibles=categorias_disponibles, ventas_totales=ventas_totales, ingresos_totales=ingresos_totales)

        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(rendered, dest=pdf_file)

        if pisa_status.err:
            return redirect(url_for('adminDashboard', actionError=True, notificacion="Error al generar el PDF"))

        pdf_file.seek(0)
        
        # Devolver el PDF como respuesta
        return send_file(pdf_file, download_name='REPORTE DE ESTADISTICAS.pdf', as_attachment=True)
    return render_template('admin/dashboard.html')

@app.route('/detallesVenta/<int:id>')
def verDetallesVenta(id):
    if session.get('sesion_jefe', False) or session.get('sesion_admin', False) or session.get('sesion_supervisor', False):
        detallesVenta = obtenerDetallesVenta(id)
        total = obtenerTotal(id)
        admin = mostrar_admin_por_id(session.get('id_usuario', False))
        return render_template('admin/verDetallesVenta.html', detallesVenta=detallesVenta, total=total, admin=admin,
            es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False), es_supervisor=session.get('sesion_supervisor', False))
    else:
        return render_template('error.html', error="401")

# <-- Area de categorias -->

# Agregar categorias
@app.route('/categorias', methods=['GET', 'POST'])
def adminCategorias():
    admin = mostrar_admin_por_id(session.get('id_usuario', False))
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
            return redirect(url_for('adminCategorias', actionOK=True, notificacion="Categoría registrada con éxito"))
    
    categorias = obtener_categorias()
    
    if session.get('sesion_jefe', False) or session.get('sesion_admin', False) or session.get('sesion_supervisor', False):
        return render_template('admin/categorias.html', admin=admin, categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK,
            es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False), es_supervisor=session.get('sesion_supervisor', False))
    else:
        return render_template('error.html', error="401")

# Editar categorias
@app.route('/editarCategoria/<int:id_categoria>')
def editarCategoriaView(id_categoria):
    admin = mostrar_admin_por_id(session.get('id_usuario', False))
    categoria = obtener_categoria_especifica(id_categoria)
    return render_template('admin/editarCategoria.html', admin=admin, categoria=categoria, es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False))

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
        return redirect(url_for('adminCategorias', actionOK=True, notificacion="Categoría actualizada con éxito"))

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

    return redirect(url_for('adminCategorias', actionOK=True, notificacion="Se eliminó la Categoría"))


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
            return redirect(url_for('adminProductos', actionOK=True, notificacion="Producto registrado con éxito"))
        
    return render_template('admin/productos.html', notificacion=notificacion, actionError=actionError, actionOK=actionOK, es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False))

# Editar productos
@app.route('/editarProducto/<int:id_producto>')
def editarProductoView(id_producto):
    admin = mostrar_admin_por_id(session.get('id_usuario', False))
    producto = obtener_producto_por_id(id_producto)
    categorias = obtener_categorias()
    return render_template('admin/editarProducto.html', admin=admin, producto=producto, categorias=categorias, es_jefe=session.get('sesion_jefe', False), es_admin=session.get('sesion_admin', False))

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
        return redirect(url_for('adminProductos', actionOK=True, notificacion="Producto actualizado con éxito"))

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

    return redirect(url_for('adminProductos', actionOK=True, notificacion="Se eliminó el Producto"))


# <-- Área de Carrito -->

def manejar_carrito():
    # Obtén el ID del producto y la cantidad desde el formulario
    if request.method == 'POST':
        producto_id = request.form.get('producto_id')
        cantidad = request.form.get('cantidad')
        next_url = request.form.get('next', 'index')  # Si no hay "next", redirige a 'index'

    if session.get('sesion_iniciada', False):
        if obtener_producto_por_id(producto_id).stock < int(cantidad):
            return redirect(f"{next_url}?actionError=True&notificacion=No contamos con stock disponible")
        
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
        if session.get('sesion_jefe', False) or session.get('sesion_admin', False) or session.get('sesion_supervisor', False):
            return redirect(f"{next_url}?actionError=True&notificacion=La parte administrativa no puede realizar compras")
        else:
            return redirect(url_for('iniciarSesion', actionError=True, notificacion="Inicia sesión para realizar compras"))

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

# Actualizar cantidad de productos agregados al carrito
@app.route('/actualizarCantidad/<int:index>', methods=['POST'])
def actualizarCantidad(index):
    if 'carrito' in session:
        nueva_cantidad = int(request.form['cantidad'])
        if 0 <= index < len(session['carrito']):
            # Actualizar la cantidad en el carrito
            session['carrito'][index]['cantidad'] = nueva_cantidad
            session.modified = True
            
            return redirect(url_for('verCarrito', actionOK=True, notificacion="Carrito actualizado correctamente"))
    return redirect(url_for('verCarrito', actionError=True, notificacion="Error al actualizar el carrito"))


# <-- Área de registros y cuentas -->

# Lógica para el registro de administradores y supervisores
@app.route('/addAdmin', methods=('GET', 'POST'))
def registerAdmin():
    if request.method == 'POST':
        usuario = request.form['admin_name']
        correo = request.form['admin_email']
        contraseña = request.form['password']

        if not registrar_cliente(usuario, correo, contraseña, 3):
            return redirect(url_for('adminAdmins', actionError=True, notificacion="El Usuario o Correo ya está registrado"))
        else:
            return redirect(url_for('adminAdmins', actionOK=True, notificacion="Administrador registrado con éxito"))

@app.route('/addSupervisor', methods=('GET', 'POST'))
def registerSupervisor():
    if request.method == 'POST':
        usuario = request.form['admin_name']
        correo = request.form['admin_email']
        contraseña = request.form['password']

        if not registrar_cliente(usuario, correo, contraseña, 4):
            return redirect(url_for('adminSupervisores', actionError=True, notificacion="El Usuario o Correo ya está registrado"))
        else:
            return redirect(url_for('adminSupervisores', actionOK=True, notificacion="Supervisor registrado con éxito"))

# Lógica para el registro de clientes
@app.route('/registerSolicitud', methods=('GET', 'POST'))
def registerSolicitud():
    if request.method == 'POST':
        usuario = request.form['username']
        correo = request.form['email']
        contraseña = request.form['password']
        confirmar_contraseña = request.form['confirm-password']

        if contraseña != confirmar_contraseña:
            return render_template('auth/register.html', actionError=True, notificacion="La Contraseña repetida no coincide")
        
        resultado = registrar_cliente(usuario, correo, contraseña, 1)
        
        if resultado:
            return redirect(url_for('iniciarSesion', actionOK=True, notificacion="Cuenta creada con éxito, ahora inicia sesión"))
        else:
            return render_template('auth/register.html', actionError=True, notificacion="El Usuario o Correo ya está registrado")

# Lógica para editar Administradores

@app.route('/editarUsuario/<int:id_admin>')
def editarAdminView(id_admin):
    admin = mostrar_admin_por_id(id_admin)
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    return render_template('admin/editarAdmin.html', admin=admin, sesion=session.get('sesion_admin', False), notificacion=notificacion, actionError=actionError, actionOK=actionOK)

@app.route('/actualizarDatosUsuarios/<int:id_admin>', methods=['GET', 'POST'])
def editarAdminDataSend(id_admin):
    if request.method == 'POST':
        nombre = request.form['admin_name']
        correo = request.form['admin_email']
        actualizar_datos_admin(id_admin, nombre, correo)
        return redirect(url_for('editarAdminView', id_admin=id_admin, actionOK=True, notificacion="Usuario actualizado con éxito"))
    
@app.route('/actualizarDatosUsuariosCliente/<int:id_cliente>', methods=['GET', 'POST'])
def editarClienteDataSend(id_cliente):
    if request.method == 'POST':
        nombre = request.form['admin_name']
        correo = request.form['admin_email']
        actualizar_datos_admin(id_cliente, nombre, correo)
        return redirect(url_for('verMiCuenta', actionOK=True, notificacion="Usuario actualizado con éxito"))
    
@app.route('/actualizarPassUsuario/<int:id_admin>', methods=['GET', 'POST'])
def editarContraseñaAdmin(id_admin):
    if request.method == 'POST':
        admin = mostrar_admin_por_id(id_admin)
        usuario = admin.nombre
        contraseñaActual = request.form['password']
        contraseñaNueva = request.form['passwordNew']
        if iniciar_sesion(usuario, contraseñaActual):
            if actualizar_contraseña(id_admin, contraseñaNueva):
                return redirect(url_for('editarAdminView', id_admin=id_admin, actionOK=True, notificacion="Contraseña actualizada con éxito"))
            else:
                return redirect(url_for('editarAdminView', id_admin=id_admin, actionError=True, notificacion="Error, no se pudo cambiar la contraseña"))
        return redirect(url_for('editarAdminView', id_admin=id_admin, actionError=True, notificacion="Error, la contraseña actual es incorrecta"))
    

@app.route('/actualizarPassUsuarioCliente/<int:id_cliente>', methods=['GET', 'POST'])
def editarContraseñaCliente(id_cliente):
    if request.method == 'POST':
        cliente = mostrar_admin_por_id(id_cliente)
        usuario = cliente.nombre
        contraseñaActual = request.form['password']
        contraseñaNueva = request.form['passwordNew']
        if iniciar_sesion(usuario, contraseñaActual):
            if actualizar_contraseña(id_cliente, contraseñaNueva):
                return redirect(url_for('verMiCuenta', actionOK=True, notificacion="Contraseña actualizada con éxito"))
            else:
                return redirect(url_for('verMiCuenta', actionError=True, notificacion="Error, no se pudo cambiar la contraseña"))
        return redirect(url_for('verMiCuenta', actionError=True, notificacion="Error, la contraseña actual es incorrecta"))

# Lógica para eliminar Administradores, Clientes y supervisores

@app.route("/deactivateCliente/<int:id_cliente>")
def desactivarCliente(id_cliente):
    desactivar_cliente(id_cliente)
    return redirect(url_for('adminClientes', actionOK=True, notificacion="Cliente desactivado con éxito"))

@app.route("/darDeBaja/<int:id_cliente>")
def desactivarMiCuenta(id_cliente):
    desactivar_cliente(id_cliente)
    return redirect(url_for('cerrarSesionSolicitud'))

@app.route("/reactivateCliente/<int:id_cliente>")
def reactivarCliente(id_cliente):
    reactivar_cliente(id_cliente)
    return redirect(url_for('adminClientes', actionOK=True, notificacion="Cliente reactivado con éxito"))

@app.route("/delete/<int:id_admin>")
def eliminarAdmin(id_admin):
    eliminar_admin(id_admin)
    return redirect(url_for('adminAdmins', actionOK=True, notificacion="Administrador eliminado con éxito"))

@app.route("/deleteSupervisor/<int:id_supervisor>")
def eliminarSupervisor(id_supervisor):
    eliminar_supervisor(id_supervisor)
    return redirect(url_for('adminSupervisores', actionOK=True, notificacion="Supervisor eliminado con éxito"))

# Lógica para iniciar sesión
@app.route('/loginSolicitud', methods=('GET', 'POST'))
def loginSolicitud():
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    
    if request.method == 'POST':
        usuario = request.form['username']
        contraseña = request.form['password']
        
        resultado = iniciar_sesion(usuario, contraseña)
        if resultado:
            rol, id_usuario = resultado
            print(f"¡Login exitoso! Rol: {rol}, ID: {id_usuario}\n")
            if rol == "cliente":
                session['sesion_iniciada'] = True
                session['id_usuario'] = id_usuario
                return redirect(url_for('index', actionOK=True, notificacion="Sesión iniciada con éxito!"))
            elif rol == "jefe":
                session['sesion_jefe'] = True
                session['id_usuario'] = id_usuario
                return redirect(url_for('adminDashboard', actionOK=True, notificacion="Sesión iniciada con éxito!"))
            elif rol == "admin":
                session['sesion_admin'] = True
                session['id_usuario'] = id_usuario
                return redirect(url_for('adminDashboard', actionOK=True, notificacion="Sesión iniciada con éxito!"))
            elif rol == "supervisor":
                session['sesion_supervisor'] = True
                session['id_usuario'] = id_usuario
                return redirect(url_for('adminDashboard', actionOK=True, notificacion="Sesión iniciada con éxito!"))
        return render_template('auth/login.html', actionError=True, notificacion="Usuario o Contraseña incorrectos")
    
    return render_template('auth/login.html', notificacion=notificacion, actionError=actionError, actionOK=actionOK)

# Lógica para cerrar sesiones
@app.route('/bye', methods=('GET', 'POST'))
def cerrarSesionSolicitud():
    session['sesion_iniciada'] = False
    session['sesion_jefe'] = False
    session['sesion_admin'] = False
    session['sesion_supervisor'] = False
    session.modified = True
    return render_template('auth/login.html', actionOK=True, notificacion="Sesión cerrada con éxito")

# Realizar Compras
@app.route('/realizarCompra', methods=['POST'])
def realizarCompra():
    if not session.get('sesion_iniciada', False):
        return redirect(url_for('iniciarSesion', actionError=True, notificacion="Inicia sesión para realizar la compra"))

    metodo_pago = request.form['metodo_pago']
    carrito = session.get('carrito', [])
    total = sumarElementos(obtenerElementosCarrito(carrito))
    id_usuario = session.get('id_usuario')  # Obtener el id_usuario de la sesión

    if not carrito:
        return redirect(url_for('verCarrito', actionError=True, notificacion="El Carrito está vacío"))

    # Guardar la venta en la base de datos
    if guardar_venta(id_usuario, carrito, total, metodo_pago):
        session['carrito'] = []  # Vaciar el carrito después de la compra
        return redirect(url_for('verCarrito', actionOK=True, notificacion="Compra realizada con éxito"))
    else:
        return redirect(url_for('verCarrito', actionError=True, notificacion="Error al realizar la compra: Stock insuficiente"))
