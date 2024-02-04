import requests

url = "https://os-sports-perform.p.rapidapi.com/v1/search/multi"

querystring = {"query":"Tampy Bay Lightning","group":"sports"}

headers = {
	"X-RapidAPI-Key": "a334258d84msh08b603e2305758fp14e80ajsn728491b73149",
	"X-RapidAPI-Host": "os-sports-perform.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())