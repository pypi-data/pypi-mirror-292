import pyodbc


def get_connection():
    # Database connection string
    connection_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=77.68.54.17;"
        "Database=plexaardynamicformlistingapi_staging;"
        "UID=sa;"
        "PWD=DFGHFG@#$%^&@#$%^&12113@1222@#$%^;"
    )
    conn = pyodbc.connect(connection_str)
    return conn