"""Streamlit dashboard for Career Skills Gap Analyzer."""
import streamlit as st
import json
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Career Skills Gap Analyzer",
    page_icon="🎯",
    layout="wide"
)

# Import tools
from tools.cache_db import get_from_cache, set_in_cache, clear_cache
from tools.export_tools import export_to_json, export_to_csv

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🎯 Career Skills Gap Analyzer</h1>', unsafe_allow_html=True)
st.markdown("**Analyze your resume, identify skill gaps, and get personalized learning recommendations**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Upload resume
    uploaded_file = st.file_uploader(
        "📄 Upload Your Resume",
        type=["pdf", "docx", "txt"],
        help="Upload your resume in PDF, DOCX, or TXT format"
    )
    
    st.divider()
    
    # Preferences
    st.subheader("Preferences")
    target_role = st.text_input("🎯 Target Role", value="Data Scientist", help="Enter your target job role")
    experience_level = st.selectbox("📊 Experience Level", ["Student", "Junior", "Mid", "Senior"])
    location = st.text_input("📍 Location", value="United States")
    time_budget_weeks = st.slider("⏳ Time Budget (weeks)", 4, 52, 12)
    
    st.divider()
    
    # Actions
    if st.button("🗑️ Clear Cache", help="Clear all cached data"):
        clear_cache()
        st.success("Cache cleared!")
    
    if st.button("🔄 Run Analysis", type="primary", disabled=not uploaded_file):
        st.session_state.run_analysis = True

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 Resume Review",
    "💼 Role Analysis", 
    "📊 Gap Analysis",
    "📚 Learning Path",
    "📥 Export"
])

# Tab 1: Resume Review
with tab1:
    st.markdown('<div class="section-header">📄 Resume Extraction Review</div>', unsafe_allow_html=True)
    
    if uploaded_file:
        st.info("Resume uploaded successfully! Click 'Run Analysis' to extract information.")
        
        # Mock extracted data (replace with actual extraction)
        if st.session_state.get("run_analysis"):
            with st.spinner("Extracting resume information..."):
                extracted_data = {
                    "candidate": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "location": "San Francisco, CA",
                        "experience_level": experience_level
                    },
                    "skills": [
                        {"name": "Python", "type": "language", "proficiency": "Advanced"},
                        {"name": "SQL", "type": "language", "proficiency": "Intermediate"},
                        {"name": "Docker", "type": "tool", "proficiency": "Beginner"}
                    ],
                    "roles_detected": [
                        {"title": "Software Engineer", "start_year": 2020, "end_year": 2023}
                    ]
                }
                
                st.session_state.extracted_data = extracted_data
        
        if "extracted_data" in st.session_state:
            data = st.session_state.extracted_data
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 Candidate Info")
                st.write(f"**Name:** {data['candidate']['name']}")
                st.write(f"**Email:** {data['candidate']['email']}")
                st.write(f"**Location:** {data['candidate']['location']}")
                st.write(f"**Level:** {data['candidate']['experience_level']}")
            
            with col2:
                st.subheader("💼 Work History")
                for role in data.get("roles_detected", []):
                    st.write(f"**{role['title']}** ({role['start_year']}-{role['end_year']})")
            
            st.subheader("🛠️ Skills Detected")
            skills_df = {
                "Skill": [s["name"] for s in data["skills"]],
                "Type": [s["type"] for s in data["skills"]],
                "Proficiency": [s["proficiency"] for s in data["skills"]]
            }
            st.table(skills_df)
    else:
        st.warning("Please upload your resume to begin analysis.")

# Tab 2: Role Analysis
with tab2:
    st.markdown('<div class="section-header">💼 Role & Market Analysis</div>', unsafe_allow_html=True)
    
    if "extracted_data" in st.session_state:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Official Title", target_role)
        
        with col2:
            st.metric("SOC Code", "15-2051.00")
        
        with col3:
            st.metric("10-Year Growth", "+21.5%", delta="Future-safe")
        
        st.divider()
        
        # Growth forecast visualization
        st.subheader("📈 Job Growth Forecast")
        growth_data = {
            "category": "Future-safe",
            "growth_percent": 21.5,
            "current_workforce": 1847900,
            "median_wage": 120730
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Growth Rate", f"{growth_data['growth_percent']}%")
            st.metric("Current Workforce", f"{growth_data['current_workforce']:,}")
        
        with col2:
            st.metric("Category", growth_data['category'])
            st.metric("Median Wage", f"${growth_data['median_wage']:,}")
        
        # Progress bar for growth
        st.progress(min(growth_data['growth_percent'] / 30, 1.0))
        
        if growth_data['growth_percent'] >= 10:
            st.success("✅ This role shows strong future demand! Great choice for career investment.")
        elif growth_data['growth_percent'] >= 0:
            st.info("ℹ️ This role shows stable demand. Focus on staying current with skills.")
        else:
            st.warning("⚠️ This role shows declining demand. Consider pivoting to growing fields.")

# Tab 3: Gap Analysis
with tab3:
    st.markdown('<div class="section-header">📊 Skills Gap Analysis</div>', unsafe_allow_html=True)
    
    if "extracted_data" in st.session_state:
        # Mock gap analysis
        gap_analysis = [
            {"skill": "AWS", "market_rank": 2, "priority": "High", "reasoning": "Top 5 in demand; cloud skills critical"},
            {"skill": "Kubernetes", "market_rank": 3, "priority": "High", "reasoning": "Container orchestration essential"},
            {"skill": "TensorFlow", "market_rank": 8, "priority": "Medium", "reasoning": "ML framework in top 10"}
        ]
        
        st.subheader("❌ Missing Skills (Prioritized)")
        
        for gap in gap_analysis:
            priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[gap["priority"]]
            
            with st.expander(f"{priority_color} **{gap['skill']}** - {gap['priority']} Priority (Market Rank #{gap['market_rank']})"):
                st.write(f"**Reasoning:** {gap['reasoning']}")
                
                # Recommendation
                if gap["priority"] == "High":
                    st.error("⚠️ **Action:** Prioritize learning this skill immediately.")
                elif gap["priority"] == "Medium":
                    st.warning("💡 **Action:** Add to learning roadmap after high-priority skills.")
                else:
                    st.info("ℹ️ **Action:** Nice-to-have; learn if time permits.")
        
        # Radar chart placeholder
        st.divider()
        st.subheader("📊 Skills Comparison")
        st.info("📊 Radar chart visualization would go here comparing your skills vs. market demands.")

# Tab 4: Learning Path
with tab4:
    st.markdown('<div class="section-header">📚 Personalized Learning Path</div>', unsafe_allow_html=True)
    
    if "extracted_data" in st.session_state:
        learning_path = ["AWS", "Kubernetes", "TensorFlow", "Docker", "CI/CD"]
        
        st.subheader(f"🎯 Recommended Path ({time_budget_weeks} weeks)")
        
        weeks_per_skill = time_budget_weeks // len(learning_path)
        
        for idx, skill in enumerate(learning_path, 1):
            with st.expander(f"**Week {(idx-1)*weeks_per_skill + 1}-{idx*weeks_per_skill}: {skill}**"):
                st.write(f"**Priority:** {'High' if idx <= 2 else 'Medium'}")
                st.write(f"**Estimated Time:** {weeks_per_skill} weeks")
                
                # Mock resources
                st.subheader("📺 Recommended Resources")
                
                resources = [
                    {
                        "title": f"{skill} Complete Tutorial",
                        "channel": "freeCodeCamp",
                        "duration_minutes": 180,
                        "views": 500000,
                        "url": "https://youtube.com/watch?v=example"
                    }
                ]
                
                for resource in resources:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"🎥 **{resource['title']}**")
                        st.caption(f"by {resource['channel']} • {resource['duration_minutes']} min • {resource['views']:,} views")
                    
                    with col2:
                        st.link_button("▶️ Watch", resource['url'])

# Tab 5: Export
with tab5:
    st.markdown('<div class="section-header">📥 Export Your Report</div>', unsafe_allow_html=True)
    
    if "extracted_data" in st.session_state:
        st.write("Download your complete analysis report in your preferred format.")
        
        # Prepare export data
        export_data = {
            "candidate": st.session_state.extracted_data.get("candidate", {}),
            "target_role": target_role,
            "gap_analysis": [
                {"skill": "AWS", "market_rank": 2, "priority": "High"},
                {"skill": "Kubernetes", "market_rank": 3, "priority": "High"}
            ],
            "recommended_learning_path": ["AWS", "Kubernetes", "TensorFlow"],
            "estimated_weeks": time_budget_weeks
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON export
            json_data = export_to_json(export_data)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name="career_analysis.json",
                mime="application/json"
            )
        
        with col2:
            # CSV export
            csv_data = export_to_csv(export_data)
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name="career_analysis.csv",
                mime="text/csv"
            )
        
        st.divider()
        
        # Preview
        st.subheader("📋 Report Preview (JSON)")
        st.json(export_data)
    else:
        st.warning("Please complete the analysis first before exporting.")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        Built with ❤️ using Streamlit | Career Skills Gap Analyzer v1.0
    </div>
""", unsafe_allow_html=True)