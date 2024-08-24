# bugster/config/base_config.py


class BaseConfig:
    VIDEO_PATH = "/tmp/tests/videos/"
    COOKIES_PATH = "/tmp/session_cookies.json"
    VIEWPORT = {"width": 1920, "height": 1080}
    USER_AGENT = "Chrome/69.0.3497.100 Safari/537.36"

    LOGIN_STRATEGY = None
    CREDENTIALS = {}

    @classmethod
    def get_browser_context_args(cls):
        return {
            "record_video_dir": cls.VIDEO_PATH,
            "viewport": cls.VIEWPORT,
            "storage_state": cls.COOKIES_PATH,
            "user_agent": cls.USER_AGENT,
        }
