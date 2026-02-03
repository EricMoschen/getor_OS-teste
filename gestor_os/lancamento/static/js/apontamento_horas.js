// ======== FILTRO DE PESQUISA E BUSCA AJAX ========

document.addEventListener("DOMContentLoaded", () => {

  // ======== FILTRO DE PESQUISA ========
  const filtro = document.getElementById("filtro");
  const linhas = document.querySelectorAll("#lista-os tr");

  if (filtro) {
    filtro.addEventListener("input", () => {
      const termo = filtro.value.toLowerCase();

      linhas.forEach(tr => {
        const texto = tr.textContent.toLowerCase();
        tr.style.display = texto.includes(termo) ? "" : "none";
      });
    });
  }

  // ======== CAMPOS DO FORMULÁRIO ========
  const matriculaInput = document.getElementById("matricula");
  const nomeInput = document.getElementById("nome_colaborador");
  const numeroOsInput = document.getElementById("numero_os");
  const descricaoInput = document.getElementById("descricao_os");

  const loadingColab = document.getElementById("loading-colaborador");
  const loadingOs = document.getElementById("loading-os");

  // ======================================================
  // BUSCAR COLABORADOR
  // ======================================================
  if (matriculaInput && nomeInput) {

    matriculaInput.addEventListener("blur", async () => {

      const matricula = matriculaInput.value.trim().toUpperCase();

      if (!matricula) {
        nomeInput.value = "";
        return;
      }

      try {
        if (loadingColab) loadingColab.style.display = "block";
        nomeInput.value = "Buscando...";

        const resp = await fetch(`/lancamento/api/colaborador/${matricula}/`);

        if (!resp.ok) throw new Error();

        const data = await resp.json();
        nomeInput.value = data.nome || "Colaborador não encontrado";

      } catch {
        nomeInput.value = "Erro ao buscar colaborador";
      } finally {
        if (loadingColab) loadingColab.style.display = "none";
      }

    });

  }

  // ======================================================
  // BUSCAR ORDEM DE SERVIÇO
  // ======================================================
  if (numeroOsInput && descricaoInput) {

    let timeout = null;

    numeroOsInput.addEventListener("input", () => {

      clearTimeout(timeout);

      timeout = setTimeout(async () => {

        const numero = numeroOsInput.value.trim().toUpperCase();

        if (!numero) {
          descricaoInput.value = "";
          return;
        }

        try {

          if (loadingOs) loadingOs.style.display = "block";
          descricaoInput.value = "Buscando...";

          const resp = await fetch(`/lancamento/api/os/${numero}/`);

          if (!resp.ok) throw new Error();

          const data = await resp.json();
          descricaoInput.value = data.descricao || "OS não encontrada";

        } catch {
          descricaoInput.value = "Erro ao buscar OS";
        } finally {
          if (loadingOs) loadingOs.style.display = "none";
        }

      }, 400);

    });

  }

  // ======================================================
  // AUTO SUMIR MENSAGENS DJANGO (10 segundos)
  // ======================================================
  const alerts = document.querySelectorAll(".alert-message");

  alerts.forEach(alert => {

    // 👇 clique para fechar
    alert.addEventListener("click", () => {
      alert.remove();
    });

    // 👇 sumir automaticamente
    setTimeout(() => {

      alert.style.transition = "opacity 0.5s ease";
      alert.style.opacity = "0";

      setTimeout(() => {
        alert.remove();
      }, 500);

    }, 4000); // 4 segundos

  });

});
