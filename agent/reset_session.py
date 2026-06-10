def reset_session():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()