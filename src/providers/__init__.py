# Provider package for lyrics and cover APIs
from .base import LyricsProviderBase, SearchResult
from .tunehub import TuneHubProvider
from .lrcapi import LrcApiProvider
from ..config import Config


def get_provider(config: Config) -> LyricsProviderBase:
    """
    Factory function to create the appropriate provider based on configuration.
    
    Args:
        config: Application configuration
        
    Returns:
        A provider instance implementing LyricsProviderBase
    """
    provider_name = config.api_provider.lower()
    
    if provider_name == "lrcapi":
        return LrcApiProvider(config)
    else:
        # Default to TuneHub
        return TuneHubProvider(config)
