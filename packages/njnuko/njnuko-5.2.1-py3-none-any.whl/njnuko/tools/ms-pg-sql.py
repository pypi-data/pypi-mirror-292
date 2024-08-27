import pymssql
import psycopg2
# user      用户名
# password  密码
# database  数据库名称
source_conn = pymssql.connect('127.0.0.1', 'sa', '231231', 'hotel')
source_cursor = source_conn.cursor()
source_cursor.execute('select * from dbo.cdsgus a where a.id > 1530001 order by a.id')

dest_conn=psycopg2.connect(database="dbname",user="xxx",password="xxxx",host="xxxxx",port="ports")
dest_cursor = dest_conn.cursor()

for i in range(1,2010):
    data = source_cursor.fetchmany(10000)
    dest_cursor.executemany("insert into records values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",data)
    dest_conn.commit()
    print("The ",i, " batch has inserted!")

dest_conn.close()
source_conn.close()
