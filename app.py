from flask import Flask, render_template, request, redirect, session, url_for
import db

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
            return redirect('/home')
        else:
            return 'Credenciales inválidas'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/home')
def home():
    if 'usuario_id' not in session:
        return redirect('/login')
    if session['tipo'] == 'user' or session['tipo'] == 'kiosco':
        conn = db.crear_conexion()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre, precio, stock FROM items')
        items = cursor.fetchall()
        conn.close()
        return render_template('home.html', items=items, nombre=session['nombre'], tipo=session['tipo'])
    else:
        return 'Tipo de usuario desconocido'

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

if __name__ == '__main__':
    app.run(debug=False)
