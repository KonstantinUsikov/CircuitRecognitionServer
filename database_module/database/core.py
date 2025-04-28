from peewee import PostgresqlDatabase

db = PostgresqlDatabase(
    database="diploma_db",
    user="postgres",
    password="password",
    host="localhost",
    port="15432"
)
