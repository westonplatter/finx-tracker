import environ


def gen_db_url():
    env = environ.Env()
    connection_dict = env.db("DATABASE_URL")
    db_url = (
        "postgresql://"
        + connection_dict["USER"]
        + ":"
        + connection_dict["PASSWORD"]
        + "@"
        + connection_dict["HOST"]
        + ":"
        + str(connection_dict["PORT"])
        + "/"
        + connection_dict["NAME"]
    )
    return db_url
