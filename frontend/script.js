
const API_TALLERES = "http://localhost:5000/api/talleres";
const API_INSCRIBIR = "http://localhost:5000/api/inscribir";

// Alternar vistas
function showView(view) {
  document.getElementById("talleresView").classList.toggle("d-none", view !== "talleres");
  document.getElementById("studentView").classList.toggle("d-none", view !== "estudiante");
  document.getElementById("adminView").classList.toggle("d-none", view !== "administración");
}

// Eventos de navbar
document.querySelectorAll(".nav-link").forEach(link => {
  link.addEventListener("click", e => {
    e.preventDefault();
    const text = e.target.textContent.toLowerCase();
    showView(text);
  });
});

// Cargar talleres
async function loadWorkshops() {
  try {
    const resp = await fetch(API_TALLERES);
    if (!resp.ok) throw new Error("Error al cargar talleres");
    const talleres = await resp.json();

    const list = document.getElementById("workshopsList");
    list.innerHTML = "";
    talleres.forEach(t => {
      list.innerHTML += `
        <div class="col-md-4">
          <div class="card workshop-card">
            <div class="card-body">
              <h5 class="card-title">${t.nombre}</h5>
              <p>Cupos disponibles: ${t.cupos}</p>
            </div>
          </div>
        </div>
      `;
    });
  } catch (error) {
    console.error(error);
  }
}

// Inscripción estudiante
document.getElementById("studentForm").addEventListener("submit", async e => {
  e.preventDefault();
  const nombre = document.getElementById("studentName").value;
  const tallerId = document.getElementById("workshopId").value;

  try {
    const resp = await fetch(API_INSCRIBIR, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ nombre: nombre, taller_id: parseInt(tallerId) })
    });
    const result = await resp.json();
    document.getElementById("studentMessage").innerText = result.message;
  } catch (error) {
    console.error(error);
  }
});

// Crear taller (admin)
document.getElementById("adminForm").addEventListener("submit", async e => {
  e.preventDefault();
  const nombre = document.getElementById("workshopName").value;
  const cupos = document.getElementById("workshopSlots").value;

  try {
    const resp = await fetch(API_TALLERES, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ nombre: nombre, cupos: parseInt(cupos) })
    });
    const result = await resp.json();
    document.getElementById("adminMessage").innerText = result.message || "Taller creado";
    loadWorkshops(); // refrescar lista
  } catch (error) {
    console.error(error);
  }
});

// Inicializar
loadWorkshops();
