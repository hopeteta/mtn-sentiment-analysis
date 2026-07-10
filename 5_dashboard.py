

from fpdf import FPDF
import tempfile
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from google_play_scraper import reviews, Sort


st.set_page_config(
    page_title="MTN Rwanda Sentiment Analysis",
    page_icon="📊",
    layout="wide"
)

USERS = {
    "mtn_admin": {"password": "mtn2026", "role": "admin"},
    "mtn_analyst": {"password": "analyst2026", "role": "analyst"}
}
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
    
        st.title("MTN Rwanda")
        st.subheader("Sentiment Analysis System")
        st.markdown("---")
        st.markdown("###  Admin Login")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.button("Login", use_container_width=True):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state['logged_in'] = True
                st.session_state['role'] = USERS[username]["role"]
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error(" Wrong username or password. Please try again.")


def get_sentiment(text):
    try:
        analysis = TextBlob(str(text))
        polarity = analysis.sentiment.polarity
        if polarity > 0.1:
            return 'positive', polarity
        elif polarity < -0.1:
            return 'negative', polarity
        else:
            return 'neutral', polarity
    except:
        return 'neutral', 0.0


@st.cache_data
def load_data():
    df = pd.read_csv('data/mtn_reviews_analysed.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df


def fetch_live_reviews():
    with st.spinner("Fetching latest reviews from Google Play Store..."):
        result, _ = reviews(
            'com.mtn1app',
            lang='en',
            country='rw',
            sort=Sort.NEWEST,
            count=100
        )
        df_live = pd.DataFrame(result)
        if len(df_live) == 0:
            return None
        df_live = df_live[['userName', 'content', 'score', 'at']]
        df_live.columns = ['username', 'review', 'rating', 'date']
        df_live = df_live.dropna(subset=['review'])

        sentiments = []
        scores = []
        for review_text in df_live['review']:
            sentiment, score = get_sentiment(review_text)
            sentiments.append(sentiment)
            scores.append(score)

        df_live['sentiment'] = sentiments
        df_live['confidence_score'] = scores
        return df_live

def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "MTN Rwanda - Sentiment Analysis Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Total Reviews Analysed: {len(df)}", ln=True, align="C")
    pdf.ln(5)

    pos = len(df[df['sentiment'] == 'positive'])
    neu = len(df[df['sentiment'] == 'neutral'])
    neg = len(df[df['sentiment'] == 'negative'])

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Positive: {pos} ({round(pos/len(df)*100,1) if len(df)>0 else 0}%)", ln=True)
    pdf.cell(0, 7, f"Neutral: {neu} ({round(neu/len(df)*100,1) if len(df)>0 else 0}%)", ln=True)
    pdf.cell(0, 7, f"Negative: {neg} ({round(neg/len(df)*100,1) if len(df)>0 else 0}%)", ln=True)
    pdf.ln(5)

    sentiment_counts = df['sentiment'].value_counts()
    colors_map = {'positive': '#2ecc71', 'negative': '#e74c3c', 'neutral': '#95a5a6'}
    colors = [colors_map[s] for s in sentiment_counts.index]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.set_title("Sentiment Distribution")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        chart_path = tmpfile.name
    plt.close(fig)

    pdf.image(chart_path, x=55, w=100)
    os.unlink(chart_path)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Review Details", ln=True)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(110, 7, "Review", border=1)
    pdf.cell(40, 7, "Sentiment", border=1)
    pdf.cell(30, 7, "Rating", border=1, ln=True)

    pdf.set_font("Helvetica", "", 8)
    for _, row in df.head(100).iterrows():
        review_text = str(row['review'])[:60].encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(110, 6, review_text, border=1)
        pdf.cell(40, 6, str(row['sentiment']), border=1)
        pdf.cell(30, 6, str(row['rating']), border=1, ln=True)

    return bytes(pdf.output())


def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def dashboard():
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(" MTN Rwanda - Customer Sentiment Analysis")
        st.markdown(" AI-Based Sentiment Analytics System")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"👤 Logged in as: **{st.session_state.get('username', '')}** ({st.session_state.get('role', '')})")
        if st.button(" Logout"):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.session_state['username'] = None
            st.rerun()

    st.divider()

    df = load_data()

    st.subheader("Live Review Analysis")
    st.markdown("Click the button below to fetch and analyse the latest MTN Rwanda reviews in real time.")

    if st.session_state.get('role') == 'admin':
        if st.button(" Refresh & Fetch Latest Reviews", use_container_width=True):
        df_live = fetch_live_reviews()
        if df_live is not None:
            st.success(f" Fetched and analysed {len(df_live)} latest reviews!")
            st.markdown("### Latest Reviews Sentiment:")
            col1, col2, col3 = st.columns(3)
            with col1:
                pos = len(df_live[df_live['sentiment']=='positive'])
                st.metric("Positive", pos)
            with col2:
                neu = len(df_live[df_live['sentiment']=='neutral'])
                st.metric("Neutral", neu)
            with col3:
                neg = len(df_live[df_live['sentiment']=='negative'])
                st.metric("Negative", neg)
            st.dataframe(
                df_live[['username', 'review', 'sentiment', 'rating']],
                use_container_width=True
            )
            st.info("These live reviews are not stored permanently.")
        else:
            st.warning("No new reviews found at this time.")

    st.divider()

   
    st.sidebar.title(" Filter Reviews")
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

    
    st.subheader(" Historical Analysis Overview")
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
        st.metric("Avg Star Rating", f"{avg_rating} ")

    st.divider()

    st.subheader(" Export Report")
    col1, col2 = st.columns(2)
    with col1:
        pdf_bytes = generate_pdf_report(filtered_df)
        st.download_button(
            label=" Download PDF Report",
            data=pdf_bytes,
            file_name="mtn_sentiment_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col2:
        csv_bytes = convert_to_csv(filtered_df)
        st.download_button(
            label=" Download Excel Report",
            data=csv_bytes,
            file_name="mtn_sentiment_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    st.divider()

    st.subheader(" Sentiment Charts")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Overall Sentiment Distribution**")
        sentiment_counts = filtered_df['sentiment'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = ['#798e8f', "#2ecc71", '#e74c3c']
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
        st.pyplot(fig)
        plt.close()

    st.divider()

  
    st.subheader(" Sentiment Trends Over Time")
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

    
    st.subheader(" Live Sentiment Tester")
    st.markdown("Type any review and the system will analyse it instantly!")
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
            st.markdown(f"**Polarity Score:** {round(polarity, 3)}")

    st.divider()

    
    st.subheader("📋 Historical Reviews Table")
    st.markdown(f"Showing {len(filtered_df)} reviews")
    st.dataframe(
        filtered_df[['username', 'review', 'sentiment', 'rating', 'date']],
        use_container_width=True
    )


if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    dashboard()
else:
    login_page()