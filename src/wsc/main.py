import requests

def main():
    s = requests.Session()
    data = {"email": "eg@gmail.com", "password": "admin"}
    url = "http://localhost:3000"
    r = s.post(url, data=data)
    print(f"post reponse: {r}")
    r = s.get('http://localhost:3000/home/coucou')
    print(f"get reponse: {r.json()}")


if __name__ == "__main__":
    main()
