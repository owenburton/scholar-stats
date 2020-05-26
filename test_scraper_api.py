import requests

if __name__ == "__main__":
    payload = {
        "url": "https://scholar.google.co.uk/citations?hl=en&user=JicYPdAAAAAJ"
        } 
    url = 'http://0.0.0.0:8080'
    r = requests.post(url=url, json=payload) 
    print(r.json())