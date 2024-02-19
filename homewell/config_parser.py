import configparser

config = configparser.ConfigParser()
config.read('conf.config')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY1 = config.get('Google', 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET1 = config.get('Google', 'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')