FROM apache/airflow:2.2.4-python3.8

ENV PYTHONBUFFERED=0 
ENV AIRFLOW_UID=501

COPY requirements.txt ./requirements.txt
COPY requirements-test.txt ./requirements-test.txt
COPY dags ./dags

USER airflow
RUN pip install --no-cache-dir --user -r requirements.txt -r requirements-test.txt
