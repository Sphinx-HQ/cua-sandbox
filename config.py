import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
env.read_env()


BITWARDEN_CLIENT_ID = env.str("BITWARDEN_CLIENT_ID")
BITWARDEN_CLIENT_SECRET = env.str("BITWARDEN_CLIENT_SECRET")
BITWARDEN_MASTER_PASSWORD = env.str("BITWARDEN_MASTER_PASSWORD")
