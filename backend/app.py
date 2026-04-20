from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workshops.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------
# MODELOS
# ----------------------

class Workshop(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    date        = db.Column(db.String(50))
    time        = db.Column(db.String(50))
    location    = db.Column(db.String(100))
    category    = db.Column(db.String(50))
    capacity    = db.Column(db.Integer, default=30)
    registrations = db.relationship('Registration', backref='workshop', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "description": self.description,
            "date":        self.date,
            "time":        self.time,
            "location":    self.location,
            "category":    self.category,
            "capacity":    self.capacity,
            "registered":  len(self.registrations)
        }


class Registration(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_email= db.Column(db.String(120))
    workshop_id  = db.Column(db.Integer, db.ForeignKey('workshop.id'), nullable=False)
    registered_at= db.Column(db.String(50), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    def to_dict(self):
        return {
            "id":            self.id,
            "student_name":  self.student_name,
            "student_email": self.student_email,
            "workshop_id":   self.workshop_id,
            "registered_at": self.registered_at
        }


# ----------------------
# CREAR BASE DE DATOS
# ----------------------

with app.app_context():
    db.create_all()
    # Datos de ejemplo si la tabla está vacía
    if Workshop.query.count() == 0:
        ejemplos = [
            Workshop(name="Python para principiantes", description="Introducción a la programación con Python desde cero.", date="2025-08-10", time="09:00", location="Sala A101", category="tecnología", capacity=25),
            Workshop(name="Emprendimiento Digital", description="Cómo lanzar tu negocio online en 30 días.", date="2025-08-15", time="14:00", location="Auditorio principal", category="emprendimiento", capacity=50),
            Workshop(name="Comunicación Efectiva", description="Mejora tus habilidades de presentación y trabajo en equipo.", date="2025-08-20", time="10:00", location="Sala B204", category="habilidades blandas", capacity=20),
        ]
        db.session.add_all(ejemplos)
        db.session.commit()

# ----------------------
# ENDPOINTS
# ----------------------

# GET todos los talleres
@app.route('/workshops', methods=['GET'])
def get_workshops():
    category = request.args.get('category')
    if category:
        workshops = Workshop.query.filter_by(category=category).all()
    else:
        workshops = Workshop.query.all()
    return jsonify([w.to_dict() for w in workshops]), 200


# GET taller por ID
@app.route('/workshops/<int:id>', methods=['GET'])
def get_workshop(id):
    w = Workshop.query.get_or_404(id)
    return jsonify(w.to_dict()), 200


# POST crear taller (solo admins)
@app.route('/workshops', methods=['POST'])
def create_workshop():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "El campo 'name' es obligatorio"}), 400

    w = Workshop(
        name        = data['name'],
        description = data.get('description', ''),
        date        = data.get('date', ''),
        time        = data.get('time', ''),
        location    = data.get('location', ''),
        category    = data.get('category', ''),
        capacity    = data.get('capacity', 30)
    )
    db.session.add(w)
    db.session.commit()
    return jsonify(w.to_dict()), 201


# PUT modificar taller (solo admins)
@app.route('/workshops/<int:id>', methods=['PUT'])
def update_workshop(id):
    w = Workshop.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    w.name        = data.get('name',        w.name)
    w.description = data.get('description', w.description)
    w.date        = data.get('date',        w.date)
    w.time        = data.get('time',        w.time)
    w.location    = data.get('location',    w.location)
    w.category    = data.get('category',    w.category)
    w.capacity    = data.get('capacity',    w.capacity)

    db.session.commit()
    return jsonify(w.to_dict()), 200


# DELETE cancelar taller (solo admins)
@app.route('/workshops/<int:id>', methods=['DELETE'])
def delete_workshop(id):
    w = Workshop.query.get_or_404(id)
    db.session.delete(w)
    db.session.commit()
    return jsonify({"message": f"Taller '{w.name}' eliminado correctamente"}), 200


# POST registrar estudiante en taller
@app.route('/workshops/<int:id>/register', methods=['POST'])
def register_student(id):
    w = Workshop.query.get_or_404(id)
    data = request.get_json()

    if not data or not data.get('student_name'):
        return jsonify({"error": "El campo 'student_name' es obligatorio"}), 400

    if len(w.registrations) >= w.capacity:
        return jsonify({"error": "El taller ha alcanzado su capacidad máxima"}), 409

    # Verificar si ya está registrado
    email = data.get('student_email', '')
    if email:
        existing = Registration.query.filter_by(workshop_id=id, student_email=email).first()
        if existing:
            return jsonify({"error": "Este estudiante ya está registrado en el taller"}), 409

    reg = Registration(
        student_name  = data['student_name'],
        student_email = email,
        workshop_id   = id
    )
    db.session.add(reg)
    db.session.commit()
    return jsonify({"message": "Registro exitoso", "registration": reg.to_dict()}), 201


# GET ver inscritos de un taller (admin)
@app.route('/workshops/<int:id>/registrations', methods=['GET'])
def get_registrations(id):
    w = Workshop.query.get_or_404(id)
    return jsonify({
        "workshop": w.name,
        "total": len(w.registrations),
        "students": [r.to_dict() for r in w.registrations]
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)