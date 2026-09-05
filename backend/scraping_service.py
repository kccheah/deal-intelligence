"""
Data Scraping Service
Collects deal and property data from multiple sources
"""

import feedparser
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# NEWS & RSS SCRAPING
# ============================================================================

class NewsSource:
    """Base class for news sources"""

    def fetch_deals(self) -> List[Dict[str, Any]]:
        raise NotImplementedError


class RSSNewsScraper(NewsSource):
    """Scrape deals from RSS feeds"""

    RSS_FEEDS = [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://feeds.finance.yahoo.com/rss/2.0/headline",
        "https://feeds.reuters.com/reuters/technologyNews",
        "https://feeds.techcrunch.com/",
    ]

    def fetch_deals(self) -> List[Dict[str, Any]]:
        deals = []

        for feed_url in self.RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:10]:  # Last 10 entries
                    # Simple heuristic: look for deal keywords
                    title_lower = entry.title.lower()
                    if any(keyword in title_lower for keyword in ["acquisition", "merger", "acquired", "invested", "funding", "pe fund", "private equity"]):
                        deal = {
                            "source": "news_rss",
                            "external_source_id": f"rss_{entry.link.hash() if hasattr(entry, 'link') else entry.title.hash()}",
                            "company_name": self._extract_company_name(entry.title),
                            "deal_type": self._extract_deal_type(entry.title),
                            "deal_description": entry.summary[:500] if hasattr(entry, 'summary') else "",
                            "announced_date": self._parse_date(entry.published) if hasattr(entry, 'published') else datetime.now(),
                            "deal_url": entry.link if hasattr(entry, 'link') else "",
                            "industry": "Technology",  # Will be enriched later
                        }
                        deals.append(deal)

            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {e}")
                continue

        return deals

    @staticmethod
    def _extract_company_name(title: str) -> str:
        """Extract company name from title"""
        # Simple heuristic: first capitalized word or words
        words = title.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                return word
        return "Unknown"

    @staticmethod
    def _extract_deal_type(title: str) -> str:
        """Extract deal type from title"""
        title_lower = title.lower()
        if "acquisition" in title_lower or "acquired" in title_lower:
            return "ma"
        elif "private equity" in title_lower or "pe fund" in title_lower:
            return "pe"
        elif "invested" in title_lower or "investment" in title_lower:
            return "fdi"
        elif "joint venture" in title_lower or "partnership" in title_lower:
            return "jv"
        return "other"

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse date string"""
        try:
            return datetime.fromisoformat(date_str)
        except:
            return datetime.now()


class GoogleNewsAPI(NewsSource):
    """Fetch deals from Google News API"""

    def fetch_deals(self) -> List[Dict[str, Any]]:
        """Fetch from Google News API"""
        deals = []

        # Using NewsAPI (free tier)
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            logger.warning("NEWSAPI_KEY not set, skipping Google News")
            return deals

        keywords = ["acquisition", "merger", "private equity", "venture funding", "cross-border deal"]

        for keyword in keywords:
            try:
                url = f"https://newsapi.org/v2/everything?q={keyword}&sortBy=publishedAt&language=en&pageSize=10&apiKey={api_key}"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    for article in data.get("articles", []):
                        deal = {
                            "source": "news_api",
                            "external_source_id": f"newsapi_{article['url'].hash()}",
                            "company_name": self._extract_company_name(article["title"]),
                            "deal_type": self._extract_deal_type(article["title"]),
                            "deal_description": article.get("description", "")[:500],
                            "announced_date": datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00")),
                            "deal_url": article["url"],
                            "industry": "Technology",
                            "raw_data": article,
                        }
                        deals.append(deal)

            except Exception as e:
                logger.error(f"Error fetching Google News for '{keyword}': {e}")
                continue

        return deals

    @staticmethod
    def _extract_company_name(title: str) -> str:
        words = title.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word
        return "Unknown"

    @staticmethod
    def _extract_deal_type(title: str) -> str:
        title_lower = title.lower()
        if "acquisition" in title_lower or "acquired" in title_lower:
            return "ma"
        elif "private equity" in title_lower:
            return "pe"
        elif "invested" in title_lower:
            return "fdi"
        return "other"


# ============================================================================
# CRUNCHBASE SCRAPING (Free API)
# ============================================================================

class CrunchbaseAPI(NewsSource):
    """Fetch deals from Crunchbase free API"""

    def fetch_deals(self) -> List[Dict[str, Any]]:
        """Fetch recent funding/M&A from Crunchbase"""
        deals = []

        # Crunchbase community API (free tier, limited)
        try:
            url = "https://api.crunchbase.com/v4/autocomplete?query=funding"
            # Note: This is a simplified example. Real Crunchbase integration needs API key

            # For MVP, use web scraping instead
            deals = self._scrape_crunchbase()

        except Exception as e:
            logger.error(f"Error fetching Crunchbase: {e}")

        return deals

    @staticmethod
    def _scrape_crunchbase() -> List[Dict[str, Any]]:
        """Web scrape Crunchbase (fallback)"""
        # Simplified mock data for MVP
        deals = [
            {
                "source": "crunchbase",
                "external_source_id": "cb_1",
                "company_name": "TechStartup XYZ",
                "deal_type": "pe",
                "deal_value_usd": 50000000,
                "industry": "SaaS",
                "target_geography": "SG",
                "announced_date": datetime.now() - timedelta(days=3),
                "deal_description": "Series B funding from regional PE fund"
            }
        ]
        return deals


# ============================================================================
# PROPERTY DATA SCRAPING
# ============================================================================

class PropertyScraper:
    """Fetch property data from various sources"""

    def fetch_properties(self, country: str = "AE") -> List[Dict[str, Any]]:
        """Fetch property listings by country"""

        if country == "AE":
            return self._fetch_dubai_properties()
        elif country == "TH":
            return self._fetch_thailand_properties()
        elif country == "SG":
            return self._fetch_singapore_properties()
        elif country == "MY":
            return self._fetch_malaysia_properties()

        return []

    @staticmethod
    def _fetch_dubai_properties() -> List[Dict[str, Any]]:
        """Fetch Dubai property data"""
        # Mock data for MVP (would integrate with Dubai Land Department API)
        properties = [
            {
                "source": "dubai_mock",
                "external_source_id": "dxb_1",
                "address": "Downtown Dubai, Marina Residences",
                "city": "Dubai",
                "country_code": "AE",
                "property_type": "residential",
                "price_usd": 500000,
                "size_sqm": 100,
                "year_built": 2020,
                "ownership_legal_status": "freehold",
                "foreign_ownership_allowed": True,
                "freehold_eligible": True,
            }
        ]
        return properties

    @staticmethod
    def _fetch_thailand_properties() -> List[Dict[str, Any]]:
        """Fetch Thailand property data"""
        properties = [
            {
                "source": "thailand_mock",
                "external_source_id": "th_1",
                "address": "Silom, Bangkok",
                "city": "Bangkok",
                "country_code": "TH",
                "property_type": "commercial",
                "price_usd": 300000,
                "size_sqm": 150,
                "year_built": 2018,
                "ownership_legal_status": "leasehold",
                "lease_remaining_years": 80,
                "foreign_ownership_allowed": False,
                "freehold_eligible": False,
            }
        ]
        return properties

    @staticmethod
    def _fetch_singapore_properties() -> List[Dict[str, Any]]:
        """Fetch Singapore property data"""
        properties = [
            {
                "source": "singapore_mock",
                "external_source_id": "sg_1",
                "address": "Marina Bay, Singapore",
                "city": "Singapore",
                "country_code": "SG",
                "property_type": "commercial",
                "price_usd": 800000,
                "size_sqm": 120,
                "year_built": 2019,
                "ownership_legal_status": "freehold",
                "foreign_ownership_allowed": True,
                "freehold_eligible": True,
            }
        ]
        return properties

    @staticmethod
    def _fetch_malaysia_properties() -> List[Dict[str, Any]]:
        """Fetch Malaysia property data"""
        properties = [
            {
                "source": "malaysia_mock",
                "external_source_id": "my_1",
                "address": "Kuala Lumpur City Centre",
                "city": "Kuala Lumpur",
                "country_code": "MY",
                "property_type": "residential",
                "price_usd": 250000,
                "size_sqm": 110,
                "year_built": 2017,
                "ownership_legal_status": "freehold",
                "foreign_ownership_allowed": True,
                "freehold_eligible": True,
            }
        ]
        return properties


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class DataCollectionService:
    """Orchestrate all data collection"""

    def __init__(self):
        self.news_scraper = RSSNewsScraper()
        self.google_news = GoogleNewsAPI()
        self.crunchbase = CrunchbaseAPI()
        self.property_scraper = PropertyScraper()

    def collect_all_deals(self) -> List[Dict[str, Any]]:
        """Collect deals from all sources"""
        all_deals = []

        logger.info("Collecting deals from RSS...")
        all_deals.extend(self.news_scraper.fetch_deals())

        logger.info("Collecting deals from Google News...")
        all_deals.extend(self.google_news.fetch_deals())

        logger.info("Collecting deals from Crunchbase...")
        all_deals.extend(self.crunchbase.fetch_deals())

        logger.info(f"Collected {len(all_deals)} total deals")
        return all_deals

    def collect_all_properties(self) -> List[Dict[str, Any]]:
        """Collect properties from all sources"""
        all_properties = []

        for country in ["AE", "TH", "SG", "MY"]:
            logger.info(f"Collecting properties from {country}...")
            all_properties.extend(self.property_scraper.fetch_properties(country))

        logger.info(f"Collected {len(all_properties)} total properties")
        return all_properties


if __name__ == "__main__":
    import os

    service = DataCollectionService()

    # Test deal collection
    deals = service.collect_all_deals()
    print(f"Fetched {len(deals)} deals")

    # Test property collection
    properties = service.collect_all_properties()
    print(f"Fetched {len(properties)} properties")
