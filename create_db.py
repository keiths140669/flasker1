import mysql.connector
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='password147',
)

my_cursor = mydb.cursor()

# my_cursor.execute("CREATE DATABASE our_users1")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)
