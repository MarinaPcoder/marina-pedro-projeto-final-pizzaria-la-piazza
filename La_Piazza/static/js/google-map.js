function initPiazzaMap() {
    const mapElement =
        document.getElementById("map");

    if (
        !mapElement
        || !window.google
        || !window.google.maps
    ) {
        return;
    }

    const piazzaLocation = {
        lat: -12.9777,
        lng: -38.5016,
    };

    const map = new google.maps.Map(
        mapElement,
        {
            zoom: 14,
            center: piazzaLocation,
            scrollwheel: false,
            mapTypeControl: false,
            streetViewControl: false,
        }
    );

    new google.maps.Marker({
        position: piazzaLocation,
        map,
        title: "La Piazza",
    });
}

window.initPiazzaMap = initPiazzaMap;
