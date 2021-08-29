# Public APIs List Crawler 

It fetch and store a list of all API in the database 


## a) Steps to run code

### With Docker
```
git clone https://github.com/Sohan022/Postman_Intern_Assignment.git
cd Postman_Intern_Assignment
docker-compose up
```
Note: After running `docker-compose up` command wait 10-15 minutes to do every step mention in Dockerfile.

### Without Docker (run locally)

Install these requirements form terminal
```
pip install mysql-connector-python
pip install python-dotenv
pip install requests
pip install rich
```
```
git clone https://github.com/Sohan022/Postman_Intern_Assignment.git
cd Postman_Intern_Assignment/app
```
Note: Make change in .env file to connect MySQL database

```
python3 crawler.py
```
## b) Details of all the tables and their schema

Only one table used 

Table Name: `apis`

| Field       | Type         | NULL | Key | Extra          |
| ----------- | ------------ | ---- | --- | -------------- |
| ID          | int          | NO   | PRI | auto_increment |
| API         | varchar(100) | YES  |     |                |
| Description | varchar(500) | YES  |     |                |
| Auth        | varchar(20)  | YES  |     |                |
| HTTPs       | boolean      | YES  |     |                |
| Cors        | varchar(20)  | YES  |     |                |
| Link        | varchar(300) | YES  |     |                |
| Category    | varchar(100) | YES  |     |                |

### Create Table Query
```
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
```

## c) What is done from “Points to achieve” and number of entries in your table
> Your code should follow concept of OOPS
>
> Support for handling authentication requirements & token expiration of server
>
> Support for pagination to get all data
>
> Develop work around for rate limited server
>
> Crawled all API entries for all categories and stored it in a database

**I have done all the 5 points**

**My Table contains 640 rows of 45 different categories**

## d) What is not done from “Points to achieve”. If not achieved, write the possible reasons and current workarounds.
**Everything has been done**

## e) What would you improve if given more days

* I would try to improve the progress bar which will look more intuitive. And I would also try to show every step with a progress bar.

* I would try to find a better way (i.e. faster method) to fetch APIs data. I would try to find a solution that overcomes rate limiting.
