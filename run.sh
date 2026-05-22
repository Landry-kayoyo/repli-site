#!/bin/bash
# Start Django backend on port 8000 (background)
(cd backend && python3 manage.py runserver localhost:8000 --settings=config.settings 2>&1 | sed 's/^/[Django] /') &
DJANGO_PID=$!

# Start Next.js frontend on port 5000
(cd frontend && npm run dev 2>&1 | sed 's/^/[Next.js] /')

wait $DJANGO_PID
