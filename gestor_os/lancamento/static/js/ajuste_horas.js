(function () {
  const filtroGeral = document.getElementById('filtro-geral');
  const filtroStatus = document.getElementById('filtro-status');
  const linhas = Array.from(document.querySelectorAll('#lista-apontamentos tr[data-id]'));

  const modal = document.getElementById('modal-ajuste');
  const campoId = document.getElementById('apontamento-id');
  const campoInicio = document.getElementById('data-inicio');
  const campoFim = document.getElementById('data-fim');
  const btnCancelar = document.getElementById('cancelar-modal');

  // Filtro da tabela
  function aplicarFiltro() {
    const termo = (filtroGeral.value || '').trim().toLowerCase();
    const status = filtroStatus.value;

    linhas.forEach((linha) => {
      const texto = [
        linha.dataset.matricula,
        linha.dataset.colaborador,
        linha.dataset.os,
        linha.dataset.status,
      ].join(' ');

      const okTermo = !termo || texto.includes(termo);
      const okStatus = !status || linha.dataset.status === status;
      linha.style.display = okTermo && okStatus ? '' : 'none';
    });
  }

  // Abrir modal
  function abrirModal(linha) {
    campoId.value = linha.dataset.id;
    campoInicio.value = linha.dataset.inicio || '';
    campoFim.value = linha.dataset.fim || '';
    modal.classList.add('active'); // usa CSS
  }

  // Fechar modal
  function fecharModal() {
    modal.classList.remove('active'); // usa CSS
  }

  // Eventos filtros
  filtroGeral?.addEventListener('input', aplicarFiltro);
  filtroStatus?.addEventListener('change', aplicarFiltro);

  // Eventos abrir modal
  document.querySelectorAll('[data-open-modal]').forEach((botao) => {
    botao.addEventListener('click', () => abrirModal(botao.closest('tr')));
  });

  // Fechar modal
  btnCancelar?.addEventListener('click', fecharModal);
  modal?.addEventListener('click', (event) => {
    if (event.target === modal) {
      fecharModal();
    }
  });
})();
