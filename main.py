"""Main execution script for Short-Term Skills Agent."""
import json
from typing import Dict, Optional
from datetime import datetime

from agents.short_term_skills_agent import create_short_term_skills_agent
from tools.adzuna_tools import fetch_job_postings, get_job_descriptions
from tools.skill_extraction import (
    extract_skills_from_descriptions,
    calculate_confidence_score,
    merge_similar_skills,
    filter_low_quality_skills
)
from tools.llm_analysis import (
    analyze_skills_with_gemini,
    analyze_skill_trends_with_gemini
)
from tools.cache_tools import (
    get_cached_skills,
    cache_skills_data,
    get_cache_stats
)


def analyze_role_skills(
    job_title: str,
    soc_code: Optional[str] = None,
    use_cache: bool = True,
    use_gemini: bool = True,
    min_jobs: int = 100
) -> Dict:
    """
    Main function to analyze skills for a given role.
    
    Args:
        job_title: Job title to analyze
        soc_code: Optional SOC code
        use_cache: Whether to use cached data
        use_gemini: Whether to use Gemini for analysis
        min_jobs: Minimum number of jobs to fetch
    
    Returns:
        Dictionary with skills analysis results
    """
    print(f"📊 Analyzing skills for: {job_title}")
    print(f"🔍 SOC Code: {soc_code or 'Not provided'}")
    print()
    
    # Check cache first
    if use_cache:
        print("💾 Checking cache...")
        cached_data = get_cached_skills(job_title, soc_code)
        if cached_data:
            print("✅ Found cached data!")
            return cached_data
        print("⚠️  No cache found, fetching fresh data...")
    
    # Fetch job postings
    print(f"🌐 Fetching job postings from Adzuna...")
    job_data = fetch_job_postings(
        job_title=job_title,
        max_days_old=90,
        results_per_page=50,
        max_pages=3
    )
    
    jobs = job_data["jobs"]
    job_count = len(jobs)
    print(f"✅ Retrieved {job_count} job postings")
    
    if job_count < min_jobs:
        print(f"⚠️  Warning: Only found {job_count} jobs (target: {min_jobs}+)")
    
    # Extract descriptions
    descriptions = get_job_descriptions(jobs)
    print(f"📝 Extracted {len(descriptions)} valid job descriptions")
    
    if len(descriptions) < 10:
        return {
            "error": "Insufficient data",
            "message": f"Only found {len(descriptions)} valid job descriptions",
            "role": job_title
        }
    
    # Extract skills
    print()
    if use_gemini:
        print("🤖 Analyzing skills with Gemini 2.5...")
        top_skills = analyze_skills_with_gemini(
            descriptions=descriptions,
            job_role=job_title,
            top_n=20
        )
        
        # Fallback to keyword extraction if Gemini fails
        if not top_skills:
            print("⚠️  Gemini analysis failed, using keyword extraction...")
            top_skills = extract_skills_from_descriptions(descriptions, top_n=20)
    else:
        print("🔤 Extracting skills using keyword matching...")
        top_skills = extract_skills_from_descriptions(descriptions, top_n=20)
    
    # Post-processing
    print("🔧 Post-processing skills...")
    top_skills = merge_similar_skills(top_skills)
    top_skills = filter_low_quality_skills(top_skills, min_frequency=5)
    top_skills = top_skills[:20]  # Ensure we have max 20
    
    # Calculate confidence
    confidence = calculate_confidence_score(job_count, len(top_skills))
    
    # Build result
    result = {
        "role": job_title,
        "soc_code": soc_code or "Not provided",
        "top_skills": top_skills,
        "data_source": f"Adzuna (90 days, {job_count} jobs)",
        "confidence": confidence,
        "cache_ttl_seconds": 86400,
        "timestamp": datetime.utcnow().isoformat(),
        "analysis_method": "Gemini 2.5" if use_gemini else "Keyword Extraction"
    }
    
    # Add trend analysis if using Gemini
    if use_gemini and top_skills:
        print("📈 Analyzing trends with Gemini...")
        trends = analyze_skill_trends_with_gemini(top_skills, job_title)
        if trends:
            result["trend_analysis"] = trends
    
    # Cache the result
    if use_cache:
        print("💾 Caching results...")
        cache_skills_data(job_title, result, soc_code)
    
    print()
    print("✅ Analysis complete!")
    return result


def print_skills_report(result: Dict):
    """
    Print a formatted report of skills analysis.
    
    Args:
        result: Skills analysis result dictionary
    """
    print("\n" + "="*70)
    print(f"📊 SKILLS ANALYSIS REPORT: {result['role']}")
    print("="*70)
    
    if result.get("error"):
        print(f"❌ Error: {result['message']}")
        return
    
    print(f"\n📍 SOC Code: {result.get('soc_code', 'N/A')}")
    print(f"📊 Data Source: {result['data_source']}")
    print(f"🎯 Confidence Score: {result['confidence']:.2%}")
    print(f"⚙️  Analysis Method: {result.get('analysis_method', 'N/A')}")
    print(f"🕒 Timestamp: {result['timestamp']}")
    
    print(f"\n🔝 TOP {len(result['top_skills'])} TRENDING SKILLS:")
    print("-" * 70)
    
    for idx, skill in enumerate(result['top_skills'], 1):
        type_emoji = {
            'language': '💻',
            'framework': '🛠️',
            'tool': '🔧',
            'cloud': '☁️',
            'database': '🗄️',
            'concept': '🧠'
        }.get(skill['type'], '📌')
        
        bar_length = int(skill['frequency'] / 5)
        bar = '█' * bar_length
        
        print(f"{idx:2}. {type_emoji} {skill['name']:20} "
              f"[{skill['type']:10}] {bar:20} "
              f"{skill['frequency']:3}% ({skill['mention_count']} mentions)")
    
    # Print trend analysis if available
    if result.get("trend_analysis"):
        print("\n📈 TREND ANALYSIS:")
        print("-" * 70)
        trends = result["trend_analysis"]
        
        if trends.get("emerging"):
            print(f"\n🚀 Emerging Technologies:\n{trends['emerging']}")
        
        if trends.get("stable_core"):
            print(f"\n🎯 Stable Core Skills:\n{trends['stable_core']}")
        
        if trends.get("recommendations"):
            print(f"\n💡 Recommendations:\n{trends['recommendations']}")
        
        if trends.get("insights"):
            print(f"\n🔍 Insights:\n{trends['insights']}")
    
    print("\n" + "="*70)


def main():
    """Main entry point."""
    # Example usage
    print("🚀 Short-Term Skills Agent")
    print("="*70)
    print()
    
    # Show cache stats
    stats = get_cache_stats()
    print(f"💾 Cache Stats: {stats['valid_files']} valid, "
          f"{stats['expired_files']} expired, "
          f"{stats['total_size_mb']} MB")
    print()
    
    # Example 1: Software Engineer
    result = analyze_role_skills(
        job_title="Software Engineer",
        soc_code="15-1252.00",
        use_cache=True,
        use_gemini=True
    )
    print_skills_report(result)
    
    # Save to file
    output_file = f"skills_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()