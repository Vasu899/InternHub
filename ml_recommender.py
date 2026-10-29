"""Content-based internship recommendations using TF-IDF and cosine similarity."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def internship_text(item):
    return " ".join(str(item.get(key) or "") for key in ("title", "field", "description", "skills", "eligibility"))

def rank_internships(user_skills, internships):
    if not internships: return []
    profile = " ".join(user_skills).strip() or "student beginner internship"
    documents = [internship_text(item) for item in internships] + [profile]
    matrix = TfidfVectorizer(stop_words="english").fit_transform(documents)
    return [round(float(score) * 100) for score in cosine_similarity(matrix[-1], matrix[:-1]).flatten()]






