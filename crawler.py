import requests
import time
from getpass import getpass
from mysql.connector import connect, Error
from rich.progress import Progress, BarColumn

class Crawler:
    __categories = []
    __data = []
    __bearerToken = ""
    __conn = None
    __cur = None

    def __connectDatabase(self):
        try:
            self.__conn =  connect(
                host="localhost",
                user=input("Enter username: "),
                password=getpass("Enter password: "),
                database = "crawldata"
            )
            self.__cur = self.__conn.cursor()    
        except Error as e:
            print(e)
    
    def __createTable(self):
        drop_table_query = "DROP TABLE IF EXISTS apis"
        create_table_query = """
        CREATE TABLE apis (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            API VARCHAR(100),
            Description VARCHAR(500),
            Auth VARCHAR(20),
            HTTPS BOOLEAN,
            Cors VARCHAR(20),
            Link VARCHAR(300),
            Category VARCHAR(100)
        )
        """
        try:
            self.__cur.execute(drop_table_query)
            self.__cur.execute(create_table_query)
            self.__conn.commit()
        except:
            self.__conn.rollback()

    def __storeDatabase(self):
        tupleDataList = []
        for ele in self.__data:
            tple = (ele["API"], ele["Description"], ele["Auth"],ele["HTTPS"],ele["Cors"],ele["Link"],ele["Category"])
            tupleDataList.append(tple)
        
            insert_apis_query = """
            INSERT INTO apis
            (API, Description, Auth, HTTPS, Cors, Link, Category)
            VALUES ( %s, %s, %s, %s, %s, %s, %s )
            """
        try:
            self.__cur.executemany(insert_apis_query,tupleDataList);
            self.__conn.commit()
        except Error as e:
            print(e)
            self.__conn.rollback()
        


    def __getToken(self):
        url = "https://public-apis-api.herokuapp.com/api/v1/auth/token"
        response = requests.request("GET", url)
        try:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                return {"error":"too many requests"}
            else:
                response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(errh)
            return {"error":"HTTP Error"}
        except requests.exceptions.ConnectionError as errc:
            print("Connection Error: Retry Again")
            return {"error":"Connection Error: Retry Again"}
        except requests.exceptions.Timeout as errt:
            print("Timeout: Retry Again")
            return {"error":"Timeout: Retry Again"}
        except requests.exceptions.TooManyRedirects as errto:
            print("Too Many Redirects: Bad Url, Try Different one")
            return {"error":"Too Many Redirects: Bad Url, Try Different one"}
        except requests.exceptions.RequestException as err:
            print("ERROR: Unknow Error")
            return {"error":"ERROR: Unknow Error"}

    def __setToken(self):
        token = self.__getToken()
        if "error" in token:
            if token["error"] == "too many requests":
                time.sleep(60)
            else:
                return False
        else:
            token = self.__getToken()
            self.__bearerToken = "".join(("Bearer ",token['token']))
        return True
        

    def __makeRequest(self,url,bearerToken,page = 1,category = None):
        headers = {"Authorization": bearerToken}
        if category != None:
            params = {"page":page, "category":category}
        else:
            params = {"page":page}
        try: 
            response = requests.request("GET", url, headers = headers, params = params)
            if response.status_code == 200 or response.status_code == 403:
                return response.json()
            elif response.status_code == 429:
                return {"error":"too many requests"}
            else:
                response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(errh)
            return {"error":"HTTP Error"}
        except requests.exceptions.ConnectionError as errc:
            print("Connection Error: Retry Again")
            return {"error":"Connection Error: Retry Again"}
        except requests.exceptions.Timeout as errt:
            print("Timeout: Retry Again")
            return {"error":"Timeout: Retry Again"}
        except requests.exceptions.TooManyRedirects as errto:
            print("Too Many Redirects: Bad Url, Try Different one")
            return {"error":"Too Many Redirects: Bad Url, Try Different one"}
        except requests.exceptions.RequestException as err:
            print("ERROR: Unknow Error")
            return {"error":"ERROR: Unknow Error"}
    
    def __getAllCategories(self):
        page = 1
        while True:
            url = "https://public-apis-api.herokuapp.com/api/v1/apis/categories"
            categoriesResponse = self.__makeRequest(url, self.__bearerToken,page)
            if 'error' in categoriesResponse:
                if categoriesResponse['error'] == "too many requests":
                    time.sleep(60)
                elif categoriesResponse['error'] == "Invalid token":
                    if self.__setToken() == False:
                        return False
                else:
                    return False
            else: 
                self.__categories.extend(categoriesResponse['categories'])
                if page*10 < categoriesResponse['count']:
                    page += 1
                else:
                    break
        return True
    
    def __getAllCategoriesAPI(self):
        progress = Progress("[progress.description]{task.description}",BarColumn(),"[progress.percentage]{task.percentage:>3.0f}%")
        with progress:
            task = progress.add_task("[green]Progress...", total=len(self.__categories))
            for category in self.__categories:
                page = 1
                while True:
                    url = "https://public-apis-api.herokuapp.com/api/v1/apis/entry"
                    categoriesResponse = self.__makeRequest(url, self.__bearerToken,page,category)
                    if 'error' in categoriesResponse:
                        if categoriesResponse['error'] == "too many requests":
                            time.sleep(60)
                        elif categoriesResponse['error'] == "Invalid token":
                            if self.__setToken() == False:
                                return False
                        else:
                            return False
                    else:
                        self.__data.extend(categoriesResponse['categories'])
                        if page*10 < categoriesResponse['count']:
                            page += 1
                        else:
                            break
                progress.update(task, advance=1)
        return True



    def crawl(self):
        if self.__setToken():
            categoriesReturn = self.__getAllCategories()
        if categoriesReturn and self.__getAllCategoriesAPI():
            print("Successfully crawled!")   

    def saveToDatabase(self):
        if len(self.__data) == 0:
            print("No Data Crawled!!!")
        else:
            self.__connectDatabase()
            self.__createTable()
            self.__storeDatabase()
            print("successfully Save to Database!")

    def crawlAndSaveToDatabase(self):
        self.crawl()
        self.saveToDatabase()

    def printCategories(self):
        if len(self.__categories) == 0:
            print("There is not data!!!")
        else:
            print(self.__categories)
    
    def printAllAPI(self):
        if len(self.__data) == 0:
            print("There is not data")
        else:
            print(self.__data)



#driver code
crawler = Crawler()
crawler.crawlAndSaveToDatabase()

