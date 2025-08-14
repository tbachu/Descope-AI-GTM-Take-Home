"""
Real-time Monitoring and Alert System
=====================================

Automated monitoring system that continuously scans for new signals
and alerts the sales team in real-time.
"""

import asyncio
import schedule
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from main import GTMEngine, SecuritySignal

class RealTimeMonitor:
    """Real-time monitoring system for GTM intelligence"""
    
    def __init__(self, gtm_engine: GTMEngine):
        self.gtm_engine = gtm_engine
        self.monitoring_active = False
        self.monitored_sources = {
            'github': True,
            'reddit': True,
            'hacker_news': True,
            'job_postings': True
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'gtm_score': 70,
            'signal_severity': 7,
            'new_signals_count': 3
        }
        
        # Notification channels
        self.notification_channels = {
            'email': True,
            'slack': False,  # Would integrate with Slack API
            'teams': False   # Would integrate with Teams API
        }
    
    async def start_monitoring(self):
        """Start the real-time monitoring system"""
        print("🔄 Starting real-time GTM monitoring...")
        self.monitoring_active = True
        
        # Schedule different monitoring tasks
        schedule.every(15).minutes.do(self._monitor_github_activity)
        schedule.every(30).minutes.do(self._monitor_social_signals)
        schedule.every(1).hours.do(self._monitor_job_postings)
        schedule.every(6).hours.do(self._generate_intelligence_digest)
        
        # Run monitoring loop
        while self.monitoring_active:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        print("⏹️ Stopping GTM monitoring...")
        self.monitoring_active = False
    
    async def _monitor_github_activity(self):
        """Monitor GitHub for new activity indicating security needs"""
        print("🔍 Monitoring GitHub activity...")
        
        # Keywords that indicate authentication/security needs
        security_keywords = [
            'authentication', 'auth', 'login', 'sso', 'oauth',
            'security', 'user management', 'permissions', 'rbac',
            'password', 'token', 'jwt', 'session', 'mfa'
        ]
        
        # Simulate GitHub monitoring (would use GitHub API in production)
        new_signals = await self._scan_github_for_keywords(security_keywords)
        
        if new_signals:
            await self._process_new_signals(new_signals)
    
    async def _scan_github_for_keywords(self, keywords: List[str]) -> List[SecuritySignal]:
        """Scan GitHub repositories for security-related keywords"""
        # Simulate finding new repositories/issues with security keywords
        mock_signals = [
            SecuritySignal(
                company_name="NewTech Solutions",
                signal_type="auth_implementation",
                source="github",
                description="Repository shows custom JWT implementation with potential security issues",
                severity=8,
                confidence=0.85,
                detected_at=datetime.now(),
                source_url="https://github.com/newtech/auth-service/issues/42",
                raw_content="We're struggling with our custom auth implementation..."
            ),
            SecuritySignal(
                company_name="DataCorp Inc",
                signal_type="sso_requirement",
                source="github",
                description="Issue requesting SSO implementation for enterprise customers",
                severity=9,
                confidence=0.9,
                detected_at=datetime.now(),
                source_url="https://github.com/datacorp/platform/issues/128",
                raw_content="Enterprise customers are requesting SSO integration..."
            )
        ]
        
        return mock_signals
    
    async def _monitor_social_signals(self):
        """Monitor social media and forums for security discussions"""
        print("📱 Monitoring social signals...")
        
        # Keywords for social monitoring
        social_keywords = [
            'authentication nightmare', 'auth headache', 'user management pain',
            'sso integration', 'security compliance', 'identity provider'
        ]
        
        new_signals = await self._scan_social_media(social_keywords)
        
        if new_signals:
            await self._process_new_signals(new_signals)
    
    async def _scan_social_media(self, keywords: List[str]) -> List[SecuritySignal]:
        """Scan social media for relevant discussions"""
        # Mock social media signals
        mock_signals = [
            SecuritySignal(
                company_name="StartupXYZ",
                signal_type="security_pain_point",
                source="reddit",
                description="Founder discussing authentication challenges on r/entrepreneur",
                severity=7,
                confidence=0.75,
                detected_at=datetime.now(),
                source_url="https://reddit.com/r/entrepreneur/post/auth_struggles",
                raw_content="Our startup is growing and manual user management is killing us..."
            )
        ]
        
        return mock_signals
    
    async def _monitor_job_postings(self):
        """Monitor job postings for security-related hiring"""
        print("💼 Monitoring job postings...")
        
        # Look for job postings that indicate security/auth needs
        job_keywords = [
            'security engineer', 'auth specialist', 'identity management',
            'sso implementation', 'security architect'
        ]
        
        new_signals = await self._scan_job_postings(job_keywords)
        
        if new_signals:
            await self._process_new_signals(new_signals)
    
    async def _scan_job_postings(self, keywords: List[str]) -> List[SecuritySignal]:
        """Scan job postings for security-related positions"""
        # Mock job posting signals
        mock_signals = [
            SecuritySignal(
                company_name="GrowthCorp",
                signal_type="security_hiring",
                source="job_posting",
                description="Company hiring security engineer with SSO experience",
                severity=6,
                confidence=0.8,
                detected_at=datetime.now(),
                source_url="https://jobs.company.com/security-engineer",
                raw_content="Looking for security engineer to implement SSO and user management..."
            )
        ]
        
        return mock_signals
    
    async def _process_new_signals(self, signals: List[SecuritySignal]):
        """Process newly detected signals"""
        high_priority_signals = []
        
        for signal in signals:
            # Add to existing company or create new profile
            if signal.company_name in self.gtm_engine.companies:
                profile = self.gtm_engine.companies[signal.company_name]
                profile.security_signals.append(signal)
                
                # Recalculate GTM score
                old_score = profile.gtm_score
                profile.gtm_score = self.gtm_engine.gtm_scorer.calculate_gtm_score(profile)
                
                # Check if this triggers an alert
                if (profile.gtm_score >= self.alert_thresholds['gtm_score'] or
                    signal.severity >= self.alert_thresholds['signal_severity'] or
                    profile.gtm_score > old_score + 10):  # Significant score increase
                    
                    high_priority_signals.append(signal)
            else:
                # New company detected - do quick analysis
                try:
                    profile = await self.gtm_engine.analyze_company(
                        signal.company_name,
                        f"{signal.company_name.lower().replace(' ', '')}.com",
                        []
                    )
                    
                    if profile.gtm_score >= self.alert_thresholds['gtm_score']:
                        high_priority_signals.append(signal)
                        
                except Exception as e:
                    print(f"Error analyzing new company {signal.company_name}: {e}")
        
        # Send alerts for high-priority signals
        if high_priority_signals:
            await self._send_real_time_alerts(high_priority_signals)
    
    async def _send_real_time_alerts(self, signals: List[SecuritySignal]):
        """Send real-time alerts for high-priority signals"""
        print(f"🚨 Sending alerts for {len(signals)} high-priority signals")
        
        for signal in signals:
            alert_data = {
                'timestamp': datetime.now(),
                'signal': signal,
                'company_profile': self.gtm_engine.companies.get(signal.company_name),
                'recommended_actions': self._generate_recommended_actions(signal)
            }
            
            # Send via configured channels
            if self.notification_channels['email']:
                await self._send_email_alert(alert_data)
            
            if self.notification_channels['slack']:
                await self._send_slack_alert(alert_data)
            
            # Add to engine alerts
            self.gtm_engine.alerts.append({
                'timestamp': datetime.now(),
                'company': signal.company_name,
                'gtm_score': self.gtm_engine.companies[signal.company_name].gtm_score if signal.company_name in self.gtm_engine.companies else 0,
                'priority': 'high',
                'key_signals': [signal.description],
                'recommended_action': 'immediate_outreach'
            })
    
    def _generate_recommended_actions(self, signal: SecuritySignal) -> List[str]:
        """Generate recommended actions based on signal type"""
        actions = []
        
        if signal.signal_type == 'auth_implementation':
            actions = [
                "Schedule demo of Descope's authentication flows",
                "Send technical documentation on JWT best practices",
                "Offer security audit of current implementation"
            ]
        elif signal.signal_type == 'sso_requirement':
            actions = [
                "Provide SSO implementation timeline and pricing",
                "Schedule call with enterprise sales specialist",
                "Send case studies of similar SSO implementations"
            ]
        elif signal.signal_type == 'security_hiring':
            actions = [
                "Reach out to hiring manager about security solutions",
                "Offer to reduce need for security engineer hire",
                "Provide ROI calculator for outsourcing auth"
            ]
        else:
            actions = [
                "Research company's specific pain points",
                "Schedule discovery call",
                "Send relevant case study"
            ]
        
        return actions
    
    async def _send_email_alert(self, alert_data: Dict):
        """Send email alert to sales team"""
        # In production, would use proper email service
        print(f"📧 Email alert sent for {alert_data['signal'].company_name}")
        
        email_content = f"""
        🚨 HIGH-PRIORITY GTM ALERT 🚨
        
        Company: {alert_data['signal'].company_name}
        Signal: {alert_data['signal'].signal_type.replace('_', ' ').title()}
        Severity: {alert_data['signal'].severity}/10
        Source: {alert_data['signal'].source}
        
        Description: {alert_data['signal'].description}
        
        Recommended Actions:
        {chr(10).join(f"• {action}" for action in alert_data['recommended_actions'])}
        
        Source URL: {alert_data['signal'].source_url}
        """
        
        # Would send actual email here
        print(email_content)
    
    async def _send_slack_alert(self, alert_data: Dict):
        """Send Slack alert to sales channel"""
        # Would integrate with Slack API
        print(f"💬 Slack alert sent for {alert_data['signal'].company_name}")
    
    async def _generate_intelligence_digest(self):
        """Generate periodic intelligence digest"""
        print("📊 Generating intelligence digest...")
        
        # Aggregate insights from last 6 hours
        recent_signals = []
        cutoff_time = datetime.now() - timedelta(hours=6)
        
        for company_profile in self.gtm_engine.companies.values():
            for signal in company_profile.security_signals:
                if signal.detected_at > cutoff_time:
                    recent_signals.append(signal)
        
        if recent_signals:
            digest = self._create_intelligence_digest(recent_signals)
            await self._send_digest(digest)
    
    def _create_intelligence_digest(self, signals: List[SecuritySignal]) -> str:
        """Create intelligence digest from recent signals"""
        signal_types = {}
        companies = set()
        
        for signal in signals:
            companies.add(signal.company_name)
            signal_types[signal.signal_type] = signal_types.get(signal.signal_type, 0) + 1
        
        digest = f"""
        📊 GTM Intelligence Digest - {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        📈 Summary (Last 6 Hours):
        • {len(signals)} new signals detected
        • {len(companies)} companies with activity
        • {len([s for s in signals if s.severity >= 7])} high-severity signals
        
        🔥 Top Signal Types:
        {chr(10).join(f"• {signal_type.replace('_', ' ').title()}: {count}" for signal_type, count in sorted(signal_types.items(), key=lambda x: x[1], reverse=True))}
        
        🎯 Companies to Prioritize:
        {chr(10).join(f"• {company}" for company in list(companies)[:5])}
        
        💡 Key Insights:
        • Authentication challenges increasing across startups
        • SSO requests trending up in enterprise segment
        • Security hiring indicates immediate pain points
        """
        
        return digest
    
    async def _send_digest(self, digest: str):
        """Send intelligence digest to team"""
        print("📬 Sending intelligence digest...")
        print(digest)

# Webhook system for real-time integrations
class WebhookHandler:
    """Handle webhooks from various services for real-time updates"""
    
    def __init__(self, gtm_engine: GTMEngine, monitor: RealTimeMonitor):
        self.gtm_engine = gtm_engine
        self.monitor = monitor
    
    async def handle_github_webhook(self, payload: Dict):
        """Handle GitHub webhook for repository events"""
        if payload.get('action') in ['opened', 'created']:
            # New issue or PR created
            if any(keyword in payload.get('title', '').lower() for keyword in ['auth', 'security', 'login']):
                signal = SecuritySignal(
                    company_name=payload.get('repository', {}).get('owner', {}).get('login', 'Unknown'),
                    signal_type='github_activity',
                    source='github_webhook',
                    description=f"New {payload.get('action')} activity: {payload.get('title')}",
                    severity=5,
                    confidence=0.7,
                    detected_at=datetime.now(),
                    source_url=payload.get('html_url', ''),
                    raw_content=payload.get('body', '')[:300]
                )
                
                await self.monitor._process_new_signals([signal])
    
    async def handle_slack_webhook(self, payload: Dict):
        """Handle Slack webhook for team communications"""
        # Could monitor Slack channels for customer mentions
        pass
    
    async def handle_crm_webhook(self, payload: Dict):
        """Handle CRM webhook for prospect updates"""
        # Integration with CRM systems like HubSpot, Salesforce
        pass

# Example usage and demo
async def demo_monitoring_system():
    """Demonstrate the real-time monitoring system"""
    print("🚀 Descope GTM Real-Time Monitoring Demo")
    print("=" * 50)
    
    # Initialize GTM engine
    from main import demo_gtm_engine
    engine, _ = await demo_gtm_engine()
    
    # Initialize monitoring system
    monitor = RealTimeMonitor(engine)
    webhook_handler = WebhookHandler(engine, monitor)
    
    print("\n📡 Starting monitoring systems...")
    
    # Simulate some real-time events
    await monitor._monitor_github_activity()
    await monitor._monitor_social_signals()
    await monitor._monitor_job_postings()
    
    # Simulate webhook events
    github_webhook_payload = {
        'action': 'opened',
        'title': 'Need help with authentication implementation',
        'repository': {'owner': {'login': 'TechStartup'}},
        'html_url': 'https://github.com/techstartup/issues/1',
        'body': 'We need to implement user authentication for our SaaS platform...'
    }
    
    await webhook_handler.handle_github_webhook(github_webhook_payload)
    
    # Generate intelligence digest
    await monitor._generate_intelligence_digest()
    
    print("\n✅ Monitoring demo complete!")
    print(f"📊 Total alerts generated: {len(engine.alerts)}")

if __name__ == "__main__":
    asyncio.run(demo_monitoring_system())
