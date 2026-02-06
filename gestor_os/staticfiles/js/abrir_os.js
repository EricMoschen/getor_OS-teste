document.addEventListener('DOMContentLoaded', () => {
  const selected = document.getElementById('dropdownSelected');
  const list = document.getElementById('dropdownList');
  const hiddenInput = document.getElementById('centro_custo');

  function toggleList(show) {
    if (typeof show === 'boolean') {
      list.classList.toggle('hidden', !show);
      list.setAttribute('aria-hidden', String(!show));
    } else {
      list.classList.toggle('hidden');
      list.setAttribute('aria-hidden', String(list.classList.contains('hidden')));
    }
  }

  selected.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleList();
  });

  // fecha ao clicar fora
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-container')) {
      list.classList.add('hidden');
      list.setAttribute('aria-hidden', 'true');
    }
  });

  // delegação de eventos para abrir/fechar e selecionar
  list.addEventListener('click', (e) => {
    const parentItem = e.target.closest('.dropdown-item.parent');
    const childItem = e.target.closest('.dropdown-item.child');

    // selecionar child
    if (childItem) {
      const cod = childItem.dataset.cod;
      const label = childItem.dataset.label || childItem.querySelector('.text')?.textContent.trim();
      hiddenInput.value = cod;
      selected.textContent = label;
      toggleList(false);
      return;
    }

    // clicar no texto do parent seleciona o parent
    if (parentItem) {
      const clickedElem = e.target;
      const isArrow = clickedElem.classList.contains('arrow');
      const parentCod = parentItem.dataset.cod;
      const parentLabel = parentItem.dataset.label || parentItem.querySelector('.text')?.textContent.trim();
      const childrenDiv = document.getElementById(`children-${parentCod}`);

      // se clicou na flecha → toggle expandir/recolher; ao expandir fecha outros
      if (isArrow) {
        // fecha outros abertos
        document.querySelectorAll('.dropdown-children').forEach(div => {
          if (div !== childrenDiv) {
            div.classList.add('hidden');
            const prev = div.previousElementSibling;
            if (prev && prev.classList.contains('parent')) {
              prev.setAttribute('aria-expanded', 'false');
              const arrow = prev.querySelector('.arrow');
              if (arrow) arrow.textContent = '▶';
            }
          }
        });

        if (!childrenDiv) return;
        const nowHidden = childrenDiv.classList.toggle('hidden');
        parentItem.setAttribute('aria-expanded', String(!nowHidden));
        const arrow = parentItem.querySelector('.arrow');
        if (arrow) arrow.textContent = nowHidden ? '▶' : '▼';
        return;
      }

      // se clicou no texto do pai → seleciona o pai
      hiddenInput.value = parentCod;
      selected.textContent = parentLabel;
      toggleList(false);
      return;
    }
  });

  // keyboard
  selected.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleList();
    }
  });

  list.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      toggleList(false);
      selected.focus();
    }
  });
});