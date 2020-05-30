import requests

if __name__ == "__main__":
    # zack burton
    # test_url = "https://scholar.google.com/citations?user=X7FY3wUAAAAJ&hl=en&oi=ao"
    # thomas wolf
    test_url = "https://scholar.google.com/citations?user=D2H5EFEAAAAJ&hl=en"
    # geoffrey hinton
    # test_url = "https://scholar.google.co.uk/citations?hl=en&user=JicYPdAAAAAJ"
    payload = {
        "url": test_url
        } 
    # url = 'http://0.0.0.0:8080'
    url = "https://scholarscraper-st2oqocqiq-uw.a.run.app" # deployed on cloud run
    r = requests.post(url=url, json=payload) 
    print(r.json())