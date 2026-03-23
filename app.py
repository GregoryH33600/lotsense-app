def polygon_area(coords):
    area = 0
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        area += (x1 * y2 - x2 * y1)
    return abs(area) / 2

def centroid(coords):
    return (
        sum(p[0] for p in coords) / len(coords),
        sum(p[1] for p in coords) / len(coords)
    )

def distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5


polygons = []
texts = []

# 🔵 1. EXTRACTION
for entity in msp:

    if entity.dxftype() == "LWPOLYLINE":
        coords = [(p[0], p[1]) for p in entity]

        if len(coords) > 3:
            surface = polygon_area(coords)

            if surface > 1:
                polygons.append({
                    "coords": coords,
                    "centroid": centroid(coords),
                    "surface": round(surface, 2)
                })

    if entity.dxftype() == "TEXT":
        texts.append({
            "text": entity.dxf.text,
            "point": (entity.dxf.insert.x, entity.dxf.insert.y)
        })


# 🔵 2. IDENTIFICATION DES LOTS (numéro encerclé)
lot_centers = []

for txt in texts:
    if re.match(r"^\d+$", txt["text"].strip()):
        lot_centers.append({
            "lot": txt["text"],
            "point": txt["point"]
        })


# 🔵 3. ASSOCIER PIÈCES → LOT
lots = {}

for poly in polygons:
    closest_lot = None
    min_dist = 999999

    for lc in lot_centers:
        d = distance(poly["centroid"], lc["point"])
        if d < min_dist:
            min_dist = d
            closest_lot = lc["lot"]

    if closest_lot:
        if closest_lot not in lots:
            lots[closest_lot] = {
                "surface_totale": 0,
                "pieces": []
            }

        lots[closest_lot]["surface_totale"] += poly["surface"]
        lots[closest_lot]["pieces"].append(poly["surface"])


# 🔵 4. FORMAT FINAL
result = []

for lot_id, data in lots.items():
    result.append({
        "Lot": lot_id,
        "Surface totale": round(data["surface_totale"], 2),
        "Nb pièces": len(data["pieces"])
    })


df = pd.DataFrame(result)
st.dataframe(df)
