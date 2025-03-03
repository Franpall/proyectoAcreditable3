from flask import Flask, render_template, redirect, url_for, request
from flaskr.dbConexion import *

app = Flask(__name__)
sesion = False

@app.route('/')
def index():
    return render_template('index.html', sesion=sesion)

@app.route('/login')
def iniciarSesion():
    return render_template('auth/login.html')

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

@app.route('/categorias')
def adminCategorias():
    return render_template('admin/categorias.html')

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
            return redirect(url_for('iniciarSesion')), print("Cuenta Creada Con Éxito, ahora Inicia Sesión")
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
            return redirect(url_for('index')), print("Inicion sesiada como cliente")
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
    return iniciarSesion(), print("Sesión Cerrada")
    
# Lógica para eliminar usuarios
@app.route("/delete/<int:id_admin>")
def eliminarAdmin(id_admin):
    eliminar_admin(id_admin)
    return adminAdmins()
