import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

st.set_page_config(
    page_title="AI Trading Pro",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Trading Pro")
st.caption("AI Trading Signal Dashboard")

market = st.sidebar.selectbox(
    "Market",
    ["Saham Indonesia","Crypto","Forex","Emas"]
)

if market=="Saham Indonesia":
    symbol=st.sidebar.text_input("Kode","BBCA.JK")
elif market=="Crypto":
    symbol=st.sidebar.text_input("Kode","BTC-USD")
elif market=="Forex":
    symbol=st.sidebar.text_input("Kode","EURUSD=X")
else:
    symbol=st.sidebar.text_input("Kode","GC=F")

interval=st.sidebar.selectbox(
    "Timeframe",
    ["5m","15m","30m","1h","1d"],
    index=1
)

period="7d"

df=yf.download(
    symbol,
    period=period,
    interval=interval,
    auto_adjust=False,
    progress=False
)

if df.empty:
    st.error("Data tidak tersedia")
    st.stop()

if isinstance(df.columns,pd.MultiIndex):
    df.columns=df.columns.droplevel(1)

df=df.dropna()

df["EMA20"]=EMAIndicator(df["Close"],20).ema_indicator()
df["EMA50"]=EMAIndicator(df["Close"],50).ema_indicator()

macd=MACD(df["Close"])

df["MACD"]=macd.macd()
df["MACD_SIGNAL"]=macd.macd_signal()

df["RSI"]=RSIIndicator(df["Close"]).rsi()

atr=AverageTrueRange(
    df["High"],
    df["Low"],
    df["Close"]
)

df["ATR"]=atr.average_true_range()

last=df.iloc[-1]

score=0

if last["EMA20"]>last["EMA50"]:
    score+=25

if last["MACD"]>last["MACD_SIGNAL"]:
    score+=25

if 50<last["RSI"]<70:
    score+=20

if last["Close"]>last["EMA20"]:
    score+=15

if last["ATR"]<df["ATR"].mean():
    score+=15

if score>=75:
    signal="🟢 BUY"
elif score>=50:
    signal="🟡 HOLD"
else:
    signal="🔴 SELL"

entry=float(last["Close"])
sl=entry-float(last["ATR"]*2)
tp=entry+float(last["ATR"]*3)

c1,c2,c3,c4=st.columns(4)

c1.metric("Signal",signal)
c2.metric("Confidence",f"{score}%")
c3.metric("Entry",f"{entry:,.2f}")
c4.metric("RSI",f"{last['RSI']:.2f}")

st.write(f"Stop Loss : {sl:,.2f}")
st.write(f"Take Profit : {tp:,.2f}")

fig=go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Price"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["EMA20"],
    name="EMA20"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["EMA50"],
    name="EMA50"
))

fig.update_layout(height=650)

st.plotly_chart(fig,use_container_width=True)
