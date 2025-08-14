"""
External API Integrations
=========================

Integration modules for connecting with external data sources and APIs
to enhance GTM intelligence gathering.
"""

import asyncio
import aiohttp
import requests
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import os
from urllib.parse import urlencode

from main import SecuritySignal, CompanyProfile

@dataclass
class APIConfig:
    """Configuration for external API integrations"""
    github_token: Optional[str] = None
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    clearbit_api_key: Optional[str] = None
    hunter_api_key: Optional[str] = None
    builtwith_api_key: Optional[str] = None
    crunchbase_api_key: Optional[str] = None

class GitHubIntegration:
    """GitHub API integration for repository and issue analysis"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {api_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def search_repositories(self, query: str, language: str = None) -> List[Dict]:
        """Search GitHub repositories for specific keywords"""
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": search_query,
            "sort": "updated",
            "order": "desc",
            "per_page": 50
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
                return []
    
    async def get_repository_issues(self, owner: str, repo: str) -> List[Dict]:
        """Get issues from a specific repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": 100
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return []
    
    async def analyze_repository_for_auth_signals(self, owner: str, repo: str) -> List[SecuritySignal]:
        """Analyze a repository for authentication-related signals"""
        signals = []
        
        # Get repository info
        repo_url = f"{self.base_url}/repos/{owner}/{repo}"
        async with aiohttp.ClientSession() as session:
            async with session.get(repo_url, headers=self.headers) as response:
                if response.status != 200:
                    return signals
                
                repo_data = await response.json()
        
        # Analyze repository description and README
        description = repo_data.get('description', '').lower()
        auth_keywords = ['auth', 'login', 'sso', 'oauth', 'jwt', 'session', 'password', 'security']
        
        if any(keyword in description for keyword in auth_keywords):
            signals.append(SecuritySignal(
                company_name=owner,
                signal_type="repository_auth_focus",
                source="github",
                description=f"Repository '{repo}' focused on authentication: {description}",
                severity=6,
                confidence=0.8,
                detected_at=datetime.now(),
                source_url=repo_data.get('html_url', ''),
                raw_content=description
            ))
        
        # Analyze recent issues
        issues = await self.get_repository_issues(owner, repo)
        for issue in issues[:10]:  # Check last 10 issues
            title = issue.get('title', '').lower()
            body = issue.get('body', '').lower() if issue.get('body') else ''
            
            if any(keyword in title + ' ' + body for keyword in auth_keywords):
                severity = 7 if any(urgent in title + ' ' + body for urgent in ['urgent', 'critical', 'security']) else 5
                
                signals.append(SecuritySignal(
                    company_name=owner,
                    signal_type="github_auth_issue",
                    source="github",
                    description=f"Authentication-related issue: {issue.get('title')}",
                    severity=severity,
                    confidence=0.75,
                    detected_at=datetime.now(),
                    source_url=issue.get('html_url', ''),
                    raw_content=body[:300]
                ))
        
        return signals

class RedditIntegration:
    """Reddit API integration for social intelligence"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str = "GTMEngine/1.0"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.access_token = None
    
    async def authenticate(self):
        """Authenticate with Reddit API"""
        auth_url = "https://www.reddit.com/api/v1/access_token"
        auth_data = {
            'grant_type': 'client_credentials'
        }
        
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        headers = {'User-Agent': self.user_agent}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=auth_data, auth=auth, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get('access_token')
    
    async def search_posts(self, query: str, subreddit: str = None, limit: int = 25) -> List[Dict]:
        """Search Reddit posts for specific keywords"""
        if not self.access_token:
            await self.authenticate()
        
        if subreddit:
            url = f"https://oauth.reddit.com/r/{subreddit}/search"
        else:
            url = "https://oauth.reddit.com/search"
        
        params = {
            'q': query,
            'sort': 'new',
            'limit': limit,
            't': 'week'  # Last week
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': self.user_agent
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', {}).get('children', [])
                return []
    
    async def analyze_auth_discussions(self, subreddits: List[str]) -> List[SecuritySignal]:
        """Analyze Reddit discussions for authentication pain points"""
        signals = []
        auth_queries = [
            'authentication problems',
            'SSO integration',
            'user management nightmare',
            'auth implementation',
            'login issues'
        ]
        
        for subreddit in subreddits:
            for query in auth_queries:
                posts = await self.search_posts(query, subreddit)
                
                for post_data in posts:
                    post = post_data.get('data', {})
                    title = post.get('title', '')
                    selftext = post.get('selftext', '')
                    
                    # Extract company mentions or identify potential prospects
                    if len(selftext) > 50:  # Substantial posts only
                        signals.append(SecuritySignal(
                            company_name=f"Reddit User ({post.get('author', 'unknown')})",
                            signal_type="social_auth_discussion",
                            source="reddit",
                            description=f"Discussion about auth challenges: {title}",
                            severity=4,
                            confidence=0.6,
                            detected_at=datetime.now(),
                            source_url=f"https://reddit.com{post.get('permalink', '')}",
                            raw_content=selftext[:300]
                        ))
        
        return signals

class ClearbitIntegration:
    """Clearbit API integration for company enrichment"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://company-stream.clearbit.com/v2"
    
    async def enrich_company(self, domain: str) -> Dict:
        """Enrich company data using Clearbit"""
        url = f"{self.base_url}/companies/find"
        params = {'domain': domain}
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    
    async def get_company_technologies(self, domain: str) -> List[str]:
        """Get company's technology stack from Clearbit"""
        company_data = await self.enrich_company(domain)
        tech_data = company_data.get('tech', [])
        
        return [tech for tech in tech_data if tech]

class HunterIntegration:
    """Hunter.io integration for email discovery"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
    
    async def find_emails(self, domain: str) -> List[Dict]:
        """Find email addresses for a domain"""
        url = f"{self.base_url}/domain-search"
        params = {
            'domain': domain,
            'api_key': self.api_key,
            'limit': 50
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', {}).get('emails', [])
                return []
    
    async def verify_email(self, email: str) -> Dict:
        """Verify if an email address is valid"""
        url = f"{self.base_url}/email-verifier"
        params = {
            'email': email,
            'api_key': self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return {}

class BuiltWithIntegration:
    """BuiltWith API integration for technology detection"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.builtwith.com/v20"
    
    async def get_technologies(self, domain: str) -> Dict:
        """Get technologies used by a domain"""
        url = f"{self.base_url}/api.json"
        params = {
            'KEY': self.api_key,
            'LOOKUP': domain
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    
    def analyze_auth_stack(self, tech_data: Dict) -> List[str]:
        """Analyze technology stack for authentication-related technologies"""
        auth_technologies = []
        
        results = tech_data.get('Results', [])
        for result in results:
            paths = result.get('Result', {}).get('Paths', [])
            for path in paths:
                technologies = path.get('Technologies', [])
                for tech in technologies:
                    tech_name = tech.get('Name', '').lower()
                    # Check if technology is auth-related
                    if any(keyword in tech_name for keyword in ['auth', 'login', 'oauth', 'sso', 'jwt']):
                        auth_technologies.append(tech.get('Name'))
        
        return auth_technologies

class DataEnrichmentEngine:
    """Central engine for enriching company data from multiple sources"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.github = GitHubIntegration(config.github_token) if config.github_token else None
        self.reddit = RedditIntegration(config.reddit_client_id, config.reddit_client_secret) if config.reddit_client_id else None
        self.clearbit = ClearbitIntegration(config.clearbit_api_key) if config.clearbit_api_key else None
        self.hunter = HunterIntegration(config.hunter_api_key) if config.hunter_api_key else None
        self.builtwith = BuiltWithIntegration(config.builtwith_api_key) if config.builtwith_api_key else None
    
    async def enrich_company_profile(self, profile: CompanyProfile) -> CompanyProfile:
        """Enrich company profile with data from multiple sources"""
        
        # Enrich with Clearbit data
        if self.clearbit:
            clearbit_data = await self.clearbit.enrich_company(profile.domain)
            if clearbit_data:
                profile.industry = clearbit_data.get('category', {}).get('industry', profile.industry)
                metrics = clearbit_data.get('metrics', {})
                if metrics.get('employees'):
                    profile.employee_count = metrics['employees']
        
        # Get technology stack
        if self.builtwith:
            tech_data = await self.builtwith.get_technologies(profile.domain)
            auth_techs = self.builtwith.analyze_auth_stack(tech_data)
            profile.tech_stack.extend(auth_techs)
        
        # Find contact emails
        if self.hunter:
            emails = await self.hunter.find_emails(profile.domain)
            # Store key contacts (would integrate with CRM)
        
        # Analyze GitHub presence
        if self.github:
            github_signals = await self.github.analyze_repository_for_auth_signals(
                profile.name.lower().replace(' ', ''), 
                'auth'  # Look for auth-related repos
            )
            profile.security_signals.extend(github_signals)
        
        # Monitor social discussions
        if self.reddit:
            reddit_signals = await self.reddit.analyze_auth_discussions(['webdev', 'programming', 'entrepreneur'])
            # Filter signals relevant to this company
            relevant_signals = [s for s in reddit_signals if profile.name.lower() in s.raw_content.lower()]
            profile.security_signals.extend(relevant_signals)
        
        return profile
    
    async def discover_new_prospects(self, keywords: List[str]) -> List[SecuritySignal]:
        """Discover new prospects based on keyword monitoring"""
        all_signals = []
        
        # GitHub repository discovery
        if self.github:
            for keyword in keywords:
                repos = await self.github.search_repositories(keyword)
                for repo in repos[:20]:  # Limit to top 20 results
                    signals = await self.github.analyze_repository_for_auth_signals(
                        repo['owner']['login'],
                        repo['name']
                    )
                    all_signals.extend(signals)
        
        # Reddit discussion monitoring
        if self.reddit:
            reddit_signals = await self.reddit.analyze_auth_discussions(['webdev', 'programming', 'startups'])
            all_signals.extend(reddit_signals)
        
        return all_signals

# Demo integration engine
async def demo_integrations():
    """Demonstrate the integration capabilities"""
    print("🔗 Descope GTM Integration Engine Demo")
    print("=" * 50)
    
    # Create config (in production, these would come from environment variables)
    config = APIConfig(
        # github_token="your_github_token",
        # reddit_client_id="your_reddit_client_id",
        # reddit_client_secret="your_reddit_client_secret",
        # clearbit_api_key="your_clearbit_key",
        # hunter_api_key="your_hunter_key",
        # builtwith_api_key="your_builtwith_key"
    )
    
    enrichment_engine = DataEnrichmentEngine(config)
    
    print("🔍 Discovering new prospects...")
    
    # Simulate prospect discovery
    auth_keywords = ['authentication', 'user management', 'sso integration', 'login system']
    
    # Mock discovered signals (since we don't have API keys for demo)
    mock_signals = [
        SecuritySignal(
            company_name="DevCorp Solutions",
            signal_type="github_repository",
            source="github",
            description="Public repository showing custom authentication implementation",
            severity=7,
            confidence=0.85,
            detected_at=datetime.now(),
            source_url="https://github.com/devcorp/auth-service",
            raw_content="Custom JWT implementation with potential security issues..."
        ),
        SecuritySignal(
            company_name="StartupTech",
            signal_type="reddit_discussion",
            source="reddit",
            description="Founder discussing SSO implementation challenges",
            severity=6,
            confidence=0.7,
            detected_at=datetime.now(),
            source_url="https://reddit.com/r/entrepreneur/post/sso_help",
            raw_content="We're a B2B SaaS and enterprise customers are demanding SSO..."
        )
    ]
    
    print(f"✅ Discovered {len(mock_signals)} new prospects")
    
    for signal in mock_signals:
        print(f"   📍 {signal.company_name}: {signal.description}")
    
    print("\n🔬 Enriching company profiles...")
    
    # Mock company profile enrichment
    from main import CompanyProfile
    sample_profile = CompanyProfile(
        name="TechStartup Inc",
        domain="techstartup.com",
        industry="Software",
        size="startup",
        tech_stack=["React", "Node.js"],
        funding_stage="Series A",
        employee_count=50,
        security_signals=[],
        gtm_score=0.0,
        priority_level="medium"
    )
    
    # Simulate enrichment (would use real APIs in production)
    sample_profile.tech_stack.extend(["Auth0", "Stripe", "PostgreSQL"])
    sample_profile.security_signals.extend(mock_signals[:1])
    
    print(f"✅ Enriched profile for {sample_profile.name}")
    print(f"   🏢 Industry: {sample_profile.industry}")
    print(f"   👥 Employees: {sample_profile.employee_count}")
    print(f"   💻 Tech Stack: {', '.join(sample_profile.tech_stack)}")
    print(f"   🚨 Signals: {len(sample_profile.security_signals)}")
    
    return enrichment_engine, mock_signals

if __name__ == "__main__":
    asyncio.run(demo_integrations())
