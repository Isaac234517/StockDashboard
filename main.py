from datetime import datetime
import math
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from pandas_datareader import data as pdr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta

def plot_kdj(dates, k, d, j, title_config, plotly_config):
   figKDJ = go.Figure()
   figKDJ.add_trace(
      go.Scatter(
         x = dates,
         y = k,
         name = 'K Line'
      )
   )

   figKDJ.add_trace(
      go.Scatter(
         x = dates,
         y = d,
         name = 'D Line'
      )
   )

   figKDJ.add_trace(
      go.Scatter(
         x = dates,
         y = j,
         name = 'J Line'
      )
   )
   figKDJ.update_layout(title='KDJ', font = title_config)
   st.plotly_chart(figKDJ, use_container_width = True, config = plotly_config)


def create_candlestick(df, stock_name):
   fig = go.Figure()
   fig.add_trace(go.Candlestick(x = df.index, open = df['Open'], high = df['High'], low =df['Low'], 
   close = df['Close'], name = stock_name))

   dt_all = pd.date_range(start = df.index[0], end = df.index[-1])
   dt = [d.strftime('%Y-%m-%d') for d in df.index]
   dt_breaks = [d for d in dt_all.strftime('%Y-%m-%d').tolist() if not d in dt_all]

   fig.update_xaxes(
      rangeslider_visible = False,
      rangebreaks = [dict(bounds=["sat", "sun"])]
   )

   fig.update_xaxes(
      rangebreaks = [dict(values = dt_breaks)]
   )
   return fig

def plot_candlestick(df, stock_name, title_config, plotly_config):
   fig = create_candlestick(df, stock_name)
   fig.update_layout(title=stock_name, font = title_config)
   st.plotly_chart(fig, use_container_width= True, config = plotly_config)

def plot_macd(index, macd, sig, hist, chart_title, title_config, plotly_config):
   #fig = make_subplots(rows=2, cols = 1, shared_xaxes= True)

   fig = go.Figure()
   fig.add_trace(go.Scatter(x = index, y=macd, line_color = 'orange', name = 'macd'))
   fig.add_trace(go.Scatter(x = index, y=sig, line_color = 'deepskyblue', name='sig'))
   colors = ['green' if val > 0 else 'red' for val in hist]
   fig.add_trace(go.Bar(x=index, y= hist,  marker_color=colors, showlegend = False))
   fig.update_yaxes(title_text='MACD')
   fig.update_layout(title=chart_title, font = title_config)
   st.plotly_chart(fig, use_container_width=True, config = plotly_config)

def plot_volume(df, title_config, plotly_config):
   colors = ['green' if row['Close'] > row['Open'] else 'red' for idx, row in df.iterrows()]
   fig = go.Figure()
   fig.add_trace(go.Bar(x=df.index, y = df['Volume'], marker_color = colors ))
   fig.update_layout(title='Volume', font = title_config)
   st.plotly_chart(fig, use_container_width=True, config = plotly_config)

def plot_rsi(index, short_rsi, mid_rsi, long_rsi, s, m, l, title_config, plotly_config):
   fig = go.Figure()
   fig.add_trace(go.Scatter(x=df.index, y=short_rsi, name=f'RSI({s})'))
   fig.add_trace(go.Scatter(x=df.index, y=mid_rsi, name=f'RSI({m})'))
   fig.add_trace(go.Scatter(x=df.index, y=long_rsi, name=f'RSI({l})'))
   fig.update_layout(title = 'RSI', font=title_config)
   st.plotly_chart(fig, use_container_width=True, config = plotly_config)

def plot_bollinger_brand(df, stock_name, upper, middle, lower, title_config, plotly_config):
   fig = create_candlestick(df, stock_name)
   fig.add_trace(go.Scatter(x = df.index, y=upper, name = 'Upper'))
   fig.add_trace(go.Scatter(x = df.index, y=middle, name = 'Middle'))
   fig.add_trace(go.Scatter(x= df.index, y=lower, name = 'Lower'))
   fig.update_layout(title='Bollinger Bands', font = title_config)
   st.plotly_chart(fig, use_container_width=True, config=plotly_config)

def plot_sar(df, stock_name, sar_value,title_config, plotly_config):
   fig = create_candlestick(df, stock_name)
   fig.add_trace(go.Scatter(x = df.index, y = sar_value,
      marker = dict(color='crimson', size= 12),
      mode = 'markers',
      name = 'sar'))
   fig.update_layout(title=stock_name, font = title_config)
   st.plotly_chart(fig, use_container_width= True, config = plotly_config)

def generateMAOption(type, ma_option):
   ma5, ma10, ma20 = st.columns(3)
   ma60, ma150, ma250 = st.columns(3)
   if(type == 'MA'):
      ma_option['check_5'] = ma5.checkbox('MA 5')
      ma_option['check_10'] = ma10.checkbox('MA 10')
      ma_option['check_20'] = ma20.checkbox('MA 20')
      ma_option['check_60'] = ma60.checkbox('MA 60')
      ma_option['check_150'] = ma150.checkbox('MA 150')
      ma_option['check_250'] = ma250.checkbox('MA 250')
   elif (type == 'EMA'):
      ma_option['check_5'] = ma5.checkbox('EMA 5')
      ma_option['check_10'] = ma10.checkbox('EMA 10')
      ma_option['check_20'] = ma20.checkbox('EMA 20')
      ma_option['check_60'] = ma60.checkbox('EMA 60')
      ma_option['check_150'] = ma150.checkbox('EMA 150')
      ma_option['check_250'] = ma250.checkbox('EMA 250')
   else:
      ma_option['check_5'] = ma5.checkbox('WMA 5')
      ma_option['check_10'] = ma10.checkbox('WMA 10')
      ma_option['check_20'] = ma20.checkbox('WMA 20')
      ma_option['check_60'] = ma60.checkbox('WMA 60')
      ma_option['check_150'] = ma150.checkbox('WMA 150')
      ma_option['check_250'] = ma250.checkbox('WMA 250')
   

def calculate_ma(df, type, ma_option):
   ma_result = {}
   for k,v in ma_option.items():
      if(v == True):
         window_param = k.split('_')[1]
         if(type == 'MA'):
            ma_result[k] = ta.ma(df['Close'], length = int(window_param))
         elif (type == 'EMA'):
            ma_result[k] = ta.ema(df['Close'], length = int(window_param))
         else:
            ma_result[k] = ta.wma(df['Close'], length = int(window_param))
   return ma_result

def plot_ma(df, stock_name, type, ma_result, title_config, plotly_config):
   fig = create_candlestick(df, stock_name)
   fig.update_layout(title=stock_name, font=title_config)
   for k, v in ma_result.items():
      window_param = k.split('_')[1]
      if not math.isnan(v[-1]):
         fig.add_trace(go.Scatter(x= df.index, y=v.values, name=f'{window_param} {type}'))
   st.plotly_chart(fig, use_container_width=True, config = plotly_config)

plotly_config = {
   'displayModeBar': True
}

title_config = {
    "family":"Courier New, monospace",
     "size":18,
     "color":"RebeccaPurple"
}


ma_option = {
   'check_5': True,
   'check_10': True,
   'check_20': True,
   'check_60': True,
   'check_150': True,
   'check_250': True,
}

st.set_page_config(layout="wide")
yf.pdr_override()

st.header("Stock Dashboard")

ta_with_price_chart = ['Bollinger Bands', 'SAR', 'MA', 'EMA', 'WMA']

col1,col2, = st.columns(2)

str_start_date = col1.text_input('From:','dd/MM/yyyy')
str_end_date = col2.text_input('To:','dd/MM/yyyy')

try:
   start_date = datetime.strptime(str_start_date, '%d/%m/%Y')
   end_date  = datetime.strptime(str_end_date, '%d/%m/%Y')
except:
   start_date = None
   end_date = None

col3, col4 = st.columns(2)

# option = col3.selectbox('Select the stock', 
# ('3690.HK', '9988.HK', '0700.HK', '9688.HK','1772',)
# )
option = col3.text_input('Stock Dashboard','')

indicator_option = col4.selectbox('Select Technical Indicator',
('MACD', 'RSI', 'MFI', 'KDJ', 'Bollinger Bands', 'SAR', 'MA', 'EMA', 'WMA')
)

if(indicator_option == 'MACD'):
   fast, slow, ema = st.columns(3)
   fast_param = fast.text_input('Short window:',12)
   slow_param = slow.text_input('Long window', 26)
   sig_param = ema.text_input('EMA window', 9)
elif(indicator_option == 'RSI'):
   short_rsi, mid_rsi, long_rsi = st.columns(3)
   short_rsi_window = short_rsi.text_input('Short RSI window', 6)
   mid_rsi_window = mid_rsi.text_input('Mid RSI window', 12)
   long_rsi_window = long_rsi.text_input('Long RSI window', 24)
elif (indicator_option == 'KDJ'):
   kdj_length, kdj_sign = st.columns(2)
   kdj_length_param = kdj_length.text_input('Fast K window', 9)
   kdj_sign_param = kdj_sign.text_input('Slow K window', 3)
elif (indicator_option == 'MFI'):
   MFI_window = st.text_input('MFI window', 14)
elif(indicator_option == 'Bollinger Bands'):
   BBW_window = st.text_input('BBW window',14)
elif(indicator_option == 'MA'):
   generateMAOption(indicator_option, ma_option)
elif(indicator_option == 'EMA'):
   generateMAOption(indicator_option, ma_option)
elif(indicator_option == 'WMA'):
   generateMAOption(indicator_option, ma_option)


if((option !=None and option !='') and start_date != None and end_date != None):
   try:
      df = pdr.get_data_yahoo(option, start_date,end_date)
      if indicator_option not in ta_with_price_chart:
         plot_candlestick(df, option, title_config, plotly_config)
         plot_volume(df,title_config, plotly_config)

      if(indicator_option == 'MACD'):
         macd_df = ta.macd(df['Close'],fast = int(fast_param), slow = int(slow_param), sign = int(sig_param))
         chart_title = f'MACD ({fast_param},{slow_param},{sig_param})'
         plot_macd(df.index, macd_df.iloc[:,0], macd_df.iloc[:,1], macd_df.iloc[:,2],chart_title,title_config, plotly_config)
      elif (indicator_option == 'RSI'):
         s_rsi = ta.rsi(df['Close'], length = int(short_rsi_window))
         m_rsi = ta.rsi(df['Close'], length = int(mid_rsi_window))
         l_rsi = ta.rsi(df['Close'], length = int(long_rsi_window))
         plot_rsi(df.index, s_rsi.values, m_rsi.values, l_rsi.values, short_rsi_window, mid_rsi_window, long_rsi_window,title_config, plotly_config)
      elif(indicator_option == 'KDJ'):
         kdj_df = ta.kdj(df['High'], df['Low'], df['Close'], length = int(kdj_length_param), sign = int(kdj_sign_param))
         plot_kdj(df.index, kdj_df.iloc[:,0], kdj_df.iloc[:,1], kdj_df.iloc[:,2], title_config, plotly_config)
      elif(indicator_option == 'MFI'):
         MFI = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length = int(MFI_window))
         chart_title = f'MFI({MFI_window})'
         mfi_fig = go.Figure()
         mfi_fig.add_trace(go.Scatter(x=df.index, y=MFI.values, name=f'MFI({MFI_window})'))
         mfi_fig.update_layout(title= chart_title, font = title_config)
         st.plotly_chart(mfi_fig, use_container_width = True, config = plotly_config)
      elif(indicator_option == 'Bollinger Bands'):
         bbands_df = ta.bbands(df['Close'], length = int(BBW_window))
         st.header(f'{option} Bollinger Bands{BBW_window} and daily price')
         plot_bollinger_brand(df, option, bbands_df.iloc[:,2], bbands_df.iloc[:,1], bbands_df.iloc[:,0],title_config, plotly_config)
         plot_volume(df,title_config, plotly_config)
      elif(indicator_option == 'SAR'):
         sar = ta.psar(df['High'], df['Low'], df['Close'])
         sar.iloc[:,0] =sar.iloc[:,0].mask(sar.iloc[:,0].isna(), sar.iloc[:,1])
         plot_sar(df, option, sar.iloc[:,0],title_config, plotly_config)
         plot_volume(df,title_config, plotly_config)
      elif(indicator_option == 'MA' or indicator_option == 'EMA' or indicator_option == 'WMA'):
         ma_result = calculate_ma(df, indicator_option, ma_option)
         # if(indicator_option == 'MA'):
         #    st.header('Simple Moving Average')
         # elif (indicator_option == 'EMA'):
         #    st.header('Exponential Moving Average')
         # else:
         #    st.header('Weighted Moving Average')
         plot_ma(df, option, indicator_option, ma_result, title_config,plotly_config)
         plot_volume(df,title_config, plotly_config)
   except:
      st.text('Incorrect stock number')