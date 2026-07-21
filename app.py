import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(
    page_title="AI Trading Pro",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Trading Pro")
st.caption("Realtime AI Trading Dashboard")

market = st.sidebar.selectbox(
    "Market",
    [
        "Saham Indonesia",
        "Crypto",
        "Forex",
        "Emas"
    ]
)

if market == "Saham Indonesia":
    symbol = st.sidebar.text_input("Kode Saham", "BBCA.JK")

elif market == "Crypto":
    symbol = st.sidebar.text_input("Kode Crypto", "BTC-USD")

elif market == "Forex":
    symbol = st.sidebar.text_input("Kode Forex", "EURUSD=X")

else:
    symbol = st.sidebar.text_input("Kode Emas", "GC=F")

interval = st.sidebar.selectbox(
    "Timeframe",
    [
        "5m",
        "15m",
        "30m",
        "1h",
        "1d"
    ]
)

period = "7d"

if st.button("🔄 Ambil Data Realtime"):

    with st.spinner("Mengambil data..."):

        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False
        )

    if df.empty:
        st.error("Data tidak ditemukan.")
        st.stop()

     last = df.iloc[-1]

harga = last["Close"]
buka = last["Open"]
tinggi = last["High"]
rendah = last["Low"]

st.metric("Harga", f"{harga}")
st.metric("Open", f"{buka}")
st.metric("High", f"{tinggi}")
st.metric("Low", f"{rendah}")
    

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Harga", f"{harga:.2f}")
    c2.metric("Open", f"{buka:.2f}")
    c3.metric("High", f"{tinggi:.2f}")
    c4.metric("Low", f"{rendah:.2f}")

    st.line_chart(df["Close"])

    st.success("Realtime berhasil diperbarui.")
