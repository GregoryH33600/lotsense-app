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

    st.write("Lots détectés :")
    st.write(lots)
