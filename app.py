import shapely.geometry as geom

lots = []
count = 0

for entity in msp:
    count += 1

    # Limite sécurité
    if count > 10000:
        st.warning("DXF très lourd → analyse partielle")
        break

    # Détection polyligne fermée
    if entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
        try:
            points = entity.get_points()
            coords = [(p[0], p[1]) for p in points]

            # Vérifie si fermé
            if len(coords) > 3 and coords[0] == coords[-1]:
                polygon = geom.Polygon(coords)
                surface = round(polygon.area, 2)

                lots.append({
                    "lot": f"Lot_{len(lots)+1}",
                    "surface": f"{surface} m²",
                    "niveau": entity.dxf.layer
                })

        except Exception:
            continue
