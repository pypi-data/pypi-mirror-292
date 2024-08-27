import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pytexttosql.sqlite import SQLiteEngine

engine = SQLiteEngine(db_name="signal")
engine.create_tables_from_csv('test/data/signal')
resp = engine.query("what is the average wifi by antenna type by device type?")
print(f'\n{resp.get('generative_result')}\n')