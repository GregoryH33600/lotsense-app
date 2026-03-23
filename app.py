lots = {}

for poly in polygons:

    # 1. trouver le lot (comme avant)
    closest_lot = None
    min_dist = 999999

    for lc in lot_centers:
        d = distance(poly["centroid"], lc["point"])
        if d < min_dist:
            min_dist = d
            closest_lot = lc["lot"]

    if not closest_lot:
        continue

    # 2. trouver le nom de la pièce
    piece_name = "Inconnu"
    for txt in texts:
        if distance(poly["centroid"], txt["point"]) < 5:
            if not re.match(r"^\d+$", txt["text"]):
                piece_name = txt["text"]

    # 3. construire le lot COMPLET
    if closest_lot not in lots:
        lots[closest_lot] = {
            "surface": 0,
            "pieces": [],
            "niveaux": set(),
            "batiments": set()
        }

    lots[closest_lot]["surface"] += poly["surface"]
    lots[closest_lot]["pieces"].append({
        "nom": piece_name,
        "surface": poly["surface"]
    })
    lots[closest_lot]["niveaux"].add(poly["layer"])

for lot_id, data in lots.items():

    st.markdown(f"## LOT {lot_id}")

    st.write(f"Surface totale : {round(data['surface'],2)} m²")

    st.write("Composition :")
    for p in data["pieces"]:
        st.write(f"- {p['nom']} : {p['surface']} m²")

    st.write(f"Niveaux : {', '.join(data['niveaux'])}")
