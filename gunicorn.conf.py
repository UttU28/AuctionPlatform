import os
import multiprocessing

max_requests = 1000
max_requests_jitter = 50

bind = f"0.0.0.0:{os.environ.get('PORT', 50505)}"

workers = (multiprocessing.cpu_count() * 2) + 1
threads = workers

timeout = 120

# Logging configuration
accesslog = '-'  # Standard output for access logs
errorlog = '-'   # Standard output for error logs
loglevel = 'info'  # Set to 'debug' for more detailed logging
