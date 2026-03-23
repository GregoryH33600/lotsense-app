import streamlit as st
import ezdxf
import tempfile
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="LotSense Pro", layout="wide")
st.title("🏢 LotSense Pro")

uploaded_file = st.file_uploader("Upload DXF", type=["dxf"])

if uploaded_file:
    st.success(f"Fichier chargé : {uploaded_file.name}")
    st.info("Analyse en cours...")

    try:
        # Sauvegarde fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Lecture DXF (sécurisée)
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

        st.info("DXF chargé, analyse des entités...")

        lots = []
        count = 0

        for entity in msp:
            count += 1

            # Sécurité : limite pour éviter blocage
            if count > 5000:
                st.warning("DXF très lourd → analyse partielle")
                break

            if entity.dxftype() == "TEXT":
                text = entity.dxf.text

                if "Lot" in text:
                    surface_match = re.search(r"(\d+\.?\d*)\s*m²", text)
                    surface = surface_match.group(1)+" m²" if surface_match else "Non détectée"

                    lots.append({
                        "lot": text.replace("Lot","").strip(),
                        "surface": surface,
                        "niveau": "Inconnu"
                    })

        st.success(f"Analyse terminée ({count} entités parcourues)")

        if lots:
            df = pd.DataFrame(lots)
            st.write("### Résultat")
            st.dataframe(df)

            # Export Excel
            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button(
                "📥 Télécharger Excel",
                data=output,
                file_name="lots.xlsx"
            )
        else:
            st.error("Aucun lot détecté ⚠️")

    except Exception as e:
        st.error("Erreur pendant l'analyse")
        st.code(str(e))
