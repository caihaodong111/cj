# Data Source Audit

Date: 2026-05-03

## Local Verification Scope

- Backend system check passed: `conda run -n 2k python backend/manage.py check`
- Crawler CLI environment passed: `conda run -n 2k python main.py --help`
- Full local audit passed: `conda run -n 2k python backend/check_data_sources.py`

## Platforms Covered

- `xhs`
- `dy`
- `ks`
- `bili`
- `wb`
- `tieba`
- `zhihu`

## What Was Verified

- API routes respond correctly:
  - `/api/health`
  - `/api/config/platforms`
  - `/api/config/options`
  - `/api/crawler/status`
  - `/api/data/stats`
  - `/api/monitor/platform-sentiment-stats`
  - `/api/monitor/feed/sensitive`
  - `/api/monitor/feed/all`
  - `/api/login/qr/<platform>`
  - `/api/login/qr/<platform>/status`
- Invalid QR platform requests are rejected with `400`
- Platform config dictionaries are consistent:
  - aliases
  - names
  - feed config
  - URL field mapping
  - QR platform support
- Model field mappings exist for every platform
- Crawler module files exist for every platform

## Current Local Result

- Total checks: `50`
- Passed: `50`
- Failed: `0`

## Important Limitations

- This audit verifies local wiring, routes, and platform module integrity.
- It does not prove that every remote platform can complete a live crawl at this moment.
- QR-code login and live crawling still depend on:
  - current upstream website DOM structure
  - real browser behavior
  - manual scan / login state
  - network accessibility
  - platform anti-bot changes

## Douyin Notes

- Added safer Playwright `evaluate()` handling to reduce navigation-context crashes.
- Added more tolerant login-entry detection for QR login.
- Forced visible browser mode for Douyin QR login when headless would be unstable.

## Recommended Next Manual Checks

1. Start backend and frontend.
2. Trigger one QR login per platform from the UI.
3. Confirm QR image appears and status changes from `pending` to `success`.
4. Run one keyword search per platform.
5. Confirm at least one record lands in storage and feed APIs.
