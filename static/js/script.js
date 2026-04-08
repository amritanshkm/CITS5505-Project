var map = L.map('map').setView([-31.95, 115.86], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Example marker
L.marker([-31.95, 115.86]).addTo(map)
    .bindPopup("Sample Event")
    .openPopup();