import requests
import time
from getpass import getpass
from mysql.connector import connect, Error

class Crawler:
    categories = []
    data = []
    bearerToken = ""

    try:
        conn =  connect(
            host="localhost",
            user=input("Enter username: "),
            password=getpass("Enter password: "),
            database = "crawldata"
        )
        cur = conn.cursor()    
    except Error as e:
        print(e)
    
    def createTable(self):
        drop_table_query = "DROP TABLE IF EXISTS apis"
        create_table_query = """
        CREATE TABLE apis (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            API VARCHAR(50),
            Description VARCHAR(200),
            Auth VARCHAR(20),
            HTTPS BOOLEAN,
            Cors VARCHAR(20),
            Link VARCHAR(100),
            Category VARCHAR(50)
        )
        """
        try:
            self.cur.execute(drop_table_query)
            self.cur.execute(create_table_query)
            self.conn.commit()
        except:
            self.conn.rollback()

    def storeDatabase(self):
        tupleDataList = []
        for ele in self.data:
            tple = (ele["API"], ele["Description"], ele["Auth"],ele["HTTPS"],ele["Cors"],ele["Link"],ele["Category"])
            tupleDataList.append(tple)
        
            insert_apis_query = """
            INSERT INTO apis
            (API, Description, Auth, HTTPS, Cors, Link, Category)
            VALUES ( %s, %s, %s, %s, %s, %s, %s )
            """
        try:
            self.cur.executemany(insert_apis_query,tupleDataList);
            self.conn.commit()
        except:
            self.conn.rollback()
        


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
        

    def makeRequest(self,url,bearerToken,page = 1,category = None):
        headers = {"Authorization": bearerToken}
        if category != None:
            params = {"page":page, "category":category}
        else:
            params = {"page":page}
        response = requests.request("GET", url, headers = headers, params = params)
        if response.status_code == 200 or response.status_code == 403:
            return response.json()
        elif response.status_code == 429:
            return {"error":"too many requests"}
        else:
            return {"error":"unknown error"}
    
    def getAllCategories(self):
        page = 1
        while True:
            url = "https://public-apis-api.herokuapp.com/api/v1/apis/categories"
            categoriesResponse = self.makeRequest(url, self.bearerToken,page)
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
        for category in self.categories:
            page = 1
            while True:
                url = "https://public-apis-api.herokuapp.com/api/v1/apis/entry"
                categoriesResponse = self.makeRequest(url, self.bearerToken,page,category)
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
crawl.createTable()
if crawl.setToken():
    categoriesReturn = crawl.getAllCategories()
    
    if categoriesReturn and crawl.getAllCategoriesAPI():
        crawl.storeDatabase()
    else:
        print("ERROR: Unknown Error")
        
else:
    print("ERROR: Unknown Error")

