from __future__ import annotations

def doctor_check() -> None:
    try:
        import rich  # noqa
        import playwright  # noqa
    except Exception:
        print('''
[!] Missing deps. Run:
    pip install -r requirements.txt
    python -m playwright install chromium
'''.strip())
        raise
    print('✅ Doctor OK')
