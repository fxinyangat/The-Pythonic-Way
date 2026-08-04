# # FAST API

# import requests
# import json

# try:
    
#     response = requests.get('https://api.github.com/search/repositories?q=stars:>=1&sort=stars&order=desc')
#     print(response)
#     data = response.json()
#     items = data.get('items', [])
    
#     selected = []
    
#     for item in items:
#         selected.append({
#             "name": item.get("name"),
#             "private": item.get("private"),
#             "repo_url": item['owner'].get('repos_url'),
#             "html_url": item.get("html_url"),
#             "description": item.get("description"),
#             "stargazers_count": item.get("stargazers_count"),
#             "language": item.get("language"),
#             "forks_count": item.get("forks_count"),
#             "forks": item.get("forks")

#         })
        
        
  

    


    
    
# except (requests.exceptions, requests.HTTPError) as e:
#     print(f"Error occured, {e}")
    
# else:
#     with open("data.json", "w") as file:
#         # pass
#         json.dump(data,file)
# finally:
#     print(f"Github operation completed")
   
   
#     # POST request 
# payload = {
#   "name": "Apple MacBook Pro 16",
#   "data": {
#     "year": 2019,
#     "price": 1849.99,
#     "CPU model": "Intel Core i9",
#     "Hard disk size": "1 TB"
#   }
# }

# headers = {
#     "Content-Type": "application/json",
#     "x-api-key": "f1ab80b3-6993-41f0-963a-7aef8288cb42"   
# }
# try:
#     response = requests.post(
#         'https://api.restful-api.dev/collections/products/objects',
#         json=payload,
#         headers=headers)

#     print(f"Post Response: {response.json()}")
# except requests.HTTPError as e:
#     print("Error occured posting: {e}")
    

# Fast API 

from fastapi import FastAPI

# initialize application
app = FastAPI()

@app.get('/health-check')
def checkApiHealth():
    return {
        "status": 200,
        "message": "Server is well and running"
            }

@app.get("/")
def read_root():
    return {"message": "Hello First API!"}

@app.get('/items/{item_id}')
def read_item(item_id: int, q: str):
    return {"item_id": item_id, "query_param": q}


   
    

