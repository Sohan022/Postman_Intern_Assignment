import requests
import time
from mysql.connector import connect, Error
from rich.progress import Progress, BarColumn
import os
from dotenv import load_dotenv

load_dotenv()

class Crawler:
    """
    It is class for fetching APIs and store into database(MySQL). 
    Note: Only those APIs which are in this github link: https://github.com/public-apis/public-apis

    Attributes:
        __categories (list of str): All categories in API 
        __data (list of dic)      : List of all APIs data (APIName,Description,Auth,HTTPS,Cors,Link,Category)
        __bearerToken (str)       : contains token for authorization which will expire after 5 mintues
    
    """

    __categories = []
    __data = []
    __bearerToken = ""
    __conn = None
    __cur = None

    
    def __connectDatabase(self):
        """
        It connects to database by providing details (host,port,user,password,database)
        """
        try:
            self.__conn =  connect(
                host = os.getenv('HOST'),
                port = os.getenv('PORT'),
                user = os.getenv('USR'),
                password = os.getenv('PASSWORD'),
                database = os.getenv('DBNAME')
            )
            self.__cur = self.__conn.cursor()    
        except Error as e:
            print(e)
    

    def __createTable(self):
        """
        It creates table into database for storing APIs
        """
        # if there is already exist table then first remove it and again create
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
        """
        It store the APIs into database. 
        """
        # if the data are in list of tuples format then we can insert all the data in one time.
        # since __data contains list of dictionaries. 
        # So, first we convert __data into list of tuples and after that insert into database.
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
        """
        It fetch token from the API.

        Returns:
            It returns in json format.
            If API fetching is successful i.e. HTTP status code 200 then return token.
            If HTTP status code is 429 i.e. too many requests due to rate limiting of 10 requests/minutes
            then return 'error' with 'too many requests'.
            Othewise it return 'error' with description.
        """
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
        """
        It calls the __getToken method fot token and set tthat oken to __bearerToken with format("Bearer xxxxxxxxxxxxxx")

        Returns:
            It returns 'True' if successfully get token
            otherwise it returns 'False'
        """
        token = self.__getToken()

        # If __getToken method return 'error' with 'too many requests' due to rate limiting of 10 requests/minutes
        # then sleep for 60 seconds and call again __getToken method.
        if "error" in token:
            if token["error"] == "too many requests":
                time.sleep(60)
            else:
                return False
        else:
            token = self.__getToken()
            self.__bearerToken = "".join(("Bearer ",token['token']))
        return True
        

    def __makeRequest(self, url, bearerToken, page = 1, category = None):
        """
        It fetch data like list of categories name or list of all APIs details.

        Parameters:
            url (str): URL from which data have to fetch
            bearerToken (str): It requires for authorization
            page (int, optional, default=1): page number from which data have to fetch
            category (str, optional, default=None): category name from which data have to fetch

        There is two cases on the basis of number of parameters.

        CASE I:
            (if page is only passed during method call from optional parameter)      
            It will fetch list category name of a particular page

            Returns:
                It returns in json format.
                If API fetch is successful i.e. HTTP status code 200 then it returns and number of category and list of categories of a particular page.
                If HTTP status code is 403 i.e. token has been expired then, it will return 'error' with 'Invalid token'.
                If HTTP status code is 429 i.e. too many requests due to rate limiting of 10 requests/minutes
                then return 'error' with 'too many requests'.
                Othewise it return 'error' with description.

        CASE II:
            (if page and category both are passed during method call from optioanl parameter)
            It will fetch all APIs details.

            Returns:
                It returns in json format.
                If API fetch is successful i.e. HTTP status code 200 then it returns number of APIs of a category and list of APIs of a paticular page & a specific category.
                If HTTP status code is 403 i.e. token has been expired then, it will return 'error' with 'Invalid token'.
                If HTTP status code is 429 i.e. too many requests due to rate limiting of 10 requests/minutes
                then return 'error' with 'too many requests'.
                Othewise it return 'error' with description.
        """

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
        """
        It calls _makeRequest method to get all categories name and store to __categories attribute.
        
        Returns:
            It returns 'True' when successfully get categories name
            otherwise return 'False'
        """
        page = 1
        while True:
            url = "https://public-apis-api.herokuapp.com/api/v1/apis/categories"
            categoriesResponse = self.__makeRequest(url, self.__bearerToken,page)

            if 'error' in categoriesResponse:
                # If __makeRequest method returns 'error' with 'too many requests' due to rate limiting of 10 requests/minutes
                # then sleep for 60 seconds and call again __makeRequest method in next iteration without incrementing page number
                if categoriesResponse['error'] == "too many requests":
                    time.sleep(60)

                # If __makeRequest returns 'error' with 'Invalid token' due to token expiry in 5 minutes
                # then call __setToken method and again call _makeRequest method in next iteration without incrementing page number
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
        """
        It calls __makeRequest method to get all APIs list of category and store to __data attribute.
        
        Returns:
            It returns 'True' when successfully get APIs list of category
            otherwise return 'False'
        """

        # Progress is used to show bar and progress percentage
        progress = Progress("[progress.description]{task.description}",BarColumn(),"[progress.percentage]{task.percentage:>3.0f}%")
        with progress:
            task = progress.add_task("[green]Progress...", total=len(self.__categories))
            for category in self.__categories:
                page = 1
                while True:
                    url = "https://public-apis-api.herokuapp.com/api/v1/apis/entry"
                    categoriesResponse = self.__makeRequest(url, self.__bearerToken,page,category)

                    if 'error' in categoriesResponse:
                        # If __makeRequest method returns 'error' with 'too many requests' due to rate limiting of 10 requests/minutes
                        # then sleep for 60 seconds and call again __makeRequest method in next iteration without incrementing page number
                        if categoriesResponse['error'] == "too many requests":
                            time.sleep(60)
                        
                        # If __makeRequest returns 'error' with 'Invalid token' due to token expiry in 5 minutes
                        # then call __setToken method and again call _makeRequest method in next iteration without incrementing page number
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
        """
        It is public method to get all categories list and all APIs list of category
        """
        if self.__setToken():
            categoriesReturn = self.__getAllCategories()
        if categoriesReturn and self.__getAllCategoriesAPI():
            print("Successfully crawled!")   


    def saveToDatabase(self):
        """
        It is public method to save data which have crawled already into database.
        """
        if len(self.__data) == 0:
            print("No Data Crawled!!!")
        else:
            self.__connectDatabase()
            self.__createTable()
            self.__storeDatabase()
            print("successfully Save to Database!")


    def crawlAndSaveToDatabase(self):
        """
        It is public method to crawl and save to database.
        """
        self.crawl()
        self.saveToDatabase()


    def printCategories(self):
        """
        It prints category list which have already crawled
        """
        if len(self.__categories) == 0:
            print("There is not data!!!")
        else:
            print(self.__categories)

    
    def printAllAPI(self):
        """
        It prints all APIs list of category.
        """
        if len(self.__data) == 0:
            print("There is not data")
        else:
            print(self.__data)



#driver code
crawler = Crawler()
crawler.crawlAndSaveToDatabase()

