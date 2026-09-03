from dotenv import load_dotenv
import os

load_dotenv(r'C:/Users/Sávio/Desktop/simul_integrado/.env')
s = os.getenv('F_KEY')
assert s is not None
SECRET_KEY = s.encode('utf-8')
