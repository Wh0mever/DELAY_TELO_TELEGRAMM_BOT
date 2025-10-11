import subprocess
import sys

# Запускаем test_certificate.py
result = subprocess.run([sys.executable, "test_certificate.py"], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("ERRORS:", result.stderr)
print("Return code:", result.returncode)

