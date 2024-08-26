#utils.py

from config import llm
import random
import time
import streamlit as st
from visualization import get_emotion_emoji

def run_tutorial():
    if 'tutorial_complete' not in st.session_state:
        st.session_state.tutorial_complete = False

    if not st.session_state.tutorial_complete:
        st.info("Welcome to the Funtime Sentiment and Emotion Analyzer! Let's take a quick tour.")
        step = st.empty()
        
        tutorial_button = st.button("Start Tutorial")
        
        if tutorial_button:
            for i in range(1, 5):
                if i == 1:
                    step.info("Step 1: Enter your text in the text area below.")
                elif i == 2:
                    step.info("Step 2: Click the 'Analyze Sentiment' button to see the results.")
                elif i == 3:
                    step.info("Step 3: Explore your sentiment history in the sidebar.")
                else:
                    step.success("Tutorial complete! Enjoy analyzing sentiments and emotions!")
                    st.session_state.tutorial_complete = True
                    step.empty()  # Clear the tutorial step after completion
                    # Use rerun to refresh the page and update UI
                    st.rerun()  # Force a rerun of the app
                time.sleep(2)
        
        if not st.session_state.tutorial_complete:
            st.stop()  # Stop the script execution until the tutorial is complete

def classify_text(text, pipe):
    result = pipe(text)[0]  # Extract the inner list from the pipeline output
    return result

def get_fun_fact(sentiment):
    positive_facts = [
        "Did you know? Smiling can boost your mood and immune system!",
        "Optimists tend to live longer than pessimists. Keep up the positivity!",
        "Laughing for 15 minutes burns up to 40 calories. Time for a comedy!",
    ]
    neutral_facts = [
        "Neutral emotions can be a sign of a balanced perspective.",
        "Did you know? Being neutral can help in making unbiased decisions.",
        "Keeping a neutral stance can sometimes be the best approach in conflicts."
    ]
    negative_facts = [
        "Chocolate can help improve your mood. Maybe it's time for a treat?",
        "Negative emotions can be useful for problem-solving and critical thinking.",
        "Did you know? Crying can help release stress and improve your mood.",
    ]
    if sentiment == "positive":
        return random.choice(positive_facts)
    elif sentiment == "neutral":
        return random.choice(neutral_facts)
    else:
        return random.choice(negative_facts)

def get_sentiment_history():
    if 'history' not in st.session_state:
        st.session_state.history = []
    return st.session_state.history

def add_to_history(text, sentiment, sentiment_score, emotion, emotion_score):
    history = get_sentiment_history()
    history.append({
        "text": text,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "emotion": emotion,
        "emotion_score": emotion_score,
        "timestamp": time.time()
    })
    st.session_state.history = history


def display_history():
    history = get_sentiment_history()
    if history:
        st.markdown("### Sentiment and Emotion Analysis History")
        for item in reversed(history):
            sentiment_emoji = {"positive": "🟢", "neutral": "🟡", "negative": "🔴"}.get(item["sentiment"], "🤷")
            emotion_emoji = get_emotion_emoji(item["emotion"])
        
            st.markdown(f"{sentiment_emoji} **Sentiment:** {item['sentiment']} (Score: {item['sentiment_score']:.2f})")
            st.markdown(f"{emotion_emoji} **Top Emotion:** {item['emotion']} (Score: {item['emotion_score']:.2f})")
            st.markdown(f"Text: _{item['text'][:50]}{'...' if len(item['text']) > 50 else ''}_")
            st.markdown(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['timestamp']))}")
            st.markdown("---")
    else:
        st.info("No history available yet. Start analyzing to build your history!")

def generate_advice(sentiment, emotions, original_text):
    prompt = (
        f"The first user prompt was: \"{original_text[:100]}...\"\n\n"
        f"Based on the user prompt and following sentiment and emotions analysis:\n\n"
        f"Sentiment: {sentiment}\n"
        f"Top Emotions: {emotions[0]['label']} ({emotions[0]['score']:.2f}), "
        f"{emotions[1]['label']} ({emotions[1]['score']:.2f}), "
        f"{emotions[2]['label']} ({emotions[2]['score']:.2f}), "
        f"{emotions[3]['label']} ({emotions[3]['score']:.2f})\n\n"
        "Provide a brief, practical suggestion or piece of advice based on this analysis.\n"
        "Ensure it is empathetic, supportive, and conveyed in a friendly manner\n"
        "without any introductory phrases just directly give your advice.\n"
        "without suggesting further interaction or implying the ability to talk."
    )

    response = llm.invoke(prompt)
    
    # Directly return the response if it's a string
    if isinstance(response, str):
        return response.strip()
    
    # Raise an error if the response is not a string
    raise ValueError("Unexpected response format from LLM")
