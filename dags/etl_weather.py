from airflow import DAG
from airflow.providers.https.hooks.http import HttpHook #for requesting data from an API 
from airflow.providers.postgres.hooks.postgres import PostgresHook #for writing data to a PostgreSQL database
from airflow.decorators import task  #for defining tasks in the DAG
from airflow.utils.dates import days_ago  #for setting the start date of the DAG
import requests
import json

#location parameters for `berlin`
latitude = "52.5200"
longitude = "13.4050"
postgres_conn_id = "postgres_default"   #connection ID for PostgreSQL database
api_conn_id = "open_meteo_api"  #connection ID for the weather API


default_args = {
    "owner": "airflow", #owner of the DAG
    "start_date": days_ago(1) #start date for the DAG
    }  #default arguments for the DAG

with DAG(
    dag_id="etl_weather",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False, #do not run past dates
) as dags:

    @task()
    def extract_weather_data():
        #use HttpHook to get connection details from Airflow connections
        http_hook = HttpHook(http_conn_id=api_conn_id,method='GET') 
        # build the api endpoint
        # https://api.open-meteo.com/v1/forecast?latitude=52.5200&longitude=13.4050&current_weather=true
        endpoint = f"/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        # make the API request and return the JSON response
        response = http_hook.run(endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        
    @task()
    def transform_weather_data(weather_data):
        current_weather = weather_data['current_weather']
        transformed_data = {
            'latitude': latitude,
            'longitude': longitude,
            'temperature': current_weather['temperature'],
            'windspeed': current_weather['windspeed'],
            'winddirection': current_weather['winddirection'],
            'weathercode': current_weather['weathercode']
        }
        return transformed_data
    @task()
    def load_weather_data(transformed_data):
        """Load transformed data into PostgreSQL."""
        pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            latitude FLOAT,
            longitude FLOAT,
            temperature FLOAT,
            windspeed FLOAT,
            winddirection FLOAT,
            weathercode INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        # Insert the transformed data
        cursor.execute("""
        INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            transformed_data['latitude'],
            transformed_data['longitude'],
            transformed_data['temperature'],
            transformed_data['windspeed'],
            transformed_data['winddirection'],
            transformed_data['weathercode']
        ))

        conn.commit()
        cursor.close()

    # Define the task dependencies
    weather_data= extract_weather_data()
    transformed_data=transform_weather_data(weather_data)
    load_weather_data(transformed_data)