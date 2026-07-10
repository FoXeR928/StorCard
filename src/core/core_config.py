from os import getenv

db_driver = getenv("SQL_DRIVER", "sqlite")
db_name=getenv("SQL_DB", "storcard_db")