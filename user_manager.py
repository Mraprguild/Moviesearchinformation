"""
User management system for tracking user preferences and interactions
Handles user data persistence and activity tracking
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class UserManager:
    """Manages user data and preferences for personalized recommendations"""
    
    def __init__(self):
        self.data_file = 'data/users.json'
        self.users_data = self._load_users_data()
        
    def _load_users_data(self) -> Dict[str, Any]:
        """Load users data from JSON file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create empty users data file
                empty_data = {}
                self._save_users_data(empty_data)
                return empty_data
                
        except Exception as e:
            logger.error(f"Error loading users data: {str(e)}")
            return {}

    def _save_users_data(self, data: Optional[Dict[str, Any]] = None):
        """Save users data to JSON file"""
        try:
            if data is None:
                data = self.users_data
                
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving users data: {str(e)}")

    def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data by user ID"""
        try:
            user_key = str(user_id)
            return self.users_data.get(user_key)
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None

    def create_or_update_user(self, user_id: int, username: str = '', first_name: str = '') -> Dict[str, Any]:
        """Create new user or update existing user"""
        try:
            user_key = str(user_id)
            current_time = datetime.now().isoformat()
            
            if user_key not in self.users_data:
                # Create new user
                self.users_data[user_key] = {
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'first_seen': current_time,
                    'last_active': current_time,
                    'search_history': [],
                    'interactions': [],
                    'preferences': {
                        'genres': {},
                        'actors': {},
                        'directors': {},
                        'content_types': {'movie': 0, 'tv': 0}
                    },
                    'favorites': [],
                    'watchlist': [],
                    'ratings': {},
                    'stats': {
                        'total_searches': 0,
                        'total_interactions': 0,
                        'movies_viewed': 0,
                        'tv_shows_viewed': 0
                    }
                }
                logger.info(f"Created new user: {user_id}")
            else:
                # Update existing user
                self.users_data[user_key]['username'] = username
                self.users_data[user_key]['first_name'] = first_name
                self.users_data[user_key]['last_active'] = current_time
            
            self._save_users_data()
            return self.users_data[user_key]
            
        except Exception as e:
            logger.error(f"Error creating/updating user: {str(e)}")
            return {}

    def update_user_activity(self, user_id: int, username: str = '', first_name: str = ''):
        """Update user's last activity timestamp"""
        try:
            user_data = self.create_or_update_user(user_id, username, first_name)
            return user_data
        except Exception as e:
            logger.error(f"Error updating user activity: {str(e)}")

    def track_search(self, user_id: int, query: str, content_type: str):
        """Track user search query"""
        try:
            user_key = str(user_id)
            if user_key not in self.users_data:
                self.create_or_update_user(user_id)
            
            search_entry = {
                'query': query,
                'content_type': content_type,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to search history (keep last 50 searches)
            self.users_data[user_key]['search_history'].append(search_entry)
            if len(self.users_data[user_key]['search_history']) > 50:
                self.users_data[user_key]['search_history'] = self.users_data[user_key]['search_history'][-50:]
            
            # Update stats
            self.users_data[user_key]['stats']['total_searches'] += 1
            self.users_data[user_key]['preferences']['content_types'][content_type] += 1
            
            self._save_users_data()
            logger.info(f"Tracked search for user {user_id}: {query} ({content_type})")
            
        except Exception as e:
            logger.error(f"Error tracking search: {str(e)}")

    def track_interaction(self, user_id: int, content_id: int, content_type: str, action: str = 'view'):
        """Track user interaction with content"""
        try:
            user_key = str(user_id)
            if user_key not in self.users_data:
                self.create_or_update_user(user_id)
            
            interaction_entry = {
                'content_id': content_id,
                'content_type': content_type,
                'action': action,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to interactions history (keep last 100 interactions)
            self.users_data[user_key]['interactions'].append(interaction_entry)
            if len(self.users_data[user_key]['interactions']) > 100:
                self.users_data[user_key]['interactions'] = self.users_data[user_key]['interactions'][-100:]
            
            # Update stats
            self.users_data[user_key]['stats']['total_interactions'] += 1
            if content_type == 'movie':
                self.users_data[user_key]['stats']['movies_viewed'] += 1
            elif content_type == 'tv':
                self.users_data[user_key]['stats']['tv_shows_viewed'] += 1
            
            self._save_users_data()
            logger.info(f"Tracked interaction for user {user_id}: {content_id} ({content_type}, {action})")
            
        except Exception as e:
            logger.error(f"Error tracking interaction: {str(e)}")

    def update_user_preferences(self, user_id: int, content_data: Dict[str, Any]):
        """Update user preferences based on content interaction"""
        try:
            user_key = str(user_id)
            if user_key not in self.users_data:
                self.create_or_update_user(user_id)
            
            preferences = self.users_data[user_key]['preferences']
            
            # Update genre preferences
            if 'genres' in content_data:
                for genre in content_data['genres']:
                    genre_name = genre.get('name') if isinstance(genre, dict) else str(genre)
                    if genre_name:
                        preferences['genres'][genre_name] = preferences['genres'].get(genre_name, 0) + 1
            
            # Update actor preferences (if available)
            if 'cast' in content_data:
                for cast_member in content_data['cast'][:5]:  # Top 5 cast members
                    actor_name = cast_member.get('name')
                    if actor_name:
                        preferences['actors'][actor_name] = preferences['actors'].get(actor_name, 0) + 1
            
            # Update director preferences (if available)
            if 'crew' in content_data:
                for crew_member in content_data['crew']:
                    if crew_member.get('job') == 'Director':
                        director_name = crew_member.get('name')
                        if director_name:
                            preferences['directors'][director_name] = preferences['directors'].get(director_name, 0) + 1
            
            self._save_users_data()
            logger.info(f"Updated preferences for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")

    def get_user_preferred_genres(self, user_id: int, limit: int = 5) -> List[str]:
        """Get user's most preferred genres"""
        try:
            user_data = self.get_user_data(user_id)
            if not user_data:
                return []
            
            genres = user_data.get('preferences', {}).get('genres', {})
            # Sort by count and return top genres
            sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
            return [genre[0] for genre in sorted_genres[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting preferred genres: {str(e)}")
            return []

    def get_user_content_type_preference(self, user_id: int) -> str:
        """Get user's preferred content type (movie or tv)"""
        try:
            user_data = self.get_user_data(user_id)
            if not user_data:
                return 'movie'  # Default preference
            
            content_types = user_data.get('preferences', {}).get('content_types', {'movie': 0, 'tv': 0})
            
            if content_types['movie'] >= content_types['tv']:
                return 'movie'
            else:
                return 'tv'
                
        except Exception as e:
            logger.error(f"Error getting content type preference: {str(e)}")
            return 'movie'

    def get_user_interaction_history(self, user_id: int, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's interaction history, optionally filtered by content type"""
        try:
            user_data = self.get_user_data(user_id)
            if not user_data:
                return []
            
            interactions = user_data.get('interactions', [])
            
            if content_type:
                interactions = [i for i in interactions if i.get('content_type') == content_type]
            
            return interactions
            
        except Exception as e:
            logger.error(f"Error getting interaction history: {str(e)}")
            return []

    def get_user_search_keywords(self, user_id: int, limit: int = 10) -> List[str]:
        """Get user's most common search keywords"""
        try:
            user_data = self.get_user_data(user_id)
            if not user_data:
                return []
            
            search_history = user_data.get('search_history', [])
            
            # Extract keywords from search queries
            all_keywords = []
            for search in search_history:
                query = search.get('query', '').lower()
                # Split by common separators and filter out short words
                keywords = [word.strip() for word in query.split() if len(word.strip()) > 2]
                all_keywords.extend(keywords)
            
            # Count keywords and return most common
            keyword_counts = Counter(all_keywords)
            return [keyword for keyword, count in keyword_counts.most_common(limit)]
            
        except Exception as e:
            logger.error(f"Error getting search keywords: {str(e)}")
            return []

    def add_to_favorites(self, user_id: int, content_id: int, content_type: str):
        """Add content to user's favorites"""
        try:
            user_key = str(user_id)
            if user_key not in self.users_data:
                self.create_or_update_user(user_id)
            
            favorite_item = {
                'content_id': content_id,
                'content_type': content_type,
                'added_date': datetime.now().isoformat()
            }
            
            favorites = self.users_data[user_key]['favorites']
            
            # Check if already in favorites
            if not any(f['content_id'] == content_id and f['content_type'] == content_type for f in favorites):
                favorites.append(favorite_item)
                self._save_users_data()
                logger.info(f"Added to favorites for user {user_id}: {content_id} ({content_type})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding to favorites: {str(e)}")
            return False

    def get_user_favorites(self, user_id: int, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's favorite content"""
        try:
            user_data = self.get_user_data(user_id)
            if not user_data:
                return []
            
            favorites = user_data.get('favorites', [])
            
            if content_type:
                favorites = [f for f in favorites if f.get('content_type') == content_type]
            
            return favorites
            
        except Exception as e:
            logger.error(f"Error getting favorites: {str(e)}")
            return []

    def get_all_users(self) -> Dict[str, Any]:
        """Get all users data (for admin/stats purposes)"""
        return self.users_data

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            user_data = self.get_user_data(user_id)
            if not user_data:
                return {}
            
            stats = user_data.get('stats', {})
            preferences = user_data.get('preferences', {})
            
            # Calculate additional stats
            top_genres = self.get_user_preferred_genres(user_id, 3)
            preferred_type = self.get_user_content_type_preference(user_id)
            
            return {
                'total_searches': stats.get('total_searches', 0),
                'total_interactions': stats.get('total_interactions', 0),
                'movies_viewed': stats.get('movies_viewed', 0),
                'tv_shows_viewed': stats.get('tv_shows_viewed', 0),
                'top_genres': top_genres,
                'preferred_content_type': preferred_type,
                'favorites_count': len(user_data.get('favorites', [])),
                'member_since': user_data.get('first_seen', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {}

    def cleanup_old_data(self, days_old: int = 90):
        """Clean up old user data (searches, interactions older than specified days)"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            for user_key in self.users_data:
                user_data = self.users_data[user_key]
                
                # Clean old search history
                search_history = user_data.get('search_history', [])
                user_data['search_history'] = [
                    search for search in search_history
                    if datetime.fromisoformat(search['timestamp']).timestamp() > cutoff_date
                ]
                
                # Clean old interactions
                interactions = user_data.get('interactions', [])
                user_data['interactions'] = [
                    interaction for interaction in interactions
                    if datetime.fromisoformat(interaction['timestamp']).timestamp() > cutoff_date
                ]
            
            self._save_users_data()
            logger.info(f"Cleaned up user data older than {days_old} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
