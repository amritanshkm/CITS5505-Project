var map = L.map('map').setView([-31.9505, 115.8605], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var events = [
    {
        title: 'Tech Networking Night',
        coords: [-31.9523, 115.8613],
        location: 'Perth CBD'
    },
    {
        title: 'Beginner Yoga in the Park',
        coords: [-31.9617, 115.8327],
        location: 'Kings Park'
    },
    {
        title: 'Startup Pitch Evening',
        coords: [-31.9478, 115.8233],
        location: 'Subiaco'
    },
    {
        title: 'Sunset Beach Meetup',
        coords: [-31.9937, 115.7528],
        location: 'Cottesloe Beach'
    }
];

events.forEach(function(event) {
    L.marker(event.coords)
        .addTo(map)
        .bindPopup('<strong>' + event.title + '</strong><br>' + event.location);
});