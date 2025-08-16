"""
API service classes for external integrations
Handles TMDB, OMDB, and YouTube API interactions
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus
from config import Config

logger = logging.getLogger(__name__)

class TMDBService:
    """The Movie Database API service"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.TMDB_API_KEY
        self.base_url = "https://api.themoviedb.org/3"
        
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """Make request to TMDB API"""
        try:
            if params is None:
                params = {}
            
            params['api_key'] = self.api_key
            url = f"{self.base_url}/{endpoint}"
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDB API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"TMDB API error: {str(e)}")
            return None

    def search_movies(self, query: str) -> List[Dict]:
        """Search for movies"""
        try:
            data = self._make_request("search/movie", {"query": query})
            if data and 'results' in data:
                return data['results'][:10]  # Return top 10 results
            return []
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            return []

    def search_tv(self, query: str) -> List[Dict]:
        """Search for TV shows"""
        try:
            data = self._make_request("search/tv", {"query": query})
            if data and 'results' in data:
                return data['results'][:10]  # Return top 10 results
            return []
        except Exception as e:
            logger.error(f"Error searching TV shows: {str(e)}")
            return []

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed movie information"""
        try:
            return self._make_request(f"movie/{movie_id}")
        except Exception as e:
            logger.error(f"Error getting movie details: {str(e)}")
            return None

    def get_tv_details(self, tv_id: int) -> Optional[Dict]:
        """Get detailed TV show information"""
        try:
            return self._make_request(f"tv/{tv_id}")
        except Exception as e:
            logger.error(f"Error getting TV details: {str(e)}")
            return None

    def get_popular_movies(self) -> List[Dict]:
        """Get popular movies"""
        try:
            data = self._make_request("movie/popular")
            if data and 'results' in data:
                return data['results'][:10]
            return []
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            return []

    def get_popular_tv(self) -> List[Dict]:
        """Get popular TV shows"""
        try:
            data = self._make_request("tv/popular")
            if data and 'results' in data:
                return data['results'][:10]
            return []
        except Exception as e:
            logger.error(f"Error getting popular TV shows: {str(e)}")
            return []

    def get_trending(self) -> List[Dict]:
        """Get trending movies and TV shows"""
        try:
            data = self._make_request("trending/all/day")
            if data and 'results' in data:
                return data['results'][:10]
            return []
        except Exception as e:
            logger.error(f"Error getting trending content: {str(e)}")
            return []

    def get_similar_movies(self, movie_id: int) -> List[Dict]:
        """Get similar movies"""
        try:
            data = self._make_request(f"movie/{movie_id}/similar")
            if data and 'results' in data:
                return data['results'][:10]
            return []
        except Exception as e:
            logger.error(f"Error getting similar movies: {str(e)}")
            return []

    def get_similar_tv(self, tv_id: int) -> List[Dict]:
        """Get similar TV shows"""
        try:
            data = self._make_request(f"tv/{tv_id}/similar")
            if data and 'results' in data:
                return data['results'][:10]
            return []
        except Exception as e:
            logger.error(f"Error getting similar TV shows: {str(e)}")
            return []

    def get_movie_recommendations(self, movie_id: int) -> List[Dict]:
        """Get movie recommendations"""
        try:
            data = self._make_request(f"movie/{movie_id}/recommendations")
            if data and 'results' in data:
                return data['results'][:10]
            return []
        except Exception as e:
            logger.error(f"Error getting movie recommendations: {str(e)}")
            return []

    def get_tv_recommendations(self, tv_id: int) -> List[Dict]:
        """Get TV show recommendations"""
        try:
            data = self._make_request(f"tv/{tv_id}/recommendations")
            if data and 'results' in data:
                return data['results'][:10]
            return []
        except Exception as e:
            logger.error(f"Error getting TV recommendations: {str(e)}")
            return []

    def discover_movies(self, **kwargs) -> List[Dict]:
        """Discover movies with filters"""
        try:
            data = self._make_request("discover/movie", kwargs)
            if data and 'results' in data:
                return data['results'][:20]
            return []
        except Exception as e:
            logger.error(f"Error discovering movies: {str(e)}")
            return []

    def discover_tv(self, **kwargs) -> List[Dict]:
        """Discover TV shows with filters"""
        try:
            data = self._make_request("discover/tv", kwargs)
            if data and 'results' in data:
                return data['results'][:20]
            return []
        except Exception as e:
            logger.error(f"Error discovering TV shows: {str(e)}")
            return []


class OMDBService:
    """Open Movie Database API service"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.OMDB_API_KEY
        self.base_url = "https://www.omdbapi.com/"

    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict]:
        """Make request to OMDB API"""
        try:
            params['apikey'] = self.api_key
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if the response indicates an error
            if data.get('Response') == 'False':
                logger.warning(f"OMDB API error: {data.get('Error', 'Unknown error')}")
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OMDB API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"OMDB API error: {str(e)}")
            return None

    def get_movie_by_title(self, title: str, year: Optional[str] = None) -> Optional[Dict]:
        """Get movie details by title"""
        try:
            params = {'t': title, 'plot': 'full'}
            if year:
                params['y'] = year
            
            return self._make_request(params)
            
        except Exception as e:
            logger.error(f"Error getting movie by title: {str(e)}")
            return None

    def get_movie_by_imdb_id(self, imdb_id: str) -> Optional[Dict]:
        """Get movie details by IMDb ID"""
        try:
            params = {'i': imdb_id, 'plot': 'full'}
            return self._make_request(params)
            
        except Exception as e:
            logger.error(f"Error getting movie by IMDb ID: {str(e)}")
            return None

    def search_movies(self, query: str) -> List[Dict]:
        """Search for movies (returns list of results)"""
        try:
            params = {'s': query, 'type': 'movie'}
            data = self._make_request(params)
            
            if data and 'Search' in data:
                return data['Search']
            return []
            
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            return []


class YouTubeService:
    """YouTube Data API service for finding trailers"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make request to YouTube API"""
        try:
            params['key'] = self.api_key
            url = f"{self.base_url}/{endpoint}"
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"YouTube API error: {str(e)}")
            return None

    def search_trailer(self, title: str, content_type: str = 'movie') -> Optional[str]:
        """Search for movie/TV show trailer on YouTube"""
        try:
            # Create search query
            query = f"{title} {content_type} trailer official"
            
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': 5,
                'order': 'relevance',
                'videoDuration': 'medium'  # Prefer medium-length videos for trailers
            }
            
            data = self._make_request('search', params)
            
            if data and 'items' in data:
                for item in data['items']:
                    # Look for official trailers by checking title and channel
                    video_title = item['snippet']['title'].lower()
                    channel_title = item['snippet']['channelTitle'].lower()
                    
                    # Prefer official sources and trailer keywords
                    if any(keyword in video_title for keyword in ['trailer', 'official']):
                        video_id = item['id']['videoId']
                        return f"https://www.youtube.com/watch?v={video_id}"
                
                # If no official trailer found, return the first result
                if data['items']:
                    video_id = data['items'][0]['id']['videoId']
                    return f"https://www.youtube.com/watch?v={video_id}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching for trailer: {str(e)}")
            return None

    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """Get detailed information about a YouTube video"""
        try:
            params = {
                'part': 'snippet,statistics',
                'id': video_id
            }
            
            data = self._make_request('videos', params)
            
            if data and 'items' in data and data['items']:
                return data['items'][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            return None

    def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for videos on YouTube"""
        try:
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance'
            }
            
            data = self._make_request('search', params)
            
            if data and 'items' in data:
                return data['items']
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching videos: {str(e)}")
            return []
