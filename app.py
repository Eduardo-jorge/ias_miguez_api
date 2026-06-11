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
    return jsonify({"status": "ok", "message": "API funcionando correctamente - Prueba CI/CD 11/06"}), 200

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
    
# Endpoint 4: Modificar un usuario existente
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json()
    
    if 'nombre' in data:
        user.nombre = data['nombre']
        
    if 'email' in data:
        # Verifica que el email nuevo no sea de otro usuario
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != id:
            return jsonify({"error": "El email ya está registrado"}), 400
        user.email = data['email']

    db.session.commit()
    return jsonify(user.to_dict()), 200
    
# Endpoint 5: Eliminar un usuario
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado correctamente"}), 200

# ==========================================
# COMPLETANDO EL ABM DE USUARIOS (Requisito del TP)
# ==========================================

# 1. Obtener un único usuario por ID (Lectura)
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

# 2. Modificar un usuario existente (Update - M)
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400
        
    # Validar si intenta cambiar el email por uno que ya existe
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "El email ya está registrado por otro usuario"}), 400
            
    # Actualizar campos si vienen en el JSON
    user.nombre = data.get('nombre', user.nombre)
    user.email = data.get('email', user.email)
    
    db.session.commit()
    return jsonify(user.to_dict()), 200

# 3. Eliminar un usuario (Delete - B)
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Usuario {user_id} eliminado correctamente"}), 200
    
if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=DEBUG_MODE)  # nosec B104
