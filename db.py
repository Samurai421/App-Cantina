import sqlite3
from sqlite3 import Error

# ----------------------------------------
# FUNCION DE CONEXION A LA BASE DE DATOS
# ----------------------------------------
def crear_conexion():
    try:
        conn = sqlite3.connect("kantina.db")  # Crea o conecta a kantina.db en la carpeta actual
        return conn
    except Error as e:
        print(f"Error al conectar a SQLite: {e}")
        return None

# ----------------------------------------
# FUNCION PARA CREAR LAS TABLAS
# ----------------------------------------
def crear_tablas():
    conn = crear_conexion()
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        tipo TEXT DEFAULT 'usuario'
    );''')

    # Tabla de items (productos)
    cursor.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER DEFAULT 0
    );''')

    # Tabla de pedidos
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    );''')

    # Tabla de pedido_items para items en cada pedido
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedido_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        item_id INTEGER,
        cantidad INTEGER,
        FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY(item_id) REFERENCES items(id)
    );''')

    conn.commit()
    conn.close()

# ----------------------------------------
# FUNCION PARA INSERTAR USUARIO
# ----------------------------------------
def insertar_usuario(nombre, email, password, tipo="usuario"):
    conn = crear_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO usuarios (nombre, email, password, tipo)
                          VALUES (?, ?, ?, ?);''', (nombre, email, password, tipo))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ----------------------------------------
# FUNCION PARA VERIFICAR USUARIO (LOGIN)
# ----------------------------------------
def verificar_usuario(email, password):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM usuarios WHERE email = ? AND password = ?;''', (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

# ----------------------------------------
# FUNCION PARA AGREGAR ITEM
# ----------------------------------------
def agregar_item(nombre, precio, stock):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO items (nombre, precio, stock)
                      VALUES (?, ?, ?);''', (nombre, precio, stock))
    conn.commit()
    conn.close()

# ----------------------------------------
# FUNCION PARA CREAR PEDIDO
# ----------------------------------------
def crear_pedido(usuario_id, items_cantidades):
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO pedidos (usuario_id) VALUES (?);''', (usuario_id,))
    pedido_id = cursor.lastrowid

    for item_id, cantidad in items_cantidades:
        cursor.execute('''INSERT INTO pedido_items (pedido_id, item_id, cantidad)
                          VALUES (?, ?, ?);''', (pedido_id, item_id, cantidad))
    conn.commit()
    conn.close()

# ----------------------------------------
# FUNCION PARA VER PEDIDOS
# ----------------------------------------
def ver_pedidos():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('''SELECT pedidos.id, usuarios.nombre, pedidos.fecha
                      FROM pedidos
                      JOIN usuarios ON pedidos.usuario_id = usuarios.id;''')
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

# ----------------------------------------
# INICIALIZACION DE TABLAS AL EJECUTAR
# ----------------------------------------
if __name__ == "__main__":
    crear_tablas()
    print("Base de datos y tablas creadas correctamente.")




def test1():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    resultados = cursor.fetchall()  # Obtener todos los resultados

    # Mostrar los resultados
    print(resultados)