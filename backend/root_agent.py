from backend.resume import run_resume_agent
from backend.role_mapper import map_role_with_careeronestop
from pprint import pprint

def run_career_pipeline(resume_path: str):
    resume_result = run_resume_agent(resume_path)

    if resume_result["roles"]:
        first_role = resume_result["roles"][0]
    else:
        None
    mapped_role = map_role_with_careeronestop(first_role)

    # Keep only what you care about
    output = {
        "input_title": first_role,
        "soc_code": mapped_role["soc_code"],
        "standard_title": mapped_role["standard_title"],
    }

    print(output)
    return output



if __name__ == "__main__":
    resume_path = input("Enter resume path: ").strip()
    result = run_career_pipeline(resume_path)

    print("\n=== FINAL RESULT ===")
    pprint(result)
