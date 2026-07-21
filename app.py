import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="AI Trading Pro",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Trading Pro")
st.caption("Realtime AI Trading Dashboard")

market = st.sidebar.selectbox(
    "Market",
    ["Saham Indonesia", "Crypto", "Forex", "Emas"]
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
    ["5m", "15m", "30m", "1h", "1d"]
)

if st.button("🔄 Ambil Data Realtime"):

    with st.spinner("Mengambil data..."):
        df = yf.download(
            symbol,
            period="7d",
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

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Harga", str(harga))
    c2.metric("Open", str(buka))
    c3.metric("High", str(tinggi))
    c4.metric("Low", str(rendah))

    st.line_chart(df["Close"])

    st.success("Realtime berhasil diperbarui.")
