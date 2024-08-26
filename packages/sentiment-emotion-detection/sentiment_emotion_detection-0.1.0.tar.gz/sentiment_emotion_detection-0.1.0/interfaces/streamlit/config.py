#config.py

from langchain_together import Together
from transformers import pipeline
TOGETHER_API_KEY = "5eed339da3bc5e71bc72d500b21c1cde4dee9409c81bc6050f1472e6c91c5188"

def get_theme_color(theme):
    if theme == "Normal":
        return "#636EFA"
    elif theme == "Unnormal":
        return "#00CC96"
    else:  # Fun theme
        return "#FF6692"

# Create a text classification pipeline for sentiment analysis
sentiment_pipe = pipeline("text-classification", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", top_k=None)

# Create a text classification pipeline for emotion detection
emotion_pipe = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

llm = Together(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    together_api_key=TOGETHER_API_KEY,
    max_tokens=100,
    temperature=0.7,
    top_p=0.7,
    top_k=50,
    repetition_penalty=1,
)
