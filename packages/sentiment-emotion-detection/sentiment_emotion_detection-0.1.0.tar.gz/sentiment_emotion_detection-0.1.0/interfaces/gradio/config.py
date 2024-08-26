from transformers import pipeline
from langchain_together import Together

# Initialize the sentiment analysis model pipeline
SENTIMENT_MODEL_NAME = "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
SENTIMENT_PIPE = pipeline("text-classification", model=SENTIMENT_MODEL_NAME, top_k=None)

# Initialize the emotion detection model pipeline
EMOTION_MODEL_NAME = "SamLowe/roberta-base-go_emotions"
EMOTION_PIPE = pipeline("text-classification", model=EMOTION_MODEL_NAME , top_k=None)

# Initialize the LLM for personalized advice
TOGETHER_API_KEY = "5eed339da3bc5e71bc72d500b21c1cde4dee9409c81bc6050f1472e6c91c5188"
llm = Together(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    together_api_key=TOGETHER_API_KEY,
    max_tokens=100,
    temperature=0.7,
    top_p=0.7,
    top_k=50,
    repetition_penalty=1,
)