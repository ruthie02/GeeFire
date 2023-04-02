var origin = "http:///127.0.0.1"
var port = "5000"

//vector layer
var source = new ol.source.Vector({wrapX: false});
var vector = new ol.layer.Vector({
    title: "Geometry",
    source: source,
  });


// raster layer
var raster = new ol.layer.Tile({
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

var map = CreateMap(layers=[raster, vector]);


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
        if (layer.values_.title == "Before Fire True Color Image" | layer.values_.title == "After Fire True Color Image" | layer.values_.title == "Before Fire Cloud Masked Image" | layer.values_.title == "After Fire Cloud Masked Image" | layer.values_.title == "dNBR Gray Image" | layer.values_.title == "Area Classification"){
            map.removeLayer(layer)
        }
      });
      
      // delete the drawn polygon from the map
      var features = source.getFeatures();
      var lastFeature = features[features.length - 1];    
      source.removeFeature(lastFeature);

});

document.getElementById('download').addEventListener('click', function () {
  document.getElementById('download').value = '...'

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
  

  const request = new Request(
    origin.concat(":").concat(port).concat('/download'),
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
      document.location.href = origin.concat(":").concat(port).concat("/").concat(response);
      document.getElementById('download').value = 'download'
    }).catch(error => {
      console.error(error);
    });      
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
    

    const request = new Request(
      origin.concat(":").concat(port).concat('/visualize'),
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
      })  // for the visualization
      .then(response => {
        // Before Fire True Color
        bfire_tc = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["before_fire_tc"]            
          }),
          title: "Before Fire True Color Image"
        });
        // After Fire True Color
        afire_tc = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["after_fire"]            
          }),
          title: "After Fire True Color Image",
        });

        // Before Fire Cloud Masked
        bfire_mos = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["before_fire_mos"]            
          }), 
          title: "Before Fire Cloud Masked Image"
        });
        // After Fire Cloud Masked
        afire_mos = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["after_fire_mos"]            
          }),
          title: "After Fire Cloud Masked Image",
        });

        // dNBR gray
        dNBR_gray = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["dNBR_gray"]            
          }),
          title: "dNBR Gray Image",
        });
        // Fire Area
        final = new ol.layer.Tile({
          source: new ol.source.XYZ({            
            url: response["fire_area"]            
          }),
          title: "Area Classification"
        });
      
        map.addLayer(final);
        map.addLayer(dNBR_gray);
        map.addLayer(afire_tc);
        map.addLayer(bfire_tc);
        map.addLayer(bfire_mos);
        map.addLayer(afire_mos);

        // add the Legend

        var names = ['NA', 'Enhanced Regrowth, High', 'Enhanced Regrowth, Low', 'Unburned', 'Low Severity', 'Moderate-low Severity', 'Moderate-high Severity', 'High Severity']        
        var colors = ['#ffffff', '#7a8737', '#acbe4d', '#0ae042', '#fff70b', '#ffaf38', '#ff641b', '#a41fd6'];

        // Define the legend HTML and CSS styles
        var legendHtml = '<div class="legend"><ul>';
        for (var i = 0; i < names.length; i++) {
          legendHtml += '<li><span class="square" style="background-color:' + colors[i] + '"></span><span class="name">' + names[i] + '</span></li>';
        }
        legendHtml += '</ul></div>';
        var legendStyle = '.legend { background-color: rgba(255, 255, 255, 0.7); border-radius: 5px; bottom: 10px; right: 10px; padding: 10px; position: absolute; z-index: 100; }' +
                          '.legend ul { list-style-type: none; margin: 0; padding: 0; }' +
                          '.legend li { display: flex; align-items: center; line-height: 30px; }' +
                          '.legend .square { display: inline-block; width: 20px; height: 20px; margin-right: 5px; border: 1px solid #000; }' +
                          '.legend .name { vertical-align: middle; margin: 0; }';

        // Create the legend control
        var legendControl = new ol.control.Control({
          element: document.createElement('div'),
        });
        legendControl.element.className = 'ol-legend ol-unselectable';
        legendControl.element.innerHTML = legendHtml;
        var style = document.createElement('style');
        style.innerHTML = legendStyle;
        document.getElementsByTagName('head')[0].appendChild(style);

        // Add the legend control to the map
        map.addControl(legendControl);

        // Show/hide the legend based on the visibility of the "MyLayer" layer
        var myLayer = map.getLayers().getArray().find(layer => layer.get('title') === 'Area Classification');
        myLayer.on('change:visible', function() {
          if (myLayer.getVisible()) {
            legendControl.element.style.display = 'block';
          } else {
            legendControl.element.style.display = 'none';
          }
        });

        var layerSwitcher = new ol.control.LayerSwitcher();
        map.addControl(layerSwitcher);
        document.getElementById('calcviz').value = 'Calculate and Visualize'

      }).catch(error => {
        console.error(error);
      });
});

addInteraction();



