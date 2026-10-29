# InternHub setup (Windows)

## 1. Install the requirements
Install Python and MySQL Server (MySQL Workbench is helpful but optional). Open PowerShell in this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run this for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 2. Create the database
Open MySQL Workbench, connect to your local server, open `database/schema.sql`, and execute the whole file. It creates the `internhub` database and tables.

## 3. Set the database password
Copy `.env.example` to `.env` and enter the password you use for your local MySQL account. Example:

```text
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_mysql_password
MYSQL_DATABASE=internhub
INTERNHUB_SECRET_KEY=replace-with-a-long-random-secret
```

The app loads `.env` automatically when it starts.

## 4. Add sample internship listings
After running `database/schema.sql` and setting your `.env`, run this once to add 120 sample records across 12 fields:

```powershell
python seed_internships.py
```

These records are clearly marked as demo data, not verified vacancies. The links open a LinkedIn job search for the role, so check the current listing before applying. Running the seed script again will not duplicate the same sample rows.

## 5. Run the website

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## 6. Enable the admin page
1. Register a normal account in InternHub.
2. Stop the app with Ctrl+C.
3. Run `python create_admin.py` and enter that account's email.
4. Start `python app.py` again and log in. The Admin link will appear.

Admin users can add listings, edit listings, or hide a listing. Hiding is used instead of permanently deleting it so existing application history remains intact.

## Password recovery note
The Forgot Password page is deliberately not pretending to send SMS. A real SMS OTP needs an SMS provider account, an API key, and a configured sender/route. No provider credentials have been supplied yet. Before enabling that part, choose a provider and confirm its setup/cost; then the SMS send and OTP verification routes can be connected. Do not use a hard-coded or pretend OTP in a real account system.

## Internship data note
The database is ready for real listings, and the Admin page is ready to add or edit them. Do not label an opening as active until its original listing has been checked. Stipend and deadlines can be left as “Not specified” if the source doesn't provide them. Listings should be reviewed periodically because openings expire. A CSV import can be added once the real source data has been collected and checked.

## Current project features
- Registration and login with hashed passwords and Flask sessions
- Home page, dashboard, profile, and logout
- Search and filters for field, work mode, payment type, and beginner-friendly roles
- Skill list, TF-IDF/cosine-similarity recommendations, and a separate skill-match percentage
- Save internships, compare up to three (linked in the top navigation and Explore cards), and track application status
- Admin page to add, edit, and hide listings
- Responsive layout with restrained teal, navy, and coral colours

## Notes for review
- Recommendations use TF-IDF and cosine similarity in `ml_recommender.py`. This is a content-based text recommendation method, not a separately trained classifier. The exact skill overlap percentage is also shown as an additional score.
- Run `python train_test_model.py` to see a tiny held-out demonstration. It uses only six hand-written examples and is not a reliable production accuracy estimate.
- The site does not automatically scrape other job boards. The application button opens the original listing URL stored in the database.
- SMS OTP is not enabled until a real provider is configured.
