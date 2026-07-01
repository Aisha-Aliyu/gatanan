"""Application configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Qwen Cloud connection (Singapore / International) ---
    # The OpenAI-compatible endpoint, called with the same key everywhere.
    dashscope_api_key: str
    dashscope_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    # --- Text models (one key calls all of them) ---
    text_model: str = "qwen3.7-plus"        # balanced workhorse for the agents
    reasoning_model: str = "qwen3.7-max"    # reserved for the critic / hard reasoning
    fast_model: str = "qwen3.6-flash"       # cheapest; used to conserve credits

    # --- Image generation (confirm model IDs on https://www.qwencloud.com/models) ---
    image_model: str = "qwen-image-plus"    # pure text-to-image
    image_size: str = "1664*928"            # 16:9 cinematic frame
    image_seed: int = 42                    # fixed seed aids look stability; reruns reuse, not re-bill

    # --- Film-wide art direction, injected into every image and video prompt. ---
    # This single knob sets the whole film's aesthetic.
    art_direction: str = (
        "Stylized 3D animated film in the polished look of a modern animation studio. "
        "Warm, expressive, characterful, family-friendly. Soft cinematic lighting, "
        "rich color, gentle depth of field. Not photorealistic, not horror, not scary."
    )

        # Voice cloning (CosyVoice on Qwen Cloud)
    clone_model: str = "cosyvoice-v3-plus"
    clone_prefix: str = "gizo"   # lowercase letters/digits only, under 10 characters

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instantiating here means the app fails loudly at startup if the key is missing,
# instead of failing deep inside a request later.
settings = Settings()
