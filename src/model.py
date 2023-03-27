import ee

ee.Initialize()

sld_intervals = """
                    <RasterSymbolizer> 
                        <ColorMap type="intervals" extended="false" >
                            <ColorMapEntry color="#ffffff" quantity="-500" label="-500"/>
                            <ColorMapEntry color="#7a8737" quantity="-250" label="-250" />
                            <ColorMapEntry color="#acbe4d" quantity="-100" label="-100" />
                            <ColorMapEntry color="#0ae042" quantity="100" label="100" />
                            <ColorMapEntry color="#fff70b" quantity="270" label="270" />
                            <ColorMapEntry color="#ffaf38" quantity="440" label="440" />
                            <ColorMapEntry color="#ff641b" quantity="660" label="660" />
                            <ColorMapEntry color="#a41fd6" quantity="2000" label="2000" />
                        </ColorMap>         
                    </RasterSymbolizer>
                """
grey = ['white', 'black']

# initialize Earth Engine Visualization Parameters to display on the map
geoviz = {
    'sentinel_tc': {'bands': ['B4', 'B3', 'B2'], 'max': 2000, 'gamma': 1.5}, 
    'landsat_tc': {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 4000, 'gamma': 1.5}, 
    'grey': grey, 
    'sld_intervals': sld_intervals

}

def display_map(pre_processing_params):
    if pre_processing_params['satellite'] == "Sentinel-2": 
        before_fire = ee.Image.visualize(pre_processing_params["cloudmasked_prefire_mosaic"], **geoviz["sentinel_tc"])
        before_fire_id = ee.data.getMapId({"image": before_fire})["tile_fetcher"].url_format

        after_fire = ee.Image.visualize(pre_processing_params["cloudmasked_postfire_mosaic"], **geoviz["sentinel_tc"])
        after_fire_id = ee.data.getMapId({"image": after_fire})["tile_fetcher"].url_format
    else: 
        before_fire = ee.Image.visualize(pre_processing_params["cloudmasked_prefire_mosaic"], **geoviz["landsat_tc"])
        before_fire_id = ee.data.getMapId({"image": before_fire})["tile_fetcher"].url_format

        after_fire = ee.Image.visualize(pre_processing_params["cloudmasked_postfire_mosaic"], **geoviz["landsat_tc"])
        after_fire_id = ee.data.getMapId({"image": after_fire})["tile_fetcher"].url_format

    display_layer = {"before_fire": before_fire_id, "after_fire": after_fire_id}

    return display_layer

# cloud masking for Sentinel-2 image collection

def maskS2sr(image):
    # Bits 10 and 11 are clouds and cirrus, respectively
    cloudBitMask = ee.Number(2).pow(10).int()
    cirrusBitMask = ee.Number(2).pow(11).int()

    # Get the pixel QA band.
    qa = image.select('QA60')

    # All flags should be set to zero, indicating clear conditions
    mask = qa.bitwiseAnd(cloudBitMask).eq(0) and qa.bitwiseAnd(cirrusBitMask).eq(0)

    # Return the masked image, scaled to TOA reflectance, without the QA bands.
    return image.updateMask(mask).select("B[0-9]*").copyProperties(image, ["system:time_start"])

# cloud masking for Landsat-8 image collection

def maskL8sr(image):
   # Bits 3 and 5 are cloud shadow and cloud, respectively.
  cloudShadowBitMask = 1 << 3
  cloudsBitMask = 1 << 5
  snowBitMask = 1 << 4

  # Get the pixel QA band.
  qa = image.select('pixel_qa')
  
  # All flags should be set to zero, indicating clear conditions.
  mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0) and (qa.bitwiseAnd(cloudsBitMask).eq(0)) and (qa.bitwiseAnd(snowBitMask).eq(0))
  
  # Return the masked image, scaled to TOA reflectance, without the QA bands.
  return image.updateMask(mask).select("B[0-9]*").copyProperties(image, ["system:time_start"])


def preprocessing(ee_geom, satellite, preFire_period, postFire_period):
    
    # define the location of the geometry
    area_of_interest = ee.FeatureCollection(ee_geom)

    # defining which satellite to use 
    if satellite == "Sentinel-2": 
        imCol = 'COPERNICUS/S2'
        imagery = ee.ImageCollection(imCol)
    else: 
        imCol = 'LANDSAT/LC08/C01/T1_SR'
        imagery = ee.ImageCollection(imCol)

    # filter the EE image collection based on range dates and area of interest
    # pre-fire image collection filtering
    prefireImCol = ee.ImageCollection(imagery.filterDate(preFire_period[0], 
                                                         preFire_period[1]).filterBounds(area_of_interest))
    # post-fire image collection filtering
    postfireImCol = ee.ImageCollection(imagery.filterDate(postFire_period[0], 
                                                          postFire_period[1]).filterBounds(area_of_interest))



    # calling the platform dependent masking algorithm within the preprocessing function 

    if satellite == "Sentinel-2":
        prefire_CM_ImCol = prefireImCol.map(maskS2sr)
        postfire_CM_ImCol = postfireImCol.map(maskS2sr)
        
    else: 
        prefire_CM_ImCol = prefireImCol.map(maskL8sr)
        postfire_CM_ImCol = postfireImCol.map(maskL8sr)


    # Mosaic and clip images to study area
    # This is especially important, if the collections created above contain more than one image
    # (if it is only one, the mosaic() does not affect the imagery).

    # Pre-fire mosaicked True Color Image
    pre_mos = prefireImCol.mosaic().clip(area_of_interest)
    # Post-Fire mosaicked True Color Image
    post_mos = postfireImCol.mosaic().clip(area_of_interest)

    # Pre-fire mosaicked Cloud Masked Image
    pre_cm_mos = prefire_CM_ImCol.mosaic().clip(area_of_interest)
    # Post-fire mosaicked Cloud Masked Image
    post_cm_mos = postfire_CM_ImCol.mosaic().clip(area_of_interest)

    return ({'prefire_mosaic': pre_mos, 'postfire_mosaic': post_mos, 'cloudmasked_prefire_mosaic': pre_cm_mos, 
             'cloudmasked_postfire_mosaic': post_cm_mos, 'area_of_interest': area_of_interest, 'satellite': satellite})

def burnSeverity(pre_processing_params, statistics=True):

    satellite = pre_processing_params["satellite"]
    cloudmasked_prefire_mosaic = pre_processing_params["cloudmasked_prefire_mosaic"]
    cloudmasked_postfire_mosaic = pre_processing_params["cloudmasked_prefire_mosaic"]

    #------------------ Calculate NBR for pre- and post-fire images ---------------------------#
    
    # Apply platform-specific NBR = (NIR-SWIR2) / (NIR+SWIR2)

    if satellite == 'Sentinel-2':
        preNBR = cloudmasked_prefire_mosaic.normalizedDifference(['B8', 'B12'])
        postNBR = cloudmasked_postfire_mosaic.normalizedDifference(['B8', 'B12'])
    else:
        preNBR = cloudmasked_prefire_mosaic.normalizedDifference(['B5', 'B7'])
        postNBR = cloudmasked_postfire_mosaic.normalizedDifference(['B5', 'B7'])



# xMin = -122.09
# yMin = 37.42
# xMax = -122.08
# yMax = 37.43

# ee_geom = ee.Geometry.Rectangle([xMin, yMin, xMax, yMax])

# satellite = "Sentinel-2"
# preFire_period = ("2019-05-01", "2019-05-10")
# postFire_period = ("2020-06-01", "2020-06-10")

# preprocessing_params = preprocessing(ee_geom, satellite, preFire_period, postFire_period)
# print(display_map(preprocessing_params))

xMin = -122.09
yMin = 37.42
xMax = -122.08
yMax = 37.43

ee_geom = ee.Geometry.Rectangle([xMin, yMin, xMax, yMax])

satellite = "Landsat-8"
preFire_period = ("2019-05-01", "2019-05-10")
postFire_period = ("2020-06-01", "2020-06-10")

preprocessing_params = preprocessing(ee_geom, satellite, preFire_period, postFire_period)
print(display_map(preprocessing_params))





    




