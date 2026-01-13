# Abstract base class for lyrics providers
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchResult:
    """A single search result from lyrics API.
    
    This is a unified result structure used by all providers.
    """
    id: str
    name: str
    artist: str
    album: str
    platform: str
    lrc_url: str
    pic_url: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "SearchResult":
        """Create SearchResult from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            artist=data.get("artist", ""),
            album=data.get("album", ""),
            platform=data.get("platform", ""),
            lrc_url=data.get("lrc", ""),
            pic_url=data.get("pic", ""),
        )


class LyricsProviderBase(ABC):
    """Abstract base class for lyrics providers.
    
    All lyrics API providers must implement this interface.
    """
    
    @abstractmethod
    def search(self, artist: str, title: str, album: str = "") -> list[SearchResult]:
        """
        Search for a song.
        
        Args:
            artist: Artist name
            title: Song title
            album: Album name (optional)
            
        Returns:
            List of matching results
        """
        pass
    
    @abstractmethod
    def get_lyrics(self, result: SearchResult) -> Optional[str]:
        """
        Fetch lyrics content for a search result.
        
        Args:
            result: Search result to fetch lyrics for
            
        Returns:
            LRC format lyrics string or None if not found
        """
        pass
    
    @abstractmethod
    def get_cover(self, result: SearchResult) -> Optional[bytes]:
        """
        Fetch album cover image for a search result.
        
        Args:
            result: Search result to fetch cover for
            
        Returns:
            Image bytes or None if not found
        """
        pass
    
    @abstractmethod
    def find_best_match(
        self,
        results: list[SearchResult],
        artist: str,
        title: str
    ) -> Optional[SearchResult]:
        """
        Find the best matching result from search results.
        
        Args:
            results: List of search results
            artist: Expected artist name
            title: Expected song title
            
        Returns:
            Best matching result or None
        """
        pass
    
    @abstractmethod
    def close(self):
        """Close any open connections."""
        pass
