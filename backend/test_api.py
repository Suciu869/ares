import requests

regions = ['UA63', 'UA14', 'UA09', 'UA12', 'UA30']
for r in regions:
    response = requests.post('http://localhost:8000/api/evalueaza-regiune', json={'region_id': r, 'timestamp': '2026-03-15T12:34:56.789Z'})
    data = response.json()
    print(f'{r}: {data["risk_percent"]}%')