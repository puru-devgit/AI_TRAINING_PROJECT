from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

_INCIDENTS = [
    # Grains & Staples
    "Monsoon floods disrupted rice supply chains in Southeast Asia causing 3-week delays and 40% price surge.",
    "Drought reduced wheat yield by 30% in key producing regions, triggering global flour shortages.",
    "Port congestion at major hubs led to 2-week shipping delays for grain imports.",
    "Pest infestation destroyed 20% of rice crop in India, reducing export availability significantly.",
    "Wheat rust fungal outbreak in Eastern Europe cut production by 25% for the season.",
    "Lentil harvest failure in Canada due to extreme heat reduced global supply by 35%.",
    "Pasta production halted at major Italian factories due to durum wheat shortage.",

    # Oils & Fats
    "Currency devaluation increased import costs for cooking oil by 18%, squeezing margins.",
    "Palm oil supply disrupted by Indonesian export ban, causing global cooking oil shortage.",
    "Olive oil prices surged 60% after Mediterranean drought destroyed 40% of olive harvest.",
    "Sunflower oil shortage triggered by Ukraine conflict reduced global edible oil supply by 30%.",

    # Beverages & Coffee
    "Coffee bean blight in Colombia caused global price surge of 40% over 6 months.",
    "Tea crop failure in Assam due to unseasonal frost reduced black tea supply by 20%.",
    "Coffee frost in Brazil destroyed 15% of arabica crop, pushing futures to decade highs.",
    "Port strike in Santos Brazil delayed coffee shipments by 3 weeks globally.",
    "Alcohol import restrictions in key markets caused beverage inventory buildup at warehouses.",
    "Beer and spirits demand spiked 35% during festive season causing widespread stockouts.",
    "Whiskey aging inventory shortage due to barrel wood supply constraints.",

    # Skincare & Haircare (supply_chain_data products)
    "Skincare raw material shortage due to chemical plant shutdown in China delayed production 4 weeks.",
    "Haircare product demand surged 45% post-pandemic as salons reopened globally.",
    "Cosmetic ingredient supplier quality failure led to 15% batch rejection rate.",
    "Packaging material shortage for beauty products caused 2-week production delays.",
    "Skincare product recall due to contamination affected 3 major SKUs across supplier network.",
    "Haircare aerosol shortage due to propellant supply disruption halted production.",

    # Logistics & Shipping
    "Fuel price spike increased logistics costs by 20%, affecting all delivery schedules.",
    "Trucking strike halted domestic distribution for 5 days across major cities.",
    "Suez Canal blockage caused 3-week delays for all sea freight from Asia.",
    "Air freight capacity reduced by 40% due to airline fleet grounding.",
    "Last-mile delivery delays of 5-7 days due to driver shortage in urban areas.",
    "Cold chain failure caused spoilage of temperature-sensitive inventory worth $2M.",
    "Container shortage at major ports increased shipping costs by 300%.",

    # Supplier & Manufacturing
    "Supplier AgriSupply Co faced quality control issues; 15% of shipments rejected.",
    "Factory fire at key supplier caused 4-week production halt and emergency sourcing.",
    "Single-source supplier bankruptcy left 8 products without supply for 6 weeks.",
    "Manufacturing lead time increased from 14 to 28 days due to labor shortage.",
    "Supplier 3 in Mumbai reported defect rate spike to 8%, triggering quality audit.",
    "Raw material price inflation of 25% forced supplier renegotiation across all categories.",

    # Demand & Market
    "Unexpected demand surge during festive season caused stockouts across retail chains.",
    "Pandemic-related border closures delayed cross-border shipments by 3 weeks.",
    "Cold snap damaged sugar cane crops, reducing supply by 25% for Q1.",
    "E-commerce demand spike overwhelmed warehouse capacity, causing 10-day fulfillment delays.",
    "Promotional campaign drove 3x demand spike, depleting 6 weeks of safety stock in 4 days.",
    "Seasonal demand forecasting error led to 40% overstock of slow-moving SKUs.",

    # Geopolitical & Macro
    "Trade tariff increase of 15% on imported goods raised landed cost for 30% of SKUs.",
    "Geopolitical tensions disrupted shipping routes, adding 8 days to average lead time.",
    "Currency exchange rate volatility increased procurement costs by 12% quarter-on-quarter.",
    "New import regulations required additional documentation, delaying customs clearance by 5 days.",
    "Energy crisis in Europe increased manufacturing costs by 30% for all processed goods.",
]

_model = SentenceTransformer("all-MiniLM-L6-v2")
_embeddings = _model.encode(_INCIDENTS, convert_to_numpy=True).astype("float32")
faiss.normalize_L2(_embeddings)
_index = faiss.IndexFlatIP(_embeddings.shape[1])
_index.add(_embeddings)


def retrieve_risks(query: str, top_k: int = 3) -> list[str]:
    q_vec = _model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(q_vec)
    scores, indices = _index.search(q_vec, top_k)
    return [
        {"incident": _INCIDENTS[i], "relevance_score": round(float(scores[0][j]), 3)}
        for j, i in enumerate(indices[0]) if i < len(_INCIDENTS)
    ]


def retrieve_risks_text(query: str, top_k: int = 3) -> list[str]:
    return [r["incident"] for r in retrieve_risks(query, top_k)]
