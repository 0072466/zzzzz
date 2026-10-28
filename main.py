import unicodedata

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

WATTS_PER_KILOWATT = 1000
HOURS_PER_DAY = 24
DAYS_PER_MONTH = 30
DAYS_PER_YEAR = 365
DEFAULT_TARIFF_PER_KWH = 0.50
HIGH_DAILY_CONSUMPTION_THRESHOLD_KWH = 30
SHOWER_DAILY_THRESHOLD_KWH = 3.5
AIR_CONDITIONER_DAILY_THRESHOLD_KWH = 8
LED_DAILY_THRESHOLD_KWH = 2
REFRIGERATOR_DAILY_THRESHOLD_KWH = 3.5
WASHER_DAILY_THRESHOLD_KWH = 1.2
MICROWAVE_DAILY_THRESHOLD_KWH = 1.2
OVEN_DAILY_THRESHOLD_KWH = 1
HAIR_DRYER_DAILY_THRESHOLD_KWH = 1.2
COMPUTER_DAILY_THRESHOLD_KWH = 1.5
TELEVISION_DAILY_THRESHOLD_KWH = 1
FAN_DAILY_THRESHOLD_KWH = 1.5
VIDEO_GAME_DAILY_THRESHOLD_KWH = 1
ROUTER_DAILY_THRESHOLD_KWH = 0.4

APPLIANCES = [
    {"name": "Geladeira", "watts": 150},
    {"name": "Chuveiro", "watts": 5500},
    {"name": "Ar-condicionado", "watts": 1200},
    {"name": "Televisão", "watts": 100},
    {"name": "Lavadora", "watts": 500},
    {"name": "Micro-ondas", "watts": 1200},
    {"name": "Computador", "watts": 200},
    {"name": "Notebook", "watts": 60},
    {"name": "Ventilador", "watts": 100},
    {"name": "Ferro de passar", "watts": 1000},
    {"name": "Forno elétrico", "watts": 1500},
    {"name": "Fritadeira elétrica", "watts": 1500},
    {"name": "Secador", "watts": 1500},
    {"name": "Lava-louças", "watts": 1500},
    {"name": "Videogame", "watts": 200},
    {"name": "Cafeteira", "watts": 800},
    {"name": "Roteador", "watts": 10},
    {"name": "Lâmpadas LED", "watts": 8},
]

ENERGY_SAVING_TIP_RULES = [
    ("chuveiro", SHOWER_DAILY_THRESHOLD_KWH, "Chuveiro está consumindo mais do que o recomendado. Tente reduzir o tempo do banho em alguns minutos."),
    ("ar-condicionado", AIR_CONDITIONER_DAILY_THRESHOLD_KWH, "Ar-condicionado está muito acima do ideal. Aumente a temperatura um pouco e reduza o uso em horários de pico."),
    ("lampada", LED_DAILY_THRESHOLD_KWH, "Lâmpadas LED estão sendo usadas por muito tempo. Aproveite mais luz natural e reduza o tempo de iluminação."),
    ("geladeira", REFRIGERATOR_DAILY_THRESHOLD_KWH, "Geladeira está consumindo mais do que o esperado. Verifique a vedação da porta e evite abrir muito."),
    ("lavadora", WASHER_DAILY_THRESHOLD_KWH, "Lavadora está elevando o consumo. Use cargas completas e reduza o número de ciclos."),
    ("micro-ondas", MICROWAVE_DAILY_THRESHOLD_KWH, "Micro-ondas está consumindo bastante. Prefira outras formas de aquecimento quando possível."),
    ("forno", OVEN_DAILY_THRESHOLD_KWH, "Forno elétrico está elevando o gasto. Tente usar o forno somente quando realmente necessário."),
    ("secador", HAIR_DRYER_DAILY_THRESHOLD_KWH, "Secador elétrico está muito pesado na conta. Reduza o tempo de uso ou priorize secagem natural."),
    ("computador", COMPUTER_DAILY_THRESHOLD_KWH, "Computador está com uso longo. Desligue quando não estiver usando para economizar."),
    ("televisao", TELEVISION_DAILY_THRESHOLD_KWH, "Televisão está consumindo mais do que o ideal. Reduza o tempo de uso e desligue quando não estiver assistindo."),
    ("ventilador", FAN_DAILY_THRESHOLD_KWH, "Ventilador está sendo usado muito tempo. Use em horários certos e em conjunto com ventilação natural."),
    ("videogame", VIDEO_GAME_DAILY_THRESHOLD_KWH, "Videogame está consumindo bastante. Reduza o horário de uso e desligue o aparelho quando não estiver em uso."),
    ("roteador", ROUTER_DAILY_THRESHOLD_KWH, "Roteador está ligado por muito tempo. A gestão de rede e uso consciente ajuda a reduzir o consumo."),
]


def parse_decimal(value):
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Os campos aceitam valores no formato brasileiro, como "1.234,5".
        text = str(value).replace(" ", "").replace(".", "").replace(",", ".")
        return float(text)
    except ValueError:
        return 0.0


def calculate_appliance_daily_kwh(appliance):
    watts = parse_decimal(appliance.get("watts", 0))
    quantity = parse_decimal(appliance.get("quantidade", 0))
    hours_per_day = parse_decimal(appliance.get("horas", 0))
    return (watts * quantity * hours_per_day) / WATTS_PER_KILOWATT


def normalize_appliance_name(name):
    decomposed_name = unicodedata.normalize("NFKD", name.lower())
    # A comparação sem acentos faz as regras funcionarem com nomes em português.
    return "".join(character for character in decomposed_name if not unicodedata.combining(character))


def generate_energy_saving_tips(appliances):
    tips = []
    seen = set()

    def add_tip(tip):
        # Um aparelho pode satisfazer mais de uma regra com a mesma recomendação.
        if tip not in seen:
            seen.add(tip)
            tips.append(tip)

    total_daily_kwh = sum(calculate_appliance_daily_kwh(appliance) for appliance in appliances)

    if total_daily_kwh > HIGH_DAILY_CONSUMPTION_THRESHOLD_KWH:
        add_tip("Seu consumo diário está acima do ideal. Revise o uso do chuveiro, ar-condicionado e outros aparelhos de maior potência.")

    for appliance in appliances:
        daily_kwh = calculate_appliance_daily_kwh(appliance)

        name = normalize_appliance_name(str(appliance.get("name", "")))
        if daily_kwh <= 0:
            continue

        for appliance_keyword, threshold_kwh, tip in ENERGY_SAVING_TIP_RULES:
            if appliance_keyword in name and daily_kwh > threshold_kwh:
                add_tip(tip)

    return tips


def calculate_energy(payload):
    city = payload.get("cidade", "Sua cidade")
    tariff_per_kwh = parse_decimal(payload.get("tarifa", DEFAULT_TARIFF_PER_KWH))
    appliances = payload.get("appliances", [])

    daily_consumption_kwh = sum(calculate_appliance_daily_kwh(appliance) for appliance in appliances)
    daily_cost = daily_consumption_kwh * tariff_per_kwh
    hourly_consumption_kwh = daily_consumption_kwh / HOURS_PER_DAY
    hourly_cost = daily_cost / HOURS_PER_DAY
    monthly_consumption_kwh = daily_consumption_kwh * DAYS_PER_MONTH
    monthly_cost = daily_cost * DAYS_PER_MONTH
    annual_consumption_kwh = daily_consumption_kwh * DAYS_PER_YEAR
    annual_cost = daily_cost * DAYS_PER_YEAR

    result = {
        "cidade": city,
        "consumo_diario": daily_consumption_kwh,
        "custo_diario": daily_cost,
        "consumo_hora": hourly_consumption_kwh,
        "custo_hora": hourly_cost,
        "consumo_mensal": monthly_consumption_kwh,
        "custo_mensal": monthly_cost,
        "consumo_anual": annual_consumption_kwh,
        "custo_anual": annual_cost,
    }

    result["dicas"] = generate_energy_saving_tips(appliances)
    return result


@app.get("/")
def index():
    return render_template("index.html", appliances=APPLIANCES)


@app.post("/api/calculate")
def api_calculate():
    payload = request.get_json(silent=True) or {}
    result = calculate_energy(payload)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)