document.addEventListener('DOMContentLoaded', () => {
    const descricaoInput = document.getElementById('descricaoInput');
    const intervIdInput = document.getElementById('intervId');
    const submitBtn = document.getElementById('submitBtn');
    const cancelBtn = document.getElementById('cancelBtn');

    // Editar
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();
            intervIdInput.value = btn.dataset.id;
            descricaoInput.value = btn.dataset.descricao;
            submitBtn.textContent = 'Salvar Alterações';
            cancelBtn.style.display = 'inline-block';
            descricaoInput.focus();
        });
    });

    // Cancelar edição
    cancelBtn.addEventListener('click', () => {
        intervIdInput.value = '';
        descricaoInput.value = '';
        submitBtn.textContent = 'Cadastrar';
        cancelBtn.style.display = 'none';
    });

    // Modal de exclusão
    const modal = document.getElementById("deleteModal");
    const modalNome = document.getElementById("modalNome");
    const deleteForm = document.getElementById("deleteForm");
    const closeBtn = document.querySelector(".modal .close");
    const modalCancelBtn = document.querySelector(".modal .cancel-btn");

    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", e => {
            e.preventDefault();
            modalNome.textContent = btn.dataset.nome;
            deleteForm.action = `/cadastro/intervencao/excluir/${btn.dataset.id}/`;
            modal.style.display = "block";
        });
    });

    closeBtn.onclick = () => modal.style.display = "none";
    modalCancelBtn.onclick = () => modal.style.display = "none";
    window.onclick = e => { if (e.target == modal) modal.style.display = "none"; }
});