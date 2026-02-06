
// Modal
const modal = document.getElementById("deleteModal");
const modalNome = document.getElementById("modalNome");
const deleteForm = document.getElementById("deleteForm");
const closeBtn = document.querySelector(".close");
const cancelBtn = document.querySelector(".cancel-btn");

document.querySelectorAll(".delete-btn").forEach(btn => {
    btn.addEventListener("click", e => {
        e.preventDefault();
        const id = btn.getAttribute("data-id");
        const nome = btn.getAttribute("data-nome");
        modalNome.textContent = nome;
        deleteForm.action = `/cadastro/colaborador/excluir/${id}/`;
        modal.style.display = "block";
    });
});

closeBtn.onclick = () => modal.style.display = "none";
cancelBtn.onclick = () => modal.style.display = "none";
window.onclick = e => { if (e.target == modal) modal.style.display = "none"; }

// Mostrar/ocultar horários personalizados dependendo do turno
const turnoSelect = document.getElementById('id_turno');
const horariosDiv = document.getElementById('horarios-personalizados');

function toggleHorarios() {
    if (turnoSelect.value === 'OUTROS') {
        horariosDiv.style.display = 'flex';
    } else {
        horariosDiv.style.display = 'none';
    }
}

turnoSelect.addEventListener('change', toggleHorarios);
toggleHorarios(); // inicializa no carregamento
