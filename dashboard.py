import streamlit as st, pandas as pd, numpy as np, yfinance as yf
import plotly.express as px
import pandas_ta as ta
from stocknews import StockNews
import requests
from textblob import TextBlob
from bs4 import BeautifulSoup
import spacy

api_key = '08580393d090448282a4532bbaa1ce1c'
nlp = spacy.load("en_core_web_sm")


st.title('Stock Dashboard')
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

data = yf.download(ticker, start=start_date, end=end_date)
fig = px.line(data, x=data.index, y=data['Adj Close'], title = ticker)
st.plotly_chart(fig)

pricing_data, tech_indicator, news = st.tabs(["Pricing Data", "Technical Analysis", "Sentiment Analysis"])

with pricing_data:
    st.header('Price Movements')
    data2 = data
    data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
    data2.dropna(inplace = True)
    st.write(data2)
    annual_return = data2['% Change'].mean()*252*100
    st.write('Annual Return is ', annual_return,'%')
    stdev = np.std(data2['% Change'])*np.sqrt(252)
    st.write('Standard Deviation is ',stdev*100,'%')
    st.write('Risk Adj Return is ',annual_return/(stdev*100),'%')



def obtenir_articles_presse(ticker):
    url = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'articles' in data:
            articles = [article['url'] for article in data['articles'][:20]]
            return articles
        else:
            return None
    else:
        st.error(f"Erreur lors de la récupération des articles de presse. Code d'erreur : {response.status_code}")
        return None

def obtenir_contenu_article(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        article_content = ' '.join([p.text for p in soup.find_all('p')])
        return article_content
    else:
        return None

def analyse_sentiments(text):
    doc = nlp(text)
    blob = TextBlob(text)
    sentiment = blob.sentiment
    return sentiment


with news:
    articles = obtenir_articles_presse(ticker)

    if articles:
        st.success(f"Press articles related to {ticker} successfully retrieved.")
        st.write("Sentiment analysis :")

        for idx, article_url in enumerate(articles, start=1):
            article_content = obtenir_contenu_article(article_url)
            if article_content:
                sentiments = analyse_sentiments(article_content)
                st.subheader(f"Article {idx} URL :")
                st.write(article_url)
                st.write("Polarity  :", sentiments.polarity)
                st.write("Subjectivity  :", sentiments.subjectivity)
                st.write("\n")
            else:
                st.warning(f"Unable to retrieve the content of the article from the URL : {article_url}")
    else:
        st.warning("Unable to obtain news articles.")

    # st.header(f'News of {ticker}')
    # sn = StockNews(ticker, save_news=False)
    # df_news = sn.read_rss()
    # for i in range(10):
    #     st.subheader(f'News {i+1}')
    #     st.write(df_news['published'][i])
    #     st.write(df_news['title'][i])
    #     st.write(df_news['summary'][i])
    #     title_sentiment = df_news['sentiment_title'][i]
    #     st.write(f'Title Sentiment {title_sentiment}')
    #     news_sentiment = df_news['sentiment_summary'][i]
    #     st.write(f'News Sentiment {news_sentiment}')




with tech_indicator:
    st.subheader('Technical Analysis Dashboard')
    df = pd.DataFrame()
    ind_list = df.ta.indicators(as_list=True)
    tech_indicator = st.selectbox('Tech Indicator', options = ind_list)
    method = tech_indicator
    indicator = pd.DataFrame(getattr(ta,method)(low=data['Low'], close=data['Close'], high=data['High'], open=data['Open'], volume=data['Volume']))
    figW_ind_new = px.line(indicator)
    st.plotly_chart(figW_ind_new)
    st.write(indicator)





