"""
Tests for STRM file support functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.config import Config
from src.scanner import MusicScanner, MusicFile


class TestMusicFileStrm:
    """Test MusicFile dataclass with is_strm field."""
    
    def test_is_strm_default_false(self):
        """Test that is_strm defaults to False for regular music files."""
        music = MusicFile(
            path=Path("/music/album/song.mp3"),
            artist="Artist",
            title="Song",
            album="Album",
        )
        assert music.is_strm is False
    
    def test_is_strm_true(self):
        """Test that is_strm can be set to True for STRM files."""
        music = MusicFile(
            path=Path("/music/album/song.strm"),
            artist="Artist",
            title="Song",
            album="Album",
            is_strm=True,
        )
        assert music.is_strm is True
    
    def test_strm_lyrics_path(self):
        """Test that STRM files generate correct lyrics path."""
        music = MusicFile(
            path=Path("/music/Artist/Album/song.strm"),
            artist="Artist",
            title="Song",
            album="Album",
            is_strm=True,
        )
        assert music.lyrics_path == Path("/music/Artist/Album/song.lrc")
    
    def test_strm_cover_path(self):
        """Test that STRM files generate correct cover path."""
        music = MusicFile(
            path=Path("/music/Artist/Album/song.strm"),
            artist="Artist",
            title="Song",
            album="Album",
            is_strm=True,
        )
        assert music.cover_path == Path("/music/Artist/Album/cover.jpg")


class TestMusicScannerStrm:
    """Test MusicScanner STRM file handling."""
    
    def test_is_strm_file_true(self, tmp_path):
        """Test _is_strm_file returns True for .strm files."""
        config = Config(music_path=str(tmp_path))
        scanner = MusicScanner(config)
        
        strm_file = tmp_path / "song.strm"
        assert scanner._is_strm_file(strm_file) is True
    
    def test_is_strm_file_false(self, tmp_path):
        """Test _is_strm_file returns False for non-STRM files."""
        config = Config(music_path=str(tmp_path))
        scanner = MusicScanner(config)
        
        mp3_file = tmp_path / "song.mp3"
        assert scanner._is_strm_file(mp3_file) is False
    
    def test_is_strm_file_case_insensitive(self, tmp_path):
        """Test _is_strm_file is case-insensitive."""
        config = Config(music_path=str(tmp_path))
        scanner = MusicScanner(config)
        
        strm_upper = tmp_path / "song.STRM"
        strm_mixed = tmp_path / "song.Strm"
        
        assert scanner._is_strm_file(strm_upper) is True
        assert scanner._is_strm_file(strm_mixed) is True
    
    def test_strm_in_audio_extensions(self):
        """Test that .strm is included in audio_extensions."""
        config = Config()
        assert ".strm" in config.audio_extensions
    
    def test_parse_strm_file_basic(self, tmp_path):
        """Test parsing a STRM file extracts title from filename."""
        config = Config(music_path=str(tmp_path), use_folder_structure=False)
        scanner = MusicScanner(config)
        
        # Create STRM file
        strm_file = tmp_path / "晴天.strm"
        strm_file.write_text("https://example.com/audio.mp3")
        
        result = scanner._parse_strm_file(strm_file)
        
        assert result is not None
        assert result.title == "晴天"
        assert result.is_strm is True
    
    def test_parse_strm_file_folder_structure(self, tmp_path):
        """Test STRM file uses folder structure for artist/album."""
        # Create folder structure: Artist/Album/song.strm
        artist_dir = tmp_path / "周杰伦"
        album_dir = artist_dir / "叶惠美"
        album_dir.mkdir(parents=True)
        
        strm_file = album_dir / "晴天.strm"
        strm_file.write_text("https://example.com/audio.mp3")
        
        config = Config(music_path=str(tmp_path), use_folder_structure=True)
        scanner = MusicScanner(config)
        
        result = scanner._parse_strm_file(strm_file)
        
        assert result is not None
        assert result.artist == "周杰伦"
        assert result.album == "叶惠美"
        assert result.title == "晴天"
        assert result.is_strm is True
    
    def test_parse_strm_file_shallow_structure(self, tmp_path):
        """Test STRM file with shallow structure: Artist/song.strm."""
        # Create folder structure: Artist/song.strm
        artist_dir = tmp_path / "周杰伦"
        artist_dir.mkdir(parents=True)
        
        strm_file = artist_dir / "晴天.strm"
        strm_file.write_text("https://example.com/audio.mp3")
        
        config = Config(music_path=str(tmp_path), use_folder_structure=True)
        scanner = MusicScanner(config)
        
        result = scanner._parse_strm_file(strm_file)
        
        assert result is not None
        assert result.artist == "周杰伦"
        assert result.album == ""  # No album in shallow structure
        assert result.title == "晴天"
        assert result.is_strm is True
    
    def test_parse_strm_file_default_artist(self, tmp_path):
        """Test STRM file uses default_artist when folder inference fails."""
        config = Config(
            music_path=str(tmp_path),
            use_folder_structure=False,
            default_artist="未知歌手"
        )
        scanner = MusicScanner(config)
        
        strm_file = tmp_path / "晴天.strm"
        strm_file.write_text("https://example.com/audio.mp3")
        
        result = scanner._parse_strm_file(strm_file)
        
        assert result is not None
        assert result.artist == "未知歌手"
        assert result.is_strm is True
    
    def test_scan_finds_strm_files(self, tmp_path):
        """Test that scan() finds and processes STRM files."""
        # Create folder structure with STRM file
        artist_dir = tmp_path / "周杰伦"
        album_dir = artist_dir / "叶惠美"
        album_dir.mkdir(parents=True)
        
        strm_file = album_dir / "晴天.strm"
        strm_file.write_text("https://example.com/audio.mp3")
        
        config = Config(music_path=str(tmp_path), use_folder_structure=True)
        scanner = MusicScanner(config)
        
        results = list(scanner.scan())
        
        assert len(results) == 1
        assert results[0].is_strm is True
        assert results[0].title == "晴天"


class TestStrmEmbedSkip:
    """Test that embedding is skipped for STRM files."""
    
    def test_strm_file_skip_embed_check(self):
        """Test that STRM files have is_strm=True for skip logic."""
        music = MusicFile(
            path=Path("/music/Artist/Album/song.strm"),
            artist="Artist",
            title="Song",
            album="Album",
            is_strm=True,
        )
        
        # In main.py, embedding is skipped when is_strm is True
        # This test verifies the flag is correctly set
        assert music.is_strm is True
        
        # Verify the skip logic condition
        needs_update = True
        should_skip = music.is_strm
        should_embed = needs_update and not should_skip
        
        assert should_embed is False
