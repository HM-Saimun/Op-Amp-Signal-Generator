const amplifierNames = {
  inverting: "Inverting amplifier",
  non_inverting: "Non-inverting amplifier",
  integrator: "Integrator",
  differentiator: "Differentiator",
  summing: "Summing amplifier",
};

const state = { amplifier: "inverting" };
const resistanceUnits = [["ohm", "ohm"], ["kOhm", "kOhm"], ["MOhm", "MOhm"]];
const voltageUnits = [["V", "V"], ["mV", "mV"]];
const capacitanceUnits = [["F", "F"], ["mF", "mF"], ["uF", "uF"], ["nF", "nF"], ["pF", "pF"]];

function quantityField(key, label, units, value, unit) {
  const options = units.map(([code, title]) =>
    `<option value="${code}"${code === unit ? " selected" : ""}>${title}</option>`
  ).join("");
  return `<div class="field"><label for="${key}">${label}</label><div class="field-control">
    <input id="${key}" name="${key}" type="number" step="any" value="${value}" required>
    <select name="${key}_unit" aria-label="${label} unit">${options}</select>
  </div></div>`;
}

function numberField(key, label, value, unit = "") {
  return `<div class="field"><label for="${key}">${label}</label><div class="field-control">
    <input id="${key}" name="${key}" type="number" step="any" value="${value}" required>
    ${unit ? `<span class="unit-suffix">${unit}</span>` : ""}
  </div></div>`;
}

function signalTypeField() {
  return `<div class="field"><label for="signal_type">Input waveform</label><div class="field-control">
    <select id="signal_type" name="signal_type" required>
      <option value="1">Sine wave</option><option value="2">Square wave</option><option value="3">Triangle wave</option>
    </select>
  </div></div>`;
}

function fieldsFor(amplifier, count) {
  if (amplifier === "inverting") {
    return quantityField("R", "Input resistor R", resistanceUnits, 10, "kOhm")
      + quantityField("Rf", "Feedback resistor Rf", resistanceUnits, 100, "kOhm")
      + quantityField("Vin_amp", "Input amplitude", voltageUnits, 0.5, "V")
      + quantityField("Vcc_pos", "Positive supply +Vcc", voltageUnits, 12, "V")
      + quantityField("Vcc_neg", "Negative supply -Vee", voltageUnits, -12, "V")
      + quantityField("RL", "Load resistor RL", resistanceUnits, 10, "kOhm");
  }
  if (amplifier === "non_inverting") {
    return quantityField("R1", "Ground resistor R1", resistanceUnits, 10, "kOhm")
      + quantityField("R2", "Feedback resistor R2", resistanceUnits, 90, "kOhm")
      + quantityField("Vi_amp", "Input amplitude", voltageUnits, 0.5, "V")
      + quantityField("Vcc_pos", "Positive supply +Vcc", voltageUnits, 12, "V")
      + quantityField("Vcc_neg", "Negative supply -Vee", voltageUnits, -12, "V")
      + quantityField("RL", "Load resistor RL", resistanceUnits, 10, "kOhm");
  }
  if (amplifier === "integrator" || amplifier === "differentiator") {
    return quantityField("R", "Input resistor R", resistanceUnits, 10, "kOhm")
      + quantityField("C", "Capacitor C", capacitanceUnits, 100, "nF")
      + quantityField("Vin_amp", "Input amplitude", voltageUnits, 1, "V")
      + signalTypeField();
  }
  let html = "";
  for (let index = 1; index <= count; index += 1) {
    html += quantityField(`Vin${index}_amp`, `Input ${index} amplitude`, voltageUnits, index === 1 ? 0.5 : 0.25, "V");
    html += quantityField(`Ri${index}`, `Input resistor R${index}`, resistanceUnits, index === 1 ? 10 : 20, "kOhm");
  }
  return html
    + quantityField("Rf", "Feedback resistor Rf", resistanceUnits, 100, "kOhm")
    + quantityField("Vcc_pos", "Positive supply +Vcc", voltageUnits, 12, "V")
    + quantityField("Vcc_neg", "Negative supply -Vee", voltageUnits, -12, "V")
    + numberField("f", "Input frequency", 50, "Hz")
    + quantityField("RL", "Load resistor RL", resistanceUnits, 10, "kOhm");
}

const wire = (path) => `<path class="wire" d="${path}"/>`;
const label = (x, y, value, className = "diagram-text", anchor = "middle") =>
  `<text class="${className}" text-anchor="${anchor}" x="${x}" y="${y}">${value}</text>`;

function horizontalResistor(x1, x2, y, name) {
  const mid = (x1 + x2) / 2;
  const start = x1 + 12;
  const end = x2 - 12;
  const step = (end - start) / 6;
  const points = Array.from({ length: 7 }, (_, index) => {
    const level = index === 0 || index === 6 ? y : y + (index % 2 ? -8 : 8);
    return `${start + step * index} ${level}`;
  }).join("L");
  return wire(`M${x1} ${y}L${points}L${x2} ${y}`)
    + label(mid, y - 15, name);
}

function verticalResistor(x, y1, y2, name) {
  return wire(
    `M${x} ${y1}V${y1 + 10}L${x - 8} ${y1 + 20}L${x + 8} ${y1 + 30}`
      + `L${x - 8} ${y1 + 40}L${x + 8} ${y1 + 50}L${x} ${y2 - 10}V${y2}`
  ) + label(x + 19, (y1 + y2) / 2 + 4, name, "diagram-text", "start");
}

function horizontalCapacitor(x1, x2, y, name) {
  const mid = (x1 + x2) / 2;
  return wire(`M${x1} ${y}H${mid - 4}`)
    + wire(`M${mid - 4} ${y - 14}V${y + 14}`)
    + wire(`M${mid + 4} ${y - 14}V${y + 14}`)
    + wire(`M${mid + 4} ${y}H${x2}`)
    + label(mid, y - 20, name);
}

function ground(x, y) {
  return wire(`M${x} ${y}v8m-12 0h24m-18 6h12m-8 6h4`);
}

function junction(x, y) {
  return `<circle class="junction" cx="${x}" cy="${y}" r="4"/>`;
}

function inputSource(y, endX, name) {
  return wire(`M45 ${y}H58`)
    + `<circle class="source-symbol" cx="70" cy="${y}" r="12"/>`
    + `<path class="source-wave" d="M66 ${y}c2-6 6-6 8 0s6 6 8 0"/>`
    + wire(`M82 ${y}H${endX}`)
    + label(70, y - 18, name, "diagram-small");
}

function opAmp() {
  return `<path class="amp-shape" d="M350 110l120 50-120 50z"/>`
    + label(365, 145, "−")
    + label(365, 185, "+")
    + wire("M390 126V92M390 194V228")
    + label(405, 96, "+Vcc", "diagram-small", "start")
    + label(405, 244, "−Vee", "diagram-small", "start");
}

function groundedNonInvertingInput() {
  return wire("M350 180H315V232") + ground(315, 232);
}

function amplifierOutput() {
  return wire("M470 160H700")
    + label(708, 164, "Vout", "diagram-accent", "start")
    + wire("M610 160V180")
    + verticalResistor(610, 180, 252, "RL")
    + ground(610, 252);
}

function feedbackResistor(returnX, name) {
  return wire(`M${returnX} 140V68H420`)
    + horizontalResistor(420, 510, 68, name)
    + wire("M510 68H650V160")
    + junction(650, 160);
}

const diagrams = {
  inverting: `<g>
    ${inputSource(140, 115, "Vin")}${horizontalResistor(115, 215, 140, "R")}${wire("M215 140H350")}
    ${feedbackResistor(350, "Rf")}${groundedNonInvertingInput()}
    ${opAmp()}${amplifierOutput()}${junction(350, 140)}
  </g>`,
  non_inverting: `<g>
    ${inputSource(180, 350, "Vin")}
    ${wire("M350 140H300V140H25V188")}${verticalResistor(25, 188, 258, "R1")}${ground(25, 258)}
    ${wire("M300 140V68H420")}${horizontalResistor(420, 510, 68, "R2")}${wire("M510 68H650V160")}
    ${opAmp()}${amplifierOutput()}
    ${junction(300, 140)}${junction(650, 160)}
  </g>`,
  integrator: `<g>
    ${inputSource(140, 100, "Vin")}${horizontalResistor(100, 200, 140, "R")}${wire("M200 140H350")}
    ${wire("M350 140V68H450")}${horizontalCapacitor(450, 550, 68, "C")}${wire("M550 68H650V160")}
    ${groundedNonInvertingInput()}${opAmp()}${amplifierOutput()}
    ${junction(350, 140)}${junction(650, 160)}
  </g>`,
  differentiator: `<g>
    ${inputSource(140, 100, "Vin")}${horizontalCapacitor(100, 180, 140, "C")}${wire("M180 140H350")}
    ${feedbackResistor(350, "R")}${groundedNonInvertingInput()}
    ${opAmp()}${amplifierOutput()}${junction(350, 140)}
  </g>`,
  summing: `<g>
    ${[90, 140, 190].map((y, index) => (
      inputSource(y, 100, index < 2 ? `Vin${index + 1}` : "Vinn")
      + horizontalResistor(100, 200, y, index < 2 ? `R${index + 1}` : "Rn")
      + wire(`M200 ${y}H300`)
    )).join("")}
    ${wire("M300 90V190M300 140H350M300 140V68H420")}
    ${horizontalResistor(420, 510, 68, "Rf")}${wire("M510 68H650V160")}
    ${groundedNonInvertingInput()}${opAmp()}${amplifierOutput()}
    ${junction(300, 90)}${junction(300, 140)}${junction(300, 190)}${junction(650, 160)}
  </g>`,
};

function updateDiagram() {
  document.getElementById("circuit-diagram").innerHTML =
    `<title>${amplifierNames[state.amplifier]} schematic</title>${diagrams[state.amplifier]}`;
  document.getElementById("diagram-title").textContent = amplifierNames[state.amplifier];
  document.getElementById("page-title").textContent = amplifierNames[state.amplifier];
}

function updateForm() {
  const isSumming = state.amplifier === "summing";
  const countWrap = document.getElementById("signal-count-wrap");
  countWrap.hidden = !isSumming;
  document.getElementById("input-fields").innerHTML =
    fieldsFor(state.amplifier, Number(document.getElementById("signal-count").value));
  updateDiagram();
}

function readForm() {
  const form = document.getElementById("simulation-form");
  const inputs = {};
  for (const control of form.querySelectorAll("input, select")) {
    if (control.name.endsWith("_unit")) continue;
    if (control.name === "signal_type") {
      inputs[control.name] = control.value;
    } else if (control.type === "number") {
      const unit = form.elements[`${control.name}_unit`];
      inputs[control.name] = unit
        ? { value: Number(control.value), unit: unit.value }
        : Number(control.value);
    }
  }
  if (state.amplifier === "summing") {
    inputs.signal_count = Number(document.getElementById("signal-count").value);
  }
  return inputs;
}

function formatKey(key) {
  return key.replaceAll("_", " ");
}

function formatValue(value) {
  if (value && typeof value === "object" && "value" in value) {
    return `${value.value} ${value.unit}`;
  }
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return Number(value.toPrecision(5)).toString();
  return String(value);
}

function appendDetailsCell(row, title, record) {
  const cell = document.createElement("td");
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  const content = document.createElement("small");
  summary.textContent = title;
  content.textContent = Object.entries({ ...record.inputs, ...record.outputs })
    .map(([key, value]) => `${formatKey(key)}: ${formatValue(value)}`)
    .join("\n");
  details.append(summary, content);
  const waveformDetails = document.createElement("details");
  const waveformSummary = document.createElement("summary");
  const waveform = document.createElement("pre");
  waveformSummary.textContent = "Full waveform samples";
  waveform.textContent = "Expand to load saved waveform data.";
  waveformDetails.append(waveformSummary, waveform);
  let waveformLoaded = false;
  waveformDetails.addEventListener("toggle", async () => {
    if (!waveformDetails.open || waveformLoaded) return;
    waveform.textContent = "Loading waveform samples…";
    try {
      const response = await fetch(`/api/history/${encodeURIComponent(record.id)}`);
      if (!response.ok) throw new Error("Could not load waveform samples.");
      const fullRecord = await response.json();
      waveform.textContent = JSON.stringify(fullRecord.outputs, null, 2);
      waveformLoaded = true;
    } catch (error) {
      waveform.textContent = error.message;
    }
  });
  details.append(waveformDetails);
  cell.append(details);
  row.append(cell);
}

function addHistoryRow(record) {
  const row = document.createElement("tr");
  const session = document.createElement("td");
  const sessionTitle = document.createElement("strong");
  const sessionId = document.createElement("small");
  sessionTitle.textContent = record.amplifier;
  sessionId.className = "session-id";
  sessionId.textContent = `${new Date(record.created_at).toLocaleString()} · ${record.id.slice(-8)}`;
  session.append(sessionTitle, sessionId);
  row.append(session);
  appendDetailsCell(row, "Inputs / results", record);
  const plots = document.createElement("td");
  const links = document.createElement("div");
  links.className = "plot-links";
  record.image_urls.forEach((url, index) => {
    const link = document.createElement("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = `Plot ${index + 1} ↗`;
    links.append(link);
  });
  plots.append(links);
  row.append(plots);
  return row;
}

async function loadHistory() {
  const response = await fetch("/api/history");
  if (!response.ok) throw new Error("Could not load session history.");
  const records = await response.json();
  const body = document.getElementById("history-body");
  body.replaceChildren(...records.map(addHistoryRow));
  document.getElementById("history-count").textContent = records.length;
  document.getElementById("empty-history").hidden = records.length > 0;
}

function displayResult(record) {
  const card = document.getElementById("result-card");
  const summary = document.getElementById("result-summary");
  const images = document.getElementById("result-images");
  summary.replaceChildren();
  images.replaceChildren();
  Object.entries(record.outputs).forEach(([key, value]) => {
    const metric = document.createElement("div");
    const label = document.createElement("span");
    const output = document.createElement("strong");
    metric.className = "metric";
    label.textContent = formatKey(key);
    output.textContent = formatValue(value);
    metric.append(label, output);
    summary.append(metric);
  });
  record.image_urls.forEach((url, index) => {
    const figure = document.createElement("div");
    const image = document.createElement("img");
    const link = document.createElement("a");
    figure.className = "result-image";
    image.src = url;
    image.alt = `${record.amplifier} output plot ${index + 1}`;
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = "Open saved plot ↗";
    figure.append(image, link);
    images.append(figure);
  });
  card.hidden = false;
}

document.querySelectorAll(".amp-choice").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".amp-choice").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.amplifier = button.dataset.amplifier;
    document.getElementById("result-card").hidden = true;
    updateForm();
  });
});

document.getElementById("signal-count").addEventListener("change", (event) => {
  const count = Math.min(8, Math.max(1, Number(event.target.value) || 1));
  event.target.value = count;
  if (state.amplifier === "summing") updateForm();
});

document.getElementById("simulation-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector(".run-button");
  const error = document.getElementById("form-error");
  button.disabled = true;
  error.textContent = "";
  try {
    const response = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amplifier: state.amplifier, inputs: readForm() }),
    });
    const record = await response.json();
    if (!response.ok) throw new Error(record.error || "Simulation failed.");
    displayResult(record);
    await loadHistory();
    if (record.plot_window_error) error.textContent = record.plot_window_error;
  } catch (reason) {
    error.textContent = reason.message || "Simulation failed.";
  } finally {
    button.disabled = false;
  }
});

updateForm();
loadHistory().catch((error) => {
  document.getElementById("form-error").textContent = error.message;
});
