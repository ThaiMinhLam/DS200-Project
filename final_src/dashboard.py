import streamlit as st
import pandas as pd
import threading
import json
import glob
import os
import plotly.express as px
import altair as alt
import ast
import re
import random
from icecream import ic
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import py_vncorenlp
from collections import Counter

labels_aspect_list = {
    "hotel": [
        "HOTEL#LOCATION", "HOTEL#QUALITY", "HOTEL#FACILITIES", "HOTEL#STYLE",
        "WIFI", "PRICE", "ROOM#QUALITY", "ROOM#STYLE", "ROOM#FACILITIES", "ROOM#SOUND",
        "ROOM#VIEW", "ROOM#ATMOSPHERE", "ROOM#CLEANLINESS", "SERVICE#STAFF", "SERVICE#CHECKIN"
    ],
    "restaurant": [
        "LOCATION", "PRICE", "FOOD#QUALITY", "FOOD#VARIETY", "FOOD#PRESENTATION",
        "FOOD#FRESHNESS", "DRINK#QUALITY", "ENVIRONMENT#CLEANLINESS", "ENVIRONMENT#AMBIENCE",
        "SERVICE#STAFF", "SERVICE#ORDER"
    ],
    "drinkplace": [
        "LOCATION", "PRICE", "FOOD#QUALITY", "DRINK#QUALITY", "DRINK#VARIETY",
        "ENVIRONMENT#CLEANLINESS", "ENVIRONMENT#AMBIENCE", "SERVICE#STAFF", "SERVICE#ORDER"
    ],
    "eatery": [
        "LOCATION", "PRICE", "FOOD#QUALITY", "FOOD#VARIETY", "DRINK#QUALITY", "DRINK#VARIETY",
        "ENVIRONMENT#CLEANLINESS", "ENVIRONMENT#AMBIENCE", "SERVICE#STAFF", "SERVICE#ORDER"
    ],
    "attraction": [
        "LOCATION", "PRICE", "SERVICE#STAFF", "ENVIRONMENT#SCENERY", 
        "ENVIRONMENT#ATMOSPHERE", "EXPERIENCE#ACTIVITY"
    ],
    "renting": [
        "LOCATION", "PRICE", "SERVICE#RENTING", "SERVICE#STAFF", "VEHICLE#QUALITY"
    ],
    "tour": [
        "LOCATION", "PRICE", "SERVICE#STAFF", "EXPERIENCE#ACTIVITY",
        "ENVIRONMENT#SCENERY", "ENVIRONMENT#ATMOSPHERE"
    ],
    "camping": [
        "LOCATION#DISTANCE", "LOCATION#ACCESSIBILITY", "SERVICE#STAFF",
        "ENVIRONMENT#SCENERY", "ENVIRONMENT#WEATHER", "ENVIRONMENT#ATMOSPHERE"
    ]
}

def combine_df(folder_path: str):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    listDF = []
    # for file in csv_files:
    #     try:
    #         listDF.append(pd.read_csv(file, index_col=0))
    #     except:
    #         raise ValueError(f"{file}")
    listDF = [pd.read_csv(file, index_col=0) for file in csv_files]
    finalDF = pd.concat(listDF, ignore_index=True)
    return finalDF


def calculate_sentiment_aspects(set_aspects: str):
    aspects = ast.literal_eval(set_aspects)
    countSentiments = [0, 0, 0]
    for sentiment in aspects.values():
        if sentiment == 'NEGATIVE':
            countSentiments[0] += 1
        elif sentiment == 'NEUTRAL':
            countSentiments[1] += 1
        elif sentiment == 'POSITIVE':
            countSentiments[2] += 1
    return countSentiments


def createDF_total_sentiments(inputDF: pd.DataFrame) -> pd.DataFrame:
    """
    Dataframe chứa tần suất sentiment xuất hiện
    """
    inputDF['sentiment'] = inputDF["aspect_result"].apply(calculate_sentiment_aspects)
    
    # Tính tổng sentiment trên toàn dataset
    total_sentiments = [0, 0, 0]
    for row in inputDF['sentiment']:
        for idx in range(3):
            total_sentiments[idx] += row[idx]
    
    sentiments = ['NEGATIVE', 'NEUTRAL', 'POSITIVE']
    resultDF = pd.DataFrame({
        'sentiment': sentiments,
        'count_sentiment': total_sentiments
    })
    
    return resultDF
    

def make_pie(sentiment_df: pd.DataFrame) -> None:
    fig = px.pie(
        sentiment_df,
        names='sentiment',
        values='count_sentiment',
        color_discrete_sequence=["#77CC7A", "#EF553B", "#86D0F6"],
        category_orders={'sentiment': ['POSITIVE', 'NEGATIVE', 'NEUTRAL']},
        hole=0.5  # Tạo donut chart, bỏ nếu muốn pie chart truyền thống
    )
    fig.update_layout(
        title={
            'text': 'Distribution of Sentiments',
            'y':0.95,
            'x':0,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': dict(size=22, color='black', family='Segoe UI, sans-serif')
        },
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,                    
            font=dict(size=14, color="black")
        ),
    )
    fig.update_traces(
        textinfo='percent',
        textfont_size=18,
        pull=0
    )
    st.plotly_chart(fig, use_container_width=True, key="sentiment_distribution")


def createDF_explode_aspects(inputDF: pd.DataFrame) -> pd.DataFrame:
    """
    Dataframe chứa aspect + sentiment
    """
    records = []
    for _, row in inputDF.iterrows():
        aspects_dict = ast.literal_eval(row["aspect_result"])
        review = row['text']
        place = row['place_extracted']
        for aspect, sentiment in aspects_dict.items():
            records.append({
                "text": review,
                'place_extracted': place,
                "aspect": aspect,
                "sentiment": sentiment
            })
    return pd.DataFrame(records)

   
def make_horizontal(aspectsDF: pd.DataFrame) -> None:
    countDF = aspectsDF.value_counts(["aspect", 'sentiment']).reset_index(name='count')
    countDF["aspect_total"] = countDF.groupby("aspect")["count"].transform("sum")
    countDF["percent"] = (countDF["count"] / countDF["aspect_total"] * 100).round(1).astype(str) + '%'
    countDF = countDF.sort_values(["aspect", 'sentiment'])
    
    fig = px.bar(
        countDF,
        x="count",
        y="aspect",
        color="sentiment",          # Hue following sentiment
        orientation='h',
        color_discrete_sequence=["#77CC7A", "#EF553B", "#86D0F6"],
        category_orders={'sentiment': ['POSITIVE', 'NEGATIVE', 'NEUTRAL']},
        text='percent'
    )
    fig.update_layout(
        title={
            'text': 'Aspect Frequency by Sentiment',
            'y':0.95,
            'x':0,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': dict(
                size=22,
                color='black',
                family='Segoe UI, sans-serif'
            )
        },
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            tickfont=dict(size=14, color='black', family='Roboto, sans-serif'), 
            title='Sentiment Mentions',
            title_font=dict(size=16, color='black', family='Roboto Bold')
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            tickfont=dict(size=14, color='black', family='Roboto, sans-serif'),
            title=None),
        legend=dict(
            title="",
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,                    
            font=dict(size=14, color="black")
        ),
        plot_bgcolor="white",
        barmode='stack',
    )
    fig.update_traces(
        textposition='inside',
        insidetextanchor='start',
        textfont=dict(size=13, color='black', family='Roboto, sans-serif')
    )
    st.plotly_chart(fig, use_container_width=True, key="aspect_frequency")


def createDF_sentiment_places(inputDF: pd.DataFrame) -> pd.DataFrame:
    inputDF['sentiment'] = inputDF["aspect_result"].apply(calculate_sentiment_aspects)
    inputDF['negative'] = inputDF['sentiment'].apply(lambda x: x[0])
    inputDF['positive'] = inputDF['sentiment'].apply(lambda x: x[2])
    summaryDF = inputDF.groupby("place_extracted").agg({
        'positive': 'sum',
        'negative': 'sum',
    }).reset_index()
    summaryDF["place_extracted"] = summaryDF["place_extracted"].apply(lambda x: x.title())
    return summaryDF


def make_horizontal_top_places(top_placesDF: pd.DataFrame, top_n: int, sentiment: str) -> None:
    top_placesDF = top_placesDF.sort_values(by=sentiment, ascending=False).head(top_n)
    if sentiment == 'positive':
        gradient_colors = list(reversed(['#FFA726', '#FFB653', '#FFC971', '#FFDC9E', "#F8E5BE"][:len(top_placesDF)]))
    elif sentiment == 'negative':
        gradient_colors = list(reversed(['#D32F2F', '#E57373', '#F48FB1', '#F8BBD0', '#FCE4EC'][:len(top_placesDF)]))

    fig = px.bar(
        top_placesDF.sort_values(by=sentiment, ascending=True),
        x=sentiment,
        y="place_extracted",
        orientation='h',
        text=None,
        height=320
    )
    fig.update_layout(
        title={
            'text': f'Top {sentiment} Places'.title(),
            'y':1,
            'x':0,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': dict(size=22, color='black', family='Segoe UI, sans-serif')
        },
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            tickfont=dict(size=14, color='black', family='Roboto, sans-serif'), 
            title=f'{sentiment} Mentions'.title(),
            title_font=dict(size=16, color='black', family='Roboto Bold')
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            tickfont=dict(size=14, color='black', family='Roboto, sans-serif'),
            title=None),
        plot_bgcolor='white',
        bargap=0.3,
        margin=dict(t=20, b=20, l=10, r=10)
    )
    fig.update_traces(
        marker_color=gradient_colors,
        marker_line_width=0,
        marker_line_color='rgba(0,0,0,0)',
        marker=dict(line=dict(width=0)),
        width=0.6 
    )
    st.plotly_chart(fig, use_container_width=True, key=f"top_{sentiment}_places")


def make_summary(inputDF: pd.DataFrame):
    numReviews = len(inputDF)
    numPlaces = len(inputDF["place_extracted"].unique())
    numAspects =  len(inputDF['aspect_result'].apply(lambda x: list(ast.literal_eval(x).keys())).explode().dropna().unique())
    
    st.markdown(
        f"""
<div style="
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    width: 300px;
    background-color: white;
    font-family: 'Segoe UI', Tahoma, sans-serif;
">
    <div style="font-size: 22px; font-weight: 600; color: #333;">📊 Mentions Summary</div>
    <div style="display: flex; align-items: center; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; margin-right: 12px;">
            <span style="font-size: 26px; color: #28C3D4;">📝</span>
        </div>
        <div>
            <div style="font-size: 20px; font-weight: bold; color: #000;">{numReviews:,}</div>
            <div style="font-size: 13px; letter-spacing: 1px; color: #888;">TOTAL REVIEWS</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; margin-right: 12px;">
            <span style="font-size: 26px; color: #28C3D4;">📍</span>
        </div>
        <div>
            <div style="font-size: 20px; font-weight: bold; color: #000;">{numPlaces:,}</div>
            <div style="font-size: 13px; letter-spacing: 1px; color: #888;">TOTAL PLACES</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; margin-right: 12px;">
            <span style="font-size: 26px; color: #28C3D4;">🎯</span>
        </div>
        <div>
            <div style="font-size: 20px; font-weight: bold; color: #000;">{numAspects:,}</div>
            <div style="font-size: 13px; letter-spacing: 1px; color: #888;">TOTAL ASPECTS</div>
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True
    )


def get_vncorenlp_model():
    if 'vncorenlp_model' not in st.session_state:
        st.session_state.vncorenlp_model = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir=r"F:\Studies\Third_year\Big_data\VnCoreNLP")
    return st.session_state.vncorenlp_model


def create_dictionary_words(inputDF: pd.DataFrame) -> pd.DataFrame:
    def is_word(token):
        return bool(re.search(r'\w+', token))
    
    def segment_clean(text):
        segmented = model.word_segment(text)[0].split()  # List từ và dấu câu
        words_only = [token for token in segmented if is_word(token)]
        return words_only
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model = get_vncorenlp_model()
    os.chdir(current_dir)
    inputDF['list_word'] = inputDF['text'].apply(segment_clean)
    allWords = inputDF['list_word'].explode().dropna().tolist()
    wordCounts = Counter(allWords)
    return wordCounts


def make_wordcloud(dictWords: dict, N: int) -> None:
    topWords = dict(sorted(dictWords.items(), key=lambda x: x[1], reverse=True)[:N])
    topWords = {k.replace('_', ' '): v for k, v in topWords.items()}
    wordcloud = WordCloud(width=700, height=400, background_color='white', colormap='viridis')
    wordcloud.generate_from_frequencies(topWords)
    st.markdown(f"<h3 style='color:black'>Frequent Words</h3>", unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off') # tắt khung
    ax.imshow(wordcloud, interpolation='bilinear')
    st.pyplot(fig)
    
    
def make_show_comments_from_places(aspectsDF: pd.DataFrame, N_places: int, N_comments: int) -> None:
    groupedDF = aspectsDF.groupby(["place_extracted", "aspect", 'sentiment'])['text'].apply(list).reset_index(name='reviews')
    
    with st.form("filter_form"):
        col = st.columns(2)
        with col[0]:
            aspect_options = groupedDF["aspect"].unique()
            st.markdown("<div style='font-size:20px; font-weight:600; color:black;'>🎯 Select Aspect</div>", unsafe_allow_html=True)
            selected_aspect = st.selectbox("", aspect_options)
        
        with col[1]:
            sentiment_options = groupedDF['sentiment'].unique()
            st.markdown("<div style='font-size:20px; font-weight:600; color:black;'>💬 Select Sentiment</div>", unsafe_allow_html=True)
            selected_sentiment = st.selectbox("", sentiment_options)

        st.markdown(f"<h3 style='color:black'>📍 Top Places Related to {selected_aspect}#{selected_sentiment}</h3>", unsafe_allow_html=True)
        submit = st.form_submit_button("✅ Apply Filter")
    
        if submit:
            filteredDF  = groupedDF[(groupedDF["aspect"] == selected_aspect) & (groupedDF['sentiment'] == selected_sentiment)]
            filteredDF['review_count'] = filteredDF['reviews'].apply(len)
            top_placesDF = filteredDF.sort_values(by='review_count', ascending=False).head(N_places).reset_index(drop=True)
            
            if not top_placesDF.empty:
                for idx, row in top_placesDF.iterrows():
                    assert row['sentiment'] == selected_sentiment
                    place = row['place_extracted']
                    reviews_list = list(set(row['reviews']))
                    random_reviews = random.sample(reviews_list, min(N_comments, len(reviews_list)))
                
                    st.markdown(f"<h3 style='color:black'>{idx+1}. {place.title()}</h3>", unsafe_allow_html=True)
                    for i, comment in enumerate(random_reviews, 1):
                        st.markdown(f"<div style='font-size:20px; font-weight:500;'>👉 {comment}</div>", unsafe_allow_html=True)
            else:
                st.warning("Không tìm thấy bình luận phù hợp.")


def make_show_places(inputDF: pd.DataFrame, N: int):
    inputDF['place_extracted'] = inputDF['place_extracted'].apply(lambda x: re.sub(r"^[,.!?]+|[,.!?]+$", "", x).strip())
    top_placesDF = inputDF['place_extracted'].dropna().value_counts().reset_index().head(N)

    st.markdown("<h3 style='color:black'>🏔️ Top Mentioned Places</h3>", unsafe_allow_html=True)
    for idx, row in top_placesDF.iterrows():
        st.markdown(f"""
            <div style='padding:10px; background-color:#f0f0f0; border-radius:8px; margin-bottom:10px;'>
                <h4 style='color:#333;'>{idx+1}. {row['place_extracted'].title()}</h4>
                <p style='font-size:18px;'>⭐ <strong>{row['count']}</strong> mentions</p>
            </div>
        """, unsafe_allow_html=True)

def main():
    st.title("Social Listening")
    
    st.set_page_config(
        page_title="Dalat Reviews Dashboard",
        page_icon="🌄",
        layout="wide",
        initial_sidebar_state="expanded")

    alt.themes.enable("dark")

    # Stop event để dừng thread an toàn
    if "viewer_stop_event" not in st.session_state:
        st.session_state.viewer_stop_event = threading.Event()
    if "viewer_thread" not in st.session_state:
        st.session_state.viewer_thread = None
    
    # finalDF = combine_df("annotated_labels")
    finalDF = pd.read_csv(r'F:\Studies\Third_year\Big_data\Final_Code\Result\result.csv')
    
    # Design SideBar
    with st.sidebar:
        st.title('🌄 Dalat Reviews Dashboard')
        all_domains = [d for d in finalDF['domain_extracted'].unique() if pd.notna(d)]
        with st.form("domain_form"):
            st.markdown("<div style='font-size:18px; font-weight:600; color:black;'>🏷️ Select Domain</div>", unsafe_allow_html=True)
            selected_domains = st.selectbox("", all_domains)
            ic(selected_domains)
            submit = st.form_submit_button("✅ Apply Filter")
            
            if submit:
                # Tải lại dữ liệu mới mỗi khi nhấn Apply Filter
                finalDF = pd.read_csv(r'F:\Studies\Third_year\Big_data\Final_Code\Result\result.csv')

    filtered_df = finalDF[finalDF['domain_extracted'] == selected_domains]
    sentimentDF = createDF_total_sentiments(filtered_df)
    
    col = st.columns((1, 2), gap='large')
    # Design Column 1
    with col[0]:
        make_summary(filtered_df)
        make_pie(sentimentDF)
        
    # Design Column 2
    with col[1]:
        top_placesDF = createDF_sentiment_places(filtered_df)
        make_horizontal_top_places(top_placesDF, 5, 'positive')
        make_horizontal_top_places(top_placesDF, 5, 'negative')
    
    aspectsDF = createDF_explode_aspects(filtered_df)
    dictWords = create_dictionary_words(filtered_df)
    
    make_horizontal(aspectsDF)
    make_wordcloud(dictWords, 100)
    make_show_places(filtered_df, 5)
    make_show_comments_from_places(aspectsDF, 5, 5)

if __name__ == "__main__":
    main()