import pandas as pd
from sqlalchemy import create_engine
import psycopg2
from time import sleep
import requests
import zipfile
import io

# Function to wait for a database to become available
def wait_for_db(host, port, user, password, database):
    while True:
        try:
            with psycopg2.connect(host=host, port=port, user=user, password=password, dbname=database) as conn:
                print("Database is ready!")
                break
        except psycopg2.OperationalError:
            print("Waiting for database to become available...")
            sleep(3)


def download_and_extract_zip(url, extract_to='data'):
    """Download a ZIP file and extract its contents."""
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as the_zip:
            the_zip.extractall(extract_to)
        print("ZIP file downloaded and extracted successfully.")
    else:
        print(f"Failed to download the ZIP file. HTTP status code: {response.status_code}")

data_url = 'https://s3.amazonaws.com/hubway-data/201905-bluebikes-tripdata.zip'
download_and_extract_zip(data_url)

# Load data from CSV files
bike_data_csv = 'data/201905-bluebikes-tripdata.csv'
rainfall_data_csv = 'data/201905-rainfall-CharlestownBunkerHill.csv'
bike_data = pd.read_csv(bike_data_csv)
rainfall_data = pd.read_csv(rainfall_data_csv)

# Database configuration
config_initial = {
    "host": "db-initial",
    "port": "5432",
    "user": "username",
    "password": "your_password",
    "database": "mydb"
}


config_transformed = {
    "host": "db-transformed",
    "port": "5432",
    "user": "username",
    "password": "your_password",
    "database": "transformeddb"
}

# Wait for the initial database
wait_for_db(**config_initial)

# Connection strings
conn_str_initial = f"postgresql://{config_initial['user']}:{config_initial['password']}@{config_initial['host']}:{config_initial['port']}/{config_initial['database']}"
conn_str_transformed = f"postgresql://{config_transformed['user']}:{config_transformed['password']}@{config_transformed['host']}:{config_transformed['port']}/{config_transformed['database']}"

# Create engines
engine_initial = create_engine(conn_str_initial)
engine_transformed = create_engine(conn_str_transformed)

# Insert data into the initial database
bike_data.to_sql('blue_bikes', con=engine_initial, if_exists='replace', index=False)
rainfall_data.to_sql('rainfall_data', con=engine_initial, if_exists='replace', index=False)

# Wait for the transformed database
wait_for_db(**config_transformed)

# Transform and insert data into the transformed database
with engine_initial.connect() as conn:
    bike_data = pd.read_sql("SELECT * FROM blue_bikes", conn)
    rainfall_data = pd.read_sql("SELECT * FROM rainfall_data", conn)

bike_data['starttime'] = pd.to_datetime(bike_data['starttime'])
bike_data['stoptime'] = pd.to_datetime(bike_data['stoptime'])

bike_data['minutes'] = (bike_data['stoptime'] - bike_data['starttime']).dt.total_seconds() / 60

bike_data['ride_date'] = bike_data['starttime'].dt.date

bike_ridership_per_day = bike_data.groupby('ride_date')['minutes'].sum().reset_index()

rainfall_data['Date'] = pd.to_datetime(rainfall_data['Date'], format='%m/%d/%y')
rainfall_data['Date'] = rainfall_data['Date'].dt.date

merged_data = pd.merge(bike_ridership_per_day, rainfall_data, how='left', left_on='ride_date', right_on='Date')

merged_data = merged_data.rename(columns={'minutes': 'ridership'}).drop(columns=['ride_date'])
merged_data = merged_data[['Date', 'ridership', 'Inches']]

print(merged_data.head())

merged_data.to_sql('avg_ridership_with_rainfall', con=engine_transformed, if_exists='replace', index=False)

print("Data processing and transformation completed successfully.")
