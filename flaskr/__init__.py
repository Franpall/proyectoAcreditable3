from flask import Flask, render_template, redirect, url_for, request
from flaskr.dbConexion import *
import os

app = Flask(__name__)
sesion = False


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
    return render_template('admin/dashboard.html', clientes=clientes)

@app.route('/productos')
def adminProductos():
    return render_template('admin/productos.html')


@app.route('/clientes')
def adminClientes():
    usuarios = mostrar_clientes()
    return render_template('admin/clientes.html', clientes=usuarios)

@app.route('/admins')
def adminAdmins():
    usuarios = mostrar_admins()
    return render_template('admin/admins.html', admins=usuarios)

@app.route('/ventas')
def adminVentas():
    return render_template('admin/ventas.html')

@app.route('/editar-producto')
def adminUpdateUI():
    return render_template('admin/editarProducto.html')

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
            return redirect(url_for('adminDashboard')), print("Inicion sesiada como admin")
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
        return adminAdmins()
    
# Lógica para cerrar sesiones
@app.route('/bye', methods=('GET', 'POST'))
def cerrarSesionSolicitud():
    global sesion
    sesion = False
    return render_template('auth/login.html', actionOK=True, notificacion="Sesion Cerrada con Exito")
    
# Lógica para eliminar usuarios
@app.route("/delete/<int:id_admin>")
def eliminarAdmin(id_admin):
    eliminar_admin(id_admin)
    return adminAdmins()


# Lógica para CATEGORIAS

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

# Crear carpeta uploads si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    
@app.route('/')
def index():
    conexion = crear_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categoria")
    categorias = cursor.fetchall()
    cursor.close()
    conexion.close()

    notificacion = request.args.get('notificacion', False)
    actionError = request.args.get('actionError', False)
    actionOK = request.args.get('actionOK', False)

    return render_template('index.html', sesion=sesion, categorias=categorias, notificacion=notificacion, actionError=actionError, actionOK=actionOK)

@app.route('/categorias', methods=['GET', 'POST'])
def adminCategorias():
    conexion = crear_conexion()
    cursor = conexion.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        imagen = request.files['imagen']

        if imagen:
            filename = imagen.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(filepath)

            cursor.execute("INSERT INTO categoria (nombre, imagen) VALUES (%s, %s)", (nombre, filename))
            conexion.commit()

    cursor.execute("SELECT * FROM categoria")
    categorias = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    return render_template('admin/categorias.html', categorias=categorias)

@app.route('/delete_categoria/<int:id_categoria>')
def eliminarCategoria(id_categoria):
    conexion = crear_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT imagen FROM categoria WHERE id = %s", (id_categoria,))
    filename, = cursor.fetchone()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.remove(filepath)
    
    cursor.execute("DELETE FROM categoria WHERE id = %s", (id_categoria,))
    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for('adminCategorias'))