//----Definitions

var stroke=new ol.style.Stroke({
      color: 'rgb(10,10,10)',
      width: 3
});
var fill=new ol.style.Fill({
      color: 'rgba(255,255,255,1)'
});

//Highlighting when Mouseover
var highlightStyle = new ol.style.Style({
    image: new ol.style.Circle({
       fill: fill,
       stroke: stroke,
       radius: 7
     }),
    fill: fill,
    stroke: stroke
});

//Content when clicked
const content = document.getElementById('popup-content');
const popup = new ol.Overlay({
  element: document.getElementById('popup')
});


//----The Map
const map=new ol.Map({
        target: 'map',
        layers: [
          new ol.layer.Image({
            source: new ol.source.ImageWMS({
			url: 'https://maps.dwd.de/geoproxy/service',
			params: {'LAYERS': 'Natural_Earth_Map', 'TRANSPARENT': 'false'}
			})
          })
        ],
        view: new ol.View({
          center: ol.proj.fromLonLat([-10.00, 50.11]), zoom: 1,
        }),
});


map.addOverlay(popup);
//----Load Monitoring data
const client = new XMLHttpRequest();
client.open('GET', 'data.csv');
client.onload = function() {
  const csv = client.responseText;
  const features = [];

  let prevIndex = 0;
  let curIndex;

  while ((curIndex = csv.indexOf('\n', prevIndex)) != -1) {
    const line = csv.substr(prevIndex, curIndex - prevIndex).split(';');
    prevIndex = curIndex + 1;

    const coords = ol.proj.fromLonLat([parseFloat(line[9]), parseFloat(line[8])]);
    if (isNaN(coords[0]) || isNaN(coords[1])) {
             continue;
     } 
     
     var f=new ol.Feature({
       geometry: new ol.geom.Point(coords)
     });
     
     f.set('code',line[0]);
     f.set('rdate',line[2]);
     f.set('rtime',line[3]);
     f.set('odate',line[4]);
     f.set('otime',line[5]);
     if (line[6]) {
       f.set('station',line[6]);
     } else {
       f.set('station',line[7]);
     }
     f.set('lat',line[8]);
     f.set('lon',line[9]);
     features.push(f);
  }
  var vectorSource = new ol.source.Vector();
  vectorSource.addFeatures(features);
  var markerVectorLayer = new ol.layer.Vector({
    source: vectorSource,
  });
  map.addLayer(markerVectorLayer);
};

client.send();

//----Mousemove
var selected = null;
map.on('pointermove', function (e) {
  if (selected !== null) {
    selected.setStyle(undefined);
    selected = null;
    popup.setPosition(undefined);
    content.innerHTML="";
  }
  
  map.forEachFeatureAtPixel(e.pixel, function (f) {
    selected = f;
    f.setStyle(highlightStyle);
    return true;
  });
});

//----Click on data
map.on('singleclick', function (e) {
  popup.setPosition(e.coordinate);
  content.innerHTML="Code Form: "+selected.get('code')+"<br>Received: "+selected.get('rdate')+" "+selected.get('rtime')+"<br>Observed: "+selected.get("odate")+" "+selected.get("otime")+"<br>Station: "+selected.get('station');
  return true;
});
