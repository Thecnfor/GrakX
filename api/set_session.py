class CookieProxy:
    def __getitem__(self, user_id):
        return _sessions[user_id]["cookies"]
