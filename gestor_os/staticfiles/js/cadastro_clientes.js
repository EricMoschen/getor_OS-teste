document.addEventListener("DOMContentLoaded", function () {

    // ===========================
    //  MODAL DE EXCLUSÃO
    // ===========================

    const modal = document.getElementById("deleteModal");
    const modalNome = document.getElementById("modalNome");
    const deleteForm = document.getElementById("deleteForm");
    const closeBtn = document.querySelector(".close");
    const cancelBtn = document.querySelector(".cancel-btn");

    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", e => {
            e.preventDefault();

            const id = btn.dataset.id;
            const nome = btn.dataset.nome;

            modalNome.textContent = nome;
            deleteForm.action = `/cadastro/cliente/excluir/${id}/`;

            modal.style.display = "block";
        });
    });

    closeBtn.onclick = () => modal.style.display = "none";
    cancelBtn.onclick = () => modal.style.display = "none";

    window.onclick = e => {
        if (e.target === modal) modal.style.display = "none";
    };


    // ===========================
    //  EDITAR CLIENTE
    // ===========================

    const editButtons = document.querySelectorAll(".edit-btn");
    const idField = document.getElementById("cliente_id");
    const codField = document.getElementById("id_cod_cliente");
    const nomeField = document.getElementById("id_nome_cliente");
    const submitBtn = document.getElementById("submitBtn");
    const btnCancelar = document.getElementById("btnCancelar");
    const mensagemErro = document.getElementById("erro-msg")

    editButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            const id = this.dataset.id;
            const cod = this.dataset.cod;
            const nome = this.dataset.nome;

            idField.value = id;
            codField.value = cod;
            nomeField.value = nome;

            submitBtn.textContent = "Salvar";
            btnCancelar.style.display = "flex";

            nomeField.focus();
        });
    });

    // ===========================
    //  BOTÃO CANCELAR
    // ===========================

    btnCancelar.addEventListener("click", () => {

        idField.value = "";
        codField.value = "";
        nomeField.value = "";

        submitBtn.textContent = "Cadastrar";
        btnCancelar.style.display = "none";

        if (mensagemErro) {
            mensagemErro.style.display = "none";
            mensagemErro.textContent = "";
        }
    });

    // ===========================
    //  AO CARREGAR A PÁGINA APÓS SALVAR
    // ===========================

    if (!idField.value) {
        btnCancelar.style.display = "none";
        if (mensagemErro) mensagemErro.style.display = "none";
    }

    // ===========================
    //  MENSAGEM DE ERRO SOME EM 10s
    // ===========================

    if (mensagemErro && mensagemErro.textContent.trim() !== "") {
        mensagemErro.style.display = "block";

        setTimeout(() => {
            mensagemErro.style.display = "none";
        }, 6000); // 10 segundos
    }

});
