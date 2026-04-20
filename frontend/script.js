// URL base de la API
const API_URL = "http://localhost:5000/workshops";

// Cargar talleres al iniciar
async function loadWorkshops() {
  const response = await fetch(API_URL);
  const workshops = await response.json();

  const tbody = document.querySelector("tbody");
  tbody.innerHTML = "";

  workshops.forEach(w => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${w.name}</td>
      <td>${w.date}</td>
      <td>${w.time}</td>
      <td>${w.location}</td>
      <td>${w.category}</td>
      <td>
        <button class="btn btn-success btn-sm" onclick="registerStudent(${w.id})">Inscribirse</button>
        <button class="btn btn-warning btn-sm" onclick="editWorkshop(${w.id})">Editar</button>
        <button class="btn btn-danger btn-sm" onclick="deleteWorkshop(${w.id})">Eliminar</button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

// Registrar estudiante
async function registerStudent(id) {
  const studentName = prompt("Ingrese su nombre:");
  if (!studentName) return;

  const response = await fetch(`${API_URL}/${id}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_name: studentName })
  });

  const result = await response.json();
  alert(result.message);
}

// Editar taller
async function editWorkshop(id) {
  const newName = prompt("Nuevo nombre del taller:");
  const newDate = prompt("Nueva fecha (dd/mm/yyyy):");
  const newTime = prompt("Nueva hora (HH:MM):");
  const newLocation = prompt("Nuevo lugar:");
  const newCategory = prompt("Nueva categoría:");

  const response = await fetch(`${API_URL}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: newName,
      description: "Actualizado",
      date: newDate,
      time: newTime,
      location: newLocation,
      category: newCategory
    })
  });

  const result = await response.json();
  alert(result.message);
  loadWorkshops();
}

// Eliminar taller
async function deleteWorkshop(id) {
  if (!confirm("¿Seguro que deseas eliminar este taller?")) return;

  const response = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
  const result = await response.json();
  alert(result.message);
  loadWorkshops();
}

// Inicializar
document.addEventListener("DOMContentLoaded", loadWorkshops);
