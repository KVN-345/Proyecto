import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db, Workshop, Registration


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


# ─── Helpers ───────────────────────────────────────────────

def create_workshop(client, name="Taller Test", category="tecnología"):
    return client.post('/workshops', json={
        "name": name,
        "description": "Descripción de prueba",
        "date": "2025-09-01",
        "time": "10:00",
        "location": "Sala A",
        "category": category,
        "capacity": 5
    })


# ─── GET /workshops ─────────────────────────────────────────

def test_get_workshops_empty(client):
    res = client.get('/workshops')
    assert res.status_code == 200
    assert res.get_json() == []


def test_get_workshops_returns_list(client):
    create_workshop(client, "Python Básico")
    create_workshop(client, "Emprendimiento Digital", "emprendimiento")
    res = client.get('/workshops')
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 2


def test_get_workshops_filter_by_category(client):
    create_workshop(client, "Python Básico", "tecnología")
    create_workshop(client, "Emprendimiento", "emprendimiento")
    res = client.get('/workshops?category=tecnología')
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 1
    assert data[0]['category'] == 'tecnología'


# ─── GET /workshops/<id> ────────────────────────────────────

def test_get_workshop_by_id(client):
    create_workshop(client, "Flask Avanzado")
    res = client.get('/workshops/1')
    data = res.get_json()
    assert res.status_code == 200
    assert data['name'] == 'Flask Avanzado'
    assert 'registered' in data
    assert 'capacity' in data


def test_get_workshop_not_found(client):
    res = client.get('/workshops/999')
    assert res.status_code == 404


# ─── POST /workshops ────────────────────────────────────────

def test_create_workshop_success(client):
    res = create_workshop(client, "Nuevo taller")
    data = res.get_json()
    assert res.status_code == 201
    assert data['name'] == 'Nuevo taller'
    assert data['id'] is not None


def test_create_workshop_missing_name(client):
    res = client.post('/workshops', json={"description": "Sin nombre"})
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_create_workshop_empty_body(client):
    res = client.post('/workshops', json={})
    assert res.status_code == 400


# ─── PUT /workshops/<id> ────────────────────────────────────

def test_update_workshop(client):
    create_workshop(client, "Taller Original")
    res = client.put('/workshops/1', json={"name": "Taller Actualizado", "location": "Sala B"})
    data = res.get_json()
    assert res.status_code == 200
    assert data['name'] == 'Taller Actualizado'
    assert data['location'] == 'Sala B'


def test_update_workshop_not_found(client):
    res = client.put('/workshops/999', json={"name": "X"})
    assert res.status_code == 404


def test_update_workshop_no_body(client):
    create_workshop(client)
    res = client.put('/workshops/1', json=None, content_type='application/json')
    assert res.status_code == 400


# ─── DELETE /workshops/<id> ─────────────────────────────────

def test_delete_workshop(client):
    create_workshop(client, "Para eliminar")
    res = client.delete('/workshops/1')
    assert res.status_code == 200
    assert 'message' in res.get_json()
    # Verify it's gone
    assert client.get('/workshops/1').status_code == 404


def test_delete_workshop_not_found(client):
    res = client.delete('/workshops/999')
    assert res.status_code == 404


# ─── POST /workshops/<id>/register ─────────────────────────

def test_register_student_success(client):
    create_workshop(client)
    res = client.post('/workshops/1/register', json={
        "student_name": "Ana García",
        "student_email": "ana@example.com"
    })
    data = res.get_json()
    assert res.status_code == 201
    assert 'registration' in data
    assert data['registration']['student_name'] == 'Ana García'


def test_register_student_missing_name(client):
    create_workshop(client)
    res = client.post('/workshops/1/register', json={"student_email": "x@x.com"})
    assert res.status_code == 400


def test_register_student_workshop_not_found(client):
    res = client.post('/workshops/999/register', json={"student_name": "Test"})
    assert res.status_code == 404


def test_register_student_capacity_full(client):
    # Capacity = 5, register 5 students
    create_workshop(client, "Taller lleno")
    for i in range(5):
        client.post('/workshops/1/register', json={"student_name": f"Estudiante {i}", "student_email": f"s{i}@test.com"})
    # 6th registration should fail
    res = client.post('/workshops/1/register', json={"student_name": "Extra", "student_email": "extra@test.com"})
    assert res.status_code == 409
    assert 'error' in res.get_json()


def test_register_student_duplicate_email(client):
    create_workshop(client)
    client.post('/workshops/1/register', json={"student_name": "Ana", "student_email": "ana@test.com"})
    res = client.post('/workshops/1/register', json={"student_name": "Ana", "student_email": "ana@test.com"})
    assert res.status_code == 409


# ─── GET /workshops/<id>/registrations ─────────────────────

def test_get_registrations(client):
    create_workshop(client, "Taller con inscritos")
    client.post('/workshops/1/register', json={"student_name": "Luis", "student_email": "luis@test.com"})
    client.post('/workshops/1/register', json={"student_name": "María", "student_email": "maria@test.com"})
    res = client.get('/workshops/1/registrations')
    data = res.get_json()
    assert res.status_code == 200
    assert data['total'] == 2
    assert len(data['students']) == 2