from peewee import PostgresqlDatabase

db_reports = PostgresqlDatabase(
    database="diploma_db",
    user="postgres",
    password="password",
    host="localhost",
    port="15432"
)
