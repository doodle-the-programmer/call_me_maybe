UV_CACHE_DIR=.uv_cache python -m uv sync
python -m uv run call_me_maybe.py
python -m venv .venv (in llm_sdk/)

export HF_HOME="$HOME/sgoinfre/gpatrici/call_me_maybe/llm_sdk/.cache/huggingface"
export HF_HUB_CACHE="$HOME/sgoinfre/gpatrici/call_me_maybe/llm_sdk/.cache/huggingface/hub"
export TRANSFORMERS_CACHE="$HOME/sgoinfre/gpatrici/call_me_maybe/llm_sdk/.cache/huggingface/transformers"
export TORCH_HOME="$HOME/sgoinfre/gpatrici/call_me_maybe/llm_sdk/.cache/torch"
export XDG_CACHE_HOME="$HOME/sgoinfre/gpatrici/call_me_maybe/llm_sdk/.cache/xdg"
