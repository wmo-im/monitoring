//----Definitions

var datastroke=new ol.style.Stroke({
      color: 'rgb(0,255,0)',
      width: 2
});
var datafill=new ol.style.Fill({
      color: 'rgba(0,255,0,1)'
});
var basestroke=new ol.style.Stroke({
      color: 'rgb(255,0,0)',
      width: 2
});
var basefill=new ol.style.Fill({
      color: 'rgba(255,0,0,1)'
});

//Highlighting when Mouseover
var highlightdataStyle = new ol.style.Style({
    image: new ol.style.Circle({
       fill: datafill,
       stroke: datastroke,
       radius: 7
     }),
    fill: datafill,
    stroke: datastroke
});
var highlightbaseStyle = new ol.style.Style({
    image: new ol.style.Circle({
       fill: basefill,
       stroke: basestroke,
       radius: 7
     }),
    fill: basefill,
    stroke: basestroke
});
var dataStyle = new ol.style.Style({
    image: new ol.style.Circle({
       fill: datafill,
       stroke: datastroke,
       radius: 2
     }),
    fill: datafill,
    stroke: datastroke
});
var baseStyle = new ol.style.Style({
    image: new ol.style.Circle({
       fill: basefill,
       stroke: basestroke,
       radius: 2
     }),
    fill: basefill,
    stroke: basestroke
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
const client1 = new XMLHttpRequest();
const client2 = new XMLHttpRequest();
client1.onload = function() {
  const csv = client1.responseText;
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
       geometry: new ol.geom.Point(coords),
     });
     
     f.setStyle(dataStyle);
     f.set('code',line[0]);
     f.set('rdate',line[2]);
     f.set('rtime',line[3]);
     f.set('odate',line[4]);
     f.set('otime',line[5]);
     f.set('layer',1);
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
  markerVectorLayer.setZIndex(1);
  map.addLayer(markerVectorLayer);
};
client2.onload = function() {
  const csv = client2.responseText;
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
       geometry: new ol.geom.Point(coords),
     });
     
     f.setStyle(baseStyle);
     f.set('code',line[0]);
     f.set('rdate',line[2]);
     f.set('rtime',line[3]);
     f.set('odate',line[4]);
     f.set('otime',line[5]);
     f.set('layer',0);
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
  markerVectorLayer.setZIndex(0);
  map.addLayer(markerVectorLayer);
};

client1.open('GET', 'data.csv');
client1.send();
client2.open('GET', 'baseline.csv');
client2.send();

//----Mousemove
var selected = null;
map.on('pointermove', function (e) {
  if (selected !== null) {
    if (selected.get('layer') == 1) {
      selected.setStyle(dataStyle);
    } else {
      selected.setStyle(baseStyle);
    }
    selected = null;
    popup.setPosition(undefined);
    content.innerHTML="";
  }
  
  map.forEachFeatureAtPixel(e.pixel, function (f) {
    selected = f;
    if (selected.get('layer') == 1) {
      selected.setStyle(highlightdataStyle);
    } else {
      selected.setStyle(highlightbaseStyle);
    }
  popup.setPosition(e.coordinate);
  content.innerHTML="Code Form: "+selected.get('code')+"<br>Received: "+selected.get('rdate')+" "+selected.get('rtime')+"<br>Observed: "+selected.get("odate")+" "+selected.get("otime")+"<br>Station: "+selected.get('station');
    return true;
  });
});

//----Click on data
map.on('singleclick', function (e) {
  popup.setPosition(e.coordinate);
  content.innerHTML="Code Form: "+selected.get('code')+"<br>Received: "+selected.get('rdate')+" "+selected.get('rtime')+"<br>Observed: "+selected.get("odate")+" "+selected.get("otime")+"<br>Station: "+selected.get('station');
  return true;
});
