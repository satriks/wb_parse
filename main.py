from WB.WBParser import WBParser
from logging_config import setup_logging


setup_logging()

article  = 197986522
rate = 3
days = 3

WBParser = WBParser(article, rate ,days)
WBParser.run()