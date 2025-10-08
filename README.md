Solar Project Frontend

This is a minimal static frontend for your solar project. It implements:

- Interactive map (Leaflet). Clicking the map places a marker and POSTs {lat,lon} to /api/location.
- A form for "Solar panel generation" inputs: system capacity, preferred brand, optimize orientation (true/false), max payback years.
- A premium toggle that enables manual tilt & azimuth inputs. Without premium the inputs are disabled and a status message is shown.
- Buttons to request solar design (/api/generate-solar) and invoice (/api/generate-invoice). Invoice is downloaded as a PDF blob if the backend returns one.

Files added:
- `index.html` — main page
- `assets/styles.css` — small styles
- `assets/app.js` — frontend JS

How to use:
1. Serve the folder `c:\Users\abels\Documents\ghacks` with any static server (for example Python: `python -m http.server 8000`).
2. Open http://localhost:8000 in your browser.
3. Click the map to choose a location (lat/lon will be POSTed to `/api/location`).
4. Fill the form and click "Generate solar design" or "Generate invoice". These endpoints are expected on your backend.

Notes / next steps:
- Backend endpoints are not included. Implement `/api/location`, `/api/generate-solar`, and `/api/generate-invoice` to integrate.
- Security: CSRF and auth not handled in this static demo.
- Premium features are locally gated by a checkbox; replace with real entitlement checks in production.
