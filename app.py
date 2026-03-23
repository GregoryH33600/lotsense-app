import streamlit as st
import ezdxf
import tempfile
import pandas as pd
import re
import math
from io import BytesIO

st.set_page_config(page_title="LotSense Pro", layout="wide")
st.title("🏢 LotSense Pro - Analyse DXF Copro")

# ==============================
# 🔧 OUTILS MATH
# ==============================

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
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# ==============================
# 📂 UPLOAD
# ==============================

uploaded_file = st.file_uploader("Upload ton plan DXF", type=["dxf"])

if uploaded_file:

    st.success(f"Fichier chargé : {uploaded_file.name}")
    st.info("Analyse en cours...")

    try:
        # ==============================
        # 📥 LECTURE DXF
        # ==============================

        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

        # ==============================
        # 🔍 EXTRACTION
        # ==============================

        polygons = []
        texts = []

        count = 0

        for entity in msp:
            count += 1
            if count > 20000:
                st.warning("DXF très lourd → analyse partielle")
                break

            # 🔵 POLYLIGNES = PIÈCES
            if entity.dxftype() == "LWPOLYLINE":
                coords = [(p[0], p[1]) for p in entity]

                if len(coords) > 3:
                    surface = polygon_area(coords)

                    if surface > 1:
                        polygons.append({
                            "coords": coords,
                            "centroid": centroid(coords),
                            "surface": round(surface, 2),
                            "layer": entity.dxf.layer
                        })

            # 🔵 TEXTES (noms + lots)
            if entity.dxftype() == "TEXT":
                texts.append({
                    "text": entity.dxf.text.strip(),
                    "point": (entity.dxf.insert.x, entity.dxf.insert.y)
                })

        st.info(f"{len(polygons)} pièces détectées")

        # ==============================
        # 🔢 DÉTECTION NUMÉROS DE LOT
        # ==============================

        lot_centers = []

        for txt in texts:
            # détecte nombres seuls (ex: "12")
            if re.match(r"^\d+$", txt["text"]):
                lot_centers.append({
                    "lot": txt["text"],
                    "point": txt["point"]
                })

        st.info(f"{len(lot_centers)} lots détectés (numéros)")

        # ==============================
        # 🔗 ASSOCIATION PIÈCES → LOT
        # ==============================

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
                        "pieces": [],
                        "niveau": poly["layer"]
                    }

                lots[closest_lot]["surface_totale"] += poly["surface"]
                lots[closest_lot]["pieces"].append(poly["surface"])

        # ==============================
        # 📊 FORMAT FINAL
        # ==============================

        result = []

        for lot_id, data in lots.items():
            result.append({
                "Lot": lot_id,
                "Surface totale (m²)": round(data["surface_totale"], 2),
                "Nb pièces": len(data["pieces"]),
                "Niveau": data["niveau"]
            })

        if result:
            df = pd.DataFrame(result)
            st.success(f"{len(df)} lots calculés")
            st.dataframe(df)

            # ==============================
            # 📥 EXPORT EXCEL
            # ==============================

            output = BytesIO()
            df.to_excel(output, index=False)

            st.download_button(
                "📥 Télécharger Excel",
                data=output,
                file_name="lots.xlsx"
            )

        else:
            st.error("Aucun lot détecté")

    except Exception as e:
        st.error("Erreur pendant l'analyse")
        st.code(str(e))
