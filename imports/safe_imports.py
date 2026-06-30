import os
import importlib
from pathlib import Path


def configure_local_download_cache() -> None:
    cache_root = Path(__file__).resolve().parent / "llm_sdk/.cache"
    huggingface_cache_root = cache_root / "huggingface"
    torch_cache_root = cache_root / "torch"
    xdg_cache_root = cache_root / "xdg"
    transformers_cache_root = huggingface_cache_root / "transformers"
    hub_cache_root = huggingface_cache_root / "hub"

    for directory in (
        hub_cache_root,
        transformers_cache_root,
        torch_cache_root,
        xdg_cache_root,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    os.environ["HF_HOME"] = str(huggingface_cache_root)
    os.environ["HF_HUB_CACHE"] = str(hub_cache_root)
    os.environ["HUGGINGFACE_HUB_CACHE"] = str(hub_cache_root)
    os.environ["TRANSFORMERS_CACHE"] = str(transformers_cache_root)
    os.environ["TORCH_HOME"] = str(torch_cache_root)
    os.environ["XDG_CACHE_HOME"] = str(xdg_cache_root)


def get_llm() -> any:
    configure_local_download_cache()
    return importlib.import_module("llm_sdk").Small_LLM_Model
