# -*- coding: utf-8 -*-
import os
from decouple import config

MODELS_CACHE_DIR = config(
    "MODELS_CACHE_DIR",
    default=os.path.expanduser("~/.cache/py-llm-core/models"),
)

if not os.path.exists(MODELS_CACHE_DIR):
    os.makedirs(MODELS_CACHE_DIR)

#: Store models in the same directory to simplify purges
os.environ["TIKTOKEN_CACHE_DIR"] = MODELS_CACHE_DIR

MISTRAL_API_KEY = config("MISTRAL_API_KEY", default=None)
OPENAI_API_KEY = config("OPENAI_API_KEY", default=None)
