"""
Management command to seed authentic Indian legal categories, Acts, sections, and real-life scenarios.
All Acts and sections reference real statutory enactments with verified India Code URLs.
"""
from django.core.management.base import BaseCommand
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
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2403",
    },
    {
        "act_name": "Payment of Gratuity Act, 1972",
        "short_code": "PGA 1972",
        "act_year": 1972,
        "enacted_by": "Parliament of India",
        "description": "An Act to provide for a scheme for the payment of gratuity to employees engaged in factories, mines, oilfields, plantations, ports, railway companies, shops or other establishments.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1470",
    },
]


SECTIONS_DATA = [
    # Consumer Protection Act, 2019
    {
        "act_code": "CPA 2019",
        "section_number": "Section 2(7)",
        "title": "Definition of Consumer",
        "legal_text": "A consumer means any person who buys any goods for a consideration which has been paid or promised... and includes any user of such goods... but does not include a person who obtains such goods for resale or for any commercial purpose. The expression 'buys any goods' or 'hires or avails any services' includes offline or online transactions through electronic means or by teleshopping or direct selling or multi-level marketing.",
        "simple_explanation": "You are legally recognized as a consumer whether you buy goods or services in a physical shop or through online e-commerce websites and apps. Sellers and platforms cannot evade liability just because the purchase was digital.",
        "punishment_or_remedy": "Confers statutory standing to file a consumer complaint against sellers, distributors, and e-commerce platforms before Consumer Commissions.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },
    {
        "act_code": "CPA 2019",
        "section_number": "Section 2(47)",
        "title": "Unfair Trade Practice Defined",
        "legal_text": "Unfair trade practice means a trade practice which, for the purpose of promoting the sale, use or supply of any goods or for the provision of any service, adopts any unfair method or unfair or deceptive practice including refusing, after selling goods or rendering services, to take back or withdraw defective goods or to refund the consideration thereof paid within the period stipulated in the bill or cash memo.",
        "simple_explanation": "Refusing to take back defective products, refusing refunds, issuing misleading warranties, or not providing a tax invoice is explicitly categorized as an illegal unfair trade practice.",
        "punishment_or_remedy": "Central Consumer Protection Authority (CCPA) can order product recall, full refund, discontinuation of unfair practice, and impose penalties up to ₹10 Lakhs.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },
    {
        "act_code": "CPA 2019",
        "section_number": "Section 35",
        "title": "Manner of Making Complaint to District Commission",
        "legal_text": "A complaint, in relation to any goods sold or delivered or agreed to be sold or delivered or any service provided or agreed to be provided, may be filed with a District Commission by the consumer to whom such goods are sold or delivered, or by any recognized consumer association, accompanied with such fee and in such manner, including electronic filing, as may be prescribed.",
        "simple_explanation": "Any citizen can file a consumer case against a manufacturer, trader, or e-commerce platform with nominal court fees. Cases can be filed online from home using the official e-Daakhil portal without necessarily hiring an advocate.",
        "punishment_or_remedy": "District Commission can order replacement of goods, removal of defects, full refund with interest, and punitive damages for mental agony.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },

    # Motor Vehicles Act, 1988
    {
        "act_code": "MVA 1988",
        "section_number": "Section 134A",
        "title": "Protection of Good Samaritans",
        "legal_text": "A Good Samaritan shall not be liable for any civil or criminal action for any injury or death of the victim of an accident involving a motor vehicle, where such injury or death resulted from the Good Samaritan's negligence in acting or failing to act while rendering emergency medical or non-medical care or assistance.",
        "simple_explanation": "Citizens who help road accident victims and transport them to the hospital are protected by law. Police and hospitals cannot detain you, force you to disclose your identity, or make you pay hospital admission fees.",
        "punishment_or_remedy": "Statutory immunity from civil and criminal prosecution; harassment of Good Samaritans attracts disciplinary action against errant officials.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },
    {
        "act_code": "MVA 1988",
        "section_number": "Section 166",
        "title": "Application for Compensation in Motor Accidents (MACT)",
        "legal_text": "An application for compensation arising out of an accident of the nature specified in sub-section (1) of section 165 may be made by the person who has sustained the injury, or by the owner of the property, or, where death has resulted from the accident, by all or any of the legal representatives of the deceased.",
        "simple_explanation": "Victims injured in road accidents (or surviving family members in case of death) can file a claim before the Motor Accidents Claims Tribunal against the offending driver, owner, and insurance company for medical expenses, loss of income, and permanent disability compensation.",
        "punishment_or_remedy": "Financial compensation awarded by Tribunal, payable directly by the statutory motor insurance company.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },
    {
        "act_code": "MVA 1988",
        "section_number": "Section 130",
        "title": "Duty to Produce Licence and Certificate of Registration",
        "legal_text": "The driver of a motor vehicle in any public place shall, on demand by any police officer in uniform, produce his licence for examination. Provided that the driver may produce the electronic form of such documents stored in the DigiLocker or mParivahan mobile applications.",
        "simple_explanation": "Drivers are legally permitted to present their Driving License, RC, Insurance, and PUC in digital format via government DigiLocker or mParivahan apps. Traffic police cannot insist on physical copies or confiscate electronic devices.",
        "punishment_or_remedy": "Digital documents carry equal legal validity under Rule 139 of the Central Motor Vehicles Rules.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },

    # Information Technology Act, 2000
    {
        "act_code": "IT Act",
        "section_number": "Section 43",
        "title": "Penalty and Compensation for Damage to Computer System",
        "legal_text": "If any person without permission of the owner or any other person who is incharge of a computer, computer system or computer network accesses or secures access to such computer... or downloads, copies or extracts any data... he shall be liable to pay damages by way of compensation to the person so affected.",
        "simple_explanation": "Provides civil compensation to victims whose computers, bank accounts, or digital systems are breached or compromised through malware, unauthorized logins, or data theft.",
        "punishment_or_remedy": "Adjudicating Officer can order financial compensation up to ₹5 Crores payable directly to the victim.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "act_code": "IT Act",
        "section_number": "Section 66C",
        "title": "Punishment for Identity Theft",
        "legal_text": "Whoever, fraudulently or dishonestly make use of the electronic signature, password or any other unique identification feature of any other person, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to rupees one lakh.",
        "simple_explanation": "Stealing or misusing someone else's passwords, UPI PINs, OTPs, Aadhaar numbers, or digital credentials constitutes a criminal offense of identity theft.",
        "punishment_or_remedy": "Cognizable criminal offense punishable with imprisonment up to 3 years and fine up to ₹1 Lakh.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "act_code": "IT Act",
        "section_number": "Section 66D",
        "title": "Punishment for Cheating by Personation Using Computer Resource",
        "legal_text": "Whoever, by means of any communication device or computer resource, cheats by personation, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to one lakh rupees.",
        "simple_explanation": "Impersonating bank officials, lottery organizers, police officers, or delivery executives over phone calls, SMS, WhatsApp, or websites to cheat citizens of money is a serious cyber crime.",
        "punishment_or_remedy": "Imprisonment up to 3 years, mandatory fine, and freezing of beneficiary bank accounts / UPI wallets by cyber police.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },

    # Code of Criminal Procedure, 1973
    {
        "act_code": "CrPC",
        "section_number": "Section 41A",
        "title": "Notice of Appearance Before Police Officer",
        "legal_text": "The police officer shall, in all cases where the arrest of a person is not required under the provisions of sub-section (1) of section 41, issue a notice directing the person against whom a reasonable complaint has been made... to appear before him or at such other place as may be specified in the notice.",
        "simple_explanation": "For any alleged offense punishable with 7 years imprisonment or less, police cannot arbitrarily arrest a citizen without first issuing a formal written notice directing appearance. If you comply with the notice, you cannot be arrested unless the officer records written judicial reasons.",
        "punishment_or_remedy": "Arbitrary arrest in violation of Section 41A violates Supreme Court guidelines in Arnesh Kumar v. State of Bihar and renders the officer liable for contempt of court and departmental action.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },
    {
        "act_code": "CrPC",
        "section_number": "Section 50",
        "title": "Person Arrested to be Informed of Grounds of Arrest and Right to Bail",
        "legal_text": "Every police officer or other person arresting any person without warrant shall forthwith communicate to him full particulars of the offence for which he is arrested or other grounds for such arrest. Where a police officer arrests without warrant any person other than a person accused of a non-bailable offence, he shall inform the person arrested that he is entitled to be released on bail.",
        "simple_explanation": "Police are legally obligated to inform you immediately why you are being arrested, provide a copy of the FIR or arrest memo, and inform you if the offense is bailable so you can arrange sureties.",
        "punishment_or_remedy": "Failure to communicate grounds of arrest invalidates the arrest and constitutes violation of Fundamental Rights under Article 22(1) of the Constitution.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },
    {
        "act_code": "CrPC",
        "section_number": "Section 57",
        "title": "Person Arrested Not to be Detained More Than Twenty-Four Hours",
        "legal_text": "No police officer shall detain in custody a person arrested without warrant for a longer period than under all the circumstances of the case is reasonable, and such period shall not, in the absence of a special order of a Magistrate under section 167, exceed twenty-four hours exclusive of the time necessary for the journey from the place of arrest to the Magistrate's Court.",
        "simple_explanation": "Police cannot keep anyone in custody for more than 24 hours without producing them in person before the nearest Judicial Magistrate. Detention beyond 24 hours without a Magistrate's order is illegal confinement.",
        "punishment_or_remedy": "Immediate ground for habeas corpus writ petition before the High Court and statutory right to default bail.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/16225",
    },

    # Transfer of Property Act, 1882
    {
        "act_code": "TP Act",
        "section_number": "Section 106",
        "title": "Duration of Certain Leases and Notice to Terminate",
        "legal_text": "In the absence of a contract or local law or usage to the contrary, a lease of immovable property for agricultural or manufacturing purposes shall be deemed to be a lease from year to year, terminable on the part of either lessor or lessee, by six months' notice; and a lease of immovable property for any other purpose shall be deemed to be a lease from month to month, terminable on the part of either lessor or lessee, by fifteen days' notice.",
        "simple_explanation": "A landlord cannot arbitrarily throw out a tenant overnight. Unless the rental contract specifies a longer period, a statutory written notice of at least 15 days is mandatory to terminate a residential tenancy.",
        "punishment_or_remedy": "Eviction attempted without statutory notice under Section 106 is void in law; tenant can seek civil court injunction against illegal dispossession.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
    },
    {
        "act_code": "TP Act",
        "section_number": "Section 108(c)",
        "title": "Lessee's Right to Quiet Enjoyment",
        "legal_text": "The lessor shall be deemed to contract with the lessee that, if the latter pays the rent reserved by the lease and performs the contracts binding on the lessee, he may hold the property during the time limited by the lease without interruption.",
        "simple_explanation": "As long as a tenant pays the agreed rent, the landlord has a legal obligation not to interfere with peaceful possession or disconnect essential supplies such as water, electricity, or lift access.",
        "punishment_or_remedy": "Tenant can approach local Rent Control Tribunal or Civil Court for emergency restoration of essential amenities and damages.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2338",
    },

    # Protection of Women from Domestic Violence Act, 2005
    {
        "act_code": "PWDVA 2005",
        "section_number": "Section 3",
        "title": "Definition of Domestic Violence",
        "legal_text": "Any act, omission or commission or conduct of the respondent shall constitute domestic violence if it harms or injures or endangers the health, safety, life, limb or well-being, whether mental or physical, of the aggrieved person... includes physical abuse, sexual abuse, verbal and emotional abuse, and economic abuse.",
        "simple_explanation": "Domestic violence is not limited to physical beatings. It covers verbal insults, emotional torture, threats of divorce, and economic abuse such as depriving a woman of household expenses, maintenance, or stridhan.",
        "punishment_or_remedy": "Gives statutory right to file application before Magistrate for protection, residence, monetary relief, and custody orders.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },
    {
        "act_code": "PWDVA 2005",
        "section_number": "Section 12",
        "title": "Application to Magistrate for Relief",
        "legal_text": "An aggrieved person or a Protection Officer or any other person on behalf of the aggrieved person may present an application to the Magistrate seeking one or more reliefs under this Act. The Magistrate shall fix the first date of hearing, which shall not ordinarily be beyond three days from the date of receipt of the application.",
        "simple_explanation": "A woman facing domestic violence can directly file an application before the Judicial Magistrate (with or without a lawyer) through a Protection Officer or Legal Aid Authority. The court must hold the first hearing within 3 days.",
        "punishment_or_remedy": "Fast-track legal relief within 60 days of first hearing; interim protection orders can be granted ex-parte on the first day.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },
    {
        "act_code": "PWDVA 2005",
        "section_number": "Section 17",
        "title": "Right to Reside in a Shared Household",
        "legal_text": "Notwithstanding anything contained in any other law for the time being in force, every woman in a domestic relationship shall have the right to reside in the shared household, whether or not she has any right, title or beneficial interest in the same. The aggrieved person shall not be evicted or excluded from the shared household or any part of it by the respondent save in accordance with the procedure established by law.",
        "simple_explanation": "A married woman has a statutory right to live in the matrimonial shared household. In-laws and husband cannot throw her out of the house even if the property is solely in the husband's or father-in-law's name.",
        "punishment_or_remedy": "Magistrate can issue a Residence Order restraining the family from dispossessing the woman or locking her out.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },

    # Payment of Wages Act, 1936 & Payment of Gratuity Act, 1972
    {
        "act_code": "PWA 1936",
        "section_number": "Section 15",
        "title": "Claims Arising Out of Deductions from Wages or Delay in Payment",
        "legal_text": "Where contrary to the provisions of this Act any deduction has been made from the wages of an employed person, or any payment of wages has been delayed, such person himself, or any legal practitioner or any official of a registered trade union... may apply to such Authority for a direction under sub-section (3).",
        "simple_explanation": "If your employer delays salary payment beyond the 7th or 10th of the month or makes unauthorized salary cuts, you can file a claim before the statutory Labour Authority without expensive court fees.",
        "punishment_or_remedy": "Authority can direct employer to pay the unpaid wages along with compensation up to ten times the amount deducted.",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/2403",
    },
    {
        "act_code": "PGA 1972",
        "section_number": "Section 4",
        "title": "Payment of Gratuity on Termination of Service",
        "legal_text": "Gratuity shall be payable to an employee on the termination of his employment after he has rendered continuous service for not less than five years: (a) on his superannuation, or (b) on his retirement or resignation, or (c) on his death or disablement due to accident or disease.",
        "simple_explanation": "Any employee who completes 5 continuous years with an organization is statutorily entitled to gratuity payment upon resignation or retirement. Employers cannot withhold gratuity arbitrarily.",
        "punishment_or_remedy": "Employer must pay gratuity within 30 days. Delayed payment incurs mandatory compound interest under Section 7(3A).",
        "official_url": "https://www.indiacode.nic.in/handle/123456789/1470",
    },
]


SCENARIOS_DATA = [
    {
        "category_slug": "consumer-rights",
        "title": "E-Commerce Seller Refuses Refund or Return for Defective Goods",
        "slug": "defective-product-refund-refusal",
        "situation_summary": "You purchased an electronic gadget, home appliance, or clothing online from an e-commerce marketplace. The product arrived broken, counterfeit, or non-functional. Upon raising a return request within the return window, the seller or platform arbitrarily denied the refund, citing fine print or blaming the courier.",
        "what_to_do": (
            "1. Document Everything: Save the invoice, order confirmation, unboxing video/photos, and screenshots of chats with customer support.\n"
            "2. Send Written Demand: Send a formal email to the nodal/grievance officer of the e-commerce company demanding full refund within 7 working days citing Section 2(47) of the Consumer Protection Act, 2019.\n"
            "3. National Consumer Helpline: Call toll-free 1915 or register your complaint at consumerhelpline.gov.in. NCH resolves over 80% of e-commerce disputes through formal pre-litigation mediation.\n"
            "4. File on e-Daakhil: If unresolved after 15 days, lodge a consumer complaint online on the official e-Daakhil portal (edaakhil.nic.in) before your local District Consumer Commission without needing a lawyer."
        ),
        "section_keys": [("CPA 2019", "Section 2(7)"), ("CPA 2019", "Section 2(47)"), ("CPA 2019", "Section 35")],
        "official_portal_url": "https://edaakhil.nic.in/",
        "helpline_number": "1915",
        "is_featured": True,
        "display_order": 1,
    },
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
        "official_portal_url": "https://vcourts.gov.in/",
        "helpline_number": "1073",
        "is_featured": True,
        "display_order": 2,
    },
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
        "official_portal_url": "https://cybercrime.gov.in/",
        "helpline_number": "1930",
        "is_featured": True,
        "display_order": 3,
    },
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
        "official_portal_url": "https://nalsa.gov.in/",
        "helpline_number": "15100",
        "is_featured": True,
        "display_order": 4,
    },
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
        "official_portal_url": "https://ecourts.gov.in/",
        "helpline_number": "15100",
        "is_featured": False,
        "display_order": 5,
    },
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
        "official_portal_url": "https://nalsa.gov.in/",
        "helpline_number": "181",
        "is_featured": True,
        "display_order": 6,
    },
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
        "official_portal_url": "https://samadhan.labour.gov.in/",
        "helpline_number": "14434",
        "is_featured": False,
        "display_order": 7,
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
            scenarios_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded Know Your Law dataset: "
            f"{LawCategory.objects.count()} categories, "
            f"{LawAct.objects.count()} Acts, "
            f"{LawSection.objects.count()} sections, "
            f"{scenarios_count} scenarios."
        ))
