import streamlit as st

st.set_page_config(
    page_title="AI Trading Pro",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Trading Pro")

st.success("Aplikasi berhasil berjalan!")

market = st.selectbox(
    "Pilih Market",
    [
        "Saham Indonesia",
        "Crypto",
        "Forex",
        "Emas"
    ]
)

st.write("Market dipilih:", market)

st.info("Versi 1.0")
st.write("Selanjutnya kita akan menambahkan data realtime dan AI Signal.")
