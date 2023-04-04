import ee

ee.Initialize()


# initialize Earth Engine Visualization Parameters to display on the map
geoviz = {
    'sentinel_tc': {'bands': ['B4', 'B3', 'B2'], 'max': 2000, 'gamma': 1.5}, 
    'landsat_tc': {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 4000, 'gamma': 1.5}, 
    'gray': {'min': -1000, 'max': 1000, 'palette': ['white', 'black']}, 
    'sld_interval': {
        'sld': """<RasterSymbolizer>
                    <ColorMap type="intervals" extended="false">
                    <ColorMapEntry color="#ffffff" quantity="-500" label="-500"/>
                    <ColorMapEntry color="#7a8737" quantity="-250" label="-250" />
                    <ColorMapEntry color="#acbe4d" quantity="-100" label="-100" />
                    <ColorMapEntry color="#0ae042" quantity="100" label="100" />
                    <ColorMapEntry color="#fff70b" quantity="270" label="270" />
                    <ColorMapEntry color="#ffaf38" quantity="440" label="440" />
                    <ColorMapEntry color="#ff641b" quantity="660" label="660" />
                    <ColorMapEntry color="#a41fd6" quantity="2000" label="2000" />
                    </ColorMap>
                </RasterSymbolizer>"""
            }
}



## -----------------Display Map Function ----------------## 

def display_map(pre_processing_params):
    
    if pre_processing_params['satellite'] == "Sentinel-2": 
        ## ------- Sentinel-2 Viz Params ---------- ##

        # before fire True Color Mosaicked Image
        before_fire_tc = ee.Image.visualize(pre_processing_params["prefire_mosaic"], **geoviz["sentinel_tc"])
        before_fire_tc_id = ee.data.getMapId({"image": before_fire_tc})["tile_fetcher"].url_format

        # after fire True Color Mosaicked Image
        after_fire_tc = ee.Image.visualize(pre_processing_params["postfire_mosaic"], **geoviz["sentinel_tc"])
        after_fire_tc_id = ee.data.getMapId({"image": after_fire_tc})["tile_fetcher"].url_format

        # before fire Cloud Masked Mosaicked Image
        before_fire_mos = ee.Image.visualize(pre_processing_params["cloudmasked_prefire_mosaic"], **geoviz["sentinel_tc"])
        before_fire_mos_id = ee.data.getMapId({"image": before_fire_mos})["tile_fetcher"].url_format

        # after fire Cloud Masked Mosaicked Image
        after_fire_mos = ee.Image.visualize(pre_processing_params["cloudmasked_postfire_mosaic"], **geoviz["sentinel_tc"])
        after_fire_mos_id = ee.data.getMapId({"image": after_fire_mos})["tile_fetcher"].url_format

        # dNBR grey image
        fire_area_grey = ee.Image.visualize(pre_processing_params["dNBR"], **geoviz["gray"])
        fire_area_gray_id = ee.data.getMapId({"image": fire_area_grey})["tile_fetcher"].url_format

        # classified image
        fire_area = ee.Image(pre_processing_params["dNBR"]).sldStyle(geoviz['sld_interval']['sld']).getMapId()['tile_fetcher'].url_format

    else: 
        ## ------- Landsat-8 Viz Params ---------- ##

        # before fire True Color Mosaicked Image
        before_fire_tc = ee.Image.visualize(pre_processing_params["prefire_mosaic"], **geoviz["landsat_tc"])
        before_fire_tc_id = ee.data.getMapId({"image": before_fire_tc})["tile_fetcher"].url_format

        # after fire True Color Mosaicked Image
        after_fire_tc = ee.Image.visualize(pre_processing_params["postfire_mosaic"], **geoviz["landsat_tc"])
        after_fire_tc_id = ee.data.getMapId({"image": after_fire_tc})["tile_fetcher"].url_format

        # before fire Cloud Masked Mosaicked Image
        before_fire_mos = ee.Image.visualize(pre_processing_params["cloudmasked_prefire_mosaic"], **geoviz["landsat_tc"])
        before_fire_mos_id = ee.data.getMapId({"image": before_fire_mos})["tile_fetcher"].url_format

        # after fire Cloud Masked Mosaicked Image
        after_fire_mos = ee.Image.visualize(pre_processing_params["cloudmasked_postfire_mosaic"], **geoviz["landsat_tc"])
        after_fire_mos_id = ee.data.getMapId({"image": after_fire_mos})["tile_fetcher"].url_format

        # dNBR grey image
        fire_area_grey = ee.Image.visualize(pre_processing_params["dNBR"], **geoviz["gray"])
        fire_area_gray_id = ee.data.getMapId({"image": fire_area_grey})["tile_fetcher"].url_format

        # classified image
        fire_area = ee.Image(pre_processing_params["dNBR"]).sldStyle(geoviz['sld_interval']['sld']).getMapId()['tile_fetcher'].url_format


    display_layer = {"before_fire_tc": before_fire_tc_id, "after_fire_tc": after_fire_tc_id, 
                     "before_fire_mos": before_fire_mos_id, "after_fire_mos": after_fire_mos_id,
                     "dNBR_gray": fire_area_gray_id, "fire_area": fire_area}

    return display_layer


## ---------- cloud masking algorithm  for Sentinel-2 image collection ---------- ##
def maskS2sr(image):

    # Bits 10 and 11 are clouds and cirrus, respectively
    cloudBitMask = ee.Number(2).pow(10).int()
    cirrusBitMask = ee.Number(2).pow(11).int()

    # Get the pixel QA band.
    qa = image.select('QA60')

    # All flags should be set to zero, indicating clear conditions
    mask = qa.bitwiseAnd(cloudBitMask).eq(0) and qa.bitwiseAnd(cirrusBitMask).eq(0)

    # Return the masked image, scaled to TOA reflectance, without the QA bands.
    return image.updateMask(mask).copyProperties(image, ["system:time_start"])

## ---------- cloud masking algorithm  for Landsat-8 image collection ---------- ##
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


## Pre-Processing algorithm using the User's preferences ---------- ##
def preprocessing(ee_geom, satellite, preFire_period, postFire_period):
    
    # define the location of the geometry
    area_of_interest = ee.FeatureCollection(ee_geom)

     ## ------- Sentinel-2 Preprocessing alogrithm with the precessing function ---------- ## 
    if satellite == "Sentinel-2": 

        imCol = 'COPERNICUS/S2'
        imagery = ee.ImageCollection(imCol)

        # filter the EE image collection based on range dates and area of interest
        # pre-fire image collection filtering
        prefireImCol = ee.ImageCollection(imagery.filterDate(preFire_period[0], 
                                                            preFire_period[1]).filterBounds(area_of_interest))
        # post-fire image collection filtering
        postfireImCol = ee.ImageCollection(imagery.filterDate(postFire_period[0], 
                                                            postFire_period[1]).filterBounds(area_of_interest))
        
        # applying the Sentinel-2 cloud masking algorithm to the image collection 
        prefire_CM_ImCol = prefireImCol.map(maskS2sr)
        postfire_CM_ImCol = postfireImCol.map(maskS2sr)

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

        # Calculate NBR for pre- and post-fire images
        preNBR = pre_cm_mos.normalizedDifference(['B8', 'B12'])
        postNBR = post_cm_mos.normalizedDifference(['B8', 'B12'])

        # Computation of delta NBR or dNBR
        dNBR_unscaled = preNBR.subtract(postNBR)
        # Scale product to USGS standards
        dNBR = dNBR_unscaled.multiply(1000)

        # Seperate result into 8 burn severity classes --> to be used for Statistics computation
        thresholds = ee.Image([-1000, -251, -101, 99, 269, 439, 659, 2000])
        classified = dNBR.lt(thresholds).reduce('sum').toInt()

    ## ------- Landsat-8 Preprocessing alogrithm with the precessing function ---------- ## 
    else: 
        imCol = 'LANDSAT/LC08/C01/T1_SR'
        imagery = ee.ImageCollection(imCol)

        # filtering the image collection using the range dates and area of interest
        prefireImCol = ee.ImageCollection(imagery.filterDate(preFire_period[0], 
                                                            preFire_period[1]).filterBounds(area_of_interest))
        # post-fire image collection filtering
        postfireImCol = ee.ImageCollection(imagery.filterDate(postFire_period[0], 
                                                            postFire_period[1]).filterBounds(area_of_interest))
        
        # applying the Landsat-8 cloud masking algorithm to the image collection 
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

        # Calculate NBR for pre- and post-fire images
        preNBR = pre_cm_mos.normalizedDifference(['B5', 'B7'])
        postNBR = post_cm_mos.normalizedDifference(['B5', 'B7'])
        
        # Computation of delta NBR or dNBR
        dNBR_unscaled = preNBR.subtract(postNBR)
        # Scale product to USGS standards
        dNBR = dNBR_unscaled.multiply(1000)


        # Seperate result into 8 burn severity classes --> to be used for Statistics computation
        thresholds = ee.Image([-1000, -251, -101, 99, 269, 439, 659, 2000])
        classified = dNBR.lt(thresholds).reduce('sum').toInt()

    return ({'prefire_mosaic': pre_mos, 'postfire_mosaic': post_mos, 'cloudmasked_prefire_mosaic': pre_cm_mos, 
             'cloudmasked_postfire_mosaic': post_cm_mos, 'dNBR': dNBR, 'area_of_interest': area_of_interest, 'satellite': satellite, 'classified': classified})

def burnSeverity(pre_processing_params):
    
    classified = pre_processing_params['classified']
    area_of_interest = pre_processing_params['area_of_interest']
    satellite = pre_processing_params["satellite"]
    arealist = []

    if satellite == "Sentinel-2":
        # count number of pixels in entire layer by masking the entire layer and count pixels in a single class
        allpix =  classified.updateMask(classified)
        pixstats = allpix.reduceRegion(reducer=ee.Reducer.count(), geometry=area_of_interest,scale=10)

        # extract pixel count as a number
        allpixels = ee.Number(pixstats.get('sum')).getInfo()

        # define function for calculating area statistics for a single class
        def areacount(cnr, name):
            # mask a single class
            singleMask = classified.updateMask(classified.eq(cnr))
            # count pixels in a single class
            stats = singleMask.reduceRegion(reducer=ee.Reducer.count(), geometry=area_of_interest, scale=10)
            # calculate number of pixels, hectares, and percentage of total area
            pix = ee.Number(stats.get('sum'))
            hect = pix.multiply(100).divide(10000).getInfo() # Sentinel pixel = 10m x 10m --> 100 sqm
            perc = pix.divide(allpixels).multiply(10000).round().divide(100).getInfo() # get area percent by class and round to 2 decimals
            # add results to list of area statistics for all classes
            return{'Class': name, 'Pixels': pix.getInfo(), 'Hectares': hect, 'Percentage': perc}


    else:
        # count number of pixels in entire layer by masking the entire layer and count pixels in a single class
        allpix =  classified.updateMask(classified)
        pixstats = allpix.reduceRegion(reducer=ee.Reducer.count(), geometry=area_of_interest,scale=30)

        # extract pixel count as a number
        allpixels = ee.Number(pixstats.get('sum')).getInfo()

        # define function for calculating area statistics for a single class
        def areacount(cnr, name):
            # mask a single class
            singleMask = classified.updateMask(classified.eq(cnr))
            # count pixels in a single class
            stats = singleMask.reduceRegion(reducer=ee.Reducer.count(), geometry=area_of_interest, scale=30)
            # calculate number of pixels, hectares, and percentage of total area
            pix = ee.Number(stats.get('sum'))
            hect = pix.multiply(900).divide(10000).getInfo() # Landsat-8 pixel = 30m x 30m --> 900 sqm
            perc = pix.divide(allpixels).multiply(10000).round().divide(100).getInfo() # get area percent by class and round to 2 decimals
            return{'Class': name, 'Pixels': pix.getInfo(), 'Hectares': hect, 'Percentage': perc}
        
    
    # severity classes in different order
    names2 = ['NA', 'High Severity', 'Moderate-high Severity',
            'Moderate-low Severity', 'Low Severity','Unburned', 'Enhanced Regrowth, Low', 'Enhanced Regrowth, High']

    # execute function for each class and append result to the list
    for i in range(8):
        arealist.append(areacount(i, names2[i]))

    return arealist
            

# xMin = -122.09
# yMin = 37.42
# xMax = -122.08
# yMax = 37.43

# ee_geom = ee.Geometry.Rectangle([xMin, yMin, xMax, yMax])

# satellite = "Sentinel-2"
# preFire_period = ("2019-05-01", "2019-05-10")
# postFire_period = ("2020-06-01", "2020-06-10")

# # preprocessing_params = preprocessing(ee_geom, satellite, preFire_period, postFire_period)
# # print(display_map(preprocessing_params))

xMin = -122.09
yMin = 37.42
xMax = -122.08
yMax = 37.43

ee_geom = ee.Geometry.Rectangle([xMin, yMin, xMax, yMax])

satellite = "Landsat-8"
preFire_period = ("2019-05-01", "2019-05-10")
postFire_period = ("2020-06-01", "2020-06-10")

preprocessing_params = preprocessing(ee_geom, satellite, preFire_period, postFire_period)
# # print(display_map(preprocessing_params))
print(burnSeverity(preprocessing_params))
# # # # print(preprocessing_params)







    