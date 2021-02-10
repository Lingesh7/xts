import configparser

from Connect import XTSConnect

# logging.basicConfig(level=logging.DEBUG)

# ----------------------------------------------------------------------------------------------------------------------
# Interactive
# ----------------------------------------------------------------------------------------------------------------------
"""Get the configurations from config.ini file"""
cfg = configparser.ConfigParser()
cfg.read('config.ini')
source = cfg['user']['source']
"""Get the configurations from config.ini file"""
appKey = cfg.get('user', 'marketdata_appkey')
secretKey = cfg.get('user', 'marketdata_secretkey')

"""Make the XTSConnect Object with Marketdata API appKey, secretKey and source"""
xt = XTSConnect(appKey, secretKey, source)

"""Using the object we call the login function Request"""
response = xt.marketdata_login()
print("MarketData Login: ", response)



"""instruments list"""
instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': 2885}, {'exchangeSegment': 1, 'exchangeInstrumentID': 22}]



"""Send Subscription Request"""
response = xt.send_subscription(instruments, 1502)
print('Subscribe :', response)


