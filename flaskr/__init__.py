from flask import Flask, render_template, redirect, url_for, request
from flaskr.dbConexion import *
import os

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

@app.route('/producto')
def verProducto():
    return render_template('producto.html', sesion=sesion)

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


# Lógica para agregar categorias
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
            return redirect(url_for('adminCategorias', actionOK=True, notificacion="Se Agregó la categoría"))
    
    categorias = obtener_categorias()
    
    return render_template('admin/categorias.html', categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK)

# Eliminar Categorias
@app.route('/delete_categoria/<int:id_categoria>')
def eliminarCategoria(id_categoria):
    eliminar_categoria(id_categoria)

    return redirect(url_for('adminCategorias', actionOK=True, notificacion="Se eliminó la categoría"))


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
    print(producto)

    categorias = obtener_categorias()

    print(categorias)
    return render_template('admin/editarProducto.html', producto=producto, categorias=categorias)

@app.route('/subirActualizacion/<int:id_producto>', methods=['GET', 'POST'])
def editarProductoSend(id_producto):
    producto = obtener_producto_por_id(id_producto)

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        stock = request.form['stock']
        precio = request.form['precio']
        categoria = request.form['categoria']
        descripcion = request.form['descripcion']
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen.filename != '':  # Si hay una nueva imagen
                filename = imagen.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagen.save(filepath)
                producto.imagen = filename  # Actualiza la imagen en el producto

        actualizar_producto(id_producto, marca, modelo, stock, precio, categoria, descripcion, producto.imagen)
        return redirect(url_for('adminProductos', actionOK=True, notificacion="Producto Actualizado con Éxito"))

    categorias = obtener_categorias()
    return render_template('admin/editarProducto.html', producto=producto, categorias=categorias)

# Eliminar Productos
@app.route('/delete_producto/<int:id_producto>')
def eliminarProducto(id_producto):
    eliminar_producto(id_producto)

    return redirect(url_for('adminProductos', actionOK=True, notificacion="Se eliminó el producto"))


# Lógica para el registro de clientes
@app.route('/registerSolicitud', methods=('GET', 'POST'))
def registerSolicitud():
    if request.method == 'POST':
        usuario = request.form['username']
        correo = request.form['email']
        contraseña = request.form['password']
        confirmar_contraseña = request.form['confirm-password']

        if contraseña != confirmar_contraseña:
            return render_template('auth/register.html', actionError=True, notificacion="La contraseña repetida no coincide")
        
        resultado = registrar_cliente(usuario, correo, contraseña, 1)
        
        if resultado:
            return redirect(url_for('iniciarSesion', actionOK=True, notificacion="Cuenta Creada Con Éxito, ahora Inicia Sesión"))
        else:
            return render_template('auth/register.html', actionError=True, notificacion="El usuario o correo ya está registrado")

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
            return render_template('auth/login.html', actionError=True, notificacion="Usuario o contraseña incorrecta")
    return render_template('auth/login.html')

# Lógica para el registro de administradores

@app.route('/addAdmin', methods=('GET', 'POST'))
def registerAdmin():
    if request.method == 'POST':
        usuario = request.form['admin_name']
        correo = request.form['admin_email']
        contraseña = request.form['password']

        registrar_cliente(usuario, correo, contraseña, 2)
        return redirect(url_for('adminAdmins', actionOK=True, notificacion="Administrador registrado con exito"))
    
# Lógica para cerrar sesiones
@app.route('/bye', methods=('GET', 'POST'))
def cerrarSesionSolicitud():
    global sesion
    sesion = False
    return render_template('auth/login.html', actionOK=True, notificacion="Sesion Cerrada con Exito")
    
# Lógica para eliminar Administradores
@app.route("/delete/<int:id_admin>")
def eliminarAdmin(id_admin):
    eliminar_admin(id_admin)
    return redirect(url_for('adminAdmins', actionOK=True, notificacion="Administrador Eliminado con exito"))

