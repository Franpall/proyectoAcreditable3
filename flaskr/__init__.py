from flask import Flask, render_template, redirect, url_for
from flaskr.dbConexion import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', productos=mostrar_productos())

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
