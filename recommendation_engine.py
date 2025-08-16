"""
Recommendation engine for personalized movie and TV show suggestions
Uses collaborative filtering and content-based filtering techniques
"""

import logging
from typing import Dict, List, Optional, Any
from collections import Counter, defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Advanced recommendation system for movies and TV shows"""
    
    def __init__(self, tmdb_service, user_manager):
        self.tmdb = tmdb_service
        self.user_manager = user_manager
        
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user"""
        try:
            user_data = self.user_manager.get_user_data(user_id)
            if not user_data:
                # Return trending content for new users
                return self._get_fallback_recommendations()
            
            # Combine multiple recommendation strategies
            recommendations = []
            
            # 1. Genre-based recommendations
            genre_recs = self._get_genre_based_recommendations(user_id)
            recommendations.extend(genre_recs)
            
            # 2. Similar content recommendations
            similar_recs = self._get_similar_content_recommendations(user_id)
            recommendations.extend(similar_recs)
            
            # 3. Popular content in user's preferred genres
            popular_genre_recs = self._get_popular_in_genres(user_id)
            recommendations.extend(popular_genre_recs)
            
            # 4. Trending content that matches user preferences
            trending_recs = self._get_filtered_trending(user_id)
            recommendations.extend(trending_recs)
            
            # Remove duplicates and score recommendations
            unique_recommendations = self._deduplicate_and_score(recommendations, user_id)
            
            # Sort by recommendation score and return top results
            sorted_recs = sorted(unique_recommendations, key=lambda x: x.get('recommendation_score', 0), reverse=True)
            
            return sorted_recs[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return self._get_fallback_recommendations()

    def _get_genre_based_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get recommendations based on user's favorite genres"""
        try:
            preferred_genres = self.user_manager.get_user_preferred_genres(user_id, 3)
            if not preferred_genres:
                return []
            
            recommendations = []
            preferred_type = self.user_manager.get_user_content_type_preference(user_id)
            
            # Get genre IDs mapping
            genre_mapping = self._get_genre_mapping()
            genre_ids = []
            
            for genre_name in preferred_genres:
                if genre_name in genre_mapping:
                    genre_ids.append(str(genre_mapping[genre_name]))
            
            if not genre_ids:
                return []
            
            # Discover content in preferred genres
            if preferred_type == 'movie':
                content = self.tmdb.discover_movies(
                    with_genres='|'.join(genre_ids),
                    sort_by='vote_average.desc',
                    vote_count_gte=100
                )
            else:
                content = self.tmdb.discover_tv(
                    with_genres='|'.join(genre_ids),
                    sort_by='vote_average.desc',
                    vote_count_gte=50
                )
            
            # Add recommendation source and score
            for item in content[:5]:
                item['recommendation_source'] = 'genre_based'
                item['recommendation_score'] = 0.8
                recommendations.append(item)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting genre-based recommendations: {str(e)}")
            return []

    def _get_similar_content_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get recommendations based on content user has interacted with"""
        try:
            interactions = self.user_manager.get_user_interaction_history(user_id)
            if not interactions:
                return []
            
            recommendations = []
            
            # Get recent interactions (last 10)
            recent_interactions = interactions[-10:]
            
            for interaction in recent_interactions:
                content_id = interaction['content_id']
                content_type = interaction['content_type']
                
                # Get similar content
                if content_type == 'movie':
                    similar_items = self.tmdb.get_similar_movies(content_id)
                    # Also get movie recommendations
                    rec_items = self.tmdb.get_movie_recommendations(content_id)
                    similar_items.extend(rec_items)
                else:
                    similar_items = self.tmdb.get_similar_tv(content_id)
                    # Also get TV recommendations
                    rec_items = self.tmdb.get_tv_recommendations(content_id)
                    similar_items.extend(rec_items)
                
                # Add recommendation source and score
                for item in similar_items[:3]:
                    item['recommendation_source'] = 'similar_content'
                    item['recommendation_score'] = 0.7
                    recommendations.append(item)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting similar content recommendations: {str(e)}")
            return []

    def _get_popular_in_genres(self, user_id: int) -> List[Dict[str, Any]]:
        """Get popular content in user's preferred genres"""
        try:
            preferred_genres = self.user_manager.get_user_preferred_genres(user_id, 2)
            if not preferred_genres:
                return []
            
            recommendations = []
            
            # Get popular movies and TV shows
            popular_movies = self.tmdb.get_popular_movies()
            popular_tv = self.tmdb.get_popular_tv()
            
            # Filter by preferred genres
            for movie in popular_movies:
                if self._content_matches_genres(movie, preferred_genres):
                    movie['recommendation_source'] = 'popular_genre'
                    movie['recommendation_score'] = 0.6
                    recommendations.append(movie)
            
            for tv in popular_tv:
                if self._content_matches_genres(tv, preferred_genres):
                    tv['recommendation_source'] = 'popular_genre'
                    tv['recommendation_score'] = 0.6
                    recommendations.append(tv)
            
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"Error getting popular genre recommendations: {str(e)}")
            return []

    def _get_filtered_trending(self, user_id: int) -> List[Dict[str, Any]]:
        """Get trending content filtered by user preferences"""
        try:
            trending = self.tmdb.get_trending()
            if not trending:
                return []
            
            preferred_genres = self.user_manager.get_user_preferred_genres(user_id, 5)
            recommendations = []
            
            for item in trending:
                # Add some weight to trending content that matches user preferences
                base_score = 0.4
                if self._content_matches_genres(item, preferred_genres):
                    base_score = 0.5
                
                item['recommendation_source'] = 'trending'
                item['recommendation_score'] = base_score
                recommendations.append(item)
            
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"Error getting filtered trending: {str(e)}")
            return []

    def _get_fallback_recommendations(self) -> List[Dict[str, Any]]:
        """Get fallback recommendations for users without history"""
        try:
            recommendations = []
            
            # Get trending content
            trending = self.tmdb.get_trending()
            for item in trending[:5]:
                item['recommendation_source'] = 'trending_fallback'
                item['recommendation_score'] = 0.3
                recommendations.append(item)
            
            # Get popular movies
            popular_movies = self.tmdb.get_popular_movies()
            for movie in popular_movies[:3]:
                movie['recommendation_source'] = 'popular_fallback'
                movie['recommendation_score'] = 0.3
                recommendations.append(movie)
            
            # Get popular TV shows
            popular_tv = self.tmdb.get_popular_tv()
            for tv in popular_tv[:2]:
                tv['recommendation_source'] = 'popular_tv_fallback'
                tv['recommendation_score'] = 0.3
                recommendations.append(tv)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting fallback recommendations: {str(e)}")
            return []

    def _deduplicate_and_score(self, recommendations: List[Dict[str, Any]], user_id: int) -> List[Dict[str, Any]]:
        """Remove duplicates and calculate final recommendation scores"""
        try:
            seen_items = set()
            unique_recommendations = []
            
            # Get user's interaction history to avoid recommending seen content
            interactions = self.user_manager.get_user_interaction_history(user_id)
            viewed_content = {(i['content_id'], i.get('content_type', 'movie')) for i in interactions}
            
            for item in recommendations:
                content_id = item.get('id')
                content_type = 'movie' if 'title' in item else 'tv'
                item_key = (content_id, content_type)
                
                # Skip if already seen this content
                if item_key in seen_items or item_key in viewed_content:
                    continue
                
                seen_items.add(item_key)
                
                # Calculate final recommendation score
                base_score = item.get('recommendation_score', 0.3)
                
                # Boost score based on content quality
                vote_average = item.get('vote_average', 0)
                vote_count = item.get('vote_count', 0)
                
                # Quality boost (higher rated content gets boost)
                if vote_average >= 8.0:
                    base_score += 0.2
                elif vote_average >= 7.0:
                    base_score += 0.1
                
                # Popularity boost (more voted content gets small boost)
                if vote_count >= 1000:
                    base_score += 0.1
                elif vote_count >= 500:
                    base_score += 0.05
                
                # Recent content boost
                release_date = item.get('release_date') or item.get('first_air_date')
                if release_date:
                    try:
                        release_year = int(release_date[:4])
                        current_year = datetime.now().year
                        if current_year - release_year <= 2:  # Recent content
                            base_score += 0.05
                    except (ValueError, TypeError):
                        pass
                
                item['final_recommendation_score'] = min(base_score, 1.0)  # Cap at 1.0
                unique_recommendations.append(item)
            
            return unique_recommendations
            
        except Exception as e:
            logger.error(f"Error deduplicating recommendations: {str(e)}")
            return recommendations

    def _content_matches_genres(self, content: Dict[str, Any], preferred_genres: List[str]) -> bool:
        """Check if content matches user's preferred genres"""
        try:
            content_genres = content.get('genre_ids', [])
            if not content_genres:
                return False
            
            # Get genre mapping
            genre_mapping = self._get_genre_mapping()
            genre_id_to_name = {v: k for k, v in genre_mapping.items()}
            
            content_genre_names = []
            for genre_id in content_genres:
                if genre_id in genre_id_to_name:
                    content_genre_names.append(genre_id_to_name[genre_id])
            
            # Check for any overlap
            return bool(set(content_genre_names) & set(preferred_genres))
            
        except Exception as e:
            logger.error(f"Error checking genre match: {str(e)}")
            return False

    def _get_genre_mapping(self) -> Dict[str, int]:
        """Get mapping of genre names to IDs (simplified version)"""
        # This is a simplified mapping. In a production environment,
        # you would fetch this from TMDB API's genre endpoints
        return {
            'Action': 28,
            'Adventure': 12,
            'Animation': 16,
            'Comedy': 35,
            'Crime': 80,
            'Documentary': 99,
            'Drama': 18,
            'Family': 10751,
            'Fantasy': 14,
            'History': 36,
            'Horror': 27,
            'Music': 10402,
            'Mystery': 9648,
            'Romance': 10749,
            'Science Fiction': 878,
            'TV Movie': 10770,
            'Thriller': 53,
            'War': 10752,
            'Western': 37,
            # TV genres
            'Action & Adventure': 10759,
            'Kids': 10762,
            'News': 10763,
            'Reality': 10764,
            'Sci-Fi & Fantasy': 10765,
            'Soap': 10766,
            'Talk': 10767,
            'War & Politics': 10768
        }

    def get_content_based_recommendations(self, content_id: int, content_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recommendations based on a specific piece of content"""
        try:
            recommendations = []
            
            # Get similar content
            if content_type == 'movie':
                similar = self.tmdb.get_similar_movies(content_id)
                recommended = self.tmdb.get_movie_recommendations(content_id)
            else:
                similar = self.tmdb.get_similar_tv(content_id)
                recommended = self.tmdb.get_tv_recommendations(content_id)
            
            # Combine and score
            for item in similar[:3]:
                item['recommendation_source'] = 'similar'
                item['recommendation_score'] = 0.8
                recommendations.append(item)
            
            for item in recommended[:3]:
                item['recommendation_source'] = 'algorithm'
                item['recommendation_score'] = 0.7
                recommendations.append(item)
            
            # Remove duplicates
            seen_ids = set()
            unique_recs = []
            for item in recommendations:
                if item['id'] not in seen_ids:
                    seen_ids.add(item['id'])
                    unique_recs.append(item)
            
            return unique_recs[:limit]
            
        except Exception as e:
            logger.error(f"Error getting content-based recommendations: {str(e)}")
            return []

    def get_recommendations_by_genre(self, genre_name: str, content_type: str = 'movie', limit: int = 10) -> List[Dict[str, Any]]:
        """Get recommendations for a specific genre"""
        try:
            genre_mapping = self._get_genre_mapping()
            
            if genre_name not in genre_mapping:
                return []
            
            genre_id = genre_mapping[genre_name]
            
            if content_type == 'movie':
                content = self.tmdb.discover_movies(
                    with_genres=str(genre_id),
                    sort_by='vote_average.desc',
                    vote_count_gte=100
                )
            else:
                content = self.tmdb.discover_tv(
                    with_genres=str(genre_id),
                    sort_by='vote_average.desc',
                    vote_count_gte=50
                )
            
            # Add recommendation info
            for item in content:
                item['recommendation_source'] = f'genre_{genre_name.lower()}'
                item['recommendation_score'] = 0.6
            
            return content[:limit]
            
        except Exception as e:
            logger.error(f"Error getting genre recommendations: {str(e)}")
            return []
