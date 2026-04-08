var map = L.map('map').setView([-31.9505, 115.8605], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var markers = [];
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
        }
    });

    if (resultsCount) {
        resultsCount.textContent =
            'Showing ' + visibleEvents.length + ' event' + (visibleEvents.length === 1 ? '' : 's');
    }

    updateMap(visibleEvents);
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

applyFilters();
var map = L.map('map').setView([-31.9505, 115.8605], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var markers = [];
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
}

function updateMap(visibleEvents) {
    clearMarkers();

    visibleEvents.forEach(function(event) {
        var marker = L.marker(event.coords)
            .addTo(map)
            .bindPopup('<strong>' + event.title + '</strong><br>' + event.location);
        markers.push(marker);
    });

    if (visibleEvents.length > 0) {
        var group = L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.2));
    } else {
        map.setView([-31.9505, 115.8605], 11);
    }
}

function getCardData(card, index) {
    var titleElement = card.querySelector('h3');
    var categoryElement = card.querySelector('.event-category');
    var metaElement = card.querySelector('.event-meta');
    var priceElement = card.querySelector('.event-price');

    var title = card.dataset.title || (titleElement ? titleElement.textContent.trim() : '');
    var category = card.dataset.category || (categoryElement ? categoryElement.textContent.trim() : '');
    var location = card.dataset.location || '';

    if (!location && metaElement) {
        var metaParts = metaElement.textContent.split('·');
        location = metaParts[metaParts.length - 1].trim();
    }

    var price = card.dataset.price || '';
    if (!price && priceElement) {
        if (priceElement.classList.contains('free')) {
            price = 'free';
        } else {
            price = 'paid';
        }
    }

    return {
        title: title,
        category: category,
        location: location,
        price: price,
        event: events[index]
    };
}

function applyFilters() {
    var searchTerm = searchInput ? searchInput.value.trim().toLowerCase() : '';
    var selectedCategory = categoryFilter ? categoryFilter.value : 'all';
    var selectedPrice = priceFilter ? priceFilter.value : 'all';
    var visibleEvents = [];

    eventCards.forEach(function(card, index) {
        var cardData = getCardData(card, index);
        var title = cardData.title.toLowerCase();
        var category = cardData.category;
        var price = cardData.price;
        var location = cardData.location.toLowerCase();

        var matchesSearch =
            title.includes(searchTerm) ||
            location.includes(searchTerm) ||
            category.toLowerCase().includes(searchTerm);
        var matchesCategory = selectedCategory === 'all' || category === selectedCategory;
        var matchesPrice = selectedPrice === 'all' || price === selectedPrice;

        if (matchesSearch && matchesCategory && matchesPrice) {
            card.style.display = '';
            if (cardData.event) {
                visibleEvents.push(cardData.event);
            }
        } else {
            card.style.display = 'none';
        }
    });

    if (resultsCount) {
        resultsCount.textContent = 'Showing ' + visibleEvents.length + ' event' + (visibleEvents.length === 1 ? '' : 's');
    }

    updateMap(visibleEvents);
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

applyFilters();