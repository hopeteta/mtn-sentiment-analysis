
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob


st.set_page_config(
    page_title="MTN Rwanda Sentiment Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 MTN Rwanda - Customer Sentiment Analysis System")
st.markdown("**Final Year Project | AI-Based Sentiment Analysis | MTN Rwanda Case Study**")
st.divider()


@st.cache_data
def load_data():
    df = pd.read_csv('data/mtn_reviews_analysed.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()


st.sidebar.title("🔍 Filter Reviews")
sentiment_filter = st.sidebar.multiselect(
    "Filter by Sentiment",
    options=['positive', 'neutral', 'negative'],
    default=['positive', 'neutral', 'negative']
)

rating_filter = st.sidebar.multiselect(
    "Filter by Star Rating",
    options=[1, 2, 3, 4, 5],
    default=[1, 2, 3, 4, 5]
)


filtered_df = df[
    (df['sentiment'].isin(sentiment_filter)) &
    (df['rating'].isin(rating_filter))
]


st.subheader("📈 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Reviews", len(filtered_df))
with col2:
    positive_pct = round(len(filtered_df[filtered_df['sentiment']=='positive']) / len(filtered_df) * 100, 1)
    st.metric("Positive", f"{positive_pct}%")
with col3:
    negative_pct = round(len(filtered_df[filtered_df['sentiment']=='negative']) / len(filtered_df) * 100, 1)
    st.metric("Negative", f"{negative_pct}%")
with col4:
    avg_rating = round(filtered_df['rating'].mean(), 1)
    st.metric("Avg Star Rating", f"{avg_rating} ⭐")

st.divider()


st.subheader("📊 Sentiment Analysis Charts")
col1, col2 = st.columns(2)

with col1:
    
    st.markdown("**Overall Sentiment Distribution**")
    sentiment_counts = filtered_df['sentiment'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = ['#2ecc71', '#95a5a6', '#e74c3c']
    ax.pie(
        sentiment_counts,
        labels=sentiment_counts.index,
        autopct='%1.1f%%',
        colors=colors,
        startangle=140
    )
    st.pyplot(fig)
    plt.close()

with col2:
    
    st.markdown("**Sentiment Count**")
    fig, ax = plt.subplots(figsize=(6, 6))
    sns.countplot(
        data=filtered_df,
        x='sentiment',
        order=['positive', 'neutral', 'negative'],
        palette=['#2ecc71', '#95a5a6', '#e74c3c'],
        ax=ax
    )
    for p in ax.patches:
        ax.annotate(
            str(int(p.get_height())),
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='bottom', fontsize=12
        )
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Number of Reviews")
    st.pyplot(fig)
    plt.close()

st.divider()


st.subheader("📅 Sentiment Trends Over Time")
filtered_df['month'] = filtered_df['date'].dt.to_period('M').astype(str)
monthly = filtered_df.groupby(['month', 'sentiment']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12, 5))
monthly.plot(
    kind='line',
    color=['#e74c3c', '#95a5a6', '#2ecc71'],
    marker='o',
    ax=ax
)
ax.set_xlabel("Month")
ax.set_ylabel("Number of Reviews")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.divider()


st.subheader("🤖 Live Sentiment Tester")
st.markdown("Type any review below and the system will analyse its sentiment instantly!")

user_input = st.text_area("Enter a review about MTN Rwanda:", placeholder="e.g. MTN network is very slow today...")

if st.button("Analyse Sentiment"):
    if user_input.strip() == "":
        st.warning("Please enter a review first!")
    else:
        analysis = TextBlob(user_input)
        polarity = analysis.sentiment.polarity

        if polarity > 0.1:
            sentiment = "POSITIVE"
            color = "green"
            emoji = "😊"
        elif polarity < -0.1:
            sentiment = "NEGATIVE"
            color = "red"
            emoji = "😠"
        else:
            sentiment = "NEUTRAL"
            color = "gray"
            emoji = "😐"

        st.markdown(f"### Result: :{color}[{emoji} {sentiment}]")
        st.markdown(f"**Polarity Score:** {round(polarity, 3)} (range: -1 negative to +1 positive)")

st.divider()


st.subheader("📋 Review Data Table")
st.markdown(f"Showing {len(filtered_df)} reviews based on your filters")
st.dataframe(
    filtered_df[['username', 'review', 'sentiment', 'rating', 'date']],
    use_container_width=True
)