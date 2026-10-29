"""Add sample internship records for local project demonstration.

These are DEMO listings, not confirmed live vacancies. Run after database/schema.sql.
Running this file again will not duplicate the same demo rows.
"""
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "internhub"),
}

# Roles are spread across the main internship fields used in Explore.
roles = {
    "IT & Software": [
        ("Python Developer Intern", "Python, Git, SQL"),
        ("Web Development Intern", "HTML, CSS, JavaScript"),
        ("Java Developer Intern", "Java, OOP, SQL"),
        ("Frontend Developer Intern", "HTML, CSS, JavaScript"),
        ("Backend Developer Intern", "Python, APIs, SQL"),
        ("Full Stack Developer Intern", "HTML, CSS, JavaScript, SQL"),
        ("Mobile App Developer Intern", "Java, APIs, Git"),
        ("Software Testing Intern", "Testing, Java, Documentation"),
        ("Cloud Support Intern", "Linux, Networking, Cloud"),
        ("DevOps Intern", "Linux, Git, Docker"),
    ],
    "Data & Analytics": [
        ("Data Analyst Intern", "Excel, SQL, Data Analysis"),
        ("Data Science Intern", "Python, Pandas, Statistics"),
        ("Machine Learning Intern", "Python, Scikit-learn, Statistics"),
        ("Business Intelligence Intern", "SQL, Excel, Power BI"),
        ("Research Data Intern", "Python, Statistics, Research"),
        ("Data Visualization Intern", "Power BI, Excel, Charts"),
        ("Database Intern", "SQL, Database Design"),
        ("Junior AI Intern", "Python, Machine Learning"),
        ("Operations Analyst Intern", "Excel, SQL, Reporting"),
        ("Product Analytics Intern", "SQL, Excel, Communication"),
    ],
    "Design": [
        ("UI Design Intern", "Figma, Wireframing, UI Design"),
        ("UX Research Intern", "Research, Figma, Communication"),
        ("Graphic Design Intern", "Canva, Typography, Design"),
        ("Product Design Intern", "Figma, Prototyping, UX"),
        ("Visual Design Intern", "Design, Canva, Typography"),
        ("Web Design Intern", "Figma, HTML, CSS"),
        ("Motion Design Intern", "Animation, Storyboarding"),
        ("Design Research Intern", "Research, Interviews, Reporting"),
        ("Content Design Intern", "Writing, UX, Editing"),
        ("Creative Intern", "Canva, Creativity, Communication"),
    ],
    "Finance": [
        ("Finance Intern", "Excel, Accounting, Reporting"),
        ("Accounts Intern", "Accounting, Excel, Tally"),
        ("Financial Analyst Intern", "Excel, Financial Analysis"),
        ("Audit Intern", "Accounting, Documentation, Excel"),
        ("Investment Research Intern", "Research, Excel, Finance"),
        ("Risk Analyst Intern", "Excel, Risk Analysis"),
        ("Taxation Intern", "Accounting, Tax, Excel"),
        ("FinTech Intern", "Python, Finance, SQL"),
        ("Payroll Intern", "Excel, Payroll, Communication"),
        ("Business Finance Intern", "Budgeting, Excel, Reporting"),
    ],
    "Marketing": [
        ("Digital Marketing Intern", "SEO, Social Media, Analytics"),
        ("Social Media Intern", "Content, Canva, Communication"),
        ("SEO Intern", "SEO, Keyword Research, Writing"),
        ("Market Research Intern", "Research, Excel, Reporting"),
        ("Brand Marketing Intern", "Marketing, Communication, Design"),
        ("Email Marketing Intern", "Writing, Analytics, Marketing"),
        ("Performance Marketing Intern", "Ads, Analytics, Excel"),
        ("Community Marketing Intern", "Communication, Social Media"),
        ("Growth Marketing Intern", "Analytics, Marketing, Research"),
        ("Marketing Operations Intern", "Excel, CRM, Reporting"),
    ],
    "Business": [
        ("Business Development Intern", "Communication, Research, Excel"),
        ("Product Management Intern", "Research, Documentation, Analytics"),
        ("Strategy Intern", "Research, Excel, Presentation"),
        ("Customer Success Intern", "Communication, Problem Solving"),
        ("Sales Intern", "Communication, CRM, Research"),
        ("Project Coordinator Intern", "Planning, Excel, Communication"),
        ("Business Operations Intern", "Excel, Reporting, Problem Solving"),
        ("Startup Research Intern", "Research, Excel, Writing"),
        ("Client Relations Intern", "Communication, Documentation"),
        ("Product Operations Intern", "Excel, Research, Coordination"),
    ],
    "Content & Writing": [
        ("Content Writing Intern", "Writing, Editing, Research"),
        ("Technical Writing Intern", "Writing, Documentation, Technology"),
        ("Copywriting Intern", "Writing, Creativity, Editing"),
        ("Blog Writing Intern", "SEO, Writing, Research"),
        ("Script Writing Intern", "Storytelling, Writing, Research"),
        ("Editorial Intern", "Editing, Proofreading, Writing"),
        ("Documentation Intern", "Writing, Documentation, Attention to Detail"),
        ("Translation Intern", "Writing, Language, Editing"),
        ("Newsletter Intern", "Writing, Editing, Communication"),
        ("Research Writing Intern", "Research, Writing, Citations"),
    ],
    "Human Resources": [
        ("HR Intern", "Communication, Excel, Recruitment"),
        ("Recruitment Intern", "Communication, Sourcing, Interviewing"),
        ("Talent Acquisition Intern", "Recruitment, Communication, Excel"),
        ("People Operations Intern", "Excel, Communication, Documentation"),
        ("Learning and Development Intern", "Presentation, Communication, Planning"),
        ("HR Analytics Intern", "Excel, Data Analysis, HR"),
        ("Employee Engagement Intern", "Communication, Event Planning"),
        ("Employer Branding Intern", "Writing, Social Media, HR"),
        ("Training Coordinator Intern", "Planning, Documentation, Communication"),
        ("HR Operations Intern", "Excel, Documentation, HR"),
    ],
    "Cybersecurity": [
        ("Cybersecurity Intern", "Networking, Linux, Security"),
        ("SOC Analyst Intern", "Networking, SIEM, Security"),
        ("Security Testing Intern", "Web Security, Linux, Testing"),
        ("Information Security Intern", "Security, Documentation, Networking"),
        ("Cloud Security Intern", "Cloud, Networking, Security"),
        ("Threat Research Intern", "Research, Security, Linux"),
        ("Digital Forensics Intern", "Linux, Investigation, Security"),
        ("Application Security Intern", "Web Security, APIs, Testing"),
        ("Governance Risk Compliance Intern", "Documentation, Risk, Security"),
        ("Network Security Intern", "Networking, Linux, Security"),
    ],
    "Healthcare": [
        ("Healthcare Data Intern", "Excel, Data Analysis, Research"),
        ("Public Health Research Intern", "Research, Statistics, Writing"),
        ("Health Content Intern", "Writing, Research, Editing"),
        ("Healthcare Operations Intern", "Excel, Communication, Reporting"),
        ("Medical Records Intern", "Documentation, Excel, Attention to Detail"),
        ("Health Informatics Intern", "SQL, Data Analysis, Healthcare"),
        ("Wellness Program Intern", "Communication, Planning, Research"),
        ("Clinical Research Support Intern", "Research, Documentation, Statistics"),
        ("Healthcare Marketing Intern", "Marketing, Writing, Research"),
        ("Patient Experience Intern", "Communication, Reporting, Problem Solving"),
    ],
    "Education": [
        ("EdTech Intern", "Communication, Research, Technology"),
        ("Teaching Assistant Intern", "Communication, Subject Knowledge"),
        ("Learning Content Intern", "Writing, Research, Editing"),
        ("Instructional Design Intern", "Figma, Writing, Learning Design"),
        ("Education Research Intern", "Research, Excel, Writing"),
        ("Online Course Intern", "Content, Communication, Technology"),
        ("Student Community Intern", "Communication, Event Planning"),
        ("Academic Operations Intern", "Excel, Documentation, Planning"),
        ("Assessment Content Intern", "Writing, Research, Editing"),
        ("Learning Analytics Intern", "Excel, Data Analysis, Reporting"),
    ],
    "Operations": [
        ("Operations Intern", "Excel, Communication, Reporting"),
        ("Supply Chain Intern", "Excel, Logistics, Planning"),
        ("Logistics Intern", "Planning, Excel, Communication"),
        ("Quality Assurance Intern", "Testing, Documentation, Reporting"),
        ("Procurement Intern", "Excel, Research, Communication"),
        ("Process Improvement Intern", "Data Analysis, Documentation"),
        ("Customer Support Intern", "Communication, Problem Solving"),
        ("Inventory Analyst Intern", "Excel, Data Analysis, Reporting"),
        ("Admin Operations Intern", "Documentation, Excel, Planning"),
        ("Service Delivery Intern", "Communication, Reporting, Coordination"),
    ],
}

companies = [
    "InternHub Demo Labs", "CampusStart Demo", "NextStep Learning", "BrightPath Projects",
    "SkillBridge Studio", "LaunchPad Demo Works", "OpenDoor Careers Lab", "FutureReady Hub",
    "StudentWorks Sample Co.", "CareerSpring Demo Team",
]

connection = mysql.connector.connect(**DB_CONFIG)
cursor = connection.cursor()
inserted = 0
for field, items in roles.items():
    for index, (title, skills) in enumerate(items):
        company = companies[(index + list(roles).index(field)) % len(companies)]
        work_mode = ["Remote", "Hybrid", "On-site"][(index + list(roles).index(field)) % 3]
        pay_type = ["Paid", "Unpaid", "Unspecified"][(index + list(roles).index(field)) % 3]
        stipend = {"Paid": "Sample: ₹5,000/month", "Unpaid": "Unpaid sample role", "Unspecified": "Not specified"}[pay_type]
        beginner = 1 if index < 6 else 0
        description = (
            "SAMPLE DATA for demonstrating the InternHub project filters and comparison feature. "
            f"This example role is in {field}. Students can practise {skills}. "
            "This is not a verified vacancy; use the search link to check current openings before applying."
        )
        search_query = title.replace(" ", "+") + "+India"
        url = "https://www.linkedin.com/jobs/search/?keywords=" + search_query
        cursor.execute(
            "SELECT id FROM internships WHERE title=%s AND company=%s",
            (title, company),
        )
        if cursor.fetchone():
            continue
        cursor.execute(
            """INSERT INTO internships
            (title, company, field, description, skills, eligibility, pay_type, stipend,
             work_mode, location, duration, application_url, beginner_friendly, is_active)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)""",
            (title, company, field, description, skills, "Students and recent graduates; verify each employer's requirements",
             pay_type, stipend, work_mode, "India / check listing", "Sample: 1–3 months", url, beginner),
        )
        inserted += 1
connection.commit()
cursor.close()
connection.close()
print(f"Added {inserted} sample internships. These are demo records, not verified vacancies.")
