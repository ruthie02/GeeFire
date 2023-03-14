import ee
from config import service_email_account, earth_engine_key


# service_account = 'geefire-ruth@geefire-380610.iam.gserviceaccount.com'
# earth_engine_key = r'src\gee_key.json'

credentials = ee.ServiceAccountCredentials(service_email_account, earth_engine_key)
ee.Initialize(credentials)

# def image_to_map_id(image_name, vis_params={}):
#     """  """
#     try:
#         ee_image = ee.Image(image_name)
#         map_info = ee_image.getMapId(vis_params)
#         return {
#             'url': map_info['tile_fetcher'].url_format
#         }
#     except Exception as e:
#         return {
#             'errMsg': str(sys.exc_info()[0])
#         }

