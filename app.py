from shapely.geometry import Polygon

lots = []
count = 0

for entity in msp:
    count += 1

    if count > 10000:
        st.warning("DXF très lourd → analyse partielle")
        break

    if entity.dxftype() == "LWPOLYLINE":
        try:
            coords = [(point[0], point[1]) for point in entity]

            if len(coords) > 3:
                polygon = Polygon(coords)

                if polygon.is_valid:
                    surface = round(polygon.area, 2)

                    lots.append({
                        "lot": f"Lot_{len(lots)+1}",
                        "surface": f"{surface} m²",
                        "niveau": entity.dxf.layer
                    })

        except Exception as e:
            st.write(f"Erreur polyligne : {e}")
