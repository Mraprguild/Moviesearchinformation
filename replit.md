# Overview

This is a Telegram Bot for movie and TV show recommendations that provides personalized content suggestions through external API integrations. The bot offers search functionality, trending content discovery, and AI-powered recommendations based on user preferences and viewing history. It's designed as a Flask web application with webhook support for deployment on cloud platforms like Render.com.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Flask-based web application** serving as the main entry point and webhook handler
- **Modular service architecture** with separate classes for different responsibilities
- **JSON file-based data persistence** for user data and preferences storage
- **Webhook pattern** for receiving Telegram updates instead of polling

## Bot Implementation
- **Command-based interaction model** with handlers for different user commands (/start, /movie, /tv, /recommend, etc.)
- **Service layer abstraction** separating bot logic from external API interactions
- **User session management** tracking preferences and interaction history
- **Rate limiting and caching** mechanisms to manage API usage

## Recommendation System
- **Hybrid recommendation engine** combining collaborative filtering and content-based filtering
- **Multi-strategy approach** using genre preferences, similar content analysis, and trending content
- **Personalization features** adapting suggestions based on user interaction patterns
- **Fallback mechanisms** providing trending content for new users without history

## Data Management
- **File-based user data storage** using JSON format in local data directory
- **In-memory data structures** for runtime user session management
- **Data retention policies** with configurable cleanup schedules
- **Error handling and data recovery** mechanisms for corrupted or missing files

## Configuration Management
- **Environment variable-based configuration** for API keys and deployment settings
- **Centralized Config class** managing all application settings
- **Development/production environment support** with appropriate defaults
- **Flexible rate limiting and caching parameters** adjustable via environment variables

# External Dependencies

## API Services
- **TMDB (The Movie Database)** - Primary source for movie and TV show metadata, search functionality, and trending content
- **OMDB (Open Movie Database)** - Additional movie information and ratings data
- **YouTube API** - Integration for movie trailers and promotional content discovery
- **Telegram Bot API** - Core messaging platform for user interactions via webhooks

## Infrastructure Services
- **Render.com hosting platform** - Cloud deployment environment with webhook endpoint support
- **Flask web framework** - HTTP server for webhook handling and health check endpoints

## Development Dependencies
- **Python requests library** - HTTP client for external API communications
- **Bootstrap CSS framework** - Frontend styling for web interface components
- **Feather Icons** - Icon library for user interface elements

## Data Storage
- **Local JSON file system** - User data persistence without external database dependencies
- **File-based configuration** - Settings and preferences stored in application directory structure