import random
import urllib.parse
import webbrowser
from config import SENTIMENT_PIPE, EMOTION_PIPE, llm
from visualization import create_bar_chart, create_emotion_bar_chart, get_emoji, get_emotion_emoji

def classify_text(text, pipeline):
    result = pipeline(text)[0]
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

def analyze_sentiment_emotion(text):
    sentiment_result = classify_text(text, SENTIMENT_PIPE)
    emotion_result = classify_text(text, EMOTION_PIPE)
    
    sentiment_sorted = sorted(sentiment_result, key=lambda x: x['score'], reverse=True)
    top_sentiment = sentiment_sorted[0]['label']
    top_sentiment_score = sentiment_sorted[0]['score']
    
    emotion_sorted = sorted(emotion_result, key=lambda x: x['score'], reverse=True)[:6]
    top_emotion = emotion_sorted[0]['label']
    top_emotion_score = emotion_sorted[0]['score']
    
    sentiment_chart = create_bar_chart(sentiment_sorted)
    emotion_chart = create_emotion_bar_chart(emotion_sorted)
    
    fun_fact = get_fun_fact(top_sentiment)
    
    advice = generate_advice(top_sentiment, emotion_sorted, text)
    
    # Prepare Twitter share URL
    tweet_text = f"I just analyzed my text and got a {top_sentiment} sentiment with a confidence score of {top_sentiment_score:.2f} and a top emotion of {top_emotion} with a score of {top_emotion_score:.2f}! Check out this cool Sentiment and Emotion Analyzer! #SentimentAnalysis #EmotionAnalysis #NLP"
    tweet_text_encoded = urllib.parse.quote(tweet_text)
    tweet_url = f"https://twitter.com/intent/tweet?text={tweet_text_encoded}"
    
    # Prepare detailed results
    detailed_sentiment_results = "\n".join([f"{item['label'].capitalize()}: {item['score']:.2f}" for item in sentiment_sorted])
    detailed_emotion_results = "\n".join([f"{item['label'].capitalize()}: {item['score']:.2f}" for item in emotion_sorted])
    
    return (
        f"{top_sentiment.capitalize()} {get_emoji(top_sentiment)}",
        detailed_sentiment_results,
        f"{top_emotion.capitalize()} {get_emotion_emoji(top_emotion)}",
        detailed_emotion_results,
        sentiment_chart,
        emotion_chart,
        fun_fact,
        tweet_url,
        advice
    )

def open_tweet_url(tweet_url):
    webbrowser.open(tweet_url)
    return tweet_url
