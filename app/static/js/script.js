var map = L.map('map').setView([-31.9505, 115.8605], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var markers = [];
var markerLookup = {};
var searchInput = document.getElementById('search-input');
var categoryFilter = document.getElementById('category-filter');
var priceFilter = document.getElementById('price-filter');
var eventCards = Array.from(document.querySelectorAll('.event-card'));
var resultsCount = document.getElementById('results-count');

function clearMarkers() {
    markers.forEach(function(marker) {
        map.removeLayer(marker);
    });
    markers = [];
    markerLookup = {};
}

function getCardData(card) {
    return {
        title: card.dataset.title || '',
        category: card.dataset.category || '',
        price: card.dataset.price || '',
        location: card.dataset.location || '',
        coords: [
            parseFloat(card.dataset.lat),
            parseFloat(card.dataset.lng)
        ]
    };
}

function updateMap(visibleEvents) {
    clearMarkers();

    visibleEvents.forEach(function(event) {
        var marker = L.marker(event.coords)
            .addTo(map)
            .bindPopup('<strong>' + event.title + '</strong><br>' + event.location);

        markers.push(marker);
        markerLookup[event.title] = marker;
    });

    if (visibleEvents.length > 0) {
        var group = L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.2));
    } else {
        map.setView([-31.9505, 115.8605], 11);
    }
}

function applyFilters() {
    var searchTerm = searchInput ? searchInput.value.trim().toLowerCase() : '';
    var selectedCategory = categoryFilter ? categoryFilter.value : 'all';
    var selectedPrice = priceFilter ? priceFilter.value : 'all';
    var visibleEvents = [];

    eventCards.forEach(function(card) {
        var event = getCardData(card);

        var matchesSearch =
            event.title.toLowerCase().includes(searchTerm) ||
            event.location.toLowerCase().includes(searchTerm) ||
            event.category.toLowerCase().includes(searchTerm);

        var matchesCategory = selectedCategory === 'all' || event.category === selectedCategory;
        var matchesPrice = selectedPrice === 'all' || event.price === selectedPrice;

        if (matchesSearch && matchesCategory && matchesPrice) {
            card.style.display = '';
            visibleEvents.push(event);
        } else {
            card.style.display = 'none';
            card.classList.remove('active-card');
        }
    });

    if (resultsCount) {
        resultsCount.textContent =
            'Showing ' + visibleEvents.length + ' event' + (visibleEvents.length === 1 ? '' : 's');
    }

    updateMap(visibleEvents);
}

function focusEventOnMap(card) {
    if (card.style.display === 'none') {
        return;
    }

    eventCards.forEach(function(otherCard) {
        otherCard.classList.remove('active-card');
    });

    card.classList.add('active-card');

    var event = getCardData(card);
    var marker = markerLookup[event.title];

    if (marker) {
        map.setView(event.coords, 14, {
            animate: true
        });
        marker.openPopup();
    }
}

if (searchInput) {
    searchInput.addEventListener('input', applyFilters);
}

if (categoryFilter) {
    categoryFilter.addEventListener('change', applyFilters);
}

if (priceFilter) {
    priceFilter.addEventListener('change', applyFilters);
}

eventCards.forEach(function(card) {
    card.addEventListener('click', function() {
        focusEventOnMap(card);
    });
});

applyFilters();

document.addEventListener('DOMContentLoaded', () => {

    const locationFilter =
        document.getElementById('locationFilter');

    if (locationFilter) {

        locationFilter.addEventListener('change', () => {

            const selectedLocation =
                locationFilter.value.toLowerCase();

            const cards =
                document.querySelectorAll('.event-card');

            cards.forEach(card => {

                const location =
                    card.dataset.location.toLowerCase();

                if (
                    selectedLocation === '' ||
                    location.includes(selectedLocation)
                ) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }

            });

        });

    }

});