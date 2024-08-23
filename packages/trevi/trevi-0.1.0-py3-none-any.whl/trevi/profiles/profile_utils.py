from trevi.profiles.app_config import AppConfig

class ProfileUtils:

    @staticmethod
    def app_config_from_profile_name(name: str) -> AppConfig:
        return AppConfig.load(f"profiles/{name}.yml")
