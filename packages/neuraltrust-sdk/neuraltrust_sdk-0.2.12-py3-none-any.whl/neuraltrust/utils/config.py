import yaml
import os

CONFIG_FILE_NAME = "config.yml"


class ConfigHelper:
    @staticmethod
    def load_config():
        try:
            with open(CONFIG_FILE_NAME, "r") as file:
                config = yaml.safe_load(file)

            if config is None:
                config = {}
            return config
        except:
            return {}

    @staticmethod
    def load_config_field(field: str):
        try:
            config = ConfigHelper.load_config()
            return config[field]
        except Exception as e:
            return None

    @staticmethod
    def load_openai_api_key():
        return ConfigHelper.load_config_field("openai_api_key") or os.getenv("OPENAI_API_KEY")

    @staticmethod
    def load_neuraltrust_api_key():
        return ConfigHelper.load_config_field("neuraltrust_api_key") or os.getenv("NEURALTRUST_API_KEY")

    @staticmethod
    def load_llm_judge_model():
        return ConfigHelper.load_config_field("llm_judge_model") or os.getenv("LLM_JUDGE_MODEL") or "gpt-4o-mini"

    @staticmethod
    def load_llm_target_model():
        return ConfigHelper.load_config_field("llm_target_model") or os.getenv("LLM_TARGET_MODEL")

    @staticmethod
    def load_llm_provider():
        return ConfigHelper.load_config_field("llm_provider") or os.getenv("LLM_PROVIDER") or "openai"

    @staticmethod
    def save_config(config_data):
        with open(CONFIG_FILE_NAME, "w") as file:
            yaml.dump(config_data, file)

    @staticmethod
    def is_set():
        try:
            with open(CONFIG_FILE_NAME, "r") as file:
                config = yaml.safe_load(file)

            if config is None or config == {}:
                return False
            else:
                return True
        except:
            return False
