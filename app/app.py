import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración segura de variables de entorno (Requisito del TP)
# NO se usa debug=True hardcodeado
DEBUG_MODE = os.environ.get('DEBUG', 'False').lower() == 'true'

# Configuración de la Base de Datos
# Por defecto usa SQLite localmente, pero en Render usará PostgreSQL
database_url = os.environ.get('DATABASE_URL', 'sqlite:///local_db.sqlite')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "email": self.email}

with app.app_context():
    db.create_all()

# Endpoint 1: Healthcheck (Requisito del TP)
@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok", "message": "API funcionando correctamente"}), 200

# Endpoint 2: Obtener todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

# Endpoint 3: Crear un nuevo usuario
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not 'nombre' in data or not 'email' in data:
        return jsonify({"error": "Faltan datos requeridos (nombre, email)"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "El email ya está registrado"}), 400

    new_user = User(nombre=data['nombre'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(new_user.to_dict()), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=DEBUG_MODE)
