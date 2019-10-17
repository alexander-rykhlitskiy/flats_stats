FROM continuumio/anaconda3:2019.10

RUN pip install streamlit

WORKDIR /app

CMD streamlit run main.py
