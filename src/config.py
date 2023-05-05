import os
import ee

# Read the environment variables from the .env file
GEE_SERVICE_ACCOUNT = os.environ.get('GEE_SERVICE_ACCOUNT')
GEE_JSON_KEY = os.environ.get("GEE_JSON_KEY")


credentials = ee.ServiceAccountCredentials(GEE_SERVICE_ACCOUNT, key_data=GEE_JSON_KEY)

# Authenticate to the Earth Engine API using the service account and JSON key file
ee.Initialize(credentials)


