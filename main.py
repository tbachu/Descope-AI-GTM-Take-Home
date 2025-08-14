"""
Descope AI GTM Intelligence Engine
=================================

A comprehensive AI-powered Go-to-Market engine that:
1. Monitors multiple data sources for security/identity signals
2. Scores accounts using firmographic and technographic data
3. Generates personalized outreach assets
4. Provides real-time alerts for high-value opportunities

Author: AI GTM Engineer Intern Candidate
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Import our AI provider system
from ai_providers import ai_client

# Load environment variables
load_dotenv()

@dataclass
class SecuritySignal:
    """Represents a security/identity signal detected from various sources"""
    company_name: str
    signal_type: str  # 'auth_weakness', 'security_initiative', 'integration_need', etc.
    source: str  # 'github', 'reddit', 'job_posting', 'website'
    description: str
    severity: int  # 1-10 scale
    confidence: float  # 0-1 scale
    detected_at: datetime
    source_url: str
    raw_content: str

@dataclass
class CompanyProfile:
    """Company profile with firmographic and technographic data"""
    name: str
    domain: str
    industry: str
    size: str  # 'startup', 'small', 'medium', 'enterprise'
    tech_stack: List[str]
    funding_stage: str
    employee_count: int
    security_signals: List[SecuritySignal]
    gtm_score: float  # Overall GTM fit score (0-100)
    priority_level: str  # 'low', 'medium', 'high', 'critical'

class SecuritySignalDetector:
    """Detects security and identity-related signals from various sources"""
    
    def __init__(self):
        # Using our AI provider abstraction instead of OpenAI directly
        pass
        
    async def detect_github_signals(self, company_name: str, github_repos: List[str]) -> List[SecuritySignal]:
        """Analyze GitHub repositories for security signals"""
        signals = []
        
        for repo_url in github_repos:
            try:
                # Simulate GitHub API call (would use PyGithub in production)
                repo_data = self._fetch_github_repo_data(repo_url)
                
                # Analyze README, issues, and recent commits for security patterns
                analysis_prompt = f"""
                Analyze this GitHub repository data for security and identity management signals relevant to a company like Descope:

                Repository: {repo_url}
                README content: {repo_data.get('readme', '')[:2000]}
                Recent issues: {repo_data.get('issues', '')[:1000]}
                
                Look for signals like:
                - Manual authentication implementations
                - Security vulnerabilities or concerns
                - Identity management challenges
                - Integration needs
                - Password/auth-related issues
                
                Return a JSON array of signals found, each with:
                - signal_type: category of signal
                - description: what was found
                - severity: 1-10 scale
                - confidence: 0-1 scale
                """
                
                # Use our AI client instead of OpenAI directly
                detected_signals = await ai_client.generate_json_completion(analysis_prompt)
                
                # Handle both array and object responses
                if isinstance(detected_signals, list):
                    signal_list = detected_signals
                elif isinstance(detected_signals, dict) and 'signals' in detected_signals:
                    signal_list = detected_signals['signals']
                else:
                    # If it's not the expected format, create a mock signal
                    signal_list = [{
                        'signal_type': 'github_analysis',
                        'description': 'Repository analyzed for authentication patterns',
                        'severity': 5,
                        'confidence': 0.7
                    }]
                
                for signal_data in signal_list:
                    signal = SecuritySignal(
                        company_name=company_name,
                        signal_type=signal_data['signal_type'],
                        source='github',
                        description=signal_data['description'],
                        severity=signal_data['severity'],
                        confidence=signal_data['confidence'],
                        detected_at=datetime.now(),
                        source_url=repo_url,
                        raw_content=str(repo_data)[:500]
                    )
                    signals.append(signal)
                    
            except Exception as e:
                print(f"Error analyzing GitHub repo {repo_url}: {e}")
                continue
                
        return signals
    
    def _fetch_github_repo_data(self, repo_url: str) -> Dict:
        """Simulate fetching GitHub repository data"""
        # In production, this would use the GitHub API
        return {
            'readme': """
            # Authentication Service
            
            This is our custom authentication service built with Node.js.
            We're currently using basic JWT tokens and have been having issues
            with session management and user provisioning.
            
            ## Known Issues
            - Manual user provisioning is taking too long
            - No SSO integration yet
            - Password reset flow is buggy
            """,
            'issues': [
                "Need to implement SSO for enterprise customers",
                "Security vulnerability in password reset",
                "User management is too manual"
            ]
        }
    
    async def detect_reddit_signals(self, company_name: str, subreddits: List[str]) -> List[SecuritySignal]:
        """Monitor Reddit for security-related discussions"""
        signals = []
        
        for subreddit in subreddits:
            try:
                # Simulate Reddit API calls
                posts = self._fetch_reddit_posts(subreddit, company_name)
                
                for post in posts:
                    analysis_prompt = f"""
                    Analyze this Reddit post for security/identity signals:
                    
                    Title: {post['title']}
                    Content: {post['content'][:1000]}
                    Subreddit: {subreddit}
                    
                    Is this relevant to identity management, authentication, or security?
                    If yes, categorize the signal and assess its importance.
                    Return JSON with signal details or null if not relevant.
                    """
                    
                    # Use our AI client
                    result = await ai_client.generate_completion(analysis_prompt)
                    if result and result.strip().lower() != 'null':
                        try:
                            signal_data = json.loads(result)
                            signal = SecuritySignal(
                                company_name=company_name,
                                signal_type=signal_data.get('signal_type', 'reddit_discussion'),
                                source='reddit',
                                description=signal_data.get('description', 'Reddit discussion about authentication'),
                                severity=signal_data.get('severity', 5),
                                confidence=signal_data.get('confidence', 0.6),
                                detected_at=datetime.now(),
                                source_url=f"https://reddit.com/r/{subreddit}",
                                raw_content=post['content'][:300]
                            )
                            signals.append(signal)
                        except json.JSONDecodeError:
                            # If JSON parsing fails, create a basic signal
                            if any(keyword in result.lower() for keyword in ['auth', 'security', 'login']):
                                signal = SecuritySignal(
                                    company_name=company_name,
                                    signal_type='reddit_discussion',
                                    source='reddit',
                                    description='Reddit discussion about authentication challenges',
                                    severity=5,
                                    confidence=0.6,
                                    detected_at=datetime.now(),
                                    source_url=f"https://reddit.com/r/{subreddit}",
                                    raw_content=post['content'][:300]
                                )
                                signals.append(signal)
                        
            except Exception as e:
                print(f"Error analyzing Reddit {subreddit}: {e}")
                continue
                
        return signals
    
    def _fetch_reddit_posts(self, subreddit: str, company_name: str) -> List[Dict]:
        """Simulate fetching Reddit posts"""
        return [
            {
                'title': f"Having auth issues with our {company_name} integration",
                'content': "We're a startup trying to implement user authentication and it's been a nightmare. Manual user management is killing our productivity. Looking for better solutions."
            },
            {
                'title': "Security best practices for startups",
                'content': "What are the must-have security features for a B2B SaaS? We need SSO, MFA, and user provisioning but don't know where to start."
            }
        ]

class FirmographicAnalyzer:
    """Analyzes company firmographic and technographic data"""
    
    def __init__(self):
        # Using our AI provider abstraction
        pass
    
    async def analyze_company(self, company_name: str, domain: str) -> CompanyProfile:
        """Comprehensive company analysis"""
        
        # Fetch company data from multiple sources
        company_data = await self._fetch_company_data(domain)
        tech_stack = await self._analyze_tech_stack(domain)
        
        # Create initial profile
        profile = CompanyProfile(
            name=company_name,
            domain=domain,
            industry=company_data.get('industry', 'Unknown'),
            size=self._categorize_company_size(company_data.get('employees', 0)),
            tech_stack=tech_stack,
            funding_stage=company_data.get('funding_stage', 'Unknown'),
            employee_count=company_data.get('employees', 0),
            security_signals=[],
            gtm_score=0.0,
            priority_level='low'
        )
        
        return profile
    
    async def _fetch_company_data(self, domain: str) -> Dict:
        """Fetch company data from various APIs"""
        # Simulate API calls to services like Clearbit, ZoomInfo, etc.
        return {
            'industry': 'Software',
            'employees': 150,
            'funding_stage': 'Series A',
            'technologies': ['React', 'Node.js', 'PostgreSQL', 'AWS']
        }
    
    async def _analyze_tech_stack(self, domain: str) -> List[str]:
        """Analyze company's technology stack"""
        # Simulate tech stack detection (would use services like BuiltWith, Wappalyzer)
        return ['React', 'Node.js', 'PostgreSQL', 'AWS', 'Stripe']
    
    def _categorize_company_size(self, employee_count: int) -> str:
        """Categorize company size"""
        if employee_count < 50:
            return 'startup'
        elif employee_count < 200:
            return 'small'
        elif employee_count < 1000:
            return 'medium'
        else:
            return 'enterprise'

class GTMScorer:
    """Scores companies for GTM fit based on signals and firmographic data"""
    
    def __init__(self):
        # Using our AI provider abstraction
        pass
    
    def calculate_gtm_score(self, profile: CompanyProfile) -> float:
        """Calculate overall GTM score for a company"""
        
        # Base score from firmographic data
        base_score = self._calculate_base_score(profile)
        
        # Signal-based score
        signal_score = self._calculate_signal_score(profile.security_signals)
        
        # Tech stack compatibility score
        tech_score = self._calculate_tech_score(profile.tech_stack)
        
        # Weighted combination
        final_score = (base_score * 0.4) + (signal_score * 0.4) + (tech_score * 0.2)
        
        return min(100.0, max(0.0, final_score))
    
    def _calculate_base_score(self, profile: CompanyProfile) -> float:
        """Calculate base score from firmographic data"""
        score = 0.0
        
        # Company size scoring (Descope targets mid-market and enterprise)
        size_scores = {
            'startup': 20,
            'small': 40,
            'medium': 80,
            'enterprise': 90
        }
        score += size_scores.get(profile.size, 0)
        
        # Industry scoring
        high_value_industries = ['software', 'fintech', 'healthtech', 'saas', 'technology']
        if any(industry in profile.industry.lower() for industry in high_value_industries):
            score += 20
        
        # Funding stage
        funding_scores = {
            'seed': 10,
            'series a': 30,
            'series b': 50,
            'series c+': 70,
            'public': 60
        }
        score += funding_scores.get(profile.funding_stage.lower(), 0)
        
        return score
    
    def _calculate_signal_score(self, signals: List[SecuritySignal]) -> float:
        """Calculate score based on detected security signals"""
        if not signals:
            return 0.0
        
        total_score = 0.0
        for signal in signals:
            # Weight by severity and confidence
            signal_value = (signal.severity * 10) * signal.confidence
            total_score += signal_value
        
        # Normalize to 0-100 scale
        return min(100.0, total_score / len(signals))
    
    def _calculate_tech_score(self, tech_stack: List[str]) -> float:
        """Calculate score based on technology stack compatibility"""
        # Technologies that indicate need for identity/auth solutions
        relevant_techs = [
            'react', 'vue', 'angular',  # Frontend frameworks
            'node.js', 'python', 'java',  # Backend languages
            'postgresql', 'mongodb',  # Databases
            'aws', 'azure', 'gcp',  # Cloud platforms
            'stripe', 'shopify'  # Payment/commerce platforms
        ]
        
        matches = sum(1 for tech in tech_stack if tech.lower() in relevant_techs)
        return min(100.0, (matches / len(relevant_techs)) * 100)

class OutreachGenerator:
    """Generates personalized outreach assets based on company intelligence"""
    
    def __init__(self):
        # Using our AI provider abstraction
        pass
    
    async def generate_email_outreach(self, profile: CompanyProfile, contact_name: str, contact_title: str) -> str:
        """Generate personalized email outreach"""
        
        # Prepare context from signals and company data
        signals_context = self._format_signals_for_context(profile.security_signals)
        
        prompt = f"""
        Create a highly personalized cold outreach email for Descope (an authentication and user management platform).
        
        Target Company: {profile.name}
        Contact: {contact_name}, {contact_title}
        Industry: {profile.industry}
        Company Size: {profile.size} ({profile.employee_count} employees)
        Tech Stack: {', '.join(profile.tech_stack)}
        
        Key Signals Detected:
        {signals_context}
        
        Email Requirements:
        - Subject line that references specific intelligence
        - Personalized opening that shows research
        - Connect their specific challenges to Descope's solutions
        - Include a specific, relevant use case
        - Professional but conversational tone
        - Clear call-to-action
        - Keep under 150 words
        
        Focus on how Descope can solve their specific authentication/identity challenges.
        """
        
        response = await ai_client.generate_completion(prompt, temperature=0.7)
        return response
    
    async def generate_linkedin_message(self, profile: CompanyProfile, contact_name: str) -> str:
        """Generate LinkedIn connection message"""
        
        signals_context = self._format_signals_for_context(profile.security_signals[:2])  # Top 2 signals
        
        prompt = f"""
        Create a personalized LinkedIn connection request message for {contact_name} at {profile.name}.
        
        Company Context:
        - Industry: {profile.industry}
        - Size: {profile.size}
        - Key challenges: {signals_context}
        
        Requirements:
        - Under 300 characters (LinkedIn limit)
        - Reference specific intelligence about their company
        - Mention Descope's relevant solution
        - Professional but friendly
        - Include specific value proposition
        """
        
        response = await ai_client.generate_completion(prompt, temperature=0.7)
        return response
    
    async def generate_video_script(self, profile: CompanyProfile, contact_name: str) -> str:
        """Generate personalized video script"""
        
        signals_context = self._format_signals_for_context(profile.security_signals)
        
        prompt = f"""
        Create a 60-second personalized video script for {contact_name} at {profile.name}.
        
        Company Intelligence:
        {signals_context}
        Company: {profile.name} ({profile.industry}, {profile.size})
        Tech Stack: {', '.join(profile.tech_stack)}
        
        Script should:
        - Open with specific research about their company
        - Reference their technology stack
        - Connect their challenges to Descope's solutions
        - Include a specific demo offer
        - Be conversational and engaging
        - End with clear next step
        
        Format as a script with timing cues.
        """
        
        response = await ai_client.generate_completion(prompt, temperature=0.7)
        return response
    
    def _format_signals_for_context(self, signals: List[SecuritySignal]) -> str:
        """Format security signals for context"""
        if not signals:
            return "No specific security signals detected."
        
        formatted = []
        for signal in signals:
            formatted.append(f"- {signal.signal_type}: {signal.description} (Source: {signal.source})")
        
        return '\n'.join(formatted)

class GTMEngine:
    """Main GTM Intelligence Engine orchestrating all components"""
    
    def __init__(self):
        self.signal_detector = SecuritySignalDetector()
        self.firmographic_analyzer = FirmographicAnalyzer()
        self.gtm_scorer = GTMScorer()
        self.outreach_generator = OutreachGenerator()
        
        # Initialize data storage
        self.companies: Dict[str, CompanyProfile] = {}
        self.alerts: List[Dict] = []
    
    async def analyze_company(self, company_name: str, domain: str, github_repos: List[str] = None) -> CompanyProfile:
        """Complete company analysis pipeline"""
        
        print(f"🔍 Analyzing {company_name}...")
        
        # Step 1: Firmographic analysis
        profile = await self.firmographic_analyzer.analyze_company(company_name, domain)
        
        # Step 2: Signal detection
        signals = []
        
        if github_repos:
            github_signals = await self.signal_detector.detect_github_signals(company_name, github_repos)
            signals.extend(github_signals)
        
        reddit_signals = await self.signal_detector.detect_reddit_signals(
            company_name, 
            ['webdev', 'programming', 'entrepreneur', 'startups', 'sysadmin']
        )
        signals.extend(reddit_signals)
        
        profile.security_signals = signals
        
        # Step 3: GTM scoring
        profile.gtm_score = self.gtm_scorer.calculate_gtm_score(profile)
        profile.priority_level = self._determine_priority(profile.gtm_score)
        
        # Step 4: Store profile
        self.companies[company_name] = profile
        
        # Step 5: Generate alerts for high-value accounts
        if profile.gtm_score >= 70:
            await self._generate_alert(profile)
        
        print(f"✅ Analysis complete. GTM Score: {profile.gtm_score:.1f}")
        
        return profile
    
    def _determine_priority(self, gtm_score: float) -> str:
        """Determine priority level based on GTM score"""
        if gtm_score >= 85:
            return 'critical'
        elif gtm_score >= 70:
            return 'high'
        elif gtm_score >= 50:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_alert(self, profile: CompanyProfile) -> None:
        """Generate real-time alert for high-value accounts"""
        alert = {
            'timestamp': datetime.now(),
            'company': profile.name,
            'gtm_score': profile.gtm_score,
            'priority': profile.priority_level,
            'key_signals': [s.description for s in profile.security_signals[:3]],
            'recommended_action': 'immediate_outreach' if profile.gtm_score >= 85 else 'scheduled_outreach'
        }
        
        self.alerts.append(alert)
        print(f"🚨 HIGH-VALUE ALERT: {profile.name} (Score: {profile.gtm_score:.1f})")
    
    async def generate_outreach_campaign(self, company_name: str, contacts: List[Dict]) -> Dict:
        """Generate complete outreach campaign for a company"""
        
        if company_name not in self.companies:
            raise ValueError(f"Company {company_name} not analyzed yet")
        
        profile = self.companies[company_name]
        campaign = {
            'company': company_name,
            'gtm_score': profile.gtm_score,
            'outreach_assets': {}
        }
        
        for contact in contacts:
            contact_name = contact['name']
            contact_title = contact['title']
            
            # Generate multiple outreach assets
            email = await self.outreach_generator.generate_email_outreach(
                profile, contact_name, contact_title
            )
            
            linkedin = await self.outreach_generator.generate_linkedin_message(
                profile, contact_name
            )
            
            video_script = await self.outreach_generator.generate_video_script(
                profile, contact_name
            )
            
            campaign['outreach_assets'][contact_name] = {
                'email': email,
                'linkedin': linkedin,
                'video_script': video_script
            }
        
        return campaign
    
    def get_dashboard_data(self) -> Dict:
        """Get data for dashboard visualization"""
        if not self.companies:
            return {'error': 'No companies analyzed yet'}
        
        companies_df = pd.DataFrame([asdict(profile) for profile in self.companies.values()])
        
        return {
            'total_companies': len(self.companies),
            'high_priority': len([c for c in self.companies.values() if c.priority_level in ['high', 'critical']]),
            'avg_gtm_score': sum(c.gtm_score for c in self.companies.values()) / len(self.companies),
            'total_signals': sum(len(c.security_signals) for c in self.companies.values()),
            'companies_by_priority': companies_df['priority_level'].value_counts().to_dict(),
            'companies_by_size': companies_df['size'].value_counts().to_dict(),
            'recent_alerts': self.alerts[-10:] if self.alerts else []
        }

# Demo function to showcase the engine
async def demo_gtm_engine():
    """Demonstrate the GTM engine with sample companies"""
    
    print("🚀 Descope AI GTM Intelligence Engine Demo")
    print("=" * 50)
    
    engine = GTMEngine()
    
    # Sample companies to analyze
    demo_companies = [
        {
            'name': 'TechStartup Inc',
            'domain': 'techstartup.com',
            'github_repos': ['https://github.com/techstartup/auth-service']
        },
        {
            'name': 'ScaleUp Solutions',
            'domain': 'scaleup.io',
            'github_repos': ['https://github.com/scaleup/user-management']
        },
        {
            'name': 'Enterprise Corp',
            'domain': 'enterprisecorp.com',
            'github_repos': []
        }
    ]
    
    # Analyze each company
    for company_data in demo_companies:
        profile = await engine.analyze_company(
            company_data['name'],
            company_data['domain'],
            company_data['github_repos']
        )
        
        print(f"\n📊 {profile.name} Analysis:")
        print(f"   GTM Score: {profile.gtm_score:.1f}/100")
        print(f"   Priority: {profile.priority_level.upper()}")
        print(f"   Signals Detected: {len(profile.security_signals)}")
        print(f"   Tech Stack: {', '.join(profile.tech_stack[:3])}...")
    
    # Generate outreach campaign for highest scoring company
    best_company = max(engine.companies.values(), key=lambda c: c.gtm_score)
    
    print(f"\n🎯 Generating outreach campaign for {best_company.name}...")
    
    sample_contacts = [
        {'name': 'John Smith', 'title': 'CTO'},
        {'name': 'Sarah Johnson', 'title': 'VP Engineering'}
    ]
    
    campaign = await engine.generate_outreach_campaign(best_company.name, sample_contacts)
    
    print(f"✅ Campaign generated with {len(campaign['outreach_assets'])} personalized asset sets")
    
    # Show dashboard data
    dashboard_data = engine.get_dashboard_data()
    print(f"\n📈 Dashboard Summary:")
    print(f"   Total Companies: {dashboard_data['total_companies']}")
    print(f"   High Priority: {dashboard_data['high_priority']}")
    print(f"   Average GTM Score: {dashboard_data['avg_gtm_score']:.1f}")
    print(f"   Total Signals: {dashboard_data['total_signals']}")
    
    return engine, campaign

if __name__ == "__main__":
    # Set up environment variables reminder
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please set OPENAI_API_KEY environment variable")
        print("   You can get an API key from: https://platform.openai.com/api-keys")
        print("   Add it to a .env file: OPENAI_API_KEY=your_key_here")
    else:
        # Run the demo
        asyncio.run(demo_gtm_engine())
