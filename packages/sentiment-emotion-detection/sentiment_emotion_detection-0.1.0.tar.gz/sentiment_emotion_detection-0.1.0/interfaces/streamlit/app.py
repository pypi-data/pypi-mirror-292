import streamlit as st
import time
import urllib.parse
from config import get_theme_color, sentiment_pipe, emotion_pipe
from utils import classify_text, get_fun_fact, add_to_history, display_history, generate_advice, run_tutorial
from visualization import create_bar_chart, create_emotion_bar_chart, get_emoji, get_emotion_emoji
from layout import apply_layout

def main():
    st.set_page_config(page_title="Funtime Sentiment and Emotion Analyzer", page_icon="🎭", layout="wide")
    
    theme = st.sidebar.selectbox("Choose Theme", ["Normal", "Unnormal", "Fun"])
    primary_color = get_theme_color(theme)
    
    apply_layout(primary_color)

    st.markdown('<p class="big-font">Funtime Sentiment and Emotion Analyzer 🎭🎉</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Discover the mood behind your words and have a blast!</p>', unsafe_allow_html=True)
    
    run_tutorial()

    with st.sidebar:
        st.image("https://exemplary.ai/img/blog/sentiment-analysis/sentiment-analysis.svg", use_column_width=True)
        st.markdown("## About")
        st.info("This app uses AI to analyze the sentiment and emotion of your text. Have fun exploring emotions!")
        
        if st.button("View Analysis History"):
            display_history()
    
    user_input = st.text_area("Enter your text here:", height=150, 
                              placeholder="Type or paste your text here... Let's see how it feels! 😊")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("Analyze Sentiment", key="analyze"):
            if user_input:
                with st.spinner("Analyzing your text... 🕵️‍♂️"):
                    sentiment_result = classify_text(user_input, sentiment_pipe)
                    emotion_result = classify_text(user_input, emotion_pipe)

                    sentiment_result_sorted = sorted(sentiment_result, key=lambda x: x['score'], reverse=True)
                    emotion_result_sorted = sorted(emotion_result, key=lambda x: x['score'], reverse=True)[:6]  # Top 6 emotions

                    top_sentiment = sentiment_result_sorted[0]['label']
                    top_sentiment_score = sentiment_result_sorted[0]['score']
                    top_emotion = emotion_result_sorted[0]['label']
                    top_emotion_score = emotion_result_sorted[0]['score']

                    st.markdown("### All Sentiment Scores")
                    add_to_history(user_input, top_sentiment, top_sentiment_score, top_emotion, top_emotion_score)
                    
                    st.plotly_chart(create_bar_chart(sentiment_result), use_container_width=True)
                    
                    sentiment_emoji = get_emoji(top_sentiment)
                    if top_sentiment == "positive":
                        st.success(f"{sentiment_emoji} Your text has a positive vibe with a confidence score of {top_sentiment_score:.2f}!")
                        st.balloons()
                    elif top_sentiment == "neutral":
                        st.info(f"{sentiment_emoji} Your text has a neutral tone with a confidence score of {top_sentiment_score:.2f}.")
                    else:
                        st.error(f"{sentiment_emoji} Your text seems a bit negative with a confidence score of {top_sentiment_score:.2f}.")
                        st.snow()

                    st.markdown("---")
                    st.markdown("### Top 6 Emotions")
                    st.plotly_chart(create_emotion_bar_chart(emotion_result_sorted), use_container_width=True)
                    
                    for emotion in emotion_result_sorted:
                        emotion_emoji = get_emotion_emoji(emotion['label'])
                        st.write(f"{emotion_emoji} {emotion['label'].capitalize()}: {emotion['score']:.2f}")

                    st.markdown("---")
                    st.markdown("### Fun Fact", unsafe_allow_html=True)
                    st.markdown(f'<div class="info-box">{get_fun_fact(top_sentiment)}</div>', unsafe_allow_html=True)

                    # Generate advice based on the analysis
                    st.markdown("---")
                    advice = generate_advice(top_sentiment, emotion_result_sorted, user_input)
                    st.markdown("### Personalized Advice")
                    st.markdown(f'<div class="info-box">{advice}</div>', unsafe_allow_html=True)

                    # Create tweet text
                    top_emotions_text = ', '.join([
                        f'{get_emotion_emoji(e["label"])} {e["label"].capitalize()} ({e["score"]:.2f})' 
                        for e in emotion_result_sorted[:3]
                    ])
                    tweet_text = (
                        f"🎉 Analyzed text: \"{user_input}\" – Sentiment: {top_sentiment} ({top_sentiment_score:.2f})\n"
                        f"Top Emotions: {top_emotions_text}\n"
                        f"Discover more with the Sentiment & Emotion Analyzer! 🌟 #SentimentAnalysis #EmotionDetection #NLP"
                    )
                    
                    tweet_text_encoded = urllib.parse.quote(tweet_text)
                    tweet_url = f"https://twitter.com/intent/tweet?text={tweet_text_encoded}"
                    st.markdown("---")
                    st.markdown(f'<a href="{tweet_url}" target="_blank" class="tweet-button">Tweet this result! 🐦</a>', unsafe_allow_html=True)
            else:
                st.warning("Oops! The text box seems lonely. Give it some words to analyze! 📝😉")

    st.markdown("---")
    st.markdown("### Recent Updates")
    updates = [
        "Added a theme switcher for personalized experience",
        "Implemented an interactive tutorial for new users",
        "Introduced animated transitions for a more dynamic feel",
        "Enhanced the layout and styling of the app",
        "Changed the model to lxyuan/distilbert-base-multilingual-cased-sentiments-student for comprehensive sentiment analysis (positive, negative, and neutral scores).",
        "Added emotion detection feature using SamLowe/roberta-base-go_emotions model.",
        "Incorporated personalized advice generation based on sentiment and emotion analysis, using the meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo model."
    ]
    for update in updates:
        st.markdown(f"- {update}")

if __name__ == "__main__":
    main()
