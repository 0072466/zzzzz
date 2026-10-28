const APPLIANCES = [
  { name: "Geladeira", watts: 150, quantidade: 1, horas: 24 },
  { name: "Chuveiro", watts: 5500, quantidade: 1, horas: 0.5 },
  { name: "Ar-condicionado", watts: 1200, quantidade: 1, horas: 6 },
  { name: "Televisão", watts: 100, quantidade: 1, horas: 4 },
  { name: "Lavadora", watts: 500, quantidade: 1, horas: 1 },
  { name: "Micro-ondas", watts: 1200, quantidade: 1, horas: 0.5 },
  { name: "Computador", watts: 200, quantidade: 1, horas: 4 },
  { name: "Notebook", watts: 60, quantidade: 1, horas: 5 },
  { name: "Ventilador", watts: 100, quantidade: 2, horas: 6 },
  { name: "Ferro de passar", watts: 1000, quantidade: 1, horas: 0.5 },
  { name: "Forno elétrico", watts: 1500, quantidade: 1, horas: 0.3 },
  { name: "Fritadeira elétrica", watts: 1500, quantidade: 1, horas: 0.4 },
  { name: "Secador", watts: 1500, quantidade: 1, horas: 0.6 },
  { name: "Lava-louças", watts: 1500, quantidade: 1, horas: 1 },
  { name: "Videogame", watts: 200, quantidade: 1, horas: 2 },
  { name: "Cafeteira", watts: 800, quantidade: 1, horas: 0.5 },
  { name: "Roteador", watts: 10, quantidade: 1, horas: 24 },
  { name: "Lâmpadas LED", watts: 8, quantidade: 8, horas: 5 }
];

const DEFAULT_TARIFF_PER_KWH = 0.50;
const INITIAL_TIPS_MESSAGE = "Preencha os dados e veja as sugestões mais relevantes para sua casa.";
const NO_TIPS_MESSAGE = "Seu consumo está dentro de um valor considerado normal. Continue mantendo hábitos eficientes.";
const RESULT_FIELDS = [
  { elementId: "consumoDiario", resultKey: "consumo_diario", formatter: formatKwh, emptyValue: "0,00 kWh" },
  { elementId: "custoDiario", resultKey: "custo_diario", formatter: formatMoney, emptyValue: "R$ 0,00" },
  { elementId: "consumoHora", resultKey: "consumo_hora", formatter: formatKwh, emptyValue: "0,00 kWh" },
  { elementId: "custoHora", resultKey: "custo_hora", formatter: formatMoney, emptyValue: "R$ 0,00" },
  { elementId: "consumoMensal", resultKey: "consumo_mensal", formatter: formatKwh, emptyValue: "0,00 kWh" },
  { elementId: "custoMensal", resultKey: "custo_mensal", formatter: formatMoney, emptyValue: "R$ 0,00" },
  { elementId: "consumoAnual", resultKey: "consumo_anual", formatter: formatKwh, emptyValue: "0,00 kWh" },
  { elementId: "custoAnual", resultKey: "custo_anual", formatter: formatMoney, emptyValue: "R$ 0,00" }
];

function parseDecimal(value) {
  if (value === "" || value === null || value === undefined) return 0;
  const cleaned = String(value).replace(/\s+/g, "").replace(".", "").replace(",", ".");
  const number = Number(cleaned);
  return Number.isFinite(number) ? number : 0;
}

function formatMoney(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL"
  }).format(value);
}

function formatKwh(value) {
  return `${Number(value).toFixed(2).replace(".", ",")} kWh`;
}

function renderApplianceCards() {
  const applianceList = document.getElementById("appliance-list");
  applianceList.innerHTML = "";

  APPLIANCES.forEach((appliance) => {
    const applianceCard = document.createElement("div");
    applianceCard.className = "appliance";

    applianceCard.innerHTML = `
      <div class="appliance-name">
        ${appliance.name}
        <small>${appliance.watts} W estimados</small>
      </div>

      <div class="field">
        <label>Quantidade</label>
        <input type="text" class="quantidade" value="${appliance.quantidade}" />
      </div>

      <div class="field">
        <label>Horas por dia</label>
        <input type="text" class="horas" value="${appliance.horas}" />
      </div>
    `;

    applianceList.appendChild(applianceCard);
  });
}

function buildCalculationPayload() {
  const selectedAppliances = [...document.querySelectorAll(".appliance")].map((applianceCard) => {
    const wattsText = applianceCard.querySelector(".appliance-name small").textContent.trim();
    const watts = parseDecimal(wattsText.match(/\d+([.,]\d+)?/g)?.[0] ?? "0");

    return {
      name: applianceCard.querySelector(".appliance-name").textContent.trim().split("\n")[0].trim(),
      watts,
      quantidade: parseDecimal(applianceCard.querySelector(".quantidade").value),
      horas: parseDecimal(applianceCard.querySelector(".horas").value)
    };
  });

  return {
    cidade: document.getElementById("cidade").value || "Sua cidade",
    tarifa: DEFAULT_TARIFF_PER_KWH,
    appliances: selectedAppliances
  };
}

function renderCalculationResults(result) {
  document.title = `REEN | Economia de Energia - ${result.cidade}`;
  document.getElementById("hero-kwh").textContent = Number(result.consumo_diario).toFixed(2).replace(".", ",");

  RESULT_FIELDS.forEach(({ elementId, resultKey, formatter }) => {
    document.getElementById(elementId).textContent = formatter(result[resultKey]);
  });
}

function renderTips(tips, emptyMessage = NO_TIPS_MESSAGE) {
  const tipList = document.getElementById("dica-list");
  tipList.innerHTML = "";

  (tips.length > 0 ? tips : [emptyMessage]).forEach((tip) => {
    const tipItem = document.createElement("li");
    tipItem.textContent = tip;
    tipList.appendChild(tipItem);
  });
}

async function calculateEnergyUsage() {
  const payload = buildCalculationPayload();

  const response = await fetch("/api/calculate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const result = await response.json();

  renderCalculationResults(result);
  renderTips(result.dicas);
}

function clearCalculationForm() {
  document.getElementById("cidade").value = "";
  document.querySelectorAll(".quantidade, .horas").forEach((input) => {
    input.value = "";
  });

  document.getElementById("hero-kwh").textContent = "0,00";
  RESULT_FIELDS.forEach(({ elementId, emptyValue }) => {
    document.getElementById(elementId).textContent = emptyValue;
  });

  renderTips([], INITIAL_TIPS_MESSAGE);
}

document.getElementById("calcular").addEventListener("click", calculateEnergyUsage);
document.getElementById("limpar").addEventListener("click", clearCalculationForm);

document.querySelectorAll(".quantidade, .horas").forEach((input) => {
  input.addEventListener("input", () => {
    input.value = input.value.replace(/[^0-9,.-]/g, "");
  });
});

document.getElementById("btnSimular").addEventListener("click", () => {
  document.getElementById("calculador").scrollIntoView({ behavior: "smooth" });
});

renderApplianceCards();
calculateEnergyUsage();