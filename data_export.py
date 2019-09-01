import pymysql
import pandas as pd
import pyreadr
import sqlalchemy as sql

connect_str = 'mysql+pymysql://ubuntu:db5656576@localhost/research'
sql_engine = sql.create_engine(connect_str)
query = "SELECT * FROM comments"
query_color = "SELECT * FROM colours"
df = pd.read_sql_query(query,sql_engine)

print(df)
pyreadr.write_rdata("comments.RData",df)
print("============break line==========")
df_color = pd.read_sql_query(query_color,sql_engine)
pyreadr.write_rdata("colours.RData",df_color)
