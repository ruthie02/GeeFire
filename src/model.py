import ee

ee.Initialize()

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

def maskS2sr(image):
   # Bits 3 and 5 are cloud shadow and cloud, respectively.
  cloudShadowBitMask = 1 << 3
  cloudsBitMask = 1 << 5
  snowBitMask = 1 << 4

  # Get the pixel QA band.
  qa = image.select('pixel_qa');
  
  # All flags should be set to zero, indicating clear conditions.
  mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0) and (qa.bitwiseAnd(cloudsBitMask).eq(0)) and (qa.bitwiseAnd(snowBitMask).eq(0))
  
  # Return the masked image, scaled to TOA reflectance, without the QA bands.
  return image.updateMask(mask).select("B[0-9]*").copyProperties(image, ["system:time_start"])


def processing(ee_geom, satellite, preFire_period, postFire_period):
    
    # define the location of the geometry
    area_of_interest = ee.FeatureCollection(ee_geom)

    # filter the EE image collection based on range dates and area of interest
    # pre-fire image collection filtering
    prefireImCol = ee.ImageCollection(imagery.filterDate(preFire_period[0], preFire_period[1]).filterBounds(area_of_interest))
    # post-fire image collection filtering
    postfireImCol = ee.ImageCollection(imagery.filterDate(postFire_period[0], postFire_period[1]).filterBounds(area_of_interest))

    # defining which satellite to use 
    if satellite == "Sentinel": 
        imCol = 'COPERNICUS/S2'
        imagery = ee.ImageCollection(imCol)
    else: 
        imCol = 'LANDSAT/LC08/C01/T1_SR'
        imagery = ee.ImageCollection(imCol)

    # calling the platform dependent masking algorithm within the preprocessing function 
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

    




