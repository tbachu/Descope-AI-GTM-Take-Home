"""
Descope AI GTM Intelligence Dashboard
====================================

Interactive Streamlit dashboard for the AI GTM engine
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
import json
from main import GTMEngine, demo_gtm_engine

# Page configuration
st.set_page_config(
    page_title="Descope AI GTM Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-container {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.high-priority {
    border-left: 4px solid #ff4b4b;
}
.medium-priority {
    border-left: 4px solid #ffa500;
}
.low-priority {
    border-left: 4px solid #00cc44;
}
.signal-card {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #e1e5e9;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_demo_data():
    """Load demo data for the dashboard"""
    return asyncio.run(demo_gtm_engine())

def main():
    # Header
    st.title("🎯 Descope AI GTM Intelligence Engine")
    st.markdown("**Intelligent prospect identification and personalized outreach generation**")
    
    # Sidebar
    st.sidebar.title("🔧 Controls")
    
    # Initialize or load engine
    if 'engine' not in st.session_state:
        with st.spinner("Loading GTM Intelligence Engine..."):
            engine, campaign = load_demo_data()
            st.session_state.engine = engine
            st.session_state.campaign = campaign
    
    engine = st.session_state.engine
    dashboard_data = engine.get_dashboard_data()
    
    # Sidebar metrics
    st.sidebar.metric("Companies Analyzed", dashboard_data['total_companies'])
    st.sidebar.metric("High Priority Accounts", dashboard_data['high_priority'])
    st.sidebar.metric("Avg GTM Score", f"{dashboard_data['avg_gtm_score']:.1f}")
    st.sidebar.metric("Security Signals", dashboard_data['total_signals'])
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🏢 Companies", 
        "🚨 Alerts", 
        "📧 Outreach", 
        "🔍 Analysis"
    ])
    
    with tab1:
        show_overview(engine, dashboard_data)
    
    with tab2:
        show_companies(engine)
    
    with tab3:
        show_alerts(engine)
    
    with tab4:
        show_outreach(engine)
    
    with tab5:
        show_analysis_tools(engine)

def show_overview(engine, dashboard_data):
    """Show overview dashboard"""
    st.header("📊 GTM Intelligence Overview")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Companies",
            dashboard_data['total_companies'],
            delta=f"+{dashboard_data['total_companies']} this session"
        )
    
    with col2:
        st.metric(
            "High Priority",
            dashboard_data['high_priority'],
            delta=f"{dashboard_data['high_priority']/dashboard_data['total_companies']*100:.0f}% of total"
        )
    
    with col3:
        st.metric(
            "Avg GTM Score",
            f"{dashboard_data['avg_gtm_score']:.1f}",
            delta="Target: 70+"
        )
    
    with col4:
        st.metric(
            "Security Signals",
            dashboard_data['total_signals'],
            delta=f"Avg: {dashboard_data['total_signals']/dashboard_data['total_companies']:.1f} per company"
        )
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Priority distribution
        priority_data = dashboard_data['companies_by_priority']
        fig_priority = px.pie(
            values=list(priority_data.values()),
            names=list(priority_data.keys()),
            title="Companies by Priority Level",
            color_discrete_map={
                'critical': '#ff4b4b',
                'high': '#ff8c00',
                'medium': '#ffd700',
                'low': '#90ee90'
            }
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    with col2:
        # Company size distribution
        size_data = dashboard_data['companies_by_size']
        fig_size = px.bar(
            x=list(size_data.keys()),
            y=list(size_data.values()),
            title="Companies by Size",
            color=list(size_data.values()),
            color_continuous_scale="viridis"
        )
        fig_size.update_layout(showlegend=False)
        st.plotly_chart(fig_size, use_container_width=True)
    
    # GTM Score distribution
    if engine.companies:
        scores = [c.gtm_score for c in engine.companies.values()]
        fig_scores = px.histogram(
            x=scores,
            nbins=10,
            title="GTM Score Distribution",
            labels={'x': 'GTM Score', 'y': 'Number of Companies'}
        )
        fig_scores.add_vline(x=70, line_dash="dash", line_color="red", 
                            annotation_text="Target Threshold (70)")
        st.plotly_chart(fig_scores, use_container_width=True)

def show_companies(engine):
    """Show companies analysis"""
    st.header("🏢 Company Intelligence")
    
    if not engine.companies:
        st.warning("No companies analyzed yet. Run the analysis first.")
        return
    
    # Company selector
    company_names = list(engine.companies.keys())
    selected_company = st.selectbox("Select Company", company_names)
    
    if selected_company:
        profile = engine.companies[selected_company]
        
        # Company header
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"🏢 {profile.name}")
            st.write(f"**Domain:** {profile.domain}")
            st.write(f"**Industry:** {profile.industry}")
        
        with col2:
            priority_colors = {
                'critical': '🔴',
                'high': '🟠', 
                'medium': '🟡',
                'low': '🟢'
            }
            st.metric("GTM Score", f"{profile.gtm_score:.1f}/100")
            st.write(f"**Priority:** {priority_colors[profile.priority_level]} {profile.priority_level.title()}")
        
        with col3:
            st.metric("Company Size", profile.size.title())
            st.metric("Employees", profile.employee_count)
        
        # Tech stack
        st.subheader("💻 Technology Stack")
        tech_cols = st.columns(len(profile.tech_stack) if profile.tech_stack else 1)
        for i, tech in enumerate(profile.tech_stack):
            with tech_cols[i % len(tech_cols)]:
                st.button(tech, disabled=True)
        
        # Security signals
        st.subheader("🔍 Security Signals Detected")
        
        if profile.security_signals:
            for signal in profile.security_signals:
                severity_color = "🔴" if signal.severity >= 8 else "🟠" if signal.severity >= 6 else "🟡" if signal.severity >= 4 else "🟢"
                
                with st.expander(f"{severity_color} {signal.signal_type.replace('_', ' ').title()} (Severity: {signal.severity}/10)"):
                    st.write(f"**Source:** {signal.source}")
                    st.write(f"**Description:** {signal.description}")
                    st.write(f"**Confidence:** {signal.confidence:.1%}")
                    st.write(f"**Detected:** {signal.detected_at.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**URL:** {signal.source_url}")
                    
                    if signal.raw_content:
                        st.code(signal.raw_content[:200] + "..." if len(signal.raw_content) > 200 else signal.raw_content)
        else:
            st.info("No security signals detected for this company.")

def show_alerts(engine):
    """Show real-time alerts"""
    st.header("🚨 Real-Time Alerts")
    
    if not engine.alerts:
        st.info("No alerts generated yet.")
        return
    
    # Recent alerts
    st.subheader("Recent High-Value Account Alerts")
    
    for alert in reversed(engine.alerts[-10:]):  # Show last 10 alerts
        priority_icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{priority_icons[alert['priority']]} {alert['company']}**")
                st.write(f"GTM Score: {alert['gtm_score']:.1f}")
            
            with col2:
                st.write(f"**Priority:** {alert['priority'].title()}")
                st.write(f"**Action:** {alert['recommended_action'].replace('_', ' ').title()}")
            
            with col3:
                st.write(f"**Time:** {alert['timestamp'].strftime('%H:%M:%S')}")
                if st.button("View Details", key=f"alert_{alert['timestamp']}"):
                    st.session_state.selected_company = alert['company']
            
            # Key signals
            if alert['key_signals']:
                with st.expander("Key Signals"):
                    for signal in alert['key_signals']:
                        st.write(f"• {signal}")
            
            st.divider()

def show_outreach(engine):
    """Show outreach generation"""
    st.header("📧 Outreach Generation")
    
    if not engine.companies:
        st.warning("No companies analyzed yet.")
        return
    
    # Company and contact selection
    col1, col2 = st.columns(2)
    
    with col1:
        company_names = list(engine.companies.keys())
        selected_company = st.selectbox("Select Company", company_names, key="outreach_company")
    
    with col2:
        contact_name = st.text_input("Contact Name", value="John Smith")
        contact_title = st.text_input("Contact Title", value="CTO")
    
    if st.button("Generate Outreach Assets", type="primary"):
        if selected_company and contact_name and contact_title:
            profile = engine.companies[selected_company]
            
            with st.spinner("Generating personalized outreach assets..."):
                # Generate assets
                try:
                    contacts = [{'name': contact_name, 'title': contact_title}]
                    campaign = asyncio.run(engine.generate_outreach_campaign(selected_company, contacts))
                    
                    assets = campaign['outreach_assets'][contact_name]
                    
                    # Display generated assets
                    st.success("✅ Outreach assets generated successfully!")
                    
                    # Email
                    st.subheader("📧 Email Outreach")
                    st.text_area("Generated Email", assets['email'], height=200)
                    
                    # LinkedIn
                    st.subheader("💼 LinkedIn Message")
                    st.text_area("Generated LinkedIn Message", assets['linkedin'], height=100)
                    
                    # Video script
                    st.subheader("🎥 Video Script")
                    st.text_area("Generated Video Script", assets['video_script'], height=250)
                    
                    # Download options
                    st.subheader("💾 Export Options")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.download_button(
                            "Download Email",
                            assets['email'],
                            file_name=f"{selected_company}_email.txt"
                        )
                    with col2:
                        st.download_button(
                            "Download LinkedIn",
                            assets['linkedin'],
                            file_name=f"{selected_company}_linkedin.txt"
                        )
                    with col3:
                        st.download_button(
                            "Download Video Script",
                            assets['video_script'],
                            file_name=f"{selected_company}_video.txt"
                        )
                
                except Exception as e:
                    st.error(f"Error generating outreach: {e}")

def show_analysis_tools(engine):
    """Show analysis and configuration tools"""
    st.header("🔍 Analysis Tools")
    
    # New company analysis
    st.subheader("🆕 Analyze New Company")
    
    with st.form("analyze_company"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", placeholder="e.g., TechCorp Inc")
            domain = st.text_input("Company Domain", placeholder="e.g., techcorp.com")
        
        with col2:
            github_repos = st.text_area(
                "GitHub Repositories (one per line)",
                placeholder="https://github.com/company/repo1\nhttps://github.com/company/repo2"
            )
        
        submitted = st.form_submit_button("🔍 Analyze Company", type="primary")
        
        if submitted and company_name and domain:
            repos = [repo.strip() for repo in github_repos.split('\n') if repo.strip()] if github_repos else []
            
            with st.spinner(f"Analyzing {company_name}..."):
                try:
                    profile = asyncio.run(engine.analyze_company(company_name, domain, repos))
                    st.success(f"✅ {company_name} analyzed successfully!")
                    st.write(f"**GTM Score:** {profile.gtm_score:.1f}/100")
                    st.write(f"**Priority:** {profile.priority_level.title()}")
                    st.write(f"**Signals Detected:** {len(profile.security_signals)}")
                    
                    # Refresh the page data
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
    
    st.divider()
    
    # Batch analysis
    st.subheader("📊 Batch Analysis")
    
    uploaded_file = st.file_uploader("Upload CSV with companies", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Preview:", df.head())
        
        if st.button("Run Batch Analysis"):
            progress_bar = st.progress(0)
            
            for i, row in df.iterrows():
                try:
                    repos = row.get('github_repos', '').split(',') if 'github_repos' in row else []
                    asyncio.run(engine.analyze_company(row['company_name'], row['domain'], repos))
                    progress_bar.progress((i + 1) / len(df))
                except Exception as e:
                    st.warning(f"Failed to analyze {row['company_name']}: {e}")
            
            st.success("Batch analysis complete!")
            st.rerun()
    
    st.divider()
    
    # Export data
    st.subheader("💾 Export Data")
    
    if engine.companies:
        # Prepare export data
        export_data = []
        for company_name, profile in engine.companies.items():
            export_data.append({
                'company_name': profile.name,
                'domain': profile.domain,
                'industry': profile.industry,
                'size': profile.size,
                'employee_count': profile.employee_count,
                'gtm_score': profile.gtm_score,
                'priority_level': profile.priority_level,
                'tech_stack': ', '.join(profile.tech_stack),
                'signal_count': len(profile.security_signals),
                'funding_stage': profile.funding_stage
            })
        
        export_df = pd.DataFrame(export_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download CSV",
                export_df.to_csv(index=False),
                file_name=f"gtm_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.download_button(
                "📥 Download JSON",
                json.dumps(export_data, indent=2, default=str),
                file_name=f"gtm_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
