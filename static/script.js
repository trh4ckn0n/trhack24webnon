
const socket = io();
let map = L.map('map').setView([48.8566, 2.3522], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18
}).addTo(map);

let marker, trailLine;

function trackFlight() {
    const flight_id = document.getElementById('flightInput').value.trim();
    if (!flight_id) return alert("❌ Entrer un callsign ou numéro de vol.");
    socket.emit('track_flight', { flight_id });
}

socket.on('update', data => {
    const { lat, lng, trail, altitude, speed, callsign } = data;
    if (marker) map.removeLayer(marker);
    if (trailLine) map.removeLayer(trailLine);

    marker = L.marker([lat, lng]).addTo(map).bindPopup(`${callsign}<br>Alt: ${altitude} ft<br>Vit: ${speed} kt`).openPopup();

    const trailLatLngs = trail.map(p => [p.lat, p.lng]);
    trailLine = L.polyline(trailLatLngs, { color: 'lime', weight: 3 }).addTo(map);

    map.setView([lat, lng], 6);
});

socket.on('error', data => {
    alert("Erreur: " + data.message);
});
