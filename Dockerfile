FROM continuumio/anaconda3:2019.10

RUN pip install streamlit==0.48.0 plotly==4.1.0

WORKDIR /app

CMD streamlit run app.py
