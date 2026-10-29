"""Small evaluation demo for InternHub's content-based recommender.

This checks whether the top-ranked reference internship has the expected field.
TF-IDF is fitted during each ranking call; this script does not train a separate
classifier. The result is only a tiny demonstration, not production accuracy.
"""
from ml_recommender import rank_internships

samples = [
    {"title": "Python Developer Intern", "field": "IT", "description": "Build backend apps and APIs", "skills": "Python, Flask, SQL", "eligibility": "Students"},
    {"title": "Data Analyst Intern", "field": "Data Analytics", "description": "Clean data and make reports", "skills": "Python, SQL, Excel", "eligibility": "Students"},
    {"title": "Graphic Design Intern", "field": "Design", "description": "Create visual layouts", "skills": "Figma, Photoshop, Design", "eligibility": "Students"},
    {"title": "Marketing Intern", "field": "Marketing", "description": "Plan campaigns and social media", "skills": "Marketing, Writing, Analytics", "eligibility": "Students"},
    {"title": "Java Developer Intern", "field": "IT", "description": "Develop Java applications", "skills": "Java, OOP, SQL", "eligibility": "Students"},
    {"title": "UI UX Intern", "field": "Design", "description": "Design app user journeys", "skills": "Figma, UI, UX", "eligibility": "Students"},
]

# Use the first four records as reference examples and hold out the last two.
reference_data = samples[:4]
test_data = samples[4:]
correct = 0

for test in test_data:
    profile = [skill.strip() for skill in test["skills"].split(",")]
    scores = rank_internships(profile, reference_data)
    best_index = max(range(len(scores)), key=scores.__getitem__)
    predicted = reference_data[best_index]
    is_correct = predicted["field"] == test["field"]
    correct += int(is_correct)

    print("Test profile:", test["title"])
    print("Expected field:", test["field"])
    print("Top-ranked field:", predicted["field"])
    print("Result:", "MATCH" if is_correct else "NO MATCH")
    print()

match_rate = correct / len(test_data) * 100
print("Reference examples:", len(reference_data))
print("Held-out test examples:", len(test_data))
print("Field-match rate: {:.0f}%".format(match_rate))
print("Note: This is a small demonstration, not a reliable production metric.")
