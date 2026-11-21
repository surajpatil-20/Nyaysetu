"""
Management command to seed authentic Indian legal categories, Acts, sections, and real-life scenarios.
All Acts and sections reference real statutory enactments with verified India Code URLs.
"""
from django.core.management.base import BaseCommand
from apps.cases.models import Case
from apps.laws.models import LawCategory, LawAct, LawSection, LegalScenario


CATEGORIES_DATA = [
    {
        "name": "Consumer Rights & E-Commerce",
        "slug": "consumer-rights",
        "icon": "ShoppingBag",
        "description": "Protection against defective products, fraudulent sellers, misleading ads, and unfair trade practices.",
        "display_order": 1,
    },
    {
        "name": "Road Traffic & Motor Accidents",
        "slug": "road-traffic-accidents",
        "icon": "Car",
        "description": "Rights during traffic police stops, hit-and-run incidents, and Motor Accident Claims Tribunal (MACT) compensation.",
        "display_order": 2,
    },
    {
        "name": "Cyber Crime & Online Fraud",
        "slug": "cyber-crime",
        "icon": "ShieldAlert",
        "description": "Legal remedies for UPI banking fraud, identity theft, phishing, cyberstalking, and online harassment.",
        "display_order": 3,
    },
    {
        "name": "Police Powers & Arrest Rights",
        "slug": "police-arrest-rights",
        "icon": "Scale",
        "description": "Constitutional and statutory rights during police summons, interrogation, search, and arrest under CrPC.",
        "display_order": 4,
    },
    {
        "name": "Tenant & Rental Housing Rights",
        "slug": "tenant-housing-rights",
        "icon": "Home",
        "description": "Protections against arbitrary eviction, disconnection of water/electricity, and unlawful withholding of security deposits.",
        "display_order": 5,
    },
    {
        "name": "Women's Safety & Domestic Protection",
        "slug": "womens-safety",
        "icon": "ShieldCheck",
        "description": "Statutory relief against domestic violence, right to reside in shared household, and immediate protection orders.",
        "display_order": 6,
    },
    {
        "name": "Workplace & Employment Rights",
        "slug": "workplace-employment",
        "icon": "Briefcase",
        "description": "Rights regarding delayed salaries, unauthorized deductions, statutory gratuity, and withholding of relieving letters.",
        "display_order": 7,
    },
]


ACTS_DATA = [
    {
        "act_name": "Consumer Protection Act, 2019",
        "short_code": "CPA 2019",
        "act_year": 2019,
        "enacted_by": "Parliament of India",
        "description": "An Act to provide for protection of the interests of consumers and for the establishment of authorities for timely and effective administration and settlement of consumers' disputes.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },
    {
        "act_name": "Motor Vehicles Act, 1988",
        "short_code": "MVA 1988",
        "act_year": 1988,
        "enacted_by": "Parliament of India",
        "description": "An Act to consolidate and amend the law relating to motor vehicles, road safety standards, liability, and compensation for motor accidents.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },
    {
        "act_name": "Information Technology Act, 2000",
        "short_code": "IT Act",
        "act_year": 2000,
        "enacted_by": "Parliament of India",
        "description": "An Act to provide legal recognition for transactions carried out by means of electronic data interchange and other means of electronic communication, and to prevent cyber crimes.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "act_name": "Code of Criminal Procedure, 1973",
        "short_code": "CrPC",
        "act_year": 1974,
        "enacted_by": "Parliament of India",
        "description": "An Act to consolidate and amend the law relating to Criminal Procedure, powers of police officers, arrest rules, and rights of accused persons.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },
    {
        "act_name": "Transfer of Property Act, 1882",
        "short_code": "TP Act",
        "act_year": 1882,
        "enacted_by": "Legislative Council of India",
        "description": "An Act to define and amend certain parts of the law relating to the transfer of property by act of parties, including leases of immovable property.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
    },
    {
        "act_name": "Protection of Women from Domestic Violence Act, 2005",
        "short_code": "PWDVA 2005",
        "act_year": 2005,
        "enacted_by": "Parliament of India",
        "description": "An Act to provide for more effective protection of the rights of women guaranteed under the Constitution who are victims of violence of any kind occurring within the family.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },
    {
        "act_name": "Payment of Wages Act, 1936",
        "short_code": "PWA 1936",
        "act_year": 1936,
        "enacted_by": "Central Legislative Assembly",
        "description": "An Act to regulate the payment of wages to certain classes of employed persons and to prevent unauthorized deductions.",
        "official_url": "https://www.indiacode.nic.in/show-data?actid=AC_CEN_6_0_00044_193604_1523351375183",
    },
    {
        "act_name": "Payment of Gratuity Act, 1972",
        "short_code": "PGA 1972",
        "act_year": 1972,
        "enacted_by": "Parliament of India",
        "description": "An Act to provide for a scheme for the payment of gratuity to employees engaged in factories, mines, oilfields, plantations, ports, railway companies, shops or other establishments.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/197239",
    },
    {
        "act_name": "Sexual Harassment of Women at Workplace Act, 2013",
        "short_code": "POSH Act 2013",
        "act_year": 2013,
        "enacted_by": "Parliament of India",
        "description": "An Act to provide protection against sexual harassment of women at workplace and for the prevention and redressal of complaints of sexual harassment.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2104",
    },
    {
        "act_name": "Maternity Benefit Act, 1961",
        "short_code": "MBA 1961",
        "act_year": 1961,
        "enacted_by": "Parliament of India",
        "description": "An Act to regulate the employment of women in certain establishments for certain periods before and after child-birth and to provide for maternity benefit.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1681",
    },
    {
        "act_name": "Employees' Provident Funds Act, 1952",
        "short_code": "EPFA 1952",
        "act_year": 1952,
        "enacted_by": "Parliament of India",
        "description": "An Act to provide for the institution of provident funds, pension fund and deposit-linked insurance fund for employees in factories and other establishments.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1898",
    },
    {
        "act_name": "Industrial Disputes Act, 1947",
        "short_code": "IDA 1947",
        "act_year": 1947,
        "enacted_by": "Central Legislative Assembly",
        "description": "An Act to make provision for the investigation and settlement of industrial disputes, and for certain other purposes relating to retrenchment and layoffs.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1897",
    },
]


SECTIONS_DATA = [
    # Consumer Protection Act, 2019
    {
        "act_code": "CPA 2019",
        "section_number": "Section 2(7)",
        "title": "Definition of Consumer",
        "legal_text": "Defines a consumer as any person who buys goods or hires services for consideration paid or promised, expressly including online transactions via e-commerce platforms and teleshopping.",
        "simple_explanation": "You are recognized as a protected consumer whether you buy goods in a physical store or through online shopping apps. Digital marketplaces cannot disclaim consumer obligations.",
        "punishment_or_remedy": "Provides legal standing to initiate consumer complaints before District, State, and National Consumer Commissions.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },
    {
        "act_code": "CPA 2019",
        "section_number": "Section 2(47)",
        "title": "Unfair Trade Practice Defined",
        "legal_text": "Prohibits deceptive trade methods including refusal to take back defective items, failure to refund money within stipulated time, and issuing false warranties or guarantees.",
        "simple_explanation": "Refusing legitimate refunds on broken or incorrect deliveries, misleading discounts, and ignoring statutory warranties constitute unlawful unfair trade practices.",
        "punishment_or_remedy": "Consumer authorities can order product recalls, complete refunds, and financial penalties up to ₹10 Lakhs.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },
    {
        "act_code": "CPA 2019",
        "section_number": "Section 35",
        "title": "Filing Complaint with District Commission",
        "legal_text": "Authorizes an aggrieved consumer or recognized consumer association to file a complaint electronically or in person with the competent District Consumer Disputes Redressal Commission.",
        "simple_explanation": "You can lodge a formal consumer case from home via the online e-Daakhil / e-Jagriti system without needing to engage an advocate.",
        "punishment_or_remedy": "The Commission can direct replacement, refund with interest, and compensation for harassment and mental distress.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },
    {
        "act_code": "CPA 2019",
        "section_number": "Section 2(11)",
        "title": "Deficiency in Service Defined",
        "legal_text": "Defines deficiency as any fault, imperfection, shortcoming or inadequacy in the quality, nature, or manner of performance required by law or contract in relation to any service.",
        "simple_explanation": "Covers service failures like arbitrary airline flight cancellations, telecom outages, banking delays, and hospital negligence.",
        "punishment_or_remedy": "Service providers can be mandated to refund service fees and pay damages for consequential loss.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },
    {
        "act_code": "CPA 2019",
        "section_number": "Section 21",
        "title": "Penalties for Misleading Advertisements",
        "legal_text": "Empowers the Central Authority to issue directions and impose penalties up to ₹10 Lakhs on manufacturers, traders, and celebrity endorsers for false or misleading ads.",
        "simple_explanation": "Brands and celebrity influencers making deceptive health, beauty, or financial claims can be penalized and banned from endorsements.",
        "punishment_or_remedy": "Mandatory corrective advertisements, monetary penalties, and endorsement bans up to one year.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },
    {
        "act_code": "CPA 2019",
        "section_number": "Section 84",
        "title": "Liability of Product Manufacturer",
        "legal_text": "Holds product manufacturers liable in product liability actions for manufacturing defects, design defects, deviation from manufacturing specs, or lack of adequate warning.",
        "simple_explanation": "If a phone battery explodes or a car brake fails due to factory defect, the manufacturer is directly liable for all physical and property damage caused.",
        "punishment_or_remedy": "Full compensation for harm, medical expenses, and replacement costs under product liability.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },

    # Motor Vehicles Act, 1988
    {
        "act_code": "MVA 1988",
        "section_number": "Section 134A",
        "title": "Protection of Good Samaritans",
        "legal_text": "Guarantees that any citizen providing emergency medical or non-medical assistance to a road accident victim will not face civil or criminal liability or police harassment.",
        "simple_explanation": "Bystanders helping accident victims cannot be detained, pressured to become witnesses, or forced to pay hospital admission charges.",
        "punishment_or_remedy": "Statutory legal immunity; official departmental action against any officer harassing a Good Samaritan.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },
    {
        "act_code": "MVA 1988",
        "section_number": "Section 166",
        "title": "Compensation Application in MACT",
        "legal_text": "Enables victims of motor vehicle collisions, or surviving family members in case of fatal accidents, to claim financial compensation before the Motor Accidents Claims Tribunal.",
        "simple_explanation": "Accident victims can seek compensation from the driver, vehicle owner, and motor insurance firm for treatment, lost wages, and disability.",
        "punishment_or_remedy": "Judicially determined financial award paid by the statutory insurance company.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },
    {
        "act_code": "MVA 1988",
        "section_number": "Section 130",
        "title": "Duty to Produce Driving Licence and Registration",
        "legal_text": "Directs drivers to produce license and registration upon demand by an officer in uniform, permitting production in digital format via authorized DigiLocker and mParivahan apps.",
        "simple_explanation": "Drivers can present digital licenses and registration certificates on government mobile apps without carrying physical paper cards.",
        "punishment_or_remedy": "Digital certificates hold equivalent legal validity; physical impoundment for lack of hardcopy is invalid.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },
    {
        "act_code": "MVA 1988",
        "section_number": "Section 161",
        "title": "Compensation in Hit-and-Run Motor Accidents",
        "legal_text": "Establishes a statutory compensation scheme for victims of hit-and-run motor accidents where the offending vehicle identity cannot be ascertained.",
        "simple_explanation": "Provides government solatium compensation of ₹2 Lakhs in death cases and ₹50,000 for grievous injury when the vehicle flees the scene.",
        "punishment_or_remedy": "Fast-track financial assistance disbursed via District Magistrate inquiry under the Motor Vehicles Solatium Scheme.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },
    {
        "act_code": "MVA 1988",
        "section_number": "Section 206",
        "title": "Power of Police Officer to Impound Documents or Seize Vehicle",
        "legal_text": "Prescribes strict conditions under which a police officer may impound a driving license or seize an unauthorized vehicle, requiring a formal seizure receipt.",
        "simple_explanation": "Traffic police cannot arbitrarily confiscate vehicle ignition keys or impound documents without issuing a formal signed seizure receipt.",
        "punishment_or_remedy": "Unauthorized vehicle seizure or key snatching is actionable as departmental misconduct and illegal restraint.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },

    # Information Technology Act, 2000
    {
        "act_code": "IT Act",
        "section_number": "Section 43",
        "title": "Penalty for Damage to Computer System and Data Extraction",
        "legal_text": "Prescribes civil liability and compensation up to ₹5 Crores for unauthorized access, downloading, copying, or introducing contaminants into any computer or digital system.",
        "simple_explanation": "Gives victims the right to claim financial damages if unauthorized access or malware causes financial or data losses.",
        "punishment_or_remedy": "Adjudicating Officer can award monetary damages paid directly to the affected person.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "act_code": "IT Act",
        "section_number": "Section 66C",
        "title": "Punishment for Identity Theft",
        "legal_text": "Punishes fraudulent or dishonest use of electronic signatures, passwords, or unique biometric identification features of another person with imprisonment up to 3 years.",
        "simple_explanation": "Stealing OTPs, passwords, UPI credentials, or using someone's Aadhaar data without consent is a serious criminal offense.",
        "punishment_or_remedy": "Cognizable criminal offense with up to 3 years imprisonment and fine up to ₹1 Lakh.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "act_code": "IT Act",
        "section_number": "Section 66D",
        "title": "Cheating by Personation Using Computer Resource",
        "legal_text": "Penalizes cheating by personation through any communication device or computer network with imprisonment up to 3 years and mandatory fine.",
        "simple_explanation": "Impersonating bank managers, courier personnel, or police officers to siphon funds via digital apps is criminally punishable.",
        "punishment_or_remedy": "Arrest, criminal trial, and freezing of illicit beneficiary bank accounts by Cyber Crime cells.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "act_code": "IT Act",
        "section_number": "Section 66E",
        "title": "Violation of Bodily Privacy",
        "legal_text": "Penalizes intentional capturing, publishing, or transmitting images of private body areas without consent with imprisonment up to 3 years or fine up to ₹2 Lakhs.",
        "simple_explanation": "Secretly photographing, filming, or sharing intimate images of someone without consent is an offense against bodily privacy.",
        "punishment_or_remedy": "Criminal prosecution and statutory right to demand immediate takedown by digital intermediaries.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "act_code": "IT Act",
        "section_number": "Section 67",
        "title": "Publishing Obscene Material in Electronic Form",
        "legal_text": "Punishes transmission or publishing of lascivious or sexually explicit electronic material with imprisonment up to 3 years on first conviction.",
        "simple_explanation": "Distributing sexually abusive content or revenge media on WhatsApp, Telegram, or websites attracts strict criminal liability.",
        "punishment_or_remedy": "Non-bailable criminal offense with up to 5 years imprisonment on repeat conviction.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },

    # Code of Criminal Procedure, 1973
    {
        "act_code": "CrPC",
        "section_number": "Section 41A",
        "title": "Notice of Appearance Before Police Officer",
        "legal_text": "Mandates that for offenses punishable with 7 years or less, police must issue a written notice of appearance rather than making automatic arrests.",
        "simple_explanation": "For less severe allegations, police cannot arbitrarily arrest you without issuing a formal summons to join the inquiry.",
        "punishment_or_remedy": "Arrest in defiance of Section 41A renders the arresting officer liable for contempt of court and departmental sanctions.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },
    {
        "act_code": "CrPC",
        "section_number": "Section 50",
        "title": "Information Regarding Grounds of Arrest and Bail Rights",
        "legal_text": "Directs police officers arresting without warrant to immediately communicate full particulars of the alleged offense and inform if the offense is bailable.",
        "simple_explanation": "Police are legally obligated to disclose why you are detained and explain your right to apply for bail immediately.",
        "punishment_or_remedy": "Uncommunicated arrest violates fundamental rights under Article 22(1) of the Indian Constitution.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },
    {
        "act_code": "CrPC",
        "section_number": "Section 57",
        "title": "Maximum Custodial Detention Period",
        "legal_text": "Prohibits police detention beyond 24 hours without producing the arrested person before a competent Judicial Magistrate.",
        "simple_explanation": "Police cannot keep any person in a lockup past 24 hours without express judicial remand from a Magistrate.",
        "punishment_or_remedy": "Immediate ground for Habeas Corpus writ petition before High Courts and entitlement to default bail.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },
    {
        "act_code": "CrPC",
        "section_number": "Section 154",
        "title": "Mandatory Registration of First Information Report (FIR)",
        "legal_text": "Requires police station officers to record every information relating to the commission of a cognizable offense in writing and furnish a free copy to the informant.",
        "simple_explanation": "Police cannot turn away victims of cognizable crimes and must record an FIR or Zero FIR immediately free of cost.",
        "punishment_or_remedy": "Refusal to record FIR is punishable under Section 166A IPC; citizen can petition Superintendent of Police or Magistrate under Sec 156(3).",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },
    {
        "act_code": "CrPC",
        "section_number": "Section 46(4)",
        "title": "Prohibition of Arrest of Women After Sunset",
        "legal_text": "Forbids arrest of a woman after sunset and before sunrise except under exceptional circumstances with prior written sanction from a Judicial Magistrate.",
        "simple_explanation": "Women cannot be arrested or summoned to a police station at night without a special written order from a Judicial Magistrate.",
        "punishment_or_remedy": "Night arrest without judicial sanction constitutes unlawful confinement and serious official misconduct.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },
    {
        "act_code": "CrPC",
        "section_number": "Section 100",
        "title": "Presence of Independent Witnesses During Searches",
        "legal_text": "Requires officers conducting searches to call upon two or more independent and respectable inhabitants of the locality to attend and witness the search.",
        "simple_explanation": "Police searching a home or private vehicle must invite two local independent witnesses and provide a signed search inventory.",
        "punishment_or_remedy": "Search conducted without adherence to procedure can be invalidated as illegal search and seizure in court.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },
    {
        "act_code": "CrPC",
        "section_number": "Section 436",
        "title": "Mandatory Bail in Bailable Offenses",
        "legal_text": "Declares that any person accused of a bailable offense shall be released on bail as a matter of right if prepared to furnish surety or personal bond.",
        "simple_explanation": "In minor and bailable offenses, granting bail is a statutory right, not a police or judicial discretion.",
        "punishment_or_remedy": "Refusal to release on bail when sureties are ready amounts to wrongful restraint and illegal custody.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },

    # Transfer of Property Act, 1882
    {
        "act_code": "TP Act",
        "section_number": "Section 106",
        "title": "Statutory Notice to Terminate Monthly Lease",
        "legal_text": "Prescribes that a monthly residential lease is terminable only by fifteen days' notice in writing expiring with the end of a month of the tenancy.",
        "simple_explanation": "A landlord cannot arbitrarily throw you out without giving at least 15 days written notice as per statute or the lease deed.",
        "punishment_or_remedy": "Eviction attempted without mandatory written notice is legally invalid; courts can issue stay orders.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
    },
    {
        "act_code": "TP Act",
        "section_number": "Section 108(c)",
        "title": "Tenant's Covenant for Quiet Enjoyment",
        "legal_text": "Obligates the lessor to ensure that the lessee may hold the property without interruption during the lease as long as rent is duly paid.",
        "simple_explanation": "Tenants have a legal right to peaceful enjoyment of their home. Landlords cannot harass or cut essential services.",
        "punishment_or_remedy": "Immediate injunction from Rent Authority / Civil Court to restore utility supplies and restrain harassment.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
    },
    {
        "act_code": "TP Act",
        "section_number": "Section 108(f)",
        "title": "Lessor's Obligation to Make Necessary Repairs",
        "legal_text": "Allows the lessee to make essential repairs neglected by the lessor after reasonable notice and deduct expenses from rent.",
        "simple_explanation": "If a landlord ignores major roof leaks or plumbing repairs, the tenant can carry out repairs and deduct the cost from future rent.",
        "punishment_or_remedy": "Statutory right to deduct essential repair expenses from monthly rent payments.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
    },
    {
        "act_code": "TP Act",
        "section_number": "Section 111",
        "title": "Determination of Lease and Return of Deposit",
        "legal_text": "Outlines how a lease is determined by efflux of time, requiring mutual settlement of rights and liabilities upon expiry.",
        "simple_explanation": "When a rental term ends and the tenant vacates in good order, the landlord must refund the security deposit without bogus deductions.",
        "punishment_or_remedy": "Summary civil suit or Rent Controller petition to recover withheld security deposits with interest.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
    },

    # Protection of Women from Domestic Violence Act, 2005
    {
        "act_code": "PWDVA 2005",
        "section_number": "Section 3",
        "title": "Definition of Domestic Violence",
        "legal_text": "Encompasses physical, sexual, verbal, emotional, and economic abuse that endangers the health, safety, life, limb, or well-being of the aggrieved woman.",
        "simple_explanation": "Domestic abuse is not just physical violence. Withholding money, verbal insults, and threats also constitute actionable abuse.",
        "punishment_or_remedy": "Enables immediate application before a Magistrate for protection, residence, and maintenance orders.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },
    {
        "act_code": "PWDVA 2005",
        "section_number": "Section 12",
        "title": "Application to Magistrate for Immediate Relief",
        "legal_text": "Authorizes an aggrieved woman or Protection Officer to present an application seeking urgent interim or final protection orders.",
        "simple_explanation": "Women facing mistreatment can file for fast-track judicial remedies without hiring expensive advocates.",
        "punishment_or_remedy": "Magistrate can grant ex-parte interim orders within 3 days to safeguard life and liberty.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },
    {
        "act_code": "PWDVA 2005",
        "section_number": "Section 17",
        "title": "Right to Reside in a Shared Household",
        "legal_text": "Grants every woman in a domestic relationship the statutory right to reside in the shared household regardless of property title ownership.",
        "simple_explanation": "A married woman cannot be thrown out of the matrimonial home even if the flat is owned solely by her spouse or in-laws.",
        "punishment_or_remedy": "Injunction prohibiting dispossession and mandating restoration of shared residence.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },
    {
        "act_code": "PWDVA 2005",
        "section_number": "Section 18",
        "title": "Protection Orders by Magistrate",
        "legal_text": "Empowers Magistrates to restrain the respondent from committing domestic violence, entering the woman's workplace, or communicating with her.",
        "simple_explanation": "Courts can issue restraining orders barring abusers from contacting the victim or approaching her place of work.",
        "punishment_or_remedy": "Breach of a protection order is a cognizable criminal offense punishable with up to one year imprisonment.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },
    {
        "act_code": "PWDVA 2005",
        "section_number": "Section 19",
        "title": "Residence Orders Restraining Eviction",
        "legal_text": "Authorizes courts to restrain respondents from dispossessing the woman, ordering respondents to remove themselves or secure alternate accommodation.",
        "simple_explanation": "Courts can mandate that the spouse provide equivalent alternative accommodation or vacate the premises to ensure safety.",
        "punishment_or_remedy": "Direct judicial enforcement backed by local police assistance.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },

    # Workplace & Employment Acts
    {
        "act_code": "PWA 1936",
        "section_number": "Section 15",
        "title": "Claims for Delayed Wages or Unlawful Deductions",
        "legal_text": "Establishes a statutory forum before the Labour Authority for recovering unpaid or delayed salaries along with compensation.",
        "simple_explanation": "If your employer withholds salary or makes unauthorized deductions, you can file a recovery claim before the Labour Commissioner.",
        "punishment_or_remedy": "Direction to pay outstanding wages plus compensation up to ten times the unpaid amount.",
        "official_url": "https://www.indiacode.nic.in/show-data?actid=AC_CEN_6_0_00044_193604_1523351375183",
    },
    {
        "act_code": "PGA 1972",
        "section_number": "Section 4",
        "title": "Payment of Gratuity upon Service Termination",
        "legal_text": "Mandates payment of gratuity to employees rendering continuous service for five years upon resignation, retirement, or superannuation.",
        "simple_explanation": "Completing 5 years entitles an employee to statutory gratuity, which cannot be forfeited arbitrarily by employers.",
        "punishment_or_remedy": "Mandatory disbursement within 30 days; delay incurs statutory compound interest under Section 7(3A).",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/197239",
    },
    {
        "act_code": "POSH Act 2013",
        "section_number": "Section 4",
        "title": "Constitution of Internal Complaints Committee (ICC)",
        "legal_text": "Mandates every employer of an administrative unit with 10 or more employees to constitute an Internal Committee to redress sexual harassment complaints.",
        "simple_explanation": "Workplaces with 10+ employees must maintain an active Internal Committee headed by a senior woman employee to investigate harassment.",
        "punishment_or_remedy": "Failure to constitute an ICC invites government fines up to ₹50,000 and cancellation of business license on repeated default.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2104",
    },
    {
        "act_code": "POSH Act 2013",
        "section_number": "Section 9",
        "title": "Complaint of Sexual Harassment at Workplace",
        "legal_text": "Allows any aggrieved woman to make a written complaint of sexual harassment at workplace to the Internal Committee within three months.",
        "simple_explanation": "Women subjected to unwelcome physical, verbal, or visual conduct at work can trigger a formal confidential inquiry.",
        "punishment_or_remedy": "Inquiry recommendations can include service termination of the harasser and compensation paid to the victim.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2104",
    },
    {
        "act_code": "MBA 1961",
        "section_number": "Section 5",
        "title": "Right to 26 Weeks of Paid Maternity Benefit",
        "legal_text": "Entitles every woman worker to 26 weeks of paid maternity leave calculated at the average daily wage rate.",
        "simple_explanation": "Eligible women employees are legally entitled to 26 weeks of fully paid leave for childbirth and early childcare.",
        "punishment_or_remedy": "Refusal to provide maternity pay is a criminal offense punishable with mandatory imprisonment up to one year.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1681",
    },
    {
        "act_code": "MBA 1961",
        "section_number": "Section 12",
        "title": "Dismissal During Pregnancy Declared Unlawful",
        "legal_text": "Declares any dismissal or discharge of a woman worker during her absence on maternity leave or pregnancy as completely void.",
        "simple_explanation": "Companies cannot fire or demote an employee because she applied for or took maternity leave.",
        "punishment_or_remedy": "Reinstatement in service with full back wages and damages.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1681",
    },
    {
        "act_code": "EPFA 1952",
        "section_number": "Section 6",
        "title": "Contributions to Provident Fund",
        "legal_text": "Requires employers to contribute and timely deposit both employee and employer shares to the statutory Provident Fund with EPFO.",
        "simple_explanation": "Employers who deduct PF contributions from your payslip must deposit them with EPFO each month without delay.",
        "punishment_or_remedy": "Failure to deposit deducted PF is criminal breach of trust under IPC Sec 406/409 and punishable under Sec 14 EPFA.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1898",
    },
    {
        "act_code": "IDA 1947",
        "section_number": "Section 25F",
        "title": "Conditions Precedent to Retrenchment of Workmen",
        "legal_text": "Requires employers to provide one month's written notice or notice pay, and retrenchment compensation of 15 days' average pay per year of service.",
        "simple_explanation": "Mass sudden layoffs without statutory notice pay and severance compensation are unlawful under Indian labour legislation.",
        "punishment_or_remedy": "Illegal retrenchment is void; labour courts can grant reinstatement with continuous service benefits.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1897",
    },
]


SCENARIOS_DATA = [
    # -------------------------------------------------------------
    # Category 1: Consumer Rights & E-Commerce (5 Scenarios)
    # -------------------------------------------------------------
    {
        "category_slug": "consumer-rights",
        "title": "E-Commerce Seller Refuses Refund or Return for Defective Goods",
        "slug": "defective-product-refund-refusal",
        "situation_summary": "You purchased an electronic gadget, home appliance, or clothing online from an e-commerce marketplace. The product arrived broken, counterfeit, or non-functional. Upon raising a return request within the return window, the seller or platform arbitrarily denied the refund, citing fine print or blaming the courier.",
        "what_to_do": (
            "1. Document Everything: Save the invoice, order confirmation, unboxing video/photos, and screenshots of chats with customer support.\n"
            "2. Send Written Demand: Send a formal email to the nodal/grievance officer of the e-commerce company demanding full refund within 7 working days citing Section 2(47) of the Consumer Protection Act, 2019.\n"
            "3. National Consumer Helpline: Call toll-free 1915 or register your complaint at consumerhelpline.gov.in. NCH resolves over 80% of e-commerce disputes through formal pre-litigation mediation.\n"
            "4. File on e-Jagriti / e-Daakhil: If unresolved after 15 days, lodge a consumer complaint online on the official consumer e-filing portal (e-jagriti.gov.in) before your local District Consumer Commission without needing a lawyer."
        ),
        "section_keys": [("CPA 2019", "Section 2(7)"), ("CPA 2019", "Section 2(47)"), ("CPA 2019", "Section 35")],
        "related_case_ids": [81, 60, 32, 23],
        "official_portal_url": "https://e-jagriti.gov.in/",
        "helpline_number": "1915",
        "is_featured": True,
        "display_order": 1,
    },
    {
        "category_slug": "consumer-rights",
        "title": "Sudden Flight Cancellation or Denial of Boarding Without Compensation",
        "slug": "flight-cancellation-airline-compensation",
        "situation_summary": "An airline abruptly cancels your booked flight, delays departure by several hours without meals or refreshments, or denies boarding due to overbooking, leaving you stranded at the airport and refusing a full cash refund.",
        "what_to_do": (
            "1. Demand Written Reason: Ask the airline counter for written confirmation of cancellation or denial of boarding.\n"
            "2. Invoke DGCA Passenger Charter: Under DGCA rules and CPA Section 2(11), airlines must offer an alternate flight, meals during delay, and statutory compensation up to ₹20,000 for denial of boarding.\n"
            "3. Register AirSewa Grievance: Lodge a complaint immediately on the Ministry of Civil Aviation AirSewa portal (airsewa.gov.in).\n"
            "4. Consumer Commission: If compensation is denied, file a claim on e-jagriti.gov.in for deficiency in service."
        ),
        "section_keys": [("CPA 2019", "Section 2(11)"), ("CPA 2019", "Section 35")],
        "related_case_ids": [81, 60, 32],
        "official_portal_url": "https://airsewa.gov.in/",
        "helpline_number": "1915",
        "is_featured": False,
        "display_order": 2,
    },
    {
        "category_slug": "consumer-rights",
        "title": "Misleading Advertisements and False Endorsements by Brands or Influencers",
        "slug": "misleading-advertisement-false-claims",
        "situation_summary": "You purchased a wellness, cosmetic, or investment product influenced by deceptive advertisements or celebrity endorsements promising guaranteed results, which turned out completely bogus or harmful.",
        "what_to_do": (
            "1. Preserve the Advertisements: Record screenshots, video clips, and promotional URLs showing the unsubstantiated claim.\n"
            "2. Report to CCPA: Submit a grievance to the Central Consumer Protection Authority at consumerhelpline.gov.in under CPA Section 21.\n"
            "3. Claim Redressal: Demand reimbursement of expenditure and damages before the District Consumer Commission."
        ),
        "section_keys": [("CPA 2019", "Section 21"), ("CPA 2019", "Section 2(47)")],
        "related_case_ids": [81, 60],
        "official_portal_url": "https://consumerhelpline.gov.in/",
        "helpline_number": "1915",
        "is_featured": False,
        "display_order": 3,
    },
    {
        "category_slug": "consumer-rights",
        "title": "Medical Facility Overcharging Above Quoted Package or Medical Negligence",
        "slug": "hospital-overcharging-billing-negligence",
        "situation_summary": "A private hospital bills exorbitant unexpected charges above an agreed cashless package or provides substandard emergency care causing physical complications.",
        "what_to_do": (
            "1. Secure Medical Dossier: Collect certified copies of all admission notes, surgery sheets, and detailed pharmacy bills.\n"
            "2. Audit Against Pre-Authorization: Compare final bill with cashless TPA pre-authorization approval letters.\n"
            "3. Lodge Regulatory Complaint: File an official complaint before the State Medical Council and District Consumer Forum for deficiency in service."
        ),
        "section_keys": [("CPA 2019", "Section 2(11)"), ("CPA 2019", "Section 35")],
        "related_case_ids": [81, 32, 60],
        "official_portal_url": "https://e-jagriti.gov.in/",
        "helpline_number": "1915",
        "is_featured": False,
        "display_order": 4,
    },
    {
        "category_slug": "consumer-rights",
        "title": "New Vehicle or Electronic Appliance Fails Due to Manufacturing Defect",
        "slug": "manufacturing-defect-product-liability",
        "situation_summary": "A recently purchased vehicle, electric scooter, or refrigerator suffers recurring mechanical failures or battery hazards due to inherent factory design flaws.",
        "what_to_do": (
            "1. Maintain Service Logs: Keep all job cards, workshop diagnostic reports, and correspondence with authorized centers.\n"
            "2. Invoke Product Liability: Serve legal notice under Section 84 of CPA 2019 demanding complete unit replacement or refund.\n"
            "3. District Commission Action: File a product liability action on e-jagriti.gov.in for full replacement and consequential damages."
        ),
        "section_keys": [("CPA 2019", "Section 84"), ("CPA 2019", "Section 35")],
        "related_case_ids": [81, 60, 23],
        "official_portal_url": "https://e-jagriti.gov.in/",
        "helpline_number": "1915",
        "is_featured": False,
        "display_order": 5,
    },

    # -------------------------------------------------------------
    # Category 2: Road Traffic & Motor Accidents (5 Scenarios)
    # -------------------------------------------------------------
    {
        "category_slug": "road-traffic-accidents",
        "title": "Injured in a Road Traffic Collision or Seeking Accident Compensation",
        "slug": "road-accident-injury-mact-compensation",
        "situation_summary": "You or a family member was struck by a speeding or negligent motor vehicle on a public road, resulting in hospitalization, surgery, or permanent disability. The at-fault driver's insurance refuses to cover the full medical expenses, or the driver fled the scene (hit-and-run).",
        "what_to_do": (
            "1. Medical Treatment & Medico-Legal Case (MLC): Ensure the hospital records the injury as an MLC. Under Section 134A, Good Samaritans who brought you cannot be questioned or harassed.\n"
            "2. Police FIR & Detailed Accident Report (DAR): Ensure an FIR is lodged at the jurisdiction police station. Police are statutorily required to file a Detailed Accident Report (DAR) within 90 days.\n"
            "3. Preserve All Evidence: Retain all hospital discharge summaries, pharmacy bills, diagnostic reports, and proof of lost income/salary slips.\n"
            "4. File MACT Claim: File an application under Section 166 of the Motor Vehicles Act before the Motor Accidents Claims Tribunal in the district where the accident occurred or where you reside."
        ),
        "section_keys": [("MVA 1988", "Section 134A"), ("MVA 1988", "Section 166")],
        "related_case_ids": [92, 101, 80, 61, 60, 40, 57, 89],
        "official_portal_url": "https://vcourts.gov.in/",
        "helpline_number": "1073",
        "is_featured": True,
        "display_order": 6,
    },
    {
        "category_slug": "road-traffic-accidents",
        "title": "Traffic Police Demanding Physical Documents When DigiLocker or mParivahan Shown",
        "slug": "digital-documents-digilocker-challan",
        "situation_summary": "Traffic police stop your vehicle and insist on inspecting physical laminated RC or Driving License cards, refusing to accept verified digital copies stored on DigiLocker or mParivahan and threatening challans.",
        "what_to_do": (
            "1. Display Verified QR on App: Open government DigiLocker or mParivahan showing the official digital certificate.\n"
            "2. Cite Section 130 MVA & Rule 139 CMVR: Politely inform officers that digital credentials carry equal legal status under Ministry notifications.\n"
            "3. Virtual Courts Review: If wrongfully penalized, challenge the challan via the national Virtual Courts portal (vcourts.gov.in)."
        ),
        "section_keys": [("MVA 1988", "Section 130")],
        "related_case_ids": [101, 92, 80],
        "official_portal_url": "https://vcourts.gov.in/",
        "helpline_number": "1073",
        "is_featured": False,
        "display_order": 7,
    },
    {
        "category_slug": "road-traffic-accidents",
        "title": "Victim of Hit-and-Run Road Accident Seeking Government Compensation",
        "slug": "hit-and-run-solatium-scheme",
        "situation_summary": "A pedestrian or two-wheeler rider is hit by an unidentified fleeing vehicle, leaving the victim severely injured or deceased with no driver to claim insurance from.",
        "what_to_do": (
            "1. Register Police FIR: Ensure the FIR records the incident as a hit-and-run case under Section 161 MVA.\n"
            "2. Form I Application: Submit Form I to the Sub-Divisional Magistrate / Claims Enquiry Officer within 6 months.\n"
            "3. Receive Solatium Payout: Government disburses ₹2 Lakhs in death cases and ₹50,000 for grievous hurt under the statutory solatium scheme."
        ),
        "section_keys": [("MVA 1988", "Section 161"), ("MVA 1988", "Section 134A")],
        "related_case_ids": [92, 101, 80],
        "official_portal_url": "https://morth.nic.in/",
        "helpline_number": "1073",
        "is_featured": False,
        "display_order": 8,
    },
    {
        "category_slug": "road-traffic-accidents",
        "title": "Traffic Personnel Unlawfully Snatching Vehicle Ignition Keys or Physical Towing",
        "slug": "unlawful-vehicle-key-snatching",
        "situation_summary": "A traffic constable or towing contractor forcefully snatches your motorcycle or car keys from the ignition or tows a car while occupants are inside.",
        "what_to_do": (
            "1. Record the Encounter: Note the officer's name badge or vehicle registration number.\n"
            "2. Know Your Rights: Snatching keys violates Police Act guidelines and MVA Section 206; towing with passengers inside is strictly prohibited.\n"
            "3. File Senior Complaint: Lodge a grievance before the Deputy Commissioner of Police (Traffic) or on the state traffic grievance portal."
        ),
        "section_keys": [("MVA 1988", "Section 206")],
        "related_case_ids": [101, 92],
        "official_portal_url": "https://echallan.parivahan.gov.in/",
        "helpline_number": "1073",
        "is_featured": False,
        "display_order": 9,
    },
    {
        "category_slug": "road-traffic-accidents",
        "title": "Contesting Wrongful or Erroneous Electronic Traffic E-Challan",
        "slug": "disputing-erroneous-echallan",
        "situation_summary": "You receive an automated SMS challan for jumping a signal or speeding in a location you never visited, caused by camera OCR error or vehicle number plate cloning.",
        "what_to_do": (
            "1. Access Parivahan Portal: Log into echallan.parivahan.gov.in and download the photographic evidence.\n"
            "2. Submit Grievance Online: File an online dispute stating mismatch in vehicle model, color, or location.\n"
            "3. Contest in Virtual Court: If rejected, contest the challan before the Virtual Court Magistrate without physically attending."
        ),
        "section_keys": [("MVA 1988", "Section 130"), ("MVA 1988", "Section 206")],
        "related_case_ids": [101, 92, 80],
        "official_portal_url": "https://echallan.parivahan.gov.in/",
        "helpline_number": "1073",
        "is_featured": False,
        "display_order": 10,
    },

    # -------------------------------------------------------------
    # Category 3: Cyber Crime & Online Fraud (5 Scenarios)
    # -------------------------------------------------------------
    {
        "category_slug": "cyber-crime",
        "title": "Victim of Online Banking Fraud, Phishing, or Unauthorized UPI Deduction",
        "slug": "online-upi-banking-fraud",
        "situation_summary": "You received a fraudulent call, clicked an SMS link, or found that money was deducted from your bank account or UPI wallet without your consent through an OTP hack, remote screen-sharing app, or spoofed banking portal.",
        "what_to_do": (
            "1. Golden Hour Reporting: Immediately dial the National Cyber Crime Helpline '1930' within the first 2-3 hours. Cyber police can issue an instant freeze command to the beneficiary bank or wallet to stop the money from being cashed out.\n"
            "2. Report on Cyber Portal: File a formal complaint at cybercrime.gov.in and download the acknowledgment number.\n"
            "3. Intimate Your Bank Immediately: Inform your home bank branch in writing within 3 calendar days. Under RBI circular guidelines (DBR.No.Leg.BC.78/09.07.005/2017-18), a customer has zero liability for unauthorized electronic transactions if reported within 3 days.\n"
            "4. Block Cards & UPI: Immediately block the compromised debit/credit card, reset internet banking passwords, and deregister the UPI handle."
        ),
        "section_keys": [("IT Act", "Section 43"), ("IT Act", "Section 66C"), ("IT Act", "Section 66D")],
        "related_case_ids": [91, 33, 93, 94, 96],
        "official_portal_url": "https://cybercrime.gov.in/",
        "helpline_number": "1930",
        "is_featured": True,
        "display_order": 11,
    },
    {
        "category_slug": "cyber-crime",
        "title": "Targeted in Cyber Blackmail, Video Call Traps, or Deepfake Extortion",
        "slug": "sextortion-video-call-blackmail",
        "situation_summary": "You received an unsolicited video call or message on WhatsApp/Instagram where criminals recorded or morphed compromising media and are threatening to blast it to your family unless extortion ransom is paid.",
        "what_to_do": (
            "1. Do Not Pay Any Money: Paying never stops blackmail; extortionists demand ever-increasing amounts.\n"
            "2. Secure Evidence & Block: Take screenshots of phone numbers, UPI IDs, and chat threads before blocking the profiles.\n"
            "3. Report to 1930 & cybercrime.gov.in: File an urgent report under IT Act Sections 66E and 67.\n"
            "4. Content Takedown: Register on StopNCII.org to generate digital hashes that prevent the imagery from uploading across major social platforms."
        ),
        "section_keys": [("IT Act", "Section 66E"), ("IT Act", "Section 67"), ("IT Act", "Section 66D")],
        "related_case_ids": [91, 33, 96],
        "official_portal_url": "https://cybercrime.gov.in/",
        "helpline_number": "1930",
        "is_featured": False,
        "display_order": 12,
    },
    {
        "category_slug": "cyber-crime",
        "title": "Identity Theft via Unauthorized SIM Swap or Fraudulent Instant Loans",
        "slug": "unauthorized-sim-swap-identity-theft",
        "situation_summary": "Your mobile network signals abruptly go blank (SIM swap), and fraudsters use your identity documents to obtain instant personal loans through illicit lending apps.",
        "what_to_do": (
            "1. Contact Telecom Provider: Immediately visit your nearest telecom gallery to deactivate the duplicate SIM card.\n"
            "2. Check CIBIL / Experian Credit: Check your credit reports for unauthorized loan accounts opened using your PAN/Aadhaar.\n"
            "3. Lodge Cyber Police Complaint: File a complaint on cybercrime.gov.in for identity theft under Section 66C."
        ),
        "section_keys": [("IT Act", "Section 43"), ("IT Act", "Section 66C")],
        "related_case_ids": [91, 96],
        "official_portal_url": "https://cybercrime.gov.in/",
        "helpline_number": "1930",
        "is_featured": False,
        "display_order": 13,
    },
    {
        "category_slug": "cyber-crime",
        "title": "Lured into Fake Work-From-Home, Task, or Crypto Investment Telegram Scam",
        "slug": "fake-work-from-home-investment-scam",
        "situation_summary": "You were contacted on WhatsApp offering part-time earnings for liking videos or hotels, directed to a Telegram channel, and coerced into depositing large sums in a sham investment portal that froze withdrawals.",
        "what_to_do": (
            "1. Immediate Account Freeze Call: Dial 1930 immediately to freeze recipient mule accounts.\n"
            "2. Preserve Payment Trails: Compile all UTR transaction IDs, beneficiary bank accounts, and chat transcripts.\n"
            "3. File Cyber Complaint: Submit complete details on cybercrime.gov.in under Section 66D for cheating by personation."
        ),
        "section_keys": [("IT Act", "Section 66D")],
        "related_case_ids": [91, 33, 94],
        "official_portal_url": "https://cybercrime.gov.in/",
        "helpline_number": "1930",
        "is_featured": False,
        "display_order": 14,
    },
    {
        "category_slug": "cyber-crime",
        "title": "Victim of Online Harassment, Doxxing, and Persistent Cyberstalking",
        "slug": "cyberstalking-online-harassment",
        "situation_summary": "An individual persistently harasses you online, creating fake social media profiles with your photos and publishing your phone number and home address publicly.",
        "what_to_do": (
            "1. Archive Evidence: Preserve URLs, usernames, screenshots, and timestamps of all abusive posts.\n"
            "2. Report to Platform Grievance Officer: Submit formal takedown requests under IT Intermediary Rules.\n"
            "3. Lodge Complaint on Cyber Portal: File under IT Act Section 66E and 67 on cybercrime.gov.in."
        ),
        "section_keys": [("IT Act", "Section 66E"), ("IT Act", "Section 67")],
        "related_case_ids": [91, 93],
        "official_portal_url": "https://cybercrime.gov.in/",
        "helpline_number": "1930",
        "is_featured": False,
        "display_order": 15,
    },

    # -------------------------------------------------------------
    # Category 4: Police Powers & Arrest Rights (5 Scenarios)
    # -------------------------------------------------------------
    {
        "category_slug": "police-arrest-rights",
        "title": "Summoned to Police Station or Facing Arbitrary Detention Without Warrant",
        "slug": "police-summons-arrest-rights",
        "situation_summary": "Police officers arrive at your residence or call you demanding immediate appearance at the police station without producing a written warrant or notice. You are threatened with arrest in connection with a complaint filed against you or an associate.",
        "what_to_do": (
            "1. Demand Written Notice under Section 41A: For any offense carrying a maximum punishment of 7 years or less, police MUST issue a written notice specifying date and time of appearance. Ask politely for the Section 41A notice.\n"
            "2. Verify Officer Identity: Every arresting officer must wear clear name tags showing their designation. Demand the creation of an official 'Memo of Arrest' signed by at least one witness and yourself.\n"
            "3. Inform a Relative: Under Section 50A CrPC, you have an absolute right to have one friend or family member notified of your detention and location immediately.\n"
            "4. 24-Hour Production Mandate: Under Section 57 CrPC and Article 22(2) of the Constitution, police cannot hold you for more than 24 hours without presenting you physically before a Judicial Magistrate."
        ),
        "section_keys": [("CrPC", "Section 41A"), ("CrPC", "Section 50"), ("CrPC", "Section 57")],
        "related_case_ids": [72, 91, 56, 95, 27, 96, 105, 15],
        "official_portal_url": "https://nalsa.gov.in/",
        "helpline_number": "15100",
        "is_featured": True,
        "display_order": 16,
    },
    {
        "category_slug": "police-arrest-rights",
        "title": "Police Station Refusing to Register First Information Report (FIR) or Zero FIR",
        "slug": "refusal-to-register-fir-zero-fir",
        "situation_summary": "You visit a police station to report a robbery, theft, or physical assault, but duty officers refuse to lodge an FIR, claiming the incident falls under another police jurisdiction.",
        "what_to_do": (
            "1. Demand a Zero FIR: In cognizable offenses, any police station is statutorily mandated to lodge a 'Zero FIR' and transfer it to the concerned police station.\n"
            "2. Send Written Complaint to SP: Under Section 154(3) CrPC, send your written complaint via registered speed post to the Superintendent of Police / Commissioner.\n"
            "3. Approach Magistrate under Section 156(3): If police fail to act, file a petition before the Judicial Magistrate for an order directing registration of FIR."
        ),
        "section_keys": [("CrPC", "Section 154")],
        "related_case_ids": [72, 91, 96],
        "official_portal_url": "https://nalsa.gov.in/",
        "helpline_number": "15100",
        "is_featured": False,
        "display_order": 17,
    },
    {
        "category_slug": "police-arrest-rights",
        "title": "Police Demanding Woman to Visit Station at Night or Arrest After Sunset",
        "slug": "women-arrest-after-sunset",
        "situation_summary": "Police attempt to arrest a woman accused of an offense after sunset or demand her physical presence at the police station during late evening hours without a female officer.",
        "what_to_do": (
            "1. Invoke Section 46(4) CrPC: Clearly cite that no woman can be arrested after sunset and before sunrise without prior written permission from a Judicial Magistrate.\n"
            "2. Demand Presence of Female Officer: Any search or detention of a female citizen can only be carried out by a female police officer.\n"
            "3. Inform National Commission for Women (NCW): Report unlawful police actions immediately to NCW (181) and District Legal Services Authority."
        ),
        "section_keys": [("CrPC", "Section 46(4)"), ("CrPC", "Section 50")],
        "related_case_ids": [72, 56, 91],
        "official_portal_url": "https://ncw.nic.in/",
        "helpline_number": "181",
        "is_featured": False,
        "display_order": 18,
    },
    {
        "category_slug": "police-arrest-rights",
        "title": "Police Searching Home or Personal Vehicle Without Warrant or Independent Witnesses",
        "slug": "unlawful-residence-search-without-warrant",
        "situation_summary": "Police personnel conduct an unannounced raid on your residence or stop your car and search personal bags without showing a search warrant or calling local witnesses.",
        "what_to_do": (
            "1. Demand Search Warrant or Section 165 Grounds: Ask for a judicial warrant or written grounds of urgency under Section 165 CrPC.\n"
            "2. Insist on Panch Witnesses under Section 100: Demand the presence of two independent local neighbors to observe the search.\n"
            "3. Demand Search List: Obtain an immediate signed copy of the panchnama listing any item seized."
        ),
        "section_keys": [("CrPC", "Section 100")],
        "related_case_ids": [72, 91, 96],
        "official_portal_url": "https://nalsa.gov.in/",
        "helpline_number": "15100",
        "is_featured": False,
        "display_order": 19,
    },
    {
        "category_slug": "police-arrest-rights",
        "title": "Police Refusing to Grant Bail at Station for a Recognizably Bailable Offense",
        "slug": "denial-of-bail-bailable-offense",
        "situation_summary": "You are detained for an offense classified as bailable under the First Schedule of CrPC, but the investigating officer refuses to accept surety bonds and keeps you detained in the lockup.",
        "what_to_do": (
            "1. Invoke Section 436 CrPC: Bail is an absolute statutory right for bailable offenses once sureties are produced.\n"
            "2. Document Surety Presentation: Submit written bond papers and take an acknowledged copy from the duty officer.\n"
            "3. Contact DLSA Duty Counsel: Contact the District Legal Services Authority lawyer at 15100 for emergency bail representation before the Magistrate."
        ),
        "section_keys": [("CrPC", "Section 436"), ("CrPC", "Section 50")],
        "related_case_ids": [72, 91, 95],
        "official_portal_url": "https://nalsa.gov.in/",
        "helpline_number": "15100",
        "is_featured": False,
        "display_order": 20,
    },

    # -------------------------------------------------------------
    # Category 5: Tenant & Rental Housing Rights (5 Scenarios)
    # -------------------------------------------------------------
    {
        "category_slug": "tenant-housing-rights",
        "title": "Landlord Disconnecting Essential Amenities or Evicting Without Notice",
        "slug": "landlord-illegal-eviction-amenity-cutoff",
        "situation_summary": "Your landlord has abruptly cut off electricity, water supply, or cooking gas connections, or locked the main gate to force you to vacate immediately or accept an unreasonable rent hike, without providing reasonable notice or following the rent agreement.",
        "what_to_do": (
            "1. Review Agreement Terms: Check your written lease agreement for the notice period clause. Under Section 106 Transfer of Property Act, a minimum 15-day statutory written notice is mandatory in monthly residential tenancies.\n"
            "2. Evidence Collection: Take video evidence and photographs demonstrating that water or power has been intentionally disconnected. Keep proof of timely rent payments (UPI receipts, bank statements).\n"
            "3. Police Complaint for Harassment: File a complaint at the local police station for wrongful restraint and criminal intimidation. Police can direct the landlord to restore essential utilities.\n"
            "4. Approach Rent Controller / Civil Court: File an urgent petition before the local Rent Authority or Civil Court seeking an interim injunction restraining the landlord from illegal dispossession."
        ),
        "section_keys": [("TP Act", "Section 106"), ("TP Act", "Section 108(c)")],
        "related_case_ids": [49, 38, 103, 48, 78, 93, 102, 71],
        "official_portal_url": "https://ecourts.gov.in/",
        "helpline_number": "15100",
        "is_featured": True,
        "display_order": 21,
    },
    {
        "category_slug": "tenant-housing-rights",
        "title": "Landlord Illegally Withholding Rental Security Deposit for Normal Wear and Tear",
        "slug": "withholding-security-deposit-deductions",
        "situation_summary": "Upon vacating the rented apartment after fulfilling full notice, the owner refuses to refund your multi-month security deposit, claiming bogus deductions for repainting and normal wear.",
        "what_to_do": (
            "1. Conduct Joint Handover: Document apartment condition with photos and videos on handover day.\n"
            "2. Issue Formal Demand Notice: Send a registered notice citing Section 111 TP Act demanding full return of deposit within 15 days.\n"
            "3. File Before Rent Authority: Lodge a recovery petition before the local Rent Controller / Civil Court for return of deposit with interest."
        ),
        "section_keys": [("TP Act", "Section 108(c)"), ("TP Act", "Section 111")],
        "related_case_ids": [49, 38, 103, 78],
        "official_portal_url": "https://ecourts.gov.in/",
        "helpline_number": "15100",
        "is_featured": False,
        "display_order": 22,
    },
    {
        "category_slug": "tenant-housing-rights",
        "title": "Landlord Entering Leased Apartment Without Prior Notice or Tenant Consent",
        "slug": "landlord-trespass-unannounced-entry",
        "situation_summary": "The property owner enters the premises using a spare master key without warning or permissions while you are away or resting, intruding upon your privacy.",
        "what_to_do": (
            "1. Assert Covenant of Quiet Enjoyment: Inform the landlord in writing that Section 108(c) TP Act grants exclusive peaceful possession to the tenant.\n"
            "2. Set Reasonable Visitation Times: Formally agree that visits for maintenance must be scheduled with at least 24 hours prior written notice.\n"
            "3. Police Complaint for Trespass: Continued unconsented entry constitutes criminal trespass under IPC Section 441/448."
        ),
        "section_keys": [("TP Act", "Section 108(c)")],
        "related_case_ids": [49, 38, 103],
        "official_portal_url": "https://ecourts.gov.in/",
        "helpline_number": "15100",
        "is_featured": False,
        "display_order": 23,
    },
    {
        "category_slug": "tenant-housing-rights",
        "title": "Landlord Demanding Sudden Arbitrary Rent Increase in Middle of Active Lease",
        "slug": "arbitrary-rent-hike-during-lease",
        "situation_summary": "The landlord demands a sudden 30% rent increase six months into an 11-month agreement and threatens eviction if the unagreed escalation is not paid immediately.",
        "what_to_do": (
            "1. Stand on Registered/Signed Agreement: Rent cannot be increased during an active contractual term without explicit mutual contract terms.\n"
            "2. Continue Agreed Rent Payments: Pay the agreed rent on time via verifiable bank transfer or UPI to maintain proof of compliance.\n"
            "3. Rent Control Protection: Approach the Rent Control Court if the landlord refuses to accept the agreed rent amount."
        ),
        "section_keys": [("TP Act", "Section 106"), ("TP Act", "Section 108(c)")],
        "related_case_ids": [49, 38, 78],
        "official_portal_url": "https://ecourts.gov.in/",
        "helpline_number": "15100",
        "is_featured": False,
        "display_order": 24,
    },
    {
        "category_slug": "tenant-housing-rights",
        "title": "Landlord Refusing Essential Structural Repairs Causing Safety or Health Hazard",
        "slug": "landlord-refusing-structural-repairs",
        "situation_summary": "Major ceiling seepage or faulty wiring develops in the flat, and the landlord refuses to carry out repairs, rendering the premises hazardous.",
        "what_to_do": (
            "1. Give Written Repair Notice: Send written notice under Section 108(f) TP Act requesting repairs within 30 days.\n"
            "2. Carry Out and Deduct: If landlord neglects repairs, the tenant may execute repairs and legally deduct the cost from monthly rent.\n"
            "3. Seek Urgent Repair Orders: Petition local Rent Authority for emergency structural maintenance directions."
        ),
        "section_keys": [("TP Act", "Section 108(f)")],
        "related_case_ids": [49, 103],
        "official_portal_url": "https://ecourts.gov.in/",
        "helpline_number": "15100",
        "is_featured": False,
        "display_order": 25,
    },

    # -------------------------------------------------------------
    # Category 6: Women's Safety & Domestic Protection (5 Scenarios)
    # -------------------------------------------------------------
    {
        "category_slug": "womens-safety",
        "title": "Facing Physical, Mental, or Economic Abuse in Shared Matrimonial Home",
        "slug": "domestic-violence-shared-household-protection",
        "situation_summary": "A married woman is subjected to physical assaults, continuous verbal humiliation, dowry harassment, or denial of basic financial resources by her spouse or in-laws, and is threatened with being expelled from the matrimonial home.",
        "what_to_do": (
            "1. Ensure Immediate Safety: If in physical danger, dial Emergency '112' or Women Helpline '181' / '1091'. Police will dispatch emergency response teams.\n"
            "2. Contact Protection Officer: Every district has designated Protection Officers under the Domestic Violence Act. They prepare a Domestic Incident Report (DIR) free of cost.\n"
            "3. File under Section 12 PWDVA: File an application before the Judicial Magistrate. You can seek: (a) Protection Order (Sec 18) preventing the abuser from entering your space; (b) Residence Order (Sec 19) confirming your right to stay in the home.\n"
            "4. Free Legal Aid: Women are entitled to 100% free legal representation from NALSA / DLSA advocates regardless of income."
        ),
        "section_keys": [("PWDVA 2005", "Section 3"), ("PWDVA 2005", "Section 12"), ("PWDVA 2005", "Section 17")],
        "related_case_ids": [93, 86, 56, 60, 48],
        "official_portal_url": "https://nalsa.gov.in/",
        "helpline_number": "181",
        "is_featured": True,
        "display_order": 26,
    },
    {
        "category_slug": "womens-safety",
        "title": "Facing Workplace Sexual Harassment and Employer Failure to Constitute ICC",
        "slug": "workplace-sexual-harassment-posh",
        "situation_summary": "A female corporate or factory employee faces sexually colored remarks, unwelcome touching, or demands for sexual favors, and the employer has no Internal Committee (ICC) to investigate.",
        "what_to_do": (
            "1. Submit Written Complaint under POSH: File a written complaint to the Internal Committee or Local Complaints Committee (LCC) within 3 months.\n"
            "2. Report Missing ICC to District Officer: If the company has no ICC, report to the District Officer under Section 4 of POSH Act.\n"
            "3. SHe-Box Portal: Register the grievance on the Ministry of Women & Child Development SHe-Box portal (shebox.wcd.gov.in)."
        ),
        "section_keys": [("POSH Act 2013", "Section 4"), ("POSH Act 2013", "Section 9")],
        "related_case_ids": [93, 56, 86],
        "official_portal_url": "https://shebox.wcd.gov.in/",
        "helpline_number": "181",
        "is_featured": False,
        "display_order": 27,
    },
    {
        "category_slug": "womens-safety",
        "title": "In-Laws or Husband Refusing to Return Stridhan and Jewelry Upon Separation",
        "slug": "withholding-stridhan-after-separation",
        "situation_summary": "Following marital separation, the husband and his relatives refuse to return the woman's jewelry, gifts, and personal assets given at wedding (Stridhan).",
        "what_to_do": (
            "1. Stridhan is Absolute Property: Under Supreme Court precedent (Pratibha Rani v. Suraj Kumar), a woman is the sole absolute owner of Stridhan.\n"
            "2. Application under Section 18(1)(f) PWDVA: Apply to the Magistrate for an immediate order directing restoration of all Stridhan articles.\n"
            "3. Criminal Breach of Trust: Withholding Stridhan also constitutes criminal breach of trust under Section 406 IPC."
        ),
        "section_keys": [("PWDVA 2005", "Section 3"), ("PWDVA 2005", "Section 18")],
        "related_case_ids": [93, 86, 48],
        "official_portal_url": "https://nalsa.gov.in/",
        "helpline_number": "181",
        "is_featured": False,
        "display_order": 28,
    },
    {
        "category_slug": "womens-safety",
        "title": "Attempted Illegal Eviction or Locking Out of Married Woman from Matrimonial Residence",
        "slug": "threat-of-expulsion-matrimonial-home",
        "situation_summary": "A husband or father-in-law changes the entrance locks or threatens to pack up the woman's belongings while she is visiting her parents, locking her out.",
        "what_to_do": (
            "1. Emergency Police Assistance: Call 112 or local Women's Cell to prevent dispossession.\n"
            "2. Ex-Parte Residence Order: File urgent petition under Section 17 & 19 PWDVA. Courts can order police to break locks and restore possession.\n"
            "3. Supreme Court Ruling: The Supreme Court (Satish Chander Ahuja v. Sneha Ahuja) affirmed that shared household includes properties owned by in-laws."
        ),
        "section_keys": [("PWDVA 2005", "Section 17"), ("PWDVA 2005", "Section 19")],
        "related_case_ids": [93, 86, 60],
        "official_portal_url": "https://nalsa.gov.in/",
        "helpline_number": "181",
        "is_featured": False,
        "display_order": 29,
    },
    {
        "category_slug": "womens-safety",
        "title": "Unlawful Recording, Voyeurism, or Dissemination of Private Photos Without Consent",
        "slug": "cyber-harassment-voyeurism-privacy",
        "situation_summary": "Hidden cameras or unconsented recording is discovered in a rented room, hostel, or changing room, or an acquaintance threatens to leak intimate pictures.",
        "what_to_do": (
            "1. Secure Device Evidence: Preserve the recording device or camera without altering forensic data.\n"
            "2. File Police FIR: Lodge an FIR under Section 354C IPC (voyeurism) and IT Act Section 66E.\n"
            "3. Immediate Digital Takedown: File report on cybercrime.gov.in and National Commission for Women portal."
        ),
        "section_keys": [("IT Act", "Section 66E"), ("PWDVA 2005", "Section 3")],
        "related_case_ids": [93, 91, 56],
        "official_portal_url": "https://ncw.nic.in/",
        "helpline_number": "181",
        "is_featured": False,
        "display_order": 30,
    },

    # -------------------------------------------------------------
    # Category 7: Workplace & Employment Rights (5 Scenarios)
    # -------------------------------------------------------------
    {
        "category_slug": "workplace-employment",
        "title": "Employer Withholding Salary, Final Settlement (FnF), or Experience Letter",
        "slug": "unpaid-wages-withheld-relieving-letter",
        "situation_summary": "You resigned from your job after serving the required contractual notice period, but the employer refuses to release your final salary, accrued leave encashment, statutory gratuity, or mandatory relieving/experience letter, claiming arbitrary company policies.",
        "what_to_do": (
            "1. Issue Formal Legal Demand Notice: Send a registered email and speed post notice to HR and Company Directors detailing your employment dates, notice period completion, and exact outstanding dues.\n"
            "2. File Before Labour Commissioner: Under Section 15 of the Payment of Wages Act, you can file an application before the controlling authority. Delayed wages attract compensation up to 10 times the unpaid amount.\n"
            "3. Claim Statutory Gratuity: If you completed 5 years of service, submit 'Form I' under the Payment of Gratuity Act, 1972. Employers must settle gratuity within 30 days or pay compound interest.\n"
            "4. Ministry of Labour Samadhan Portal: Register your grievance on the Central Government Samadhan portal (samadhan.labour.gov.in) for conciliation proceedings."
        ),
        "section_keys": [("PWA 1936", "Section 15"), ("PGA 1972", "Section 4")],
        "related_case_ids": [40, 94, 97, 95, 50, 21, 22, 23],
        "official_portal_url": "https://samadhan.labour.gov.in/",
        "helpline_number": "14434",
        "is_featured": True,
        "display_order": 31,
    },
    {
        "category_slug": "workplace-employment",
        "title": "Sudden Retrenchment or Termination Without Statutory Notice Pay or Compensation",
        "slug": "illegal-termination-without-notice-retrenchment",
        "situation_summary": "Your company carries out sudden terminations overnight, terminating your employment with immediate effect without providing 30 days notice or statutory retrenchment compensation.",
        "what_to_do": (
            "1. Review Appointment Letter & IDA: Check retrenchment clauses. Under Section 25F Industrial Disputes Act, retrenchment is void without 1 month notice and 15 days pay per year of service.\n"
            "2. Contest Termination Legality: Send written protest refusing unlawful termination without statutory benefits.\n"
            "3. Conciliation on Samadhan Portal: Raise an industrial dispute on samadhan.labour.gov.in before the Labour Officer."
        ),
        "section_keys": [("IDA 1947", "Section 25F")],
        "related_case_ids": [40, 95, 94, 50],
        "official_portal_url": "https://samadhan.labour.gov.in/",
        "helpline_number": "14434",
        "is_featured": False,
        "display_order": 32,
    },
    {
        "category_slug": "workplace-employment",
        "title": "Denial of Paid Maternity Leave or Termination During Pregnancy and Childbirth",
        "slug": "denial-of-maternity-benefits-or-firing",
        "situation_summary": "A female employee informs management of pregnancy and requests 26 weeks statutory maternity leave, but the employer cancels the benefits or terminates her service.",
        "what_to_do": (
            "1. Invoke Section 5 & 12 Maternity Benefit Act: Women completing 80 days of service in 12 months are legally entitled to 26 weeks paid leave; termination during pregnancy is void in law.\n"
            "2. Formal Written Protest: Send email to HR citing statutory obligations and Supreme Court rulings.\n"
            "3. File Complaint with Labour Inspector: File formal complaint with the State Labour Commissioner; violation invites criminal penalties for employers."
        ),
        "section_keys": [("MBA 1961", "Section 5"), ("MBA 1961", "Section 12")],
        "related_case_ids": [40, 93, 86],
        "official_portal_url": "https://samadhan.labour.gov.in/",
        "helpline_number": "14434",
        "is_featured": False,
        "display_order": 33,
    },
    {
        "category_slug": "workplace-employment",
        "title": "Employer Deducting Provident Fund (PF) from Monthly Salary but Failing to Deposit",
        "slug": "non-remittance-of-provident-fund",
        "situation_summary": "You check your EPFO Member Passbook online and discover your employer deducted PF money from your monthly salary for 6 months but never deposited it with the EPFO.",
        "what_to_do": (
            "1. Download EPFO Passbook & Payslips: Gather salary slips showing monthly PF deduction and matching EPFO UAN passbook statement showing missing deposits.\n"
            "2. File EPFiGMS Grievance: Lodge an official complaint on the EPFO grievance portal (epfigms.gov.in).\n"
            "3. Criminal Liability: Non-remittance of employee contributions amounts to criminal breach of trust; EPFO initiates recovery and prosecution."
        ),
        "section_keys": [("EPFA 1952", "Section 6"), ("PWA 1936", "Section 15")],
        "related_case_ids": [97, 40, 94],
        "official_portal_url": "https://epfigms.gov.in/",
        "helpline_number": "14434",
        "is_featured": False,
        "display_order": 34,
    },
    {
        "category_slug": "workplace-employment",
        "title": "Employer Forcibly Retaining Original Educational Certificates or Demanding Bond Amount",
        "slug": "withholding-degree-certificates-service-bond",
        "situation_summary": "Upon hiring, the company took your original degree marksheets and certificates, refusing to return them upon resignation unless an exorbitant employment bond sum is paid.",
        "what_to_do": (
            "1. Retaining Originals is Unlawful: Ministry of Labour and AICTE guidelines explicitly prohibit employers from seizing original educational documents.\n"
            "2. Serve Legal Notice: Demand unconditional return of personal documents within 7 days.\n"
            "3. Police Complaint for Unlawful Retention: File a complaint for wrongful confinement of property and extortion."
        ),
        "section_keys": [("PWA 1936", "Section 15")],
        "related_case_ids": [40, 94, 95],
        "official_portal_url": "https://samadhan.labour.gov.in/",
        "helpline_number": "14434",
        "is_featured": False,
        "display_order": 35,
    },
]


class Command(BaseCommand):
    help = "Seed database with verified Indian legal categories, Acts, sections, and real-life citizen scenarios."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing laws data before seeding.'
        )

    def handle(self, *args, **options):
        if options.get('clear'):
            LegalScenario.objects.all().delete()
            LawSection.objects.all().delete()
            LawAct.objects.all().delete()
            LawCategory.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing Know Your Law data."))

        # 1. Seed Categories
        categories_map = {}
        for cdata in CATEGORIES_DATA:
            cat, created = LawCategory.objects.update_or_create(
                slug=cdata["slug"],
                defaults=cdata,
            )
            categories_map[cdata["slug"]] = cat

        # 2. Seed Acts
        acts_map = {}
        for adata in ACTS_DATA:
            act, created = LawAct.objects.update_or_create(
                act_name=adata["act_name"],
                defaults=adata,
            )
            if adata["short_code"]:
                acts_map[adata["short_code"]] = act
            acts_map[adata["act_name"]] = act

        # 3. Seed Sections
        sections_map = {}
        for sdata in SECTIONS_DATA:
            act = acts_map.get(sdata["act_code"])
            if not act:
                continue
            sec, created = LawSection.objects.update_or_create(
                act=act,
                section_number=sdata["section_number"],
                defaults={
                    "title": sdata["title"],
                    "legal_text": sdata["legal_text"],
                    "simple_explanation": sdata["simple_explanation"],
                    "punishment_or_remedy": sdata.get("punishment_or_remedy", ""),
                    "official_url": sdata["official_url"],
                }
            )
            sections_map[(sdata["act_code"], sdata["section_number"])] = sec

        # 4. Seed Scenarios & Link Sections
        scenarios_count = 0
        for scdata in SCENARIOS_DATA:
            cat = categories_map.get(scdata["category_slug"])
            if not cat:
                continue

            scenario, created = LegalScenario.objects.update_or_create(
                slug=scdata["slug"],
                defaults={
                    "category": cat,
                    "title": scdata["title"],
                    "situation_summary": scdata["situation_summary"],
                    "what_to_do": scdata["what_to_do"],
                    "official_portal_url": scdata.get("official_portal_url", ""),
                    "helpline_number": scdata.get("helpline_number", ""),
                    "is_featured": scdata.get("is_featured", False),
                    "display_order": scdata.get("display_order", 0),
                }
            )

            # Link sections
            sections_to_add = []
            for act_code, sec_num in scdata.get("section_keys", []):
                sec = sections_map.get((act_code, sec_num))
                if sec:
                    sections_to_add.append(sec)
            scenario.sections.set(sections_to_add)

            # Link related authentic Supreme Court cases
            related_ids = scdata.get("related_case_ids", [])
            if related_ids:
                cases_to_add = Case.objects.filter(id__in=related_ids).exclude(source_name="DEMO SOURCE")
                scenario.related_cases.set(cases_to_add)

            scenarios_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded Know Your Law dataset: "
            f"{LawCategory.objects.count()} categories, "
            f"{LawAct.objects.count()} Acts, "
            f"{LawSection.objects.count()} sections, "
            f"{scenarios_count} scenarios."
        ))
