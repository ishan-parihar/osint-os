"""
Compatibility shim for ScrapeGraphAI to work with new langchain structure.
"""

import sys
from typing import Any, Callable, Optional

# Import the modules we need to create shims for
import langchain_core.prompts
import langchain_core.output_parsers
import langchain_core.language_models.chat_models
import langchain_community.chat_models

# Import the actual init_chat_model function
_init_chat_model: Optional[Callable[..., Any]]
try:
    from langchain.chat_models import init_chat_model
    _init_chat_model = init_chat_model
except ImportError:
    _init_chat_model = None

class LangchainPrompts:
    """Compatibility shim for langchain.prompts"""
    def __getattr__(self, name: str) -> Any:
        return getattr(langchain_core.prompts, name)

class LangchainOutputParsers:
    """Compatibility shim for langchain.output_parsers"""
    def __getattr__(self, name: str) -> Any:
        return getattr(langchain_core.output_parsers, name)

class LangchainChatModels:
    """Compatibility shim for langchain_core.chat_models"""
    def __getattr__(self, name: str) -> Any:
        if name == 'init_chat_model' and _init_chat_model is not None:
            return _init_chat_model
        # Redirect to the correct import path
        return getattr(langchain_core.language_models.chat_models, name)

class LangchainCommunityChatModels:
    """Compatibility shim for langchain.chat_models (redirects to community)"""
    def __getattr__(self, name: str) -> Any:
        return getattr(langchain_community.chat_models, name)

# Install the compatibility shims
sys.modules['langchain.prompts'] = LangchainPrompts()  # type: ignore[assignment]
sys.modules['langchain.output_parsers'] = LangchainOutputParsers()  # type: ignore[assignment]
sys.modules['langchain_core.chat_models'] = LangchainChatModels()  # type: ignore[assignment]
sys.modules['langchain.chat_models'] = LangchainCommunityChatModels()  # type: ignore[assignment]