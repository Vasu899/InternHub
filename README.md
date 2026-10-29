# InternHub

A student-friendly internship discovery and tracking website built with HTML, CSS, JavaScript, Python Flask, and MySQL.

## Main features
- Register and log in with email and password
- Explore and filter internships across fields
- Add skills and see simple matching recommendations
- Save and compare internships
- Track application status
- Edit student profile
- Admin page for adding, editing, and hiding listings

## Setup
Follow `SETUP.md` for Windows and MySQL instructions. Execute `database/schema.sql` in MySQL Workbench, configure environment variables, install `requirements.txt`, and run `python app.py`.

## Data and recovery
Only publish internship openings after checking the original source. The app does not scrape live job boards automatically. Forgot-password SMS is not active until a real SMS provider and API credentials are configured; see `SETUP.md`.


## Sample internship data
Run `python seed_internships.py` after creating the MySQL tables to load 120 clearly labelled demo records across 12 fields. These are for demonstrating search, filters, recommendations, and comparison; they are not verified vacancies.

## Machine-learning recommendation
The recommendation page uses a content-based text approach. `ml_recommender.py` combines each internship's title, field, description, skills, and eligibility; TF-IDF converts the text into vectors, and cosine similarity compares them with the student's skill profile. This is not a separately trained classifier.

To run the small evaluation demonstration from this folder:

```powershell
python train_test_model.py
```

The test uses six hand-written examples, with four reference examples and two held-out examples. Its field-match rate is only a demonstration and should not be presented as production accuracy.
