const API_URL = "http://localhost:5000/workshops"; // Ajusta según tu backend

async function loadWorkshops() {
  try {
    const resp = await fetch(API_URL);
    if (!resp.ok) throw new Error("Error al cargar talleres");
    const talleres = await resp.json();

    const list = document.getElementById("workshopsList");
    list.innerHTML = "";
    talleres.forEach(t => {
      list.innerHTML += `
        <div class="col-md-4">
          <div class="card workshop-card">
            <div class="card-body">
              <h5 class="card-title">${t.name}</h5>
              <p class="card-text">${t.description}</p>
              <p><strong>${t.date}</strong> - ${t.time}</p>
              <p>${t.location} (${t.category})</p>
              <button class="btn btn-primary">Inscribirse</button>
            </div>
          </div>
        </div>
      `;
    });
  } catch (error) {
    console.error(error);
  }
}

loadWorkshops();
