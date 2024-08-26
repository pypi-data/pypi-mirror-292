#visualization.py

import plotly.graph_objects as go

def get_emoji(sentiment):
    if sentiment == "positive":
        return "😊"
    elif sentiment == "negative":
        return "😞"
    elif sentiment == "neutral":
        return "😐"
    return "🤔"

def get_emotion_emoji(emotion):
    emojis = {
        "admiration": "👏",
        "amusement": "😄",
        "anger": "😡",
        "annoyance": "😒",
        "approval": "👍",
        "caring": "🤗",
        "confusion": "😕",
        "curiosity": "🤔",
        "desire": "😍",
        "disappointment": "😞",
        "disapproval": "👎",
        "disgust": "🤮",
        "embarrassment": "😳",
        "excitement": "😆",
        "fear": "😨",
        "gratitude": "🙏",
        "grief": "😭",
        "joy": "😂",
        "love": "❤️",
        "nervousness": "😬",
        "optimism": "😊",
        "pride": "😌",
        "realization": "💡",
        "relief": "😌",
        "remorse": "😔",
        "sadness": "😢",
        "surprise": "😲",
        "neutral": "😐"
    }
    return emojis.get(emotion, "🤔")

def create_bar_chart(result):
    labels = [item['label'] for item in result]
    scores = [item['score'] for item in result]
    emojis = [get_emoji(label) for label in labels]
    
    colors = ['#00CC96' if label == 'positive' else '#EF553B' if label == 'negative' else '#636EFA' for label in labels]

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=scores,
        marker_color=colors,
        text=emojis,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}<br>%{text}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Sentiment Scores',
        xaxis_title='Sentiment',
        yaxis_title='Score',
        yaxis=dict(range=[0, 1]),
        font=dict(family="Arial", size=14, color="#636EFA")
    )
    
    return fig

def create_emotion_bar_chart(result):
    labels = [item['label'] for item in result]
    scores = [item['score'] for item in result]
    emojis = [get_emotion_emoji(label) for label in labels]
    
    colors = ['#FF6692', '#636EFA', '#00CC96', '#EF553B', '#AB63FA', '#FFA15A']

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=scores,
        marker_color=colors[:len(labels)],
        text=emojis,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}<br>%{text}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Top 6 Emotions',
        xaxis_title='Emotion',
        yaxis_title='Score',
        yaxis=dict(range=[0, 1]),
        font=dict(family="Arial", size=14, color="#636EFA")
    )
    
    return fig
