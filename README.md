# Weather Data Pipeline with Apache Airflow

This project is focused on building a data pipeline that extracts weather data from a public API using **Apache Airflow**.

## 📌 Project Goal

The goal is to design a scalable and automated pipeline that:

- ⛅ Retrieves weather data from a weather API
- 🗂 Stores the data for further analysis or reporting

## ⚙️ Tools & Technologies

- **Apache Airflow** – for orchestrating and scheduling the pipeline
- **Python** – for API calls and custom logic
- **Weather API** – the data source (e.g., OpenWeatherMap, WeatherAPI, etc.)
- (Optional) **PostgreSQL / Google BigQuery / AWS S3** – for data storage 

## 🚀 Project Structure

```bash
weather-pipeline/
├── dags/                 # Airflow DAGs (main pipeline logic)
├── scripts/              # Python scripts for API calls and processing
├── logs/                 # Airflow logs
├── .env                  # Environment variables (API keys, configs)
└── README.md             # Project overview 