import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Collect static files
subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput', '--settings=config.settings'], check=False)

# Start gunicorn
subprocess.run([
    'gunicorn',
    'config.wsgi:application',
    '--bind', 'localhost:8000',
    '--workers', '2',
    '--timeout', '120',
    '--access-logfile', '-',
    '--error-logfile', '-',
    '--reload',
], check=True)
