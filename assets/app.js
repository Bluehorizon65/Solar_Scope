// Premium frontend logic
let map, modalMap;
let marker = null;
let selectedLatLng = null;

function setStatus(msg) {
  document.getElementById('status').textContent = msg;
}

async function postJson(path, obj) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(obj)
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json().catch(() => null);
}

// Initialize modal map when modal shown
const mapModalEl = document.getElementById('mapModal');
const mapModal = new bootstrap.Modal(mapModalEl);
mapModalEl.addEventListener('shown.bs.modal', () => {
  setTimeout(() => {
    if (!modalMap) {
      modalMap = L.map('map').setView([20, 0], 2);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(modalMap);
      modalMap.on('click', async (e) => {
        if (marker) modalMap.removeLayer(marker);
        marker = L.marker(e.latlng).addTo(modalMap);
        selectedLatLng = e.latlng;
        document.getElementById('locationDisplay').textContent = `Selected: ${e.latlng.lat.toFixed(6)}, ${e.latlng.lng.toFixed(6)}`;
        setStatus('Location selected — sending to backend...');
        try {
          await postJson('/api/location', { lat: e.latlng.lat, lon: e.latlng.lng });
          setStatus('Location sent to backend.');
        } catch (err) {
          console.error(err);
          setStatus('Failed to send location to backend.');
        }
      });
    } else {
      modalMap.invalidateSize();
    }
  }, 100);
});

document.getElementById('openMapBtn').addEventListener('click', () => mapModal.show());
document.getElementById('clearLocationBtn').addEventListener('click', () => {
  if (marker && modalMap) { modalMap.removeLayer(marker); marker = null; }
  selectedLatLng = null;
  document.getElementById('locationDisplay').textContent = 'No location selected';
  setStatus('Location cleared');
});

// form interactions
const premiumToggle = document.getElementById('premiumToggle');
const tiltInput = document.getElementById('tiltAngle');
const azimuthInput = document.getElementById('azimuthAngle');
premiumToggle.addEventListener('change', () => {
  const enabled = premiumToggle.checked;
  tiltInput.disabled = !enabled;
  azimuthInput.disabled = !enabled;
});

function collectForm() {
  const capacity = parseFloat(document.getElementById('systemCapacity').value || '0');
  const brand = document.getElementById('preferredBrand').value || null;
  const optimize = document.getElementById('optimizeOrientation').value || null;
  const maxPayback = parseInt(document.getElementById('maxPayback').value || '0', 10) || null;
  const budget = parseFloat(document.getElementById('budget').value || '0') || null;
  const premium = premiumToggle.checked;
  const tilt = premium ? parseFloat(tiltInput.value || '0') : null;
  const az = premium ? parseFloat(azimuthInput.value || '0') : null;
  return {
    systemCapacity: capacity,
    preferredBrand: brand,
    optimizeOrientation: optimize,
    maxPaybackYears: maxPayback,
    budget,
    premiumManualAngles: premium ? { tilt, azimuth: az } : null
  };
}

document.getElementById('generateBtn').addEventListener('click', async () => {
  if (!selectedLatLng) return setStatus('Please pick a location first.');
  const payload = collectForm();
  payload.location = { lat: selectedLatLng.lat, lon: selectedLatLng.lng };
  setStatus('Requesting solar design...');
  try {
    const resp = await postJson('/api/generate-solar', payload);
    setStatus('Design request submitted.');
    if (resp && resp.fileUrl) window.open(resp.fileUrl, '_blank');
  } catch (err) {
    console.error(err);
    setStatus('Design request failed.');
  }
});

document.getElementById('invoiceBtn').addEventListener('click', async () => {
  if (!selectedLatLng) return setStatus('Please pick a location first.');
  const payload = collectForm();
  payload.location = { lat: selectedLatLng.lat, lon: selectedLatLng.lng };
  setStatus('Requesting invoice...');
  try {
    const res = await fetch('/api/generate-invoice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    // If backend returns JSON with a fileUrl, open preview page
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const json = await res.json();
      if (json.fileUrl) {
        window.open(`/preview.html?url=${encodeURIComponent(json.fileUrl)}`, '_blank');
        setStatus('Invoice preview opened.');
        return;
      }
    }

    // Otherwise assume blob (PDF) and open a preview page with object URL
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    window.open(`/preview.html?url=${encodeURIComponent(url)}`, '_blank');
    setStatus('Invoice downloaded to preview.');
    // Note: object URL will be revoked when the tab is closed; backend should ideally provide permanent URL
  } catch (err) {
    console.error(err);
    setStatus('Invoice request failed.');
  }
});

document.getElementById('previewInvoiceBtn').addEventListener('click', () => {
  // This simply opens the preview page; for a real app you'd pass last invoice URL or generate a preview ID
  window.open('/preview.html', '_blank');
});

setStatus('Ready — pick a location to begin.');
