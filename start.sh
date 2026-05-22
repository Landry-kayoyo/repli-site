#!/bin/bash
# Start Django backend in background
cd backend
python3 manage.py collectstatic --noinput --settings=config.settings 2>/dev/null || true
python3 manage.py runserver localhost:8000 --settings=config.settings &
cd ..
# Start Next.js frontend on port 5000
cd frontend
npm run dev
