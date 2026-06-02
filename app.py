from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import json, math, os, uuid, datetime

BASE = Path(__file__).parent
DATA = BASE / 'data'
UPLOADS = BASE / 'uploads'
DATA.mkdir(exist_ok=True)
UPLOADS.mkdir(exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = str(UPLOADS)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024


def load_json(name, default):
    path = DATA / name
    if not path.exists():
        path.write_text(json.dumps(default, indent=2), encoding='utf-8')
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(name, payload):
    (DATA / name).write_text(json.dumps(payload, indent=2), encoding='utf-8')


def km_between(a_lat, a_lng, b_lat, b_lng):
    r = 6371
    dlat = math.radians(b_lat - a_lat)
    dlng = math.radians(b_lng - a_lng)
    x = math.sin(dlat/2)**2 + math.cos(math.radians(a_lat))*math.cos(math.radians(b_lat))*math.sin(dlng/2)**2
    return 2 * r * math.atan2(math.sqrt(x), math.sqrt(1-x))


def ai_score(printer, query='', service='', lat=None, lng=None):
    score = 50
    text = ' '.join([printer.get('name',''), printer.get('city',''), printer.get('province',''), ' '.join(printer.get('services',[]))]).lower()
    for token in (query + ' ' + service).lower().split():
        if token and token in text:
            score += 8
    if printer.get('verified'):
        score += 12
    score += float(printer.get('rating', 4)) * 6
    if lat is not None and lng is not None:
        d = km_between(float(lat), float(lng), printer['lat'], printer['lng'])
        printer['distance_km'] = round(d, 1)
        score += max(0, 40 - min(d, 40))
    return round(score, 2)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/printers')
def printers():
    records = load_json('printers.json', [])
    q = request.args.get('q','')
    service = request.args.get('service','')
    province = request.args.get('province','')
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    out = []
    for p in records:
        if province and p.get('province') != province:
            continue
        if service and service not in p.get('services', []):
            continue
        if q and q.lower() not in json.dumps(p).lower():
            # still allow AI to rank service-like phrases
            pass
        p = dict(p)
        p['ai_score'] = ai_score(p, q, service, lat, lng) if lat and lng else ai_score(p, q, service)
        out.append(p)
    out.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
    return jsonify(out)

@app.route('/api/quote', methods=['POST'])
def quote():
    payload = request.form.to_dict() or request.get_json(force=True, silent=True) or {}
    quotes = load_json('quotes.json', [])
    file = request.files.get('artwork')
    if file:
        filename = secure_filename(file.filename)
        stored = f"{uuid.uuid4().hex}_{filename}"
        file.save(UPLOADS / stored)
        payload['artwork_file'] = stored
    payload['id'] = 'Q-' + datetime.datetime.now().strftime('%Y%m%d') + '-' + uuid.uuid4().hex[:6].upper()
    payload['status'] = 'New AI Quote'
    payload['created_at'] = datetime.datetime.now().isoformat(timespec='seconds')
    payload['estimated_price'] = estimate_price(payload)
    quotes.insert(0, payload)
    save_json('quotes.json', quotes)
    return jsonify(payload)


def estimate_price(p):
    qty = int(p.get('quantity') or 100)
    service = (p.get('service') or '').lower()
    base = 120
    rates = {'business cards': 1.8, 'flyers': 1.2, 'banners': 95, 'vehicle branding': 850, 't-shirts': 75, 'stickers': 2.4, 'signage': 550, 'packaging': 6.5}
    rate = next((v for k, v in rates.items() if k in service), 2.0)
    urgent = 1.35 if p.get('turnaround') == 'Urgent / Same Day' else 1
    return f"R{round((base + qty * rate) * urgent):,}"

@app.route('/api/quotes')
def quotes():
    return jsonify(load_json('quotes.json', []))

@app.route('/api/onboard-printer', methods=['POST'])
def onboard_printer():
    p = request.get_json(force=True)
    printers = load_json('printers.json', [])
    p['id'] = 'P-' + uuid.uuid4().hex[:8]
    p['verified'] = False
    p['rating'] = 4.0
    p['services'] = p.get('services', []) if isinstance(p.get('services'), list) else [s.strip() for s in p.get('services','').split(',')]
    printers.insert(0, p)
    save_json('printers.json', printers)
    return jsonify(p)

@app.route('/uploads/<path:name>')
def upload(name):
    return send_from_directory(UPLOADS, name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
