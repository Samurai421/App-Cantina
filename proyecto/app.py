from flask import Flask, render_template, request, redirect, session, url_for, make_response
import db
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_segura'

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect('/home')
    else: 
        return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        tipo = request.form['tipo']
        if db.insertar_usuario(nombre, email, password, tipo):
            return redirect('/login')
        else:
            return 'Usuario ya existe'
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.verificar_usuario(email, password)
        if user:
            session['usuario_id'] = user[0]
            session['nombre'] = user[1]
            session['tipo'] = user[4]
            resp = make_response(redirect('/home'))
            resp.set_cookie('nombre_usuario', user[1], max_age=60*60*24*7)  # 7 días
            return resp
        else:
            return 'Credenciales inválidas'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect('/'))
    resp.delete_cookie('nombre_usuario')
    resp.delete_cookie('carrito')
    return resp

@app.route('/home')
def home():
    if 'usuario_id' not in session:
        return redirect('/login')

    nombre_cookie = request.cookies.get('nombre_usuario')
    tipo = session['tipo']

    busqueda = request.args.get('busqueda')

    conn = db.crear_conexion()
    cursor = conn.cursor()

    if busqueda:
        cursor.execute("SELECT id, nombre, precio, stock FROM items WHERE nombre LIKE ?", ('%' + busqueda + '%',))
    else:
        cursor.execute("SELECT id, nombre, precio, stock FROM items")

    items = cursor.fetchall()
    conn.close()

    return render_template('home.html', items=items, nombre=nombre_cookie, tipo=tipo)

@app.route('/panel_kiosco', methods=['GET', 'POST'])
def panel_kiosco():
    if 'usuario_id' not in session or session['tipo'] != 'kiosco':
        return redirect('/login')

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        db.agregar_item(nombre, precio, stock)

    conn = db.crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, precio, stock FROM items')
    items = cursor.fetchall()
    conn.close()

    return render_template('panel_kiosco.html', items=items, nombre=session['nombre'])

@app.route('/agregar_carrito/<int:item_id>')
def agregar_carrito(item_id):
    carrito = request.cookies.get('carrito')
    if carrito:
        carrito = json.loads(carrito)
    else:
        carrito = {}

    conn = db.crear_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT nombre, precio FROM items WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()

    if item:
        if str(item_id) in carrito:
            carrito[str(item_id)]['cantidad'] += 1
        else:
            carrito[str(item_id)] = {
                'nombre': item[0],
                'precio': item[1],
                'cantidad': 1
            }

    session['carrito'] = carrito  # opcional si querés tenerlo también en sesión
    resp = make_response(redirect('/home'))
    resp.set_cookie('carrito', json.dumps(carrito), max_age=60*60*24*7)
    return resp

@app.route('/carrito')
def ver_carrito():
    carrito_json = request.cookies.get('carrito')
    if carrito_json:
        carrito = json.loads(carrito_json)
    else:
        carrito = {}

    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/eliminar_item/<int:item_id>')
def eliminar_item(item_id):
    carrito_json = request.cookies.get('carrito')
    if carrito_json:
        carrito = json.loads(carrito_json)
        if str(item_id) in carrito:
            del carrito[str(item_id)]
    else:
        carrito = {}

    session['carrito'] = carrito
    resp = make_response(redirect('/carrito'))
    resp.set_cookie('carrito', json.dumps(carrito), max_age=60*60*24*7)
    return resp

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session['carrito'] = {}
    resp = make_response(redirect('/carrito'))
    resp.set_cookie('carrito', '', expires=0)
    return resp

@app.route('/')
def home_v2():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=False)
