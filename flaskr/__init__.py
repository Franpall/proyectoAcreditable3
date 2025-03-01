from flask import Flask, render_template, redirect, url_for, request
from flaskr.dbConexion import * 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def iniciarSesion():
    return render_template('auth/login.html')

@app.route('/register')
def registrarse():
    return render_template('auth/register.html')

@app.route('/carrito')
def verCarrito():
    return render_template('carrito.html')

@app.route('/producto')
def verProducto():
    return render_template('producto.html')

# Rutas para administradores

@app.route('/dashboard')
def adminDashboard():
    return render_template('admin/dashboard.html')

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

        registrar_cliente(usuario, correo, contraseña, 1)
        #mensaje = "Cuenta Creada Con Éxito, ahora Inicia Sesión"
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