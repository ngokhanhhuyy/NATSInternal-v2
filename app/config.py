databaseConfigurationNEONTECT = {
    "host":                 "ep-wandering-hat-558903-pooler.ap-southeast-1.aws.neon.tech",
    "port":                 "5432",
    "database":             "neondb",
    "user":                 "ngokhanhhuyy",
    "password":             "ABZktC6vh5UJ"            
}
databaseConfiguration = {
    "host":                 "localhost",
    "port":                 "5432",
    "database":             "NATSInternal",
    "user":                 "postgres",
    "password":             "f.t0rres"
}
localDatabaseURI =  f"postgresql://{databaseConfiguration['user']}:{databaseConfiguration['password']}" \
                                        f"@{databaseConfiguration['host']}:{databaseConfiguration['port']}/" \
                                        f"{databaseConfiguration['database']}"

# NeoTect
# databaseConfiguration["databaseURI"] = "postgresql://ngokhanhhuyy:ABZktC6vh5UJ@ep-wandering-hat-558903.ap-southeast-1.aws.neon.tech/neondb"
# Railway
railwayDatabaseURI= "postgresql://postgres:DMPu5pwzkSYbOFqKGPhf@containers-us-west-119.railway.app:7614/railway"
sqliteDatabaseURL = 'sqlite:///app/data/database.db'

configurations = {
    "debug":                True,
    "applicationName":      "NATSInternal",
    "secretKey":            "BackInBlackACDC",
    "databaseURI":          railwayDatabaseURI,
    "logging":              None,
    "catching":             None,
    "email":                None,
    "uploadFolder":         "./app/static/upload",
    "maxContentLength":     None,
    "timeZone":             "Asia/Ho_Chi_Minh"
}