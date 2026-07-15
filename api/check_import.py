"""Quick import check."""
import sys
sys.path.insert(0, '.')
print('hello')
from app.services.exercise_runner import run_code
print('imported ok')