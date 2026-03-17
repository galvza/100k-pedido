"""Gera CSVs de amostra para testes com foreign keys consistentes."""

import csv
import os
import random
import uuid
from datetime import datetime, timedelta

random.seed(42)

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "tests", "fixtures"
)
os.makedirs(FIXTURES_DIR, exist_ok=True)


def uid() -> str:
    return uuid.uuid4().hex


def rand_ts(start: datetime, end: datetime) -> str:
    delta = end - start
    offset = random.randint(0, int(delta.total_seconds()))
    dt = start + timedelta(seconds=offset)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# =============================================================
# Parâmetros
# =============================================================

N_ORDERS = 200
N_ITEMS = 200
N_PAYMENTS = 200
N_REVIEWS = 200
N_CUSTOMERS = 200
N_PRODUCTS = 100
N_SELLERS = 30
N_GEO = 500
N_TRANSLATIONS = 71

# Datas
DATE_START = datetime(2017, 1, 1)
DATE_END = datetime(2018, 8, 31)

# Estados e cidades reais
STATES_CITIES = {
    "SP": ["sao paulo", "campinas", "santos", "guarulhos", "sorocaba"],
    "RJ": ["rio de janeiro", "niteroi", "petropolis", "volta redonda"],
    "MG": ["belo horizonte", "uberlandia", "juiz de fora", "contagem"],
    "RS": ["porto alegre", "caxias do sul", "pelotas"],
    "PR": ["curitiba", "londrina", "maringa"],
    "SC": ["florianopolis", "joinville", "blumenau"],
    "BA": ["salvador", "feira de santana", "vitoria da conquista"],
    "PE": ["recife", "jaboatao dos guararapes", "olinda"],
    "CE": ["fortaleza", "juazeiro do norte", "sobral"],
    "DF": ["brasilia"],
    "GO": ["goiania", "anapolis"],
    "PA": ["belem", "ananindeua"],
    "AM": ["manaus"],
    "ES": ["vitoria", "vila velha", "serra"],
    "MT": ["cuiaba", "rondonopolis"],
}

ALL_STATES = list(STATES_CITIES.keys())

# Pesos pra distribuição de estados (SP e RJ dominam)
STATE_WEIGHTS = {
    "SP": 50, "RJ": 20, "MG": 15, "RS": 8, "PR": 8, "SC": 6,
    "BA": 7, "PE": 5, "CE": 5, "DF": 4, "GO": 3, "PA": 2,
    "AM": 2, "ES": 3, "MT": 2,
}

STATUS_OPTIONS = ["delivered", "shipped", "canceled", "unavailable", "invoiced",
                  "processing", "created", "approved"]
STATUS_WEIGHTS = [150, 15, 10, 3, 5, 7, 5, 5]

PAYMENT_TYPES = ["credit_card", "boleto", "voucher", "debit_card"]
PAYMENT_WEIGHTS = [120, 40, 20, 20]

CATEGORIES_PT = [
    "beleza_saude", "informatica_acessorios", "automotivo", "cama_mesa_banho",
    "moveis_decoracao", "esporte_lazer", "perfumaria", "utilidades_domesticas",
    "telefonia", "relogios_presentes", "alimentos_bebidas", "bebes",
    "papelaria", "tablets_impressao_imagem", "brinquedos", "telefonia_fixa",
    "ferramentas_jardim", "fashion_bolsas_e_acessorios", "eletrionicos",
    "fashion_calcados", "pet_shop", "moveis_escritorio", "market_place",
    "consoles_games", "malas_acessorios", "construcao_ferramentas_construcao",
    "eletrodomesticos", "construcao_ferramentas_seguranca",
    "fashion_roupa_masculina", "industria_comercio_e_negocios",
    "moveis_sala", "livros_interesse_geral", "construcao_ferramentas_iluminacao",
    "fashion_underwear_e_moda_praia", "fashion_roupa_feminina",
    "sinalizacao_e_seguranca", "eletrodomesticos_2", "musica",
    "moveis_colchao_e_estofado", "artes_e_artesanato", "climatizacao",
    "moveis_cozinha_area_de_servico_jantar_e_jardim", "cool_stuff",
    "artigos_de_natal", "artigos_de_festas", "portateis_casa_forno_e_cafe",
    "casa_conforto", "audio", "cds_dvds_musicais", "dvds_blu_ray",
    "flores", "artes", "livros_tecnicos", "agro_industria_e_comercio",
    "casa_conforto_2", "pcs", "instrumentos_musicais",
    "seguros_e_servicos", "la_cuisine", "casa_construcao",
    "alimentos", "fashion_esporte", "fashion_roupa_infanto_juvenil",
    "construcao_ferramentas_jardim", "fashion_roupa_feminina",
    "cine_foto", "fraldas_higiene", "livros_importados",
    "pc_gamer", "portateis_cozinha_e_preparadores_de_alimentos", None,
]

CATEGORIES_EN = [
    "health_beauty", "computers_accessories", "auto", "bed_bath_table",
    "furniture_decor", "sports_leisure", "perfumery", "housewares",
    "telephony", "watches_gifts", "food_drink", "baby",
    "stationery", "tablets_printing_image", "toys", "fixed_telephony",
    "garden_tools", "fashion_bags_accessories", "electronics",
    "fashion_shoes", "pet_shop", "office_furniture", "market_place",
    "consoles_games", "luggage_accessories", "construction_tools_construction",
    "home_appliances", "construction_tools_safety",
    "fashion_male_clothing", "industry_commerce_and_business",
    "furniture_living_room", "books_general_interest", "construction_tools_lights",
    "fashion_underwear_beach", "fashion_female_clothing",
    "signaling_and_security", "home_appliances_2", "music",
    "furniture_mattress_and_upholstery", "arts_and_craftmanship", "air_conditioning",
    "furniture_kitchen_dining_laundry_garden", "cool_stuff",
    "christmas_supplies", "party_supplies", "small_appliances_home_oven_and_coffee",
    "home_comfort", "audio", "cds_dvds_musicals", "dvds_blu_ray",
    "flowers", "arts", "books_technical", "agro_industry_and_commerce",
    "home_comfort_2", "computers", "musical_instruments",
    "insurance_and_services", "la_cuisine", "home_construction",
    "food", "fashion_sport", "fashion_children_clothes",
    "garden_tools", "fashion_female_clothing",
    "cine_photo", "diapers_and_hygiene", "books_imported",
    None, None, None,
]


def pick_state() -> str:
    return random.choices(ALL_STATES, weights=[STATE_WEIGHTS[s] for s in ALL_STATES])[0]


def pick_city(state: str) -> str:
    return random.choice(STATES_CITIES[state])


def zip_for_state(state: str) -> str:
    """Gera CEP fake mas consistente por estado."""
    base_map = {
        "SP": "01", "RJ": "20", "MG": "30", "RS": "90", "PR": "80",
        "SC": "88", "BA": "40", "PE": "50", "CE": "60", "DF": "70",
        "GO": "74", "PA": "66", "AM": "69", "ES": "29", "MT": "78",
    }
    prefix = base_map.get(state, "01")
    return f"{prefix}{random.randint(100, 999)}"


# =============================================================
# 1. Customers (200)
# =============================================================

# 15 recompra customers: 12 com 2 orders, 3 com 3 orders = 33 orders
# 167 single-purchase = 167 orders. Total = 200.
recompra_unique_ids = [uid() for _ in range(15)]
recompra_counts = [2] * 12 + [3] * 3  # 12×2 + 3×3 = 33

customers = []
customer_ids_all = []

# Gerar customers de recompra
for i, unique_id in enumerate(recompra_unique_ids):
    state = pick_state()
    city = pick_city(state)
    zipcode = zip_for_state(state)
    for _ in range(recompra_counts[i]):
        cid = uid()
        customers.append({
            "customer_id": cid,
            "customer_unique_id": unique_id,
            "customer_zip_code_prefix": zipcode,
            "customer_city": city,
            "customer_state": state,
        })
        customer_ids_all.append(cid)

# Single-purchase customers
remaining = N_CUSTOMERS - len(customers)
for _ in range(remaining):
    cid = uid()
    unique_id = uid()
    state = pick_state()
    city = pick_city(state)
    zipcode = zip_for_state(state)
    customers.append({
        "customer_id": cid,
        "customer_unique_id": unique_id,
        "customer_zip_code_prefix": zipcode,
        "customer_city": city,
        "customer_state": state,
    })
    customer_ids_all.append(cid)

random.shuffle(customers)

# =============================================================
# 2. Products (100)
# =============================================================

# Use only categories that have translations (first 68 are valid)
valid_categories = [c for c in CATEGORIES_PT[:68] if c is not None]

products = []
product_ids = []
for i in range(N_PRODUCTS):
    pid = uid()
    product_ids.append(pid)
    cat = random.choice(valid_categories) if random.random() > 0.03 else None
    products.append({
        "product_id": pid,
        "product_category_name": cat or "",
        "product_name_length": random.randint(10, 70),
        "product_description_length": random.randint(50, 2000),
        "product_photos_qty": random.randint(1, 6),
        "product_weight_g": random.randint(100, 30000),
        "product_length_cm": random.randint(5, 100),
        "product_height_cm": random.randint(2, 80),
        "product_width_cm": random.randint(5, 80),
    })

# =============================================================
# 3. Sellers (30)
# =============================================================

sellers = []
seller_ids = []
for i in range(N_SELLERS):
    sid = uid()
    seller_ids.append(sid)
    state = pick_state()
    sellers.append({
        "seller_id": sid,
        "seller_zip_code_prefix": zip_for_state(state),
        "seller_city": pick_city(state),
        "seller_state": state,
    })

# =============================================================
# 4. Orders (200) — linked to customers 1:1
# =============================================================

orders = []
order_ids = []
for i in range(N_ORDERS):
    oid = uid()
    order_ids.append(oid)
    cid = customers[i]["customer_id"]
    status = random.choices(STATUS_OPTIONS, weights=STATUS_WEIGHTS)[0]

    purchase_ts = DATE_START + timedelta(
        seconds=random.randint(0, int((DATE_END - DATE_START).total_seconds()))
    )
    approved_ts = purchase_ts + timedelta(hours=random.randint(1, 48))
    carrier_ts = approved_ts + timedelta(days=random.randint(1, 5))
    estimated_ts = purchase_ts + timedelta(days=random.randint(7, 40))

    if status == "delivered":
        # Some delivered on time, some late
        if random.random() < 0.3:
            # Late delivery
            delivered_ts = estimated_ts + timedelta(days=random.randint(1, 20))
        else:
            delivered_ts = estimated_ts - timedelta(days=random.randint(0, 10))
        delivered_str = delivered_ts.strftime("%Y-%m-%d %H:%M:%S")
        carrier_str = carrier_ts.strftime("%Y-%m-%d %H:%M:%S")
    elif status == "shipped":
        delivered_str = ""
        carrier_str = carrier_ts.strftime("%Y-%m-%d %H:%M:%S")
    elif status in ("canceled", "unavailable"):
        delivered_str = ""
        carrier_str = ""
    else:
        delivered_str = ""
        carrier_str = carrier_ts.strftime("%Y-%m-%d %H:%M:%S") if random.random() > 0.5 else ""

    orders.append({
        "order_id": oid,
        "customer_id": cid,
        "order_status": status,
        "order_purchase_timestamp": purchase_ts.strftime("%Y-%m-%d %H:%M:%S"),
        "order_approved_at": approved_ts.strftime("%Y-%m-%d %H:%M:%S") if status != "created" else "",
        "order_delivered_carrier_date": carrier_str,
        "order_delivered_customer_date": delivered_str,
        "order_estimated_delivery_date": estimated_ts.strftime("%Y-%m-%d %H:%M:%S"),
    })

# =============================================================
# 5. Order Items (200) — one item per order for simplicity
# =============================================================

order_items = []
for i in range(N_ITEMS):
    oid = order_ids[i]
    pid = random.choice(product_ids)
    sid = random.choice(seller_ids)
    price = round(random.uniform(10, 500), 2)
    freight = round(random.uniform(5, 80), 2)

    # shipping_limit_date based on order purchase
    purchase_ts = datetime.strptime(orders[i]["order_purchase_timestamp"], "%Y-%m-%d %H:%M:%S")
    shipping_limit = purchase_ts + timedelta(days=random.randint(3, 10))

    order_items.append({
        "order_id": oid,
        "order_item_id": 1,
        "product_id": pid,
        "seller_id": sid,
        "shipping_limit_date": shipping_limit.strftime("%Y-%m-%d %H:%M:%S"),
        "price": f"{price:.2f}",
        "freight_value": f"{freight:.2f}",
    })

# =============================================================
# 6. Order Payments (200) — one payment per order
# =============================================================

order_payments = []
for i in range(N_PAYMENTS):
    oid = order_ids[i]
    ptype = random.choices(PAYMENT_TYPES, weights=PAYMENT_WEIGHTS)[0]
    installments = random.randint(1, 12) if ptype == "credit_card" else 1
    # Payment value ~ item price + freight
    item = order_items[i]
    value = round(float(item["price"]) + float(item["freight_value"]), 2)

    order_payments.append({
        "order_id": oid,
        "payment_sequential": 1,
        "payment_type": ptype,
        "payment_installments": installments,
        "payment_value": f"{value:.2f}",
    })

# =============================================================
# 7. Order Reviews (200) — one review per order
# =============================================================

order_reviews = []
for i in range(N_REVIEWS):
    oid = order_ids[i]
    status = orders[i]["order_status"]

    # Reviews correlate with delivery status
    if status == "delivered":
        delivered_str = orders[i]["order_delivered_customer_date"]
        estimated_str = orders[i]["order_estimated_delivery_date"]
        if delivered_str and estimated_str:
            delivered_dt = datetime.strptime(delivered_str, "%Y-%m-%d %H:%M:%S")
            estimated_dt = datetime.strptime(estimated_str, "%Y-%m-%d %H:%M:%S")
            if delivered_dt > estimated_dt:
                # Late: skew towards low scores
                score = random.choices([1, 2, 3, 4, 5], weights=[30, 25, 20, 15, 10])[0]
            else:
                # On time: skew towards high scores
                score = random.choices([1, 2, 3, 4, 5], weights=[5, 5, 10, 25, 55])[0]
        else:
            score = random.choices([1, 2, 3, 4, 5], weights=[10, 10, 20, 25, 35])[0]
    elif status == "canceled":
        score = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
    else:
        score = random.choices([1, 2, 3, 4, 5], weights=[10, 15, 25, 25, 25])[0]

    purchase_ts = datetime.strptime(orders[i]["order_purchase_timestamp"], "%Y-%m-%d %H:%M:%S")
    review_creation = purchase_ts + timedelta(days=random.randint(5, 60))
    review_answer = review_creation + timedelta(days=random.randint(0, 5))

    # ~60% have comment
    has_comment = random.random() < 0.6
    comment_title = ""
    comment_msg = ""
    if has_comment:
        if score <= 2:
            comment_msg = random.choice([
                "Produto chegou com defeito",
                "Muito atrasado, pessimo servico",
                "Nao recomendo, qualidade ruim",
                "Veio errado e nao consegui trocar",
                "Entrega demorou demais",
                "Produto nao corresponde a descricao",
                "Frete caro e entrega lenta",
            ])
        elif score == 3:
            comment_msg = random.choice([
                "Produto ok, mas demorou pra chegar",
                "Razoavel, esperava mais",
                "Entrega no prazo, produto medio",
                "Nada de especial",
            ])
        else:
            comment_msg = random.choice([
                "Otimo produto, recomendo!",
                "Chegou antes do prazo, muito bom",
                "Excelente qualidade",
                "Amei! Produto perfeito",
                "Entrega rapida, produto conforme descrito",
                "Muito satisfeito com a compra",
                "Bom custo beneficio",
            ])
        comment_title = random.choice(["", "Recomendo", "Bom", "Ruim", "Otimo", "Pessimo", ""])

    order_reviews.append({
        "review_id": uid(),
        "order_id": oid,
        "review_score": score,
        "review_comment_title": comment_title,
        "review_comment_message": comment_msg,
        "review_creation_date": review_creation.strftime("%Y-%m-%d %H:%M:%S"),
        "review_answer_timestamp": review_answer.strftime("%Y-%m-%d %H:%M:%S"),
    })

# =============================================================
# 8. Geolocation (500)
# =============================================================

# Collect all zip codes used by customers and sellers
used_zips = set()
for c in customers:
    used_zips.add((c["customer_zip_code_prefix"], c["customer_city"], c["customer_state"]))
for s in sellers:
    used_zips.add((s["seller_zip_code_prefix"], s["seller_city"], s["seller_state"]))

geolocation = []

# First, ensure all used zips appear in geolocation
for zipcode, city, state in used_zips:
    # Base lat/lng by state (approximate)
    base_coords = {
        "SP": (-23.55, -46.63), "RJ": (-22.91, -43.17), "MG": (-19.92, -43.94),
        "RS": (-30.03, -51.23), "PR": (-25.43, -49.27), "SC": (-27.60, -48.55),
        "BA": (-12.97, -38.51), "PE": (-8.05, -34.87), "CE": (-3.72, -38.52),
        "DF": (-15.78, -47.93), "GO": (-16.68, -49.26), "PA": (-1.46, -48.50),
        "AM": (-3.12, -60.02), "ES": (-20.32, -40.34), "MT": (-15.60, -56.10),
    }
    lat_base, lng_base = base_coords.get(state, (-15.78, -47.93))
    # Add some entries per zip (1-3)
    for _ in range(random.randint(1, 3)):
        geolocation.append({
            "geolocation_zip_code_prefix": zipcode,
            "geolocation_lat": round(lat_base + random.uniform(-0.5, 0.5), 6),
            "geolocation_lng": round(lng_base + random.uniform(-0.5, 0.5), 6),
            "geolocation_city": city,
            "geolocation_state": state,
        })

# Fill remaining with random geolocations
while len(geolocation) < N_GEO:
    state = pick_state()
    city = pick_city(state)
    zipcode = zip_for_state(state)
    base_coords = {
        "SP": (-23.55, -46.63), "RJ": (-22.91, -43.17), "MG": (-19.92, -43.94),
        "RS": (-30.03, -51.23), "PR": (-25.43, -49.27), "SC": (-27.60, -48.55),
        "BA": (-12.97, -38.51), "PE": (-8.05, -34.87), "CE": (-3.72, -38.52),
        "DF": (-15.78, -47.93), "GO": (-16.68, -49.26), "PA": (-1.46, -48.50),
        "AM": (-3.12, -60.02), "ES": (-20.32, -40.34), "MT": (-15.60, -56.10),
    }
    lat_base, lng_base = base_coords.get(state, (-15.78, -47.93))
    geolocation.append({
        "geolocation_zip_code_prefix": zipcode,
        "geolocation_lat": round(lat_base + random.uniform(-0.5, 0.5), 6),
        "geolocation_lng": round(lng_base + random.uniform(-0.5, 0.5), 6),
        "geolocation_city": city,
        "geolocation_state": state,
    })

# =============================================================
# 9. Category Translations (71)
# =============================================================

translations = []
for i in range(N_TRANSLATIONS):
    cat_pt = CATEGORIES_PT[i]
    cat_en = CATEGORIES_EN[i]
    if cat_pt is not None:
        translations.append({
            "product_category_name": cat_pt,
            "product_category_name_english": cat_en if cat_en else "",
        })

# Ensure we reach 71 rows — add remaining if needed
while len(translations) < N_TRANSLATIONS:
    translations.append({
        "product_category_name": f"categoria_extra_{len(translations)}",
        "product_category_name_english": f"extra_category_{len(translations)}",
    })


# =============================================================
# Write CSVs
# =============================================================

def write_csv(filename: str, data: list[dict], fieldnames: list[str]) -> None:
    filepath = os.path.join(FIXTURES_DIR, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"  OK {filename}: {len(data)} rows")


print("Gerando CSVs de amostra em tests/fixtures/...\n")

write_csv("olist_customers_dataset.csv", customers,
    ["customer_id", "customer_unique_id", "customer_zip_code_prefix",
     "customer_city", "customer_state"])

write_csv("olist_orders_dataset.csv", orders,
    ["order_id", "customer_id", "order_status", "order_purchase_timestamp",
     "order_approved_at", "order_delivered_carrier_date",
     "order_delivered_customer_date", "order_estimated_delivery_date"])

write_csv("olist_order_items_dataset.csv", order_items,
    ["order_id", "order_item_id", "product_id", "seller_id",
     "shipping_limit_date", "price", "freight_value"])

write_csv("olist_order_payments_dataset.csv", order_payments,
    ["order_id", "payment_sequential", "payment_type",
     "payment_installments", "payment_value"])

write_csv("olist_order_reviews_dataset.csv", order_reviews,
    ["review_id", "order_id", "review_score", "review_comment_title",
     "review_comment_message", "review_creation_date", "review_answer_timestamp"])

write_csv("olist_products_dataset.csv", products,
    ["product_id", "product_category_name", "product_name_length",
     "product_description_length", "product_photos_qty", "product_weight_g",
     "product_length_cm", "product_height_cm", "product_width_cm"])

write_csv("olist_sellers_dataset.csv", sellers,
    ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"])

write_csv("olist_geolocation_dataset.csv", geolocation,
    ["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng",
     "geolocation_city", "geolocation_state"])

write_csv("product_category_name_translation.csv", translations,
    ["product_category_name", "product_category_name_english"])

# =============================================================
# Validate referential integrity
# =============================================================

print("\nValidando integridade referencial...\n")

customer_id_set = {c["customer_id"] for c in customers}
order_id_set = {o["order_id"] for o in orders}
product_id_set = {p["product_id"] for p in products}
seller_id_set = {s["seller_id"] for s in sellers}

errors = []

# orders.customer_id → customers
for o in orders:
    if o["customer_id"] not in customer_id_set:
        errors.append(f"Order {o['order_id']} has invalid customer_id")

# order_items.order_id → orders
for item in order_items:
    if item["order_id"] not in order_id_set:
        errors.append(f"Item for order {item['order_id']} not in orders")
    if item["product_id"] not in product_id_set:
        errors.append(f"Item has invalid product_id {item['product_id']}")
    if item["seller_id"] not in seller_id_set:
        errors.append(f"Item has invalid seller_id {item['seller_id']}")

# order_payments.order_id → orders
for p in order_payments:
    if p["order_id"] not in order_id_set:
        errors.append(f"Payment for order {p['order_id']} not in orders")

# order_reviews.order_id → orders
for r in order_reviews:
    if r["order_id"] not in order_id_set:
        errors.append(f"Review for order {r['order_id']} not in orders")

# Geolocation covers customer and seller zips
customer_zips = {c["customer_zip_code_prefix"] for c in customers}
seller_zips = {s["seller_zip_code_prefix"] for s in sellers}
geo_zips = {g["geolocation_zip_code_prefix"] for g in geolocation}
missing_customer_zips = customer_zips - geo_zips
missing_seller_zips = seller_zips - geo_zips
if missing_customer_zips:
    errors.append(f"Customer zips missing from geo: {missing_customer_zips}")
if missing_seller_zips:
    errors.append(f"Seller zips missing from geo: {missing_seller_zips}")

# Recompra validation
unique_ids = [c["customer_unique_id"] for c in customers]
from collections import Counter
recompra_count = sum(1 for uid_val, cnt in Counter(unique_ids).items() if cnt > 1)

# States validation
customer_states = {c["customer_state"] for c in customers}

if errors:
    print("ERROS:")
    for e in errors:
        print(f"  X {e}")
else:
    print("  OK Todos os foreign keys sao validos")
    print(f"  OK {recompra_count} clientes com recompra (customer_unique_id repetido)")
    print(f"  OK {len(customer_states)} estados representados: {sorted(customer_states)}")

    # Score distribution
    score_dist = Counter(r["review_score"] for r in order_reviews)
    print(f"  OK Distribuicao de scores: {dict(sorted(score_dist.items()))}")

    # Status distribution
    status_dist = Counter(o["order_status"] for o in orders)
    print(f"  OK Distribuicao de status: {dict(sorted(status_dist.items()))}")

    # Late deliveries
    late = sum(1 for o in orders
               if o["order_status"] == "delivered"
               and o["order_delivered_customer_date"]
               and o["order_estimated_delivery_date"]
               and o["order_delivered_customer_date"] > o["order_estimated_delivery_date"])
    delivered = sum(1 for o in orders if o["order_status"] == "delivered")
    print(f"  OK Entregas com atraso: {late}/{delivered}")

print("\nDone!")
