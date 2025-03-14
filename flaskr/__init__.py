from flask import Flask, render_template, redirect, url_for, request
from flaskr.dbConexion import *
import os
from flaskr.models import Producto

app = Flask(__name__)
sesion = False

# Creación de carpeta para subir las imagenes

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

# Crear carpeta uploads si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    categorias = obtener_categorias()

    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)

    return render_template('index.html', productos=mostrar_productos(), productos_recomendados=mostrar_productos_recomendados(), sesion=sesion, 
        categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK
    )

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
    return render_template('carrito.html', sesion=sesion)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.ico') # Evitar llamar un icono en vez del id_categoria

@app.route('/verProducto/<int:id>')
def verProducto(id):
    producto = obtener_producto_por_id(id)
    return render_template('producto.html', sesion=sesion, producto = producto)

@app.route('/<string:categoria>')
def verProductosCategoria(categoria):
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    
    print(f"Categoría solicitada: {categoria}")  # Depuración
    
    id_categoria = obtener_id_categoria(categoria)
    
    if id_categoria is None:  # Si la categoría no existe
        return redirect(url_for('index', actionError=True, notificacion="Categoría no encontrada"))
    categoriaSeleccionada = obtener_categoria_especifica(id_categoria)
    
    return render_template('categoria.html', productos=mostrar_productos_categoria(id_categoria), sesion=sesion, notificacion=notificacion, actionError=actionError, actionOK=actionOK, categoria = categoriaSeleccionada
        )

# Rutas para administradores

@app.route('/dashboard')
def adminDashboard():
    clientes = contarClientes()
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    return render_template('admin/dashboard.html', clientes=clientes, notificacion=notificacion, actionError=actionError, actionOK=actionOK)

@app.route('/productos')
def adminProductos():
    categorias = verCategorias()
    productos = mostrar_productos_admin()
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    return render_template('admin/productos.html', productos=productos, categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK)

@app.route('/clientes')
def adminClientes():
    usuarios = mostrar_clientes()
    return render_template('admin/clientes.html', clientes=usuarios)

@app.route('/admins')
def adminAdmins():
    usuarios = mostrar_admins()
    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)
    return render_template('admin/admins.html', admins=usuarios, notificacion=notificacion, actionError=actionError, actionOK=actionOK)

@app.route('/ventas')
def adminVentas():
    return render_template('admin/ventas.html')

@app.route('/editar-producto')
def adminUpdateUI():
    return render_template('admin/editarProducto.html')

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
    
    return render_template('admin/categorias.html', categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK)

# Editar categorias
@app.route('/editarCategoria/<int:id_categoria>')
def editarCategoriaView(id_categoria):
    categoria = obtener_categoria_especifica(id_categoria)
    return render_template('admin/editarCategoria.html', categoria=categoria)

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
        else:
            filename = obtener_id_categoria(id_categoria)
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
                
    print(productos)  # Verifica qué se está devolviendo
    for producto in productos:
        print(vars(producto))  # Imprime los atributos del objeto
    
    eliminar_categoria(id_categoria)

    return redirect(url_for('adminCategorias', actionOK=True, notificacion="Se Eliminó la Categoría"))


# <-- Area de productos -->

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
        
    return render_template('admin/productos.html', notificacion=notificacion, actionError=actionError, actionOK=actionOK)

# Editar productos
@app.route('/editarProducto/<int:id_producto>')
def editarProductoView(id_producto):
    producto = obtener_producto_por_id(id_producto)
    categorias = obtener_categorias()
    return render_template('admin/editarProducto.html', producto=producto, categorias=categorias)

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
            print(recomendado)
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
        else:
            filename = obtener_producto_por_id(id_producto).imagen
        actualizar_producto(id_producto, marca, modelo, descripcion, id_categoria, filename, precio, stock, recomendado)
        return redirect(url_for('adminProductos', actionOK=True, notificacion="Producto Actualizado con Éxito"))

# Eliminar Productos
@app.route('/delete_producto/<int:id_producto>')
def eliminarProducto(id_producto):
    
    producto = obtener_producto_por_id(id_producto)
    
    if producto and producto.imagen:
        try:
            filepath = os.remove(os.path.join(app.config['UPLOAD_FOLDER'], producto.imagen))
            os.remove(filepath)
        except FileNotFoundError:
            print("Imagen de producto no encontrada")
    
    eliminar_producto(id_producto)

    return redirect(url_for('adminProductos', actionOK=True, notificacion="Se Eliminó el Producto"))


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

# Lógica para iniciar sesión
@app.route('/loginSolicitud', methods=('GET', 'POST'))
def loginSolicitud():
    global sesion
    if request.method == 'POST':
        usuario = request.form['username']
        contraseña = request.form['password']

        resultado = iniciar_sesion(usuario, contraseña)
        if resultado == "cliente":
            sesion = True
            return redirect(url_for('index', actionOK=True, notificacion="Sesión Iniciada con Exito!"))
        elif resultado == "admin":
            return redirect(url_for('adminDashboard', actionOK=True, notificacion="Sesión Iniciada con Exito!"))
        else:
            return render_template('auth/login.html', actionError=True, notificacion="Usuario o Contraseña Incorrectos")
    return render_template('auth/login.html')

# Lógica para el registro de administradores

@app.route('/addAdmin', methods=('GET', 'POST'))
def registerAdmin():
    if request.method == 'POST':
        usuario = request.form['admin_name']
        correo = request.form['admin_email']
        contraseña = request.form['password']

        registrar_cliente(usuario, correo, contraseña, 2)
        return redirect(url_for('adminAdmins', actionOK=True, notificacion="Administrador Registrado con Éxito"))
    
# Lógica para cerrar sesiones
@app.route('/bye', methods=('GET', 'POST'))
def cerrarSesionSolicitud():
    global sesion
    sesion = False
    return render_template('auth/login.html', actionOK=True, notificacion="Sesión Cerrada con Éxito")
    
# Lógica para eliminar Administradores
@app.route("/delete/<int:id_admin>")
def eliminarAdmin(id_admin):
    eliminar_admin(id_admin)
    return redirect(url_for('adminAdmins', actionOK=True, notificacion="Administrador Eliminado con Éxito"))

