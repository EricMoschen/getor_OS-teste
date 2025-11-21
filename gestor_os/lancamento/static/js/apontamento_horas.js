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

  // ======== BUSCAR COLABORADOR ========
  if (matriculaInput && nomeInput) {
    matriculaInput.addEventListener("input", async () => {
      const matricula = matriculaInput.value.trim();
      if (!matricula) {
        nomeInput.value = "";
        return;
      }

      try {
        const resp = await fetch(`/lancamento/api/colaborador/${matricula}/`);
        if (!resp.ok) throw new Error();
        const data = await resp.json();
        nomeInput.value = data.nome || "Colaborador não encontrado";
      } catch {
        nomeInput.value = "Erro ao buscar colaborador";
      }
    });
  }

  // ======== BUSCAR ORDEM DE SERVIÇO ========
  if (numeroOsInput && descricaoInput) {
    numeroOsInput.addEventListener("input", async () => {
      const numero = numeroOsInput.value.trim();
      if (!numero) {
        descricaoInput.value = "";
        return;
      }

      try {
        const resp = await fetch(`/lancamento/api/os/${numero}/`);
        if (!resp.ok) throw new Error();
        const data = await resp.json();
        descricaoInput.value = data.descricao || "OS não encontrada";
      } catch {
        descricaoInput.value = "Erro ao buscar OS";
      }
    });
  }
});
