import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pytexttosql.sqlite import SQLiteEngine

engine = SQLiteEngine(db_name="test")
engine.create_tables_from_csv('test')
resp = engine.query("how many harry styles songs?")
print(resp)
print(resp.get('generative_result'))