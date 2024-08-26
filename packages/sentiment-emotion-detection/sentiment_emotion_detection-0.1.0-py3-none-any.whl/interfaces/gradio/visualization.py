import plotly.graph_objects as go
import random

def get_emoji(sentiment):
    if sentiment == "positive":
        return random.choice(["😊", "😄", "🎉", "👍", "🌟"])
    elif sentiment == "neutral":
        return random.choice(["😐", "😶", "🤔", "😑", "😏"])
    else:
        return random.choice(["😔", "😢", "👎", "🌧️", "💔"])

def get_emotion_emoji(emotion):
    emotion_emoji_map = {
        "disappointment": "😞",
        "sadness": "😢",
        "annoyance": "😒",
        "neutral": "😐",
        "disapproval": "👎",
        "realization": "💡",
        "nervousness": "😬",
        "approval": "👍",
        "joy": "😊",
        "anger": "😠",
        "embarrassment": "😳",
        "caring": "🤗",
        "remorse": "😔",
        "disgust": "🤢",
        "grief": "😭",
        "confusion": "😕",
        "relief": "😌",
        "desire": "😍",
        "admiration": "👏",
        "optimism": "😃",
        "fear": "😨",
        "love": "❤️",
        "excitement": "🤩",
        "curiosity": "🤔",
        "amusement": "😂",
        "surprise": "😲",
        "gratitude": "🙏",
        "pride": "😌",
    }
    return emotion_emoji_map.get(emotion, "🤷")

def create_bar_chart(result):
    labels = [item['label'] for item in result]
    scores = [item['score'] for item in result]
    colors = ['#00CC96' if label == 'positive' else '#EF553B' if label == 'negative' else '#636EFA' for label in labels]
    emojis = [get_emoji(label) for label in labels]

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=scores,
        marker_color=colors,
        text=emojis,  # Add emojis as text
        textposition='outside',  # Position text outside the bars (top)
        hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}<br>%{text}<extra></extra>'  # Display emoji in hover info
    )])
    
    fig.update_layout(
        title='Sentiment Scores',
        xaxis_title='Sentiment',
        yaxis_title='Score',
        yaxis=dict(range=[0, 1]),
        font=dict(family="Arial", size=14, color="#2D3E50")  # Dark Blue Gray for text
    )
    
    return fig

def create_emotion_bar_chart(result):
    # Extract labels and scores from the result
    labels = [item['label'] for item in result]
    scores = [item['score'] for item in result]
    emojis = [get_emotion_emoji(label) for label in labels]
    
    # Define a set of creative and vibrant colors for the emotions
    colors = ['#FF6347', '#FFD700', '#4CAF50', '#00BFFF', '#FF69B4', '#8A2BE2']  # Tomato, Gold, Green, Deep Sky Blue, Hot Pink, Blue Violet

    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=scores,
        marker_color=colors[:len(labels)],  # Assign colors to the bars
        text=emojis,  # Add emojis as text
        textposition='outside',  # Position text outside the bars
        hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}<br>%{text}<extra></extra>'  # Display emoji in hover info
    )])
    
    # Update layout for better visualization
    fig.update_layout(
        title='Top 6 Emotions',
        xaxis_title='Emotion',
        yaxis_title='Score',
        yaxis=dict(range=[0, 1]),
        font=dict(family="Arial", size=14, color="#2D3E50")  # Dark Blue Gray for text
    )
    
    return fig