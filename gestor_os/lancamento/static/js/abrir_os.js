document.addEventListener('DOMContentLoaded', () => {

  /* ================================
     ELEMENTOS
  ================================= */

  const form = document.querySelector('.abrir-os form');
  const numeroOS = document.getElementById('numero_os');
  const saveBtn = document.querySelector('.save-btn');
  const cancelBtn = document.querySelector('.cancel-btn');
  const deleteBtn = document.querySelector('.delete-btn');

  const dropdown = {
    selected: document.getElementById('dropdownSelected'),
    list: document.getElementById('dropdownList'),
    hidden: document.getElementById('centro_custo'),

    set(cod, label) {
      this.hidden.value = cod || '';
      this.selected.textContent = label || 'Selecione um centro de custo';
    },

    toggle() {
      this.list.classList.toggle('hidden');
    },

    close() {
      this.list.classList.add('hidden');
    }
  };

  /* ================================
     DROPDOWN
  ================================= */

  dropdown.selected.addEventListener('click', e => {
    e.stopPropagation();
    dropdown.toggle();
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.dropdown-container')) {
      dropdown.close();
    }
  });

  dropdown.list.addEventListener('click', e => {

    // ===== ABRIR / FECHAR FILHOS DO CENTRO DE CUSTO =====
    const parentToggle = e.target.closest('.parent');
    const isArrow = e.target.classList.contains('arrow');

    if (parentToggle && isArrow) {

      const cod = parentToggle.dataset.cod;
      const children = document.getElementById(`children-${cod}`);
      const arrow = parentToggle.querySelector('.arrow');

      if (!children) return;

      children.classList.toggle('hidden');
      arrow.textContent = children.classList.contains('hidden') ? '▶' : '▼';

      return; // ⛔ impede selecionar o pai
    }

    // ===== SELEÇÃO NORMAL (SEU CÓDIGO ORIGINAL) =====
    const child = e.target.closest('.child');
    const parent = e.target.closest('.parent');

    if (child) {
      dropdown.set(child.dataset.cod, child.dataset.label);
      dropdown.close();
      return;
    }

    if (parent && !isArrow) {
      dropdown.set(parent.dataset.cod, parent.dataset.label);
      dropdown.close();
    }

  });

  /* ================================
     UTIL FORM
  ================================= */

  function setFormValue(name, value) {

    const input = form.querySelector(`[name="${name}"]`);
    if (!input) return;

    if (input.tagName === 'SELECT') {
      input.value = value ?? '';
      return;
    }

    if (input.type === 'checkbox') {
      input.checked = Boolean(value);
      return;
    }

    input.value = value ?? '';
  }

  function preencherFormulario(data) {

    numeroOS.value = data.numero;
    dropdown.set(data.centroCod, data.centroLabel);

    form.action = `/lancamento/editar_os/${data.id}/`;

    saveBtn.textContent = '💾 Salvar Alterações';
    cancelBtn.style.display = 'inline-block';
    deleteBtn.style.display = 'inline-block';

    deleteBtn.href = `/lancamento/excluir/${data.id}/`;

    Object.entries(data.campos).forEach(([k, v]) => {
      setFormValue(k, v);
    });
  }

  function resetForm() {

    form.reset();
    dropdown.set('', '');

    saveBtn.textContent = '💾 Abrir OS';
    cancelBtn.style.display = 'none';
    deleteBtn.style.display = 'none';

    form.action = window.URL_ABRIR_OS;
    numeroOS.value = window.PROXIMO_NUMERO_OS;
  }

  cancelBtn.addEventListener('click', resetForm);

  /* ================================
     API
  ================================= */

  async function carregarOS(id, fallback) {

    try {

      const r = await fetch(`/lancamento/api/os/detalhes/${id}/`);
      if (!r.ok) throw new Error();

      const d = await r.json();

      preencherFormulario({
        id: d.id,
        numero: d.numero_os,
        centroCod: d.centro_custo?.id,
        centroLabel: d.centro_custo?.label,
        campos: {
          descricao_os: d.descricao_os,
          cliente: d.cliente,
          motivo_intervencao: d.motivo_intervencao,
          ssm: d.ssm
        }
      });

    } catch {

      if (fallback) preencherFormulario(fallback);
    }
  }

  /* ================================
     BOTÃO EDITAR
  ================================= */

  document.querySelectorAll('.edit-btn').forEach(btn => {

    btn.addEventListener('click', e => {

      const tr = e.target.closest('tr');

      carregarOS(tr.dataset.osId, {
        id: tr.dataset.osId,
        numero: tr.dataset.numeroOs,
        centroCod: tr.dataset.centroCusto,
        centroLabel: tr.dataset.centroLabel,
        campos: {
          descricao_os: tr.dataset.descricaoOs,
          cliente: tr.dataset.cliente,
          motivo_intervencao: tr.dataset.motivoIntervencao,
          ssm: tr.dataset.ssm
        }
      });

    });

  });

  /* ================================
     EXCLUIR
  ================================= */

  deleteBtn.addEventListener('click', e => {



    e.preventDefault();

    if (confirm('Deseja excluir esta OS?')) {
      window.location.href = deleteBtn.href;
    }
  });

});
