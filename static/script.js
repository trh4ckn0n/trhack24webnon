const socket = io();
let map = L.map('map').setView([46, 2], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
let marker, trail;

async function init() {
  const countries = await fetch('/countries').then(r => r.json());
  const sel = document.getElementById('country');
  sel.innerHTML = countries.map(c => `<option>${c}</option>`).join('');
  sel.onchange = () => loadAirports(sel.value);
  loadAirports(countries[0]);
}

async function loadAirports(country) {
  const aps = await fetch('/airports', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({country})}).then(r => r.json());
  const sel = document.getElementById('airport');
  sel.innerHTML = aps.map(a => `<option value="${a.icao}">${a.icao} – ${a.name}</option>`).join('');
  sel.onchange = () => loadFlights(sel.value);
  loadFlights(aps[0]?.icao);
}

async function loadFlights(icao) {
  const fls = await fetch('/flights', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({icao})}).then(r => r.json());
  document.getElementById('flight').innerHTML = fls.map(f => `<option value="${f.id}">${f.callsign} (${f.origin} → ${f.destination})</option>`).join('');
}

function startTrackById() {
  const id = document.getElementById('flight-id').value.trim();
  if (!id) return alert('Entrer ID ou Callsign');
  track(id);
}

function trackFromAirport() {
  const id = document.getElementById('flight').value;
  if (!id) return alert('Choisir un vol');
  track(id);
}

function track(id) {
  socket.emit('track', {flight_id: id});
  if (marker) map.removeLayer(marker);
  if (trail) map.removeLayer(trail);
}

socket.on('position', data => {
  const {lat, lng, alt, spd} = data;
  if (marker) map.removeLayer(marker);
  if (trail) map.removeLayer(trail);
  marker = L.marker([lat, lng]).addTo(map)
     .bindPopup(`Alt: ${alt} ft, Speed: ${spd} kt`).openPopup();
  socket.emit('track', {flight_id: document.getElementById('flight-id').value});
});
socket.on('error', e => alert(e.msg));

init();
