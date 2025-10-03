(() => {
  const cfg = window.GUI_CONFIG || { rows: 4, cols: 5 };
  const rows = cfg.rows;
  const cols = cfg.cols;

  // Well state matrix (rows x cols)
  // Convention: rows-1 ist unterste Reihe (Stammlösung)
  const state = Array.from({ length: rows }, () => Array(cols).fill(false));

  const grid = document.getElementById('wellGrid');
  const btnStart = document.getElementById('startBtn');
  const btnCancel = document.getElementById('cancelBtn');

  function wellId(r, c) { return `well-${r}-${c}`; }

  function renderGrid() {
    grid.innerHTML = '';
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const el = document.createElement('div');
        el.id = wellId(r, c);
        el.classList.add('well');

        const isBottom = r === rows - 1;
        const checked = state[r][c];

        // Color logic nach Mock-Vorlage im Bild:
        // Oberste Zeile: hell-rot (inactive red), mittlere: rot aktiv, unterste: grün aktiv, letzte Spalte etwas heller
        if (r === rows - 1) {
          // bottom row (clickable toggles the entire column)
          el.classList.add('clickable');
          el.classList.add(checked ? 'active-green' : 'inactive-green');
          el.addEventListener('click', () => toggleColumn(c));
        } else if (r === 0) {
          el.classList.add(checked ? 'active-red' : 'inactive');
        } else {
          el.classList.add(checked ? 'active-red' : 'inactive');
        }

        grid.appendChild(el);
      }
    }
  }

  function toggleColumn(c) {
    // Mehrfaches Toggle erlauben: orientiere dich am Zustand der untersten Zelle,
    // setze alle ERLAUBTEN Reihen (laut Checkboxen) auf das Ziel; verbotene Reihen bleiben aus.
    const bottomWas = state[rows - 1][c];
    const target = !bottomWas;

    for (let r = 0; r < rows - 1; r++) {
      if (isRowEnabled(r)) {
        state[r][c] = target;
      } else {
        state[r][c] = false;
      }
    }
    // Stammlösung (unterste) folgt immer dem Toggle
    state[rows - 1][c] = target;
    renderGrid();
  }

  // Left side nice checkboxes toggle entire rows (except stock volume input row)
  function attachRowCheckboxes() {
    for (let r = 0; r < rows - 1; r++) {
      const el = document.getElementById(`rowCheck-${r}`);
      if (!el) continue;
      const initial = el.getAttribute('aria-checked') === 'true';
      if (initial) el.classList.add('checked');
      state[r].fill(initial);
      el.addEventListener('click', () => toggleRowCheckbox(el, r));
      el.addEventListener('keydown', (e) => {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          toggleRowCheckbox(el, r);
        }
      });
    }
    // Verdünnung 1 (r=2) muss immer aktiv sein -> setze state[2] auf true (Checkbox existiert nicht)
    if (rows >= 3) state[2].fill(true);
    // Stammlösung (unterste Reihe) initial aktiv
    state[rows - 1].fill(true);
  }

  function toggleRowCheckbox(el, r) {
    let checked = !(el.getAttribute('aria-checked') === 'true');

    // Regel: Wenn Verdünnung 3 (r==0) gewählt ist, darf Verdünnung 2 (r==1) nicht abgewählt werden
    if (r === 1) {
      const v3 = document.getElementById('rowCheck-0');
      const v3On = v3 && v3.getAttribute('aria-checked') === 'true';
      if (v3On && checked === false) {
        // verbieten, V2 abzuwählen wenn V3 aktiv ist
        return; 
      }
    }
    // Wenn V3 aktiviert wird, stelle sicher, dass V2 auch aktiv ist
    if (r === 0 && checked === true) {
      const v2 = document.getElementById('rowCheck-1');
      if (v2 && v2.getAttribute('aria-checked') !== 'true') {
        v2.setAttribute('aria-checked', 'true');
        v2.classList.add('checked');
        state[1].fill(true);
      }
    }

    // Verdünnung 1 (r=2) darf nicht deaktiviert werden (Safety):
    if (r === 2 && checked === false) {
      checked = true;
    }

    el.setAttribute('aria-checked', String(checked));
    el.classList.toggle('checked', checked);
    state[r].fill(checked);

    // Nach Änderung: Spaltenstatus beschneiden gemäß erlaubten Reihen
    constrainColumnsToEnabledRows();
    renderGrid();
  }

  function isRowEnabled(r) {
    // r: 0..rows-2 (ohne Stammlösung)
    if (r === 2) return true; // Verdünnung 1 immer aktiv
    const el = document.getElementById(`rowCheck-${r}`);
    return !!(el && el.getAttribute('aria-checked') === 'true');
  }

  function constrainColumnsToEnabledRows() {
    // Lösche alle Zellen in nicht erlaubten Reihen
    for (let c = 0; c < cols; c++) {
      for (let r = 0; r < rows - 1; r++) {
        if (!isRowEnabled(r)) state[r][c] = false;
      }
    }
  }

  async function startProgram() {
    const payload = {
      program: 'dilute',
      params: {
        grid: state,
        stockVolume: parseFloat(document.getElementById('stockVolume').value || '0')
      }
    };
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.task_id) {
      notify('Task gestartet: ' + data.task_id);
    } else {
      notify('Fehler: ' + (data.error || JSON.stringify(data)), true);
    }
  }

  function notify(msg, isErr=false) {
    console[isErr ? 'error' : 'log'](msg);
  }

  function cancelProgram() {
    // Placeholder: Könnte später aktiven Task abbrechen
    notify('Cancel gedrückt – Implementierung folgt');
  }

  function init() {
    attachRowCheckboxes();
    renderGrid();
    btnStart.addEventListener('click', startProgram);
    btnCancel.addEventListener('click', cancelProgram);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
