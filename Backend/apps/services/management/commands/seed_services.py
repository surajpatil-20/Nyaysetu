"""
Management command to seed official judicial services data.
All URLs are verified official government/court portals.
"""
from django.core.management.base import BaseCommand
from apps.services.models import Service

SERVICES_DATA = [
    {
        "service_name": "NALSA Free Legal Services",
        "category": "LEGAL_AID",
        "department": "National Legal Services Authority (NALSA)",
        "state": None,
        "description": (
            "NALSA provides free legal services to eligible citizens including legal advice, "
            "representation in courts, drafting of legal documents, and mediation/Lok Adalat services. "
            "Access through State Legal Services Authorities (SLSAs) or District Legal Services Authorities (DLSAs)."
        ),
        "eligibility": (
            "Women and children, members of SC/ST communities, industrial workmen, persons with disabilities, "
            "victims of mass disasters or ethnic violence, persons in custody, persons with annual income "
            "below Rs. 3,00,000 (under Section 12 of the Legal Services Authorities Act, 1987)."
        ),
        "official_url": "https://nalsa.gov.in/",
    },
    {
        "service_name": "eCourts Services Portal – Case Status",
        "category": "CASE_STATUS",
        "department": "Department of Justice, Ministry of Law & Justice",
        "state": None,
        "description": (
            "Citizens can check the status of their case in any District Court, High Court, or the Supreme Court "
            "of India using the eCourts Services Portal. Search by Case Number, CNR Number, Party Name, "
            "FIR Number, or filing number. Cause lists, orders, and hearing dates are available."
        ),
        "eligibility": "All citizens. No registration required for case status check.",
        "official_url": "https://ecourts.gov.in/ecourts_home/",
    },
    {
        "service_name": "Supreme Court of India – e-Filing",
        "category": "E_FILING",
        "department": "Supreme Court of India",
        "state": None,
        "description": (
            "The Supreme Court of India's e-Filing portal allows advocates and parties-in-person to file "
            "new cases, interlocutory applications, and other petitions electronically. "
            "Documents can be filed 24x7 without visiting the court registry."
        ),
        "eligibility": "Advocates enrolled with Bar Council and parties filing in person.",
        "official_url": "https://efiling.sci.gov.in/",
    },
    {
        "service_name": "High Court e-Filing (Delhi High Court)",
        "category": "E_FILING",
        "department": "Delhi High Court",
        "state": "Delhi",
        "description": (
            "The Delhi High Court e-Filing system allows advocates to file petitions, applications, and replies "
            "online without physical submission. Includes case tracking and cause list access."
        ),
        "eligibility": "Advocates enrolled with Bar Council of Delhi.",
        "official_url": "https://delhihighcourt.nic.in/",
    },
    {
        "service_name": "e-Daakhil – Consumer Dispute e-Filing",
        "category": "CONSUMER_FORUM",
        "department": "Department of Consumer Affairs, Ministry of Consumer Affairs",
        "state": None,
        "description": (
            "e-Daakhil is the official portal for filing consumer complaints online before District Consumer "
            "Disputes Redressal Commissions (DDRCs), State Consumer Disputes Redressal Commissions (SDRCs), "
            "and the National Consumer Disputes Redressal Commission (NCDRC)."
        ),
        "eligibility": "Any consumer aggrieved by deficiency of goods or services.",
        "official_url": "https://edaakhil.nic.in/",
    },
    {
        "service_name": "Virtual Courts – Traffic Challan & Petty Offences",
        "category": "TRAFFIC_CHALLAN",
        "department": "Department of Justice, Ministry of Law & Justice",
        "state": None,
        "description": (
            "Virtual Courts allow citizens to pay traffic challans and settle petty compoundable offences "
            "online without appearing in physical court. Available 24x7."
        ),
        "eligibility": "Any person issued a traffic challan or summons for a compoundable offence.",
        "official_url": "https://vcourts.gov.in/",
    },
    {
        "service_name": "Certified Copy Application (eCourts)",
        "category": "CERTIFIED_COPY",
        "department": "Department of Justice, Ministry of Law & Justice",
        "state": None,
        "description": (
            "Citizens and advocates can apply online for certified copies of court orders, judgments, "
            "and other judicial records through the eCourts Services portal."
        ),
        "eligibility": "Parties to the case or their advocates.",
        "official_url": "https://services.ecourts.gov.in/ecourtindia_v6/",
    },
    {
        "service_name": "TELE-LAW – Legal Aid via Common Service Centres",
        "category": "LEGAL_AID",
        "department": "Department of Justice, Ministry of Law & Justice / NALSA",
        "state": None,
        "description": (
            "Tele-Law connects citizens in rural areas with empanelled lawyers via video conferencing at "
            "Common Service Centres (CSCs) across India for pre-litigation legal advice."
        ),
        "eligibility": "Marginalized communities, rural citizens, women, SC/ST communities.",
        "official_url": "https://tele-law.in/",
    },
    {
        "service_name": "National Judicial Data Grid (NJDG)",
        "category": "CASE_STATUS",
        "department": "Department of Justice, Ministry of Law & Justice",
        "state": None,
        "description": (
            "The National Judicial Data Grid provides aggregated data on case pendency and disposal across "
            "High Courts and District/Taluka Courts in India."
        ),
        "eligibility": "Open to all. No registration required.",
        "official_url": "https://njdg.ecourts.gov.in/",
    },
    {
        "service_name": "Supreme Court of India – Judgment Search (JUDIS)",
        "category": "CASE_STATUS",
        "department": "Supreme Court of India",
        "state": None,
        "description": (
            "JUDIS (Judgment Information System) is the official repository of Supreme Court of India judgments "
            "from 1950 onwards."
        ),
        "eligibility": "Open to all. No registration required.",
        "official_url": "https://judis.nic.in/",
    },
]


class Command(BaseCommand):
    help = "Seed the database with official judicial services data."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing services before seeding.'
        )

    def handle(self, *args, **options):
        if options.get('clear'):
            count = Service.objects.count()
            Service.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing services."))

        created = 0
        updated = 0
        for data in SERVICES_DATA:
            obj, is_created = Service.objects.update_or_create(
                service_name=data["service_name"],
                defaults=data,
            )
            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Services seeded: {created} created, {updated} updated. Total: {Service.objects.count()}."
        ))

