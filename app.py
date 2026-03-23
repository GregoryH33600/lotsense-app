import streamlit as st
import ezdxf
import tempfile
import pandas as pd
import re
from io import BytesIO
import math

st.set_page_config(page_title="LotSense Pro", layout="wide")
st.title("🏢 LotSense Pro - DXF → Lots + EDD-RCP")

# ==============================
# 🔧 FONCTIONS UTILES
# ==============================

def polygon_area(coords):
    """Calcul surface polygone (shoelace)"""
    area = 0
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        area += (x1 * y2 - x2 * y1)
    return abs(area) / 2

def centroid(coords):
    x = sum(p[0] for p in coords) / len(coords)
    y = sum(p[1] for p in coords) / len(coords)
    return (x, y)

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
        # Sauvegarde temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Lecture DXF
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

        st.info("Lecture des polylignes...")

        polygons = []
        texts = []

        count = 0

        for entity in msp:
            count += 1
            if count > 20000:
                st.warning("DXF très lourd → analyse partielle")
                break

            # 🔵 POLYLIGNES = LOTS
            if entity.dxftype() == "LWPOLYLINE":
                coords = [(p[0], p[1]) for p in entity]
                if len(coords) > 3:
                    surface = polygon_area(coords)
                    if surface > 1:  # filtre bruit
                        polygons.append({
                            "coords": coords,
                            "centroid": centroid(coords),
                            "surface": round(surface, 2),
                            "layer": entity.dxf.layer
                        })

            # 🔵 TEXTES
            if entity.dxftype() == "TEXT":
                texts.append({
                    "text": entity.dxf.text,
                    "point": (entity.dxf.insert.x, entity.dxf.insert.y)
                })

        st.info(f"{len(polygons)} polygones détectés")

        # ==============================
        # 🔗 ASSOCIATION TEXTE → LOT
        # ==============================

        lots = []

        for poly in polygons:
            closest_text = None
            min_dist = 999999

            for txt in texts:
                d = distance(poly["centroid"], txt["point"])
                if d < min_dist:
                    min_dist = d
                    closest_text = txt["text"]

            # Extraction infos
            lot_name = f"Lot_{len(lots)+1}"
            surface_txt = "Non détectée"

            if closest_text:
                lot_match = re.search(r"[Ll]ot\s*\d+", closest_text)
                if lot_match:
                    lot_name = lot_match.group()

                surf_match = re.search(r"(\d+\.?\d*)\s*m²", closest_text)
                if surf_match:
                    surface_txt = surf_match.group()

            # Catégories simples
            category = "Partie privée"
            if any(k in (closest_text or "").lower() for k in ["hall","escalier","parking","terrasse"]):
                category = "Partie commune spéciale"

            lots.append({
                "Lot": lot_name,
                "Surface calculée": f"{poly['surface']} m²",
                "Surface texte": surface_txt,
                "Niveau": poly["layer"],
                "Catégorie": category
            })

        # ==============================
        # 📊 AFFICHAGE
        # ==============================

        if lots:
            df = pd.DataFrame(lots)
            st.success(f"{len(df)} lots détectés")
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
