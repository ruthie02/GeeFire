var origin = "http:///127.0.0.1"
var port = "5000"

//vector layer
var source = new ol.source.Vector({wrapX: false});
var vector = new ol.layer.Vector({
    title: "geometry",
    source: source,
  });


// raster layer
var osm = new ol.layer.Tile({
        title: "OSM Base Map", 
        source: new ol.source.OSM()
    });

// var topomap = new ol.layer.Tile({
//     title: "Esri World Imagery", 
//     source: new ol.source.XYZ({
//       attributions: ['Powered by Esri',
//              'Source: Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community'],
//       attributionsCollapsible: false,
//       url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
//       maxZoom: 29
//   })
// });

// Create Map
var CreateMap = (layers) => {
    var map = new ol.Map({
        target: 'map',
        layers: layers,
        view: new ol.View({
            center: ol.proj.transform([0,20], 'EPSG:4326', 'EPSG:3857'),
            zoom: 2
        })    
    });
    return map        
}

var map = CreateMap(layers=[osm, vector]);


// Add sidebar
var sidebar = new ol.control.Sidebar({ element: 'sidebar', position: 'left' });
map.addControl(sidebar);

// draw POI 
var draw; // global so we can remove it later
var addInteraction = () => {        
    draw = new ol.interaction.Draw({
        source: source,
        type: "Circle",
        geometryFunction: ol.interaction.Draw.createBox()
    });
    // Add vector draw layer to the main map
    map.addInteraction(draw);
};

// Event handling to remove all the layers on the map without refreshing the page
document.getElementById('reset').addEventListener('click', function () {
    map.getLayers().getArray().forEach(layer => {
        if (layer.values_.title == "Fire Area" | layer.values_.title == "After Fire" | layer.values_.title == "Before Fire"){
            map.removeLayer(layer)
        }
      });
      
      // delete the drawn polygon from the map
      var features = source.getFeatures();
      var lastFeature = features[features.length - 1];    
      source.removeFeature(lastFeature);

});

document.getElementById('calcviz').addEventListener('click', function () {
    document.getElementById('calcviz').value = '...'

        // Access element for pre-fire range dates
        var pre_start = document.getElementById('pre_start').value;
        var pre_last = document.getElementById('pre_last').value;
    
        // Access element for post range dates
        var fire_start = document.getElementById('fire_start').value;
        var fire_last = document.getElementById('fire_last').value;
    
        // Access what satellite collection to use
        var satellite = document.getElementById('SatImage').value;
    
        // Obtain AOI
        var features = source.getFeatures();
        var lastFeature = features[features.length - 1].clone();
        var bbox = lastFeature.getGeometry().transform('EPSG:3857', 'EPSG:4326').getExtent().toString();
    
        console.log(pre_start, pre_last, fire_start, fire_last, satellite, bbox);

    const request = new Request(
      'http://127.0.0.1:5000/visualize',
        {
            method: 'POST',
            body: JSON.stringify(
                {
                    bbox: bbox,
                    pre_start: pre_start,
                    pre_last: pre_last,
                    fire_start: fire_start,
                    fire_last: fire_last,
                    satellite: satellite
                }
            )
        }
    );

    fetch(request)
    .then(response => {
        if (response.status === 200) {
          return response.json();
        } else {
          throw new Error('Something went wrong on api server!');
        }
      })
      .then(response => {
        // Before Fire
        bfire = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["before_fire"]            
          }),
          title: "Before Fire"
        });
        // After Fire
        afire = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["after_fire"]            
          }),
          title: "After Fire",
        });

        // Fire Area
        final = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["fire_area"]            
          }),
          title: "Fire Area"
        });
        
        map.addLayer(final);
        map.addLayer(afire);
        map.addLayer(bfire);
        
        var layerSwitcher = new ol.control.LayerSwitcher();
        map.addControl(layerSwitcher);
        document.getElementById('calcviz').value = 'Calculate and Visualize'

      }).catch(error => {
        console.error(error);
      });
});

addInteraction();
