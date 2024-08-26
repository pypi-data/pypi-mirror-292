import streamlit as st

def apply_layout(primary_color):
    st.markdown(f"""
    <style>
    .big-font {{
        font-size: 50px !important;
        font-weight: bold;
        color: {primary_color};
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }}
    .subheader {{
        font-size: 25px;
        font-style: italic;
        color: {primary_color};
        text-align: center;
        margin-bottom: 30px;
    }}
    .stButton > button {{
        background-color: {primary_color};
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 18px;
        border: none;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .stButton > button:hover {{
        background-color: {primary_color};
        opacity: 0.8;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }}
    .info-box {{
        border-radius: 12px;
        color: #333333;
        background: linear-gradient(145deg, #f5f5f5, #e0e0e0);
        padding: 20px;
        box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.1);
        font-size: 16px;
        margin-top: 20px;
    }}
    .tweet-button {{
        margin-top: 15px;
        background-color: #2413B4;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 18px;
        cursor: pointer;
        text-decoration: none;
        transition: background-color 0.3s;
        justify-content: center;
        align-items: center;
        text-align: center;
        margin: 0 auto; /* Center horizontally */
    }}
    .tweet-button:hover {{
        background-color: #1991DA;
    }}
    </style>
    """, unsafe_allow_html=True)
