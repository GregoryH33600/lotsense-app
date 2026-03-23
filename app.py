import streamlit as st
import ezdxf
import tempfile

st.title("LotSense")

uploaded_file = st.file_uploader("Upload DXF", type=["dxf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    doc = ezdxf.readfile(tmp_path)
    msp = doc.modelspace()

    lots = []

    for entity in msp:
        if entity.dxftype() == "TEXT":
            if "Lot" in entity.dxf.text:
                lots.append(entity.dxf.text)

import pandas as pd

if lots:
    df = pd.DataFrame(lots)
    st.write("### Lots détectés")
    st.table(df)

import io

if lots:
    output = io.BytesIO()
    df.to_excel(output, index=False)
    st.download_button(
        label="📥 Télécharger Excel",
        data=output,
        file_name="lots_detectes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
