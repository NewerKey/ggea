import enum


class Environment(str, enum.Enum):
    PRODUCTION = "PROD"
    HEROKU_PRODUCTION = "HEROKU_PROD"
    DEVELOPMENT = "DEV"
    STAGING = "STAGE"
