import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

# ======================
# CONFIG
# ======================

st.set_page_config(
    page_title="AI Trading Pro V5",
    page_icon="📈",
    layout="wide"
)

st_autorefresh(
    interval=30000,
    key="refresh"
)

st.title("📈 AI Trading Pro V5")
st.caption("Realtime AI Trading Dashboard")

st.info(
    f"🕒 Update : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

# ======================
# SIDEBAR
# ======================

market = st.sidebar.selectbox(
    "Market",
    [
        "Saham Indonesia",
        "Crypto",
        "Forex",
        "Emas"
    ]
)

default_symbol = {
    "Saham Indonesia": "BBCA.JK",
    "Crypto": "BTC-USD",
    "Forex": "EURUSD=X",
    "Emas": "GC=F"
}

symbol = st.sidebar.text_input(
    "Kode",
    default_symbol[market]
)

interval = st.sidebar.selectbox(
    "Timeframe",
    [
        "5m",
        "15m",
        "30m",
        "1h",
        "1d"
    ],
    index=1
)

period = "30d"

# ======================
# DOWNLOAD DATA
# ======================

with st.spinner("Mengambil data realtime..."):

    df = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False
    )

if df.empty:
    st.error("Data tidak tersedia")
    st.stop()

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)

df = df.dropna()

# ======================
# INDIKATOR
# ======================

df["EMA20"] = EMAIndicator(
    df["Close"],
    window=20
).ema_indicator()

df["EMA50"] = EMAIndicator(
    df["Close"],
    window=50
).ema_indicator()

macd = MACD(df["Close"])

df["MACD"] = macd.macd()
df["MACD_SIGNAL"] = macd.macd_signal()

df["RSI"] = RSIIndicator(
    df["Close"]
).rsi()

df["ATR"] = AverageTrueRange(
    df["High"],
    df["Low"],
    df["Close"]
).average_true_range()

df["VOL_MA20"] = df["Volume"].rolling(20).mean()

last = df.iloc[-1]

entry = float(last["Close"])
sl = entry - float(last["ATR"] * 2)
tp = entry + float(last["ATR"] * 3)

support = float(df["Low"].tail(20).min())
resistance = float(df["High"].tail(20).max())

volume_now = float(last["Volume"])
volume_avg = float(last["VOL_MA20"]) if pd.notna(last["VOL_MA20"]) else 0

volume_ratio = (
    volume_now / volume_avg
    if volume_avg > 0 else 1
)

high20 = float(df["High"].tail(20).max())
low20 = float(df["Low"].tail(20).min())

if entry >= high20 * 0.998:
    breakout = "🚀 Bullish Breakout"
elif entry <= low20 * 1.002:
    breakout = "🔻 Bearish Breakdown"
else:
    breakout = "➡️ Sideways"
# ======================
# SMART AI SCORE
# ======================

ai_score = 0
alasan = []

# EMA
if last["EMA20"] > last["EMA50"]:
    ai_score += 25
    alasan.append("✅ EMA Bullish")
else:
    alasan.append("❌ EMA Bearish")

# MACD
if last["MACD"] > last["MACD_SIGNAL"]:
    ai_score += 20
    alasan.append("✅ MACD Bullish")
else:
    alasan.append("❌ MACD Bearish")

# RSI
if 50 <= last["RSI"] <= 70:
    ai_score += 20
    alasan.append("✅ RSI Ideal")
elif last["RSI"] < 30:
    ai_score += 15
    alasan.append("✅ Oversold")
elif last["RSI"] > 70:
    alasan.append("⚠️ Overbought")

# Trend
if last["Close"] > last["EMA20"]:
    ai_score += 10
    alasan.append("✅ Harga di atas EMA20")

# Volume
if volume_ratio >= 2:
    ai_score += 15
    alasan.append("✅ Volume Spike")
elif volume_ratio >= 1.3:
    ai_score += 10
    alasan.append("✅ Volume Di Atas Rata-rata")

# Breakout
if breakout == "🚀 Bullish Breakout":
    ai_score += 10
    alasan.append("✅ Breakout")

confidence = min(ai_score, 100)

if confidence >= 85:
    signal = "🟢 STRONG BUY"
elif confidence >= 70:
    signal = "🟢 BUY"
elif confidence >= 50:
    signal = "🟡 HOLD"
else:
    signal = "🔴 SELL"

# ======================
# DASHBOARD
# ======================

st.subheader("📊 Dashboard")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Signal", signal)
c2.metric("Confidence", f"{confidence}%")
c3.metric("Entry", f"{entry:,.2f}")
c4.metric("RSI", f"{last['RSI']:.2f}")

st.progress(confidence / 100)

c1, c2 = st.columns(2)

c1.success(f"🎯 Take Profit : {tp:,.2f}")
c2.error(f"🛑 Stop Loss : {sl:,.2f}")

with st.expander("🤖 Analisis AI"):
    for a in alasan:
        st.write(a)

# ======================
# CHART
# ======================

st.subheader("📈 Candlestick Chart")

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["EMA20"],
        name="EMA20"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["EMA50"],
        name="EMA50"
    )
)

fig.update_layout(
    height=700,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(
    fig,
    use_container_width=True
  )
# ======================
# AI SCANNER
# ======================

st.divider()
st.subheader("📋 AI Scanner")

watchlist = {
    "Saham": [
        "BBCA.JK",
        "BBRI.JK",
        "BMRI.JK",
        "BBNI.JK",
        "TLKM.JK",
        "ASII.JK",
        "ANTM.JK",
        "MDKA.JK"
    ],
    "Crypto": [
        "BTC-USD",
        "ETH-USD",
        "BNB-USD",
        "SOL-USD",
        "XRP-USD",
        "DOGE-USD"
    ],
    "Forex": [
        "EURUSD=X",
        "GBPUSD=X",
        "USDJPY=X",
        "AUDUSD=X"
    ],
    "Emas": [
        "GC=F"
    ]
}

kategori = st.selectbox(
    "Scanner Market",
    list(watchlist.keys())
)

scanner = []

for kode in watchlist[kategori]:

    try:

        d = yf.download(
            kode,
            period="10d",
            interval="1h",
            auto_adjust=False,
            progress=False
        )

        if d.empty:
            continue

        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.droplevel(1)

        d = d.dropna()

        d["EMA20"] = EMAIndicator(d["Close"],20).ema_indicator()
        d["EMA50"] = EMAIndicator(d["Close"],50).ema_indicator()
        d["RSI"] = RSIIndicator(d["Close"]).rsi()

        m = MACD(d["Close"])
        d["MACD"] = m.macd()
        d["MACD_SIGNAL"] = m.macd_signal()

        x = d.iloc[-1]

        score = 0

        if x["EMA20"] > x["EMA50"]:
            score += 30

        if x["MACD"] > x["MACD_SIGNAL"]:
            score += 30

        if x["RSI"] > 50:
            score += 20

        if x["Close"] > x["EMA20"]:
            score += 20

        score = min(score,100)

        if score >= 85:
            sig = "🟢 STRONG BUY"

        elif score >= 70:
            sig = "🟢 BUY"

        elif score >= 50:
            sig = "🟡 HOLD"

        else:
            sig = "🔴 SELL"

        scanner.append({
            "Kode": kode,
            "Harga": round(float(x["Close"]),2),
            "RSI": round(float(x["RSI"]),2),
            "Score": score,
            "Signal": sig
        })

    except:
        pass

if scanner:

    hasil = pd.DataFrame(scanner)

    hasil = hasil.sort_values(
        by="Score",
        ascending=False
    )

    st.dataframe(
        hasil,
        use_container_width=True,
        hide_index=True
    )

    terbaik = hasil.iloc[0]

    st.success(
        f"⭐ Rekomendasi Terbaik : "
        f"{terbaik['Kode']} | "
        f"{terbaik['Signal']} | "
        f"Score {terbaik['Score']}/100"
    )
# ======================
# MULTI TIMEFRAME AI
# ======================

st.divider()
st.subheader("🧠 Multi Timeframe Analysis")

tf_list = ["15m", "1h", "1d"]

mtf = []

for tf in tf_list:

    try:

        d = yf.download(
            symbol,
            period="30d",
            interval=tf,
            auto_adjust=False,
            progress=False
        )

        if d.empty:
            continue

        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.droplevel(1)

        d = d.dropna()

        d["EMA20"] = EMAIndicator(d["Close"],20).ema_indicator()
        d["EMA50"] = EMAIndicator(d["Close"],50).ema_indicator()
        d["RSI"] = RSIIndicator(d["Close"]).rsi()

        x = d.iloc[-1]

        score = 0

        if x["EMA20"] > x["EMA50"]:
            score += 50

        if x["RSI"] > 50:
            score += 50

        if score >= 80:
            sig = "🟢 BUY"
        elif score >= 50:
            sig = "🟡 HOLD"
        else:
            sig = "🔴 SELL"

        mtf.append({
            "Timeframe": tf,
            "Signal": sig,
            "Confidence": score
        })

    except:
        pass

if mtf:

    st.dataframe(
        pd.DataFrame(mtf),
        use_container_width=True,
        hide_index=True
    )

# ======================
# VOLUME ANALYSIS
# ======================

st.divider()
st.subheader("📊 Volume Analysis")

if volume_ratio >= 2:
    volume_status = "🔥 Volume Spike"

elif volume_ratio >= 1.3:
    volume_status = "🟢 Above Average"

else:
    volume_status = "⚪ Normal"

v1, v2, v3 = st.columns(3)

v1.metric(
    "Volume",
    f"{volume_now:,.0f}"
)

v2.metric(
    "Avg 20",
    f"{volume_avg:,.0f}"
)

v3.metric(
    "Status",
    volume_status
)

# ======================
# BREAKOUT DETECTION
# ======================

st.divider()
st.subheader("🚀 Breakout Detection")

st.info(breakout)

b1, b2 = st.columns(2)

b1.metric(
    "Resistance",
    f"{resistance:,.2f}"
)

b2.metric(
    "Support",
    f"{support:,.2f}"
)
# ======================
# RISK MANAGEMENT
# ======================

st.divider()
st.subheader("⚖️ Risk Management")

risk = entry - sl
reward = tp - entry

rr = reward / risk if risk > 0 else 0

r1, r2, r3 = st.columns(3)

r1.metric(
    "Risk",
    f"{risk:,.2f}"
)

r2.metric(
    "Reward",
    f"{reward:,.2f}"
)

r3.metric(
    "Risk : Reward",
    f"1 : {rr:.2f}"
)

# ======================
# AI RECOMMENDATION
# ======================

st.divider()
st.subheader("🤖 AI Recommendation")

if confidence >= 85:
    st.success("🟢 STRONG BUY")

elif confidence >= 70:
    st.info("🟢 BUY")

elif confidence >= 50:
    st.warning("🟡 HOLD")

else:
    st.error("🔴 SELL")

for item in alasan:
    st.write(item)

# ======================
# TREND ANALYSIS
# ======================

st.divider()
st.subheader("📈 Trend Analysis")

if last["EMA20"] > last["EMA50"]:
    st.success("Trend Utama : BULLISH 📈")
else:
    st.error("Trend Utama : BEARISH 📉")

trend_strength = abs(last["EMA20"] - last["EMA50"])

st.metric(
    "Trend Strength",
    f"{trend_strength:.2f}"
)

# ======================
# PRICE POSITION
# ======================

st.divider()
st.subheader("🎯 Price Position")

if entry > resistance:
    st.success("Harga berada di atas Resistance")

elif entry < support:
    st.error("Harga berada di bawah Support")

else:
    st.info("Harga berada di dalam area Support-Resistance")

# ======================
# DATA TERAKHIR
# ======================

st.divider()
st.subheader("📄 Data Terakhir")

st.dataframe(
    df.tail(20),
    use_container_width=True,
    hide_index=False
)

# ======================
# MARKET SUMMARY
# ======================

st.divider()
st.subheader("📌 Market Summary")

summary = pd.DataFrame({
    "Item": [
        "Symbol",
        "Signal",
        "AI Score",
        "Entry",
        "Stop Loss",
        "Take Profit",
        "Support",
        "Resistance",
        "Trend",
        "Breakout"
    ],
    "Value": [
        symbol,
        signal,
        f"{confidence}/100",
        f"{entry:,.2f}",
        f"{sl:,.2f}",
        f"{tp:,.2f}",
        f"{support:,.2f}",
        f"{resistance:,.2f}",
        "Bullish" if last["EMA20"] > last["EMA50"] else "Bearish",
        breakout
    ]
})

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)
# ======================
# WIN PROBABILITY
# ======================

st.divider()
st.subheader("🎯 Win Probability")

buy_score = confidence

if volume_ratio >= 2:
    buy_score += 5

if breakout == "🚀 Bullish Breakout":
    buy_score += 5

buy_score = min(buy_score, 100)

st.metric(
    "Probabilitas Sukses",
    f"{buy_score}%"
)

st.progress(buy_score / 100)

# ======================
# POSITION SIZE
# ======================

st.divider()
st.subheader("💰 Position Size Calculator")

modal = st.number_input(
    "Modal",
    value=10000000.0,
    step=1000000.0
)

risk_percent = st.slider(
    "Risk (%)",
    1,
    10,
    2
)

risk_amount = modal * risk_percent / 100

if entry > sl:

    lot = risk_amount / (entry - sl)

else:

    lot = 0

c1, c2, c3 = st.columns(3)

c1.metric(
    "Risk Dana",
    f"{risk_amount:,.0f}"
)

c2.metric(
    "Ukuran Posisi",
    f"{lot:,.2f}"
)

c3.metric(
    "Modal",
    f"{modal:,.0f}"
)

# ======================
# AI NEXT CANDLE
# ======================

st.divider()
st.subheader("🤖 AI Prediksi Candle Berikutnya")

if confidence >= 85:
    prediksi = "📈 Sangat berpotensi naik"

elif confidence >= 70:
    prediksi = "📈 Berpotensi naik"

elif confidence >= 50:
    prediksi = "➡️ Sideways"

else:
    prediksi = "📉 Berpotensi turun"

st.info(prediksi)

# ======================
# TOP SIGNAL
# ======================

st.divider()
st.subheader("⭐ Top Scanner")

if 'hasil' in locals():

    top5 = (
        pd.DataFrame(hasil)
        .sort_values("Confidence", ascending=False)
        .head(5)
    )

    st.dataframe(
        top5,
        use_container_width=True,
        hide_index=True
    )

# ======================
# ALERT
# ======================

st.divider()
st.subheader("🔔 Alert")

if confidence >= 85:
    st.success("✅ STRONG BUY")

elif confidence >= 70:
    st.success("✅ BUY")

elif confidence >= 50:
    st.warning("⚠️ HOLD")

else:
    st.error("❌ SELL")

# ======================
# FOOTER
# ======================

st.divider()

st.caption(
    "AI Trading Pro V6 | EMA • MACD • RSI • ATR • Scanner • Multi Timeframe • AI Score"
)
