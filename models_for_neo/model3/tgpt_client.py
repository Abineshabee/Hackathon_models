import requests

url1 = "http://127.0.0.1:8080/query"  # Change to the server's IP if hosting remotely

url2 = "http://127.0.0.1:8080/web_search/query"  

query = "Tell me a joke"  # Example query

response = requests.post(url1, json={"query": query})  # Send request
print(response.json())  # Print the response


#response = requests.post(url2, json={"query": query})  # Send request
#print(response.json())  # Print the response
