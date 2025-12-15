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
  // Loader-UI wurde auf eine separate Seite ausgelagert

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
    // Ensure bottom row (stock) is active before propagating initial row states
    state[rows - 1].fill(true);
    // Verdünnung 1 (r=2) muss immer aktiv sein -> setze initialen Zustand (wird beschränkt auf aktive Spalten)
    if (rows >= 3) {
      for (let c = 0; c < cols; c++) state[2][c] = true && state[rows - 1][c];
    }

    for (let r = 0; r < rows - 1; r++) {
      const el = document.getElementById(`rowCheck-${r}`);
      if (!el) continue;
      const initial = el.getAttribute('aria-checked') === 'true';
      if (initial) el.classList.add('checked');
      // When initializing a row, only enable columns that themselves are enabled (bottom row)
      for (let c = 0; c < cols; c++) {
        state[r][c] = initial ? !!state[rows - 1][c] : false;
      }
      el.addEventListener('click', () => toggleRowCheckbox(el, r));
      el.addEventListener('keydown', (e) => {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          toggleRowCheckbox(el, r);
        }
      });
    }
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
        for (let c = 0; c < cols; c++) {
          state[1][c] = !!state[rows - 1][c];
        }
      }
    }

    // Verdünnung 1 (r=2) darf nicht deaktiviert werden (Safety):
    if (r === 2 && checked === false) {
      checked = true;
    }

    el.setAttribute('aria-checked', String(checked));
    el.classList.toggle('checked', checked);
    // When toggling a row on, only enable cells for columns that are enabled (bottom row)
    for (let c = 0; c < cols; c++) {
      state[r][c] = checked ? !!state[rows - 1][c] : false;
    }

    // Nach Änderung: Spaltenstatus beschneiden gemäß erlaubten Reihen
    constrainColumnsToEnabledRows();
    renderGrid();
    setEnabledInputs();
  }

  function setInputClass(el, notEnabled){
    if (notEnabled) {
      el.classList.add("input-disabled");
      el.classList.remove("input-enabled");
    } else {
      el.classList.add("input-enabled");
      el.classList.remove("input-disabled");
    }
  }

  function setEnabledInputs() {
    // Enable/disable input fields based on checkbox state
    // Rows 0 and 1 have checkboxes that control their inputs


      const checkbox3El = document.getElementById(`rowCheck-0`);
      const factor3El   = document.getElementById(`factor-0`);
      const fill3El     = document.getElementById(`fill-0`);

      const checkbox2El = document.getElementById(`rowCheck-1`);
      const factor2El   = document.getElementById(`factor-1`);
      const fill2El     = document.getElementById(`fill-1`);

      const factor1El   = document.getElementById(`factor-2`);
      const fill1El   = document.getElementById(`fill-2`);

      const v3 = checkbox3El.getAttribute('aria-checked') === 'true'
      const v2 = checkbox2El.getAttribute('aria-checked') === 'true'

      
      factor3El.disabled   = !v3;
      factor3El.setAttribute('aria-disabled', String(!v3));
      setInputClass(factor3El, !v3);
      factor2El.disabled   = !v2;
      factor2El.setAttribute('aria-disabled', String(!v2));
      setInputClass(factor2El, !v2);
      setInputClass(factor1El, false)

      if(v3 === true){
        fill3El.disabled = false;
        fill2El.disabled = true;
        fill1El.disabled = true;
        fill3El.setAttribute('aria-disabled', String(false));
        fill2El.setAttribute('aria-disabled', String(true));
        fill1El.setAttribute('aria-disabled', String(true));
        setInputClass(fill3El, false);
        setInputClass(fill2El, true);
        setInputClass(fill1El, true);


      }
      else if (v3 === false && v2 === true) {
        fill3El.disabled = true;
        fill2El.disabled = false;
        fill1El.disabled = true;
        fill3El.setAttribute('aria-disabled', String(true));
        fill2El.setAttribute('aria-disabled', String(false));
        fill1El.setAttribute('aria-disabled', String(true));
        setInputClass(fill3El, true);
        setInputClass(fill2El, false);
        setInputClass(fill1El, true);
      } 
      else if (v3 === false && v2 === false) {
        fill3El.disabled = true;
        fill2El.disabled = true;
        fill1El.disabled = false;
        fill3El.setAttribute('aria-disabled', String(true));
        fill2El.setAttribute('aria-disabled', String(true));
        fill1El.setAttribute('aria-disabled', String(false));
        setInputClass(fill3El, true);
        setInputClass(fill2El, true);
        setInputClass(fill1El, false);
      }
    
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

  function collectFactors() {
    // Mapping: row index -> factor value (nur für Reihen 0..2)
    const factors = {};
    for (let r = 0; r < rows - 1; r++) {
      const el = document.getElementById(`factor-${r}`) //|| document.getElementById(`factor-${r}`);
      // aufgrund manueller Umbenennungen im Template robust lesen
      const val = el && el.value !== '' ? Number(el.value) : null;
      if (val !== null && !Number.isNaN(val)) factors[r] = val;
    }
    return factors;
  }

  function collectFills() {
    // Mapping: row index -> fill value (nur für Reihen 0..2)
    const fills = {};
    for (let r = 0; r < rows - 1; r++) {
      const el = document.getElementById(`fill-${r}`);
      const val = el && el.value !== '' ? Number(el.value) : null;
      if (val !== null && !Number.isNaN(val)) fills[r] = val;
    }
    return fills;
  }

  function collectEnabledRows() {
    const enabled = {};
    for (let r = 0; r < rows - 1; r++) enabled[r] = isRowEnabled(r);
    enabled[rows - 1] = true; // Stammlösung
    return enabled;
  }

  async function callApi(url, payload) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return res.json();
  }

  async function startProgram() {
    clearError();
    const payload = {
      grid: state,
      enabledRows: collectEnabledRows(),
      factors: collectFactors(),
      fills: collectFills(),
      stockVolume: parseFloat(document.getElementById('stockVolume').value || '0'),
      cover: getCoverCheckboxValue()
    };
    const data = await callApi('/api/start', payload);

    if (data.error) {
      showError(data.error);
      return;
    }
    if (data && data.ok) {
      notify('Eingaben geprüft');
      // Verarbeiteten Payload an Check-Seite übergeben
      const form = document.querySelector("form");
      const dataInput = document.createElement("input");
      dataInput.type = "hidden";
      dataInput.name = "processedData";
      dataInput.value = JSON.stringify(data.data);
      form.appendChild(dataInput);
      form.submit(); // zeigt die Check-Seite VOR Start
    } else {
      notify('Prüfung fehlgeschlagen', true);
    }
  }

  function notify(msg, isErr=false) {
    console[isErr ? 'error' : 'log'](msg);
  }

  async function cancelProgram() {
    const payload = {
      reason: 'user',
      timestamp: Date.now()
    };
    const data = await callApi('/api/cancel', payload);
    if (data && data.ok) notify('Cancel gesendet'); else notify('Cancel fehlgeschlagen', true);
  }


  function getCoverCheckboxValue() {
    const el = document.getElementById("cover");
    return el.getAttribute("aria-checked") === "true";
  }

  function toggleCoverCheckbox(el) {
    const checked = !(el.getAttribute('aria-checked') === 'true');
    el.setAttribute('aria-checked', String(checked));
    el.classList.toggle('checked', checked);
  }

  function setCoverCheckbox(value) {
    const el = document.getElementById("cover");
    el.setAttribute('aria-checked', String(value));
    el.classList.toggle('checked', value);
  }

  function showError(msg) {
    const box = document.getElementById("errorBox");
    box.textContent = msg;
    box.style.display = "block";
  }

  function clearError() {
    const box = document.getElementById("errorBox");
    box.textContent = "";
    box.style.display = "none";
  }

  // In-Page-Polling entfällt, da die Laufzeit-Seite dies übernimmt

  function init() {
    attachRowCheckboxes();
    renderGrid();
    setEnabledInputs();
    setCoverCheckbox(getCoverCheckboxValue());
    btnStart.addEventListener('click', startProgram);
    btnCancel.addEventListener('click', cancelProgram);
    document.getElementById("cover").addEventListener("click", () => {
    toggleCoverCheckbox(document.getElementById("cover"));
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
