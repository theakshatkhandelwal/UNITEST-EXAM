"""
Vercel serverless entrypoint.

All application code lives in `app.py`. This module just exposes the Flask
`app` instance so Vercel can route requests correctly.
"""

from app import app  # noqa: F401

