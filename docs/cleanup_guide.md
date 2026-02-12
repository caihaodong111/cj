# Project Cleanup Guide

This guide explains what you can delete safely, and what you should keep if you
want full crawler functionality.

## Safe to delete (will be regenerated)
- __pycache__/ and *.pyc
  - Python bytecode caches. They are recreated on next run.
- frontend/node_modules/
  - Frontend dependencies. Reinstall with `npm install`.
- frontend/dist/, frontend/.vite/
  - Vite build output and dev cache. Rebuilt by `npm run build` or `npm run dev`.
- backend/logs/
  - Django log files. They are recreated on next run.
- browser_data/
  - Browser profile/cache for crawling. Remove if you do not need stored sessions.

## Optional to delete (you will lose data or local settings)
- data/
  - Crawler output files (json/csv/xlsx). Deleting removes all collected data.
- .idea/
  - Local IDE settings.
- .claude/
  - Local assistant metadata (if not needed).
- .env
  - Local environment config. Only delete if you have another copy.

## Required for full crawler functionality
Do NOT delete these if you want crawling to work:
- backend/crawler/main.py
- backend/crawler/base/, backend/crawler/media_platform/, backend/crawler/store/
- backend/crawler/config/, backend/crawler/cmd_arg/, backend/crawler/tools/
- backend/crawler/model/, backend/crawler/proxy/, backend/crawler/database/
- backend/crawler/constant/, backend/crawler/libs/
- backend/crawler/var.py, backend/requirements.txt

## Required for Django backend + frontend UI
- backend/
- frontend/

## Minimal cleanup command examples
Run from the project root:

```bash
find . -name "__pycache__" -type d -prune -exec rm -rf {} +
find . -name "*.pyc" -delete
rm -rf backend/logs browser_data
rm -rf frontend/node_modules frontend/dist frontend/.vite
```
