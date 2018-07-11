import requests

def main():
    s = requests.Session()
    #data = {"email": "eg@gmail.com", "password": "admin"}
    data = {"email": "notify@gmail.com", "password": "7scAq08BH3sfh2AFNCjFaztePJ"}
    url = "http://localhost:3000"
    r = s.post(url, data=data)
    print(f"post reponse: {r}")
    r = s.get('http://localhost:3000/home/alarmnotfy')
    print(f"get reponse: {r.json()}")


if __name__ == "__main__":
    main()
