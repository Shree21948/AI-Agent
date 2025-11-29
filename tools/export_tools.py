"""Tools for exporting data as JSON and CSV."""
import json
import csv
from typing import Dict, Any
from io import StringIO


def export_to_json(data: Dict[str, Any]) -> str:
    """
    Export data as formatted JSON string.
    
    Args:
        data: Data to export
    
    Returns:
        JSON string
    """
    return json.dumps(data, indent=2)


def export_to_csv(data: Dict[str, Any]) -> str:
    """
    Export gap analysis and recommendations as CSV.
    
    Args:
        data: Data containing gap_analysis and recommendations
    
    Returns:
        CSV string
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Write gap analysis
    if "gap_analysis" in data:
        writer.writerow(["=== GAP ANALYSIS ==="])
        writer.writerow(["Skill", "Market Rank", "Priority", "Reasoning"])
        
        for gap in data["gap_analysis"]:
            writer.writerow([
                gap.get("skill", ""),
                gap.get("market_rank", ""),
                gap.get("priority", ""),
                gap.get("reasoning", "")
            ])
        
        writer.writerow([])
    
    # Write recommended learning path
    if "recommended_learning_path" in data:
        writer.writerow(["=== RECOMMENDED LEARNING PATH ==="])
        writer.writerow(["Order", "Skill"])
        
        for idx, skill in enumerate(data["recommended_learning_path"], 1):
            writer.writerow([idx, skill])
        
        writer.writerow([])
    
    # Write resources
    if "resources" in data:
        writer.writerow(["=== LEARNING RESOURCES ==="])
        writer.writerow(["Skill", "Title", "Channel", "Duration (min)", "Views", "URL"])
        
        for skill, resource_data in data["resources"].items():
            for resource in resource_data.get("resources", []):
                writer.writerow([
                    skill,
                    resource.get("title", ""),
                    resource.get("channel", ""),
                    resource.get("duration_minutes", ""),
                    resource.get("views", ""),
                    resource.get("url", "")
                ])
    
    return output.getvalue()