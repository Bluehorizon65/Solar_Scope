import React, { useState } from 'react'

export default function FormPanel({ location, onInvoice }){
  const [systemCapacity, setSystemCapacity] = useState('')
  const [preferredBrand, setPreferredBrand] = useState('')
  const [optimizeOrientation, setOptimizeOrientation] = useState('')
  const [maxPayback, setMaxPayback] = useState('')
  const [budget, setBudget] = useState('')
  const [premium, setPremium] = useState(false)
  const [tilt, setTilt] = useState('')
  const [azimuth, setAzimuth] = useState('')
  const [status, setStatus] = useState('Ready')

  const collect = ()=> ({
    systemCapacity: parseFloat(systemCapacity)||0,
    preferredBrand: preferredBrand||null,
    optimizeOrientation: optimizeOrientation||null,
    maxPaybackYears: parseInt(maxPayback)||null,
    budget: parseFloat(budget)||null,
    premiumManualAngles: premium ? { tilt: parseFloat(tilt)||0, azimuth: parseFloat(azimuth)||0 } : null
  })

  const handleGenerate = async ()=>{
    if (!location) return setStatus('Pick location first')
    setStatus('Requesting design...')
    try{
      const payload = collect(); payload.location = { lat: location.lat, lon: location.lng }
      const res = await fetch('/api/generate-solar', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
      if (!res.ok) throw new Error('HTTP '+res.status)
      const json = await res.json().catch(()=>null)
      setStatus('Design requested')
      if (json && json.fileUrl) window.open(json.fileUrl, '_blank')
    }catch(e){ console.error(e); setStatus('Design request failed') }
  }

  const handleInvoice = async ()=>{
    if (!location) return setStatus('Pick location first')
    setStatus('Requesting invoice...')
    try{
      const payload = collect(); payload.location = { lat: location.lat, lon: location.lng }
      const res = await fetch('/api/generate-invoice', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
      if (!res.ok) throw new Error('HTTP '+res.status)
      const ct = res.headers.get('content-type')||''
      if (ct.includes('application/json')){
        const json = await res.json(); if (json.fileUrl){ onInvoice && onInvoice(json.fileUrl); window.open(`/preview?url=${encodeURIComponent(json.fileUrl)}`, '_blank') }
      } else {
        const blob = await res.blob(); const url = URL.createObjectURL(blob); onInvoice && onInvoice(url); window.open(`/preview?url=${encodeURIComponent(url)}`, '_blank')
      }
      setStatus('Invoice ready')
    }catch(e){ console.error(e); setStatus('Invoice request failed') }
  }

  return (
    <div className="card p-3 shadow-sm">
      <h4>Solar inputs</h4>
      <div className="mb-2">
        <label className="form-label">System capacity (kW)</label>
        <input className="form-control form-control-lg rounded-pill" value={systemCapacity} onChange={e=> setSystemCapacity(e.target.value)} placeholder="e.g. 5.5" />
      </div>
      <div className="mb-2">
        <label className="form-label">Preferred brand (optional)</label>
        <input className="form-control rounded-pill" value={preferredBrand} onChange={e=> setPreferredBrand(e.target.value)} placeholder="e.g. SunPower" />
      </div>
      <div className="mb-2">
        <label className="form-label">Optimize orientation (optional)</label>
        <select className="form-select rounded-pill" value={optimizeOrientation} onChange={e=> setOptimizeOrientation(e.target.value)}>
          <option value="">(auto)</option>
          <option value="true">true</option>
          <option value="false">false</option>
        </select>
      </div>
      <div className="row g-2 mb-2">
        <div className="col-6">
          <label className="form-label">Max payback years</label>
          <input className="form-control rounded-pill" value={maxPayback} onChange={e=> setMaxPayback(e.target.value)} placeholder="e.g. 8" />
        </div>
        <div className="col-6">
          <label className="form-label">Budget</label>
          <input className="form-control rounded-pill" value={budget} onChange={e=> setBudget(e.target.value)} placeholder="e.g. 10000" />
        </div>
      </div>

      <div className="form-check form-switch mb-2">
        <input className="form-check-input" type="checkbox" id="premiumToggleLocal" checked={premium} onChange={e=> setPremium(e.target.checked)} />
        <label className="form-check-label" htmlFor="premiumToggleLocal">Enable manual tilt & azimuth (premium)</label>
      </div>

      <div className="row g-2 mb-3">
        <div className="col-6">
          <label className="form-label">Tilt (°)</label>
          <input className="form-control rounded-pill" disabled={!premium} value={tilt} onChange={e=> setTilt(e.target.value)} />
        </div>
        <div className="col-6">
          <label className="form-label">Azimuth (°)</label>
          <input className="form-control rounded-pill" disabled={!premium} value={azimuth} onChange={e=> setAzimuth(e.target.value)} />
        </div>
      </div>

      <div className="d-grid gap-2">
        <button className="btn btn-gradient btn-lg rounded-pill" onClick={handleGenerate}><i className="bi bi-lightning-fill me-2"></i>Generate solar design</button>
        <button className="btn btn-outline-gradient btn-lg rounded-pill" onClick={handleInvoice}><i className="bi bi-receipt me-2"></i>Generate invoice</button>
      </div>

      <div className="mt-3 small text-muted">{status}</div>
    </div>
  )
}
