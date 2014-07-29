/*
 * GeoIP plugin from https://github.com/jakubdostal/leaflet-geoip
 * <script src="leaflet-geoip.js"></script>
 * var pos = L.GeoIP.getPosition();
 * L.GeoIP.centerMapOnPosition(map);
 *
 */
L.GeoIP = L.extend({

    getPosition: function (ip) {
        var url = "http://freegeoip.net/json/";
        var result = L.latLng(0, 0);

        if (ip !== undefined) {
            url = url + ip;
        } else {
            //lookup our own ip address
        }

        var xhr = new XMLHttpRequest();
        xhr.open("GET", url, false);
        xhr.onload = function () {
            var status = xhr.status;
            if (status == 200) {
                var geoip_response = JSON.parse(xhr.responseText);
                result.lat = geoip_response.latitude;
                result.lng = geoip_response.longitude;
                console.log("Leaflet.GeoIP.getPosition found lat/long: " + result.lat + " " + result.lng);
            } else {
                console.log("Leaflet.GeoIP.getPosition failed because its XMLHttpRequest got this response: " + xhr.status);
            }
        };
        xhr.send();
        return result;
    },

    centerMapOnPosition: function (map, ip) {
        var position = L.GeoIP.getPosition(ip);
        map.setView(position);

    }
});
