//vector layer
var source = new ol.source.Vector({wrapX: false});
var vector = new ol.layer.Vector({
    title: "geometry",
    source: source,
  });

// raster layer
var raster = new ol.layer.Tile({
        title: "OSM Base Map", 
            source: new ol.source.OSM()
    });

// Create Map
var CreateMap = (layers) => {
    var map = new ol.Map({
        target: 'map',
        layers: layers,
        view: new ol.View({
            center: ol.proj.transform([34.09, -17.87], 'EPSG:4326', 'EPSG:3857'),
            zoom: 8
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

addInteraction()


