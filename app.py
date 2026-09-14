"""Production entry point for the AI Blackjack Trainer.

WSGI servers (gunicorn, App Runner, Docker) import the module-level ``app``:

    gunicorn --bind 0.0.0.0:$PORT app:app

Running this file directly starts Flask's development server instead.
"""

import os

from simple_complete_app import app

__all__ = ["app", "main"]


def main():
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
