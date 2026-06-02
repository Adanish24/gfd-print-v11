let gps = {lat:null,lng:null};
const $ = id => document.getElementById(id);
function scrollToId(id){document.getElementById(id).scrollIntoView({behavior:'smooth'});}
async function loadPrinters(){
  const params = new URLSearchParams({q:$('q').value,province:$('province').value,service:$('service').value});
  if(gps.lat){params.set('lat',gps.lat);params.set('lng',gps.lng)}
  const data = await fetch('/api/printers?'+params).then(r=>r.json());
  $('printerCount').textContent = data.length;
  $('heroMatch').textContent = data[0] ? `${data[0].name} • AI Score ${data[0].ai_score}` : 'No printers found yet';
  $('printerCards').innerHTML = data.map(p=>`<article><span class="badge">${p.verified?'VERIFIED':'NEW'} ${p.network||''}</span><h3>${p.name}</h3><p>${p.city}, ${p.province} ${p.distance_km?`• ${p.distance_km}km`:''}</p><p>⭐ ${p.rating} • AI Score ${p.ai_score}</p><div class="services">${(p.services||[]).slice(0,6).map(s=>`<span>${s}</span>`).join('')}</div><div class="card-actions"><a href="tel:${p.phone}">Call</a><a href="${p.whatsapp?'https://wa.me/'+p.whatsapp:'#'}">WhatsApp</a><a target="_blank" href="https://www.google.com/maps/search/?api=1&query=${p.lat},${p.lng}">Directions</a><a target="_blank" href="${p.website}">Website</a></div></article>`).join('');
}
function useGPS(){
  navigator.geolocation?.getCurrentPosition(pos=>{gps.lat=pos.coords.latitude;gps.lng=pos.coords.longitude;loadPrinters();},()=>alert('GPS permission was not allowed.'));
}
$('quoteForm').addEventListener('submit', async e=>{
  e.preventDefault();
  const form = new FormData(e.target);
  const q = await fetch('/api/quote',{method:'POST',body:form}).then(r=>r.json());
  $('quoteResult').innerHTML = `<h3>${q.id}</h3><p>Status: ${q.status}</p><h2>${q.estimated_price}</h2><p>AI estimate saved. Admin can contact the customer and route it to the nearest printer.</p>`;
  loadQuotes(); e.target.reset();
});
async function loadQuotes(){
  const data = await fetch('/api/quotes').then(r=>r.json());
  $('quoteCount').textContent = data.length;
  $('quotes').innerHTML = data.map(q=>`<article><b>${q.id} • ${q.service||'Print Job'} • ${q.estimated_price}</b><p>${q.customer||'Customer'} • ${q.phone||''} • ${q.status}</p><small>${q.notes||''}</small></article>`).join('') || '<p>No quotes yet.</p>';
}
$('onboardForm').addEventListener('submit', async e=>{
  e.preventDefault();
  const obj = Object.fromEntries(new FormData(e.target).entries());
  obj.lat = parseFloat(obj.lat||'-26.2041'); obj.lng = parseFloat(obj.lng||'28.0473');
  await fetch('/api/onboard-printer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)});
  alert('Printer added to marketplace.'); e.target.reset(); loadPrinters();
});
if('serviceWorker' in navigator){navigator.serviceWorker.register('/static/service-worker.js').catch(()=>{})}
loadPrinters(); loadQuotes();
