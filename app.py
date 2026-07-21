import streamlit as st
import yfinance as yf

st.set_page_config(page_title="AI Trading Pro", page_icon="📈", layout="wide")

st.title("📈 AI Trading Pro")

market = st.selectbox(
    "Pilih Market",
    ["Saham Indonesia", "Crypto", "Forex", "Emas"]
)

if market == "Saham Indonesia":
    symbol = st.text_input("Kode Saham", "BBCA.JK")

elif market == "Crypto":
    symbol = st.text_input("Kode Crypto", "BTC-USD")

elif market == "Forex":
    symbol = st.text_input("Kode Forex", "EURUSD=X")

else:
    symbol = st.text_input("Kode Emas", "GC=F")

st.divider()

if st.button("Ambil Data Realtime"):
    try:
        data = yf.Ticker(symbol)
        info = data.history(period="5d")

        if info.empty:
            st.error("Data tidak ditemukan.")
        else:
            harga = info["Close"].iloc[-1]
            tinggi = info["High"].iloc[-1]
            rendah = info["Low"].iloc[-1]

            st.metric("Harga Terakhir", f"{harga:.2f}")
            st.metric("High", f"{tinggi:.2f}")
            st.metric("Low", f"{rendah:.2f}")

            st.line_chart(info["Close"])

    except Exception as e:
        st.error(e)
