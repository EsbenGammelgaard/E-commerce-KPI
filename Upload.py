# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 20:01:44 2021

@author: Esben Gammelgaard
"""

#%% Conection to local SQL server
import pyodbc 
import pandas as pd

driver = '{SQL Server}'
server = 'LAPTOP-S1H0GINM\MYSERVER' 
databaseName = 'E_Commerce_Data'

#%% Creating Database
conn = pyodbc.connect('Driver=' +driver+ ';'
                      'Server=' +server+ ';'
                      'Trusted_Connection=yes;')


pd.read_sql_query('CREATE DATABASE ' +databaseName,conn)

conn.close()

#%% Connecting to the Database 

conn_db = pyodbc.connect('Driver=' +driver+ ';'
                      'Server=' +server+ ';'
                      'Database=' +databaseName+ ';'
                      'Trusted_Connection=yes;')
cursor = conn_db.cursor()


#%% Dropping tables if needed
ID_list = ['SalesTargets_temp',
           'OrderDetails_temp',
           'dbo.ListOfOrders_temp',
           'SalesTargets',
           'OrderDetails',
           'ListOfOrders']
           
for ID in ID_list:
    cursor.execute("""IF OBJECT_ID(N'"""+ ID +"""', 'U') IS NOT NULL
               BEGIN
                   DROP TABLE """+ ID +""";
               END;""")
    conn_db.commit

# Creating tables that match the 3 CSV files

cursor.execute('CREATE TABLE dbo.SalesTargets_temp (MonthOfOrderDate VARCHAR(255), Category VARCHAR(255), SalesTarget DECIMAL(5,0))')

cursor.execute('''CREATE TABLE dbo.OrderDetails_temp (OrderID VARCHAR(255), Amount DECIMAL(5,0), Profit DECIMAL(5,0),
               Quantity DECIMAL(5,0), Category VARCHAR(255), SubCategory VARCHAR(255))''')

cursor.execute('''CREATE TABLE dbo.ListOfOrders_temp (OrderID VARCHAR(255), OrderDate VARCHAR(255), 
               CustomerName VARCHAR(255), State VARCHAR(255), City VARCHAR(255))''')
conn_db.commit()
            
# Inserting all the data from CSV as VARCHAR(255)

cursor.execute("""BULK INSERT dbo.SalesTargets_temp FROM
               'C:\\Users\esbe1\Desktop\Portfolio\Server\E_Commerce_Data\Sales target.csv'
               WITH (FORMAT = 'CSV', FIRSTROW=2);""")
               
cursor.execute("""BULK INSERT dbo.OrderDetails_temp FROM
               'C:\\Users\esbe1\Desktop\Portfolio\Server\E_Commerce_Data\Order Details.csv'
               WITH (FORMAT = 'CSV', FIRSTROW=2);""")
               
cursor.execute("""BULK INSERT dbo.ListOfOrders_temp FROM
               'C:\\Users\esbe1\Desktop\Portfolio\Server\E_Commerce_Data\List of Orders.csv'
               WITH (FORMAT = 'CSV', FIRSTROW=2);""")
               
conn_db.commit()

# Converting data to the correct datatypes

cursor.execute('''SELECT CAST(LEFT(MonthOfOrderDate,3) + ' 01, ' + RIGHT(MonthOfOrderDate,2) AS DATE) AS MonthOfOrderDate,
               Category, 
               CAST(SalesTarget as SMALLINT) AS SalesTarget
			   INTO dbo.SalesTargets
               FROM dbo.SalesTargets_temp
               DROP TABLE dbo.SalesTargets_temp''')

cursor.execute('''SELECT  OrderID,
               CAST(Amount AS SMALLINT) AS Amount,
               CAST(PROFIT AS SMALLINT) AS Profit,
               CAST(QUANTITY AS TINYINT) AS Quantity,
               Category,
               SubCategory
               INTO dbo.OrderDetails
               FROM dbo.OrderDetails_temp
               DROP TABLE OrderDetails_temp''')
               
cursor.execute('''SET DATEFORMAT dmy;
               SELECT  OrderID,
               CAST(OrderDate AS DATE) AS OrderDate,
               CustomerName,
               State,
               City
               INTO dbo.ListOfOrders
               FROM dbo.ListOfOrders_temp
               DROP TABLE dbo.ListOfOrders_temp''')
conn_db.commit()
