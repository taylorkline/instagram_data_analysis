/*
 * Playing around with leaflet
 * by creating a heatmap.
 */

/* sets up the map at the lat/long location */
var map = L.map('map').setView([38, -99], 4);

/* sets up attribution properties on the map */
var mapID = "taylorkline.iheaicei";
L.tileLayer('https://{s}.tiles.mapbox.com/v3/' + mapID + '/{z}/{x}/{y}.png', {
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
      '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      'Imagery © <a href="http://mapbox.com">Mapbox</a>',
      maxZoom: 18
      }).addTo(map);

var heatmapLayer = new L.DivHeatmapLayer(
      {
         radius: 20
      });

/* Load heatmap data from a .js file */
heatmapLayer.setData(heatmapData); //heatmap data defined by external js file

heatmapLayer.addTo(map);

/* Create a legend */
var legend = L.control({position: 'topright'});

legend.onAdd = function (map) {
   var div = L.DomUtil.create('div','info legend');
   div.innerHTML += "<b>Followers of " + user + "</b>"; //user defined by external js file
   return div;
   //TODO: Figure out what CSS will do for me.
};

legend.addTo(map);
