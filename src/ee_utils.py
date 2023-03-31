import ee
import sys


service_account = 'geefire-ruth@geefire-380610.iam.gserviceaccount.com'
earth_engine_key = r'gee_key.json'

credentials = ee.ServiceAccountCredentials(service_account, earth_engine_key)
ee.Initialize(credentials)
