from flask import Flask, render_template, redirect, url_for
# from flaskr.dbConexion import * deje esa vaina para después

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

@app.route('/products')
def adminProducts():
    return render_template('admin/productos.html')