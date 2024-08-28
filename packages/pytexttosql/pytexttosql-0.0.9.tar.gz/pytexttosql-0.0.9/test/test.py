import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pytexttosql.sqlite import SQLiteEngine

engine = SQLiteEngine(db_name="signal")
engine.create_tables_from_csv('test/data/signal')
resp = engine.query("What is the average signal strength recorded?", include_recommendations_in_generation=True)

# out of domain test
# resp = engine.query("what is a hotdog?")

# print(f'\n{resp.get('generative_result')}\n')
print(json.dumps(resp, indent=4))