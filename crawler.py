import requests
import time

class Crawler:
    categories = []
    data = []
    bearerToken = ""

    def getToken(self):
        url = "https://public-apis-api.herokuapp.com/api/v1/auth/token"
        response = requests.request("GET", url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            return {"error":"too many requests"}
        else:
            return {"error":"unknown error"}

    def setToken(self):
        token = self.getToken()
        if "error" in token:
            if token["error"] == "too many requests":
                time.sleep(60)
            else:
                return False
        else:
            token = self.getToken()
            self.bearerToken = "".join(("Bearer ",token['token']))
        return True
        

    def makeRequest(self,url,bearerToken):
        headers = {"Authorization": bearerToken}
        response = requests.request("GET", url, headers = headers)
        if response.status_code == 200 or response.status_code == 403:
            return response.json()
        elif response.status_code == 429:
            return {"error":"too many requests"}
        else:
            return {"error":"unknown error"}
    
    def getAllCategories(self):
        page = 1
        while True:
            url = "".join(("https://public-apis-api.herokuapp.com/api/v1/apis/categories?page=",str(page)))
            categoriesResponse = self.makeRequest(url, self.bearerToken)
            if 'error' in categoriesResponse:
                if categoriesResponse['error'] == "too many requests":
                    time.sleep(60)
                elif categoriesResponse['error'] == "Invalid token":
                    if self.setToken() == False:
                        return False
                else:
                    return False
            else: 
                self.categories.extend(categoriesResponse['categories'])
                if page*10 < categoriesResponse['count']:
                    page += 1
                else:
                    break
        return True
    
    def getAllCategoriesAPI(self):
        for category in self.categories[:10]:
            page = 1
            category = category.replace("&","%26")
            while True:
                url = "".join(("https://public-apis-api.herokuapp.com/api/v1/apis/entry?page=",str(page),"&category=",category))
                categoriesResponse = self.makeRequest(url, self.bearerToken)
                if 'error' in categoriesResponse:
                    if categoriesResponse['error'] == "too many requests":
                        time.sleep(60)
                    elif categoriesResponse['error'] == "Invalid token":
                        if self.setToken() == False:
                            return False
                    else:
                        return False
                else:
                    self.data.extend(categoriesResponse['categories'])
                    if page*10 < categoriesResponse['count']:
                        page += 1
                    else:
                        break
        return True

#driver code
crawl = Crawler()

if crawl.setToken():
    if crawl.getAllCategories():
        print(crawl.categories)
    else:
        print("ERROR: Unknown Error")

    if crawl.getAllCategoriesAPI():
        print(crawl.data)
    else:
        print("ERROR: Unknown Error")
        
else:
    print("ERROR: Unknown Error")

