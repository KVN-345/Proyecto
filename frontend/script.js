const API_URL = "http://localhost:5000/api"; // apunta al backend Flask

// Mostrar vistas
function showView(view) {
  document.getElementById("studentView").classList.toggle("d-none", view !== "student");
  document.getElementById("adminView").classList.toggle("d-none", view !== "admin");
}

// Cargar talleres
async function loadWorkshops() {
  try {
    const resp = await fetch(`${API_URL}/talleres`);
    if (!resp.ok) throw new Error("Error al cargar talleres");
    const talleres = await resp.json();

    // Vista estudiante
    const list = document.getElementById("workshopsList");
    list.innerHTML = "";
    talleres.forEach(t => {
      list.innerHTML += `
        <div class="col-md-4">
          <div class="card mb-3">
            <div class="card-body">
              <h5 class="card-title">${t.nombre}</h5>
              <p>${t.descripcion || ""}</p>
              <p><strong>Fecha:</strong> ${t.fecha} ${t.hora}</p>
              <p><strong>Lugar:</strong> ${t.lugar}</p>
              <p><strong>Categoría:</strong> ${t.categoria}</p>
              <p><strong>Cupos:</strong> ${t.cupos}</p>
              <button class="btn btn-success" onclick="openRegister(${t.id})">Inscribirse</button>
            </div>
          </div>
        </div>`;
    });

    // Vista admin
    const adminTable = document.getElementById("adminWorkshops");
    adminTable.innerHTML = "";
    talleres.forEach(t => {
      adminTable.innerHTML += `
        <tr>
          <td>${t.nombre}</td>
          <td>${t.fecha} ${t.hora}</td>
          <td>${t.lugar}</td>
          <td>${t.categoria}</td>
          <td>${t.cupos}</td>
          <td>
            <button class="btn btn-warning btn-sm" onclick="editWorkshop(${t.id})">Editar</button>
            <button class="btn btn-danger btn-sm" onclick="deleteWorkshop(${t.id})">Eliminar</button>
          </td>
        </tr>`;
    });
  } catch (err) {
    alert("No se pudo cargar talleres: " + err.message);
  }
}

// Abrir modal inscripción
function openRegister(id) {
  document.getElementById("registerWorkshopId").value = id;
  new bootstrap.Modal(document.getElementById("registerModal")).show();
}

// Enviar inscripción
document.getElementById("registerForm").addEventListener("submit", async e => {
  e.preventDefault();
  const tallerId = document.getElementById("registerWorkshopId").value;
  const estudiante = document.getElementById("studentName").value;

  try {
    const resp = await fetch(`${API_URL}/talleres/${tallerId}/register`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ estudiante })
    });
    const result = await resp.json();
    if (resp.ok) {
      alert(result.message);
      bootstrap.Modal.getInstance(document.getElementById("registerModal")).hide();
      loadWorkshops();
    } else {
      alert(result.message);
    }
  } catch (error) {
    alert("No se pudo conectar con la API");
    console.error(error);
  }
});

// Crear taller (admin)
document.getElementById("createForm").addEventListener("submit", async e => {
  e.preventDefault();
  const data = {
    nombre: document.getElementById("newName").value,
    descripcion: document.getElementById("newDescription").value,
    fecha: document.getElementById("newDate").value,
    hora: document.getElementById("newTime").value,
    lugar: document.getElementById("newPlace").value,
    categoria: document.getElementById("newCategory").value,
    cupos: parseInt(document.getElementById("newCupos").value)
  };

  try {
    const resp = await fetch(`${API_URL}/talleres`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });
    const result = await resp.json();
    if (resp.ok) {
      alert(result.message);
      loadWorkshops();
    } else {
      alert(result.message);
    }
  } catch (error) {
    alert("Error al crear taller");
    console.error(error);
  }
});

// Eliminar taller (admin)
async function deleteWorkshop(id) {
  if (!confirm("¿Seguro que quieres eliminar este taller?")) return;
  try {
    const resp = await fetch(`${API_URL}/talleres/${id}`, { method: "DELETE" });
    const result = await resp.json();
    alert(result.message);
    loadWorkshops();
  } catch (error) {
    alert("Error al eliminar taller");
    console.error(error);
  }
}

// Inicializar
loadWorkshops();