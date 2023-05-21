import re

text = 'Binance Liquidated Long on BTCUSDT @ $4.33: Sell $162,720'
pattern = '([Ss]hort|[Ll]ong).+(BTCUSDT|BTCUSD|XBTUSDT|XBTUSD|XBTUSDT) @ \$(.+):.+\$(\S+)$'
search = re.findall(pattern, text)
print(search)