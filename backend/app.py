from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# ----------------------
# CONFIGURACIÓN
# ----------------------
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///talleres.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------
# MODELOS
# ----------------------
class Taller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cupos = db.Column(db.Integer, nullable=False)
    inscripciones = db.relationship('Inscripcion', backref='taller', lazy=True)

class Inscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudiante = db.Column(db.String(100), nullable=False)
    taller_id = db.Column(db.Integer, db.ForeignKey('taller.id'), nullable=False)

# ----------------------
# ENDPOINTS
# ----------------------

# Obtener todos los talleres
@app.route('/api/talleres', methods=['GET'])
def get_talleres():
    talleres = Taller.query.all()
    return jsonify([{"id": t.id, "nombre": t.nombre, "cupos": t.cupos} for t in talleres])

# Inscribir estudiante en un taller
@app.route('/api/inscribir', methods=['POST'])
def inscribir():
    data = request.json
    taller = Taller.query.get(data['taller_id'])
    count = Inscripcion.query.filter_by(taller_id=taller.id).count()

    if count < taller.cupos:
        nueva_inscripcion = Inscripcion(estudiante=data['nombre'], taller_id=taller.id)
        db.session.add(nueva_inscripcion)
        db.session.commit()
        return jsonify({"status": "success", "message": "Inscrito correctamente"}), 201
    return jsonify({"status": "error", "message": "Taller lleno"}), 400

# ----------------------
# INICIALIZACIÓN DE BD
# ----------------------
with app.app_context():
    db.create_all()
    if not Taller.query.first():
        db.session.add_all([
            Taller(nombre="Redes e Infraestructura", cupos=10),
            Taller(nombre="Programación Python", cupos=15),
            Taller(nombre="Seguridad Informática", cupos=8)
        ])
        db.session.commit()

# ----------------------
# MAIN
# ----------------------
if __name__ == '__main__':
    app.run(debug=True)