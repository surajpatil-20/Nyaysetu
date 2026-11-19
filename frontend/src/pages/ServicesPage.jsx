import { useState, useEffect, useMemo } from 'react';
import { servicesApi } from '../api/services';
import AppLayout from '../components/AppLayout';
import {
  Building2,
  ExternalLink,
  Scale,
  Search,
  Shield,
  FileText,
  Copy,
  Check,
  PhoneCall,
  HelpCircle,
  Sparkles,
  CheckCircle2,
  MapPin,
  Gavel,
  BookOpen,
  Info,
  ArrowRight,
  Filter,
  X
} from 'lucide-react';
import { ServicesSkeleton } from '../components/Skeleton';
import './ServicesPage.css';

// 10 Authentic Government Judicial Services Fallback
const DEFAULT_SERVICES = [
  {
    id: 1,
    service_name: 'NALSA Free Legal Services',
    category: 'LEGAL_AID',
    category_display: 'Free Legal Aid (NALSA / SLSA / DLSA)',
    department: 'National Legal Services Authority (NALSA)',
    state: null,
    description:
      'NALSA provides free legal services to eligible citizens including legal advice, representation in courts, drafting of legal documents, and mediation/Lok Adalat services. Access through State Legal Services Authorities (SLSAs) or District Legal Services Authorities (DLSAs).',
    eligibility:
      'Women and children, members of SC/ST communities, industrial workmen, persons with disabilities, victims of mass disasters or ethnic violence, persons in custody, persons with annual income below Rs. 3,00,000 (under Section 12 of the Legal Services Authorities Act, 1987).',
    official_url: 'https://nalsa.gov.in/',
  },
  {
    id: 2,
    service_name: 'eCourts Services Portal – Case Status',
    category: 'CASE_STATUS',
    category_display: 'eCourts Case Status & Cause List',
    department: 'Department of Justice, Ministry of Law & Justice',
    state: null,
    description:
      'Citizens can check the status of their case in any District Court, High Court, or the Supreme Court of India using the eCourts Services Portal. Search by Case Number, CNR Number, Party Name, FIR Number, or filing number. Cause lists, orders, and hearing dates are available.',
    eligibility: 'All citizens. No registration required for case status check.',
    official_url: 'https://ecourts.gov.in/ecourts_home/',
  },
  {
    id: 3,
    service_name: 'Supreme Court of India – e-Filing',
    category: 'E_FILING',
    category_display: 'e-Filing Portal (High Courts & District Courts)',
    department: 'Supreme Court of India',
    state: null,
    description:
      "The Supreme Court of India's e-Filing portal allows advocates and parties-in-person to file new cases, interlocutory applications, and other petitions electronically. Documents can be filed 24x7 without visiting the court registry.",
    eligibility: 'Advocates enrolled with Bar Council and parties filing in person.',
    official_url: 'https://efiling.sci.gov.in/',
  },
  {
    id: 4,
    service_name: 'High Court e-Filing (Delhi High Court)',
    category: 'E_FILING',
    category_display: 'e-Filing Portal (High Courts & District Courts)',
    department: 'Delhi High Court',
    state: 'Delhi',
    description:
      'The Delhi High Court e-Filing system allows advocates to file petitions, applications, and replies online without physical submission. Includes case tracking and cause list access.',
    eligibility: 'Advocates enrolled with Bar Council of Delhi.',
    official_url: 'https://delhihighcourt.nic.in/',
  },
  {
    id: 5,
    service_name: 'e-Daakhil – Consumer Dispute e-Filing',
    category: 'CONSUMER_FORUM',
    category_display: 'e-Daakhil (Consumer Disputes)',
    department: 'Department of Consumer Affairs, Ministry of Consumer Affairs',
    state: null,
    description:
      'e-Daakhil is the official portal for filing consumer complaints online before District Consumer Disputes Redressal Commissions (DDRCs), State Consumer Disputes Redressal Commissions (SDRCs), and the National Consumer Disputes Redressal Commission (NCDRC).',
    eligibility: 'Any consumer aggrieved by deficiency of goods or services.',
    official_url: 'https://edaakhil.nic.in/',
  },
  {
    id: 6,
    service_name: 'Virtual Courts – Traffic Challan & Petty Offences',
    category: 'TRAFFIC_CHALLAN',
    category_display: 'Virtual Courts (Traffic & Petty Offences)',
    department: 'Department of Justice, Ministry of Law & Justice',
    state: null,
    description:
      'Virtual Courts allow citizens to pay traffic challans and settle petty compoundable offences online without appearing in physical court. Available 24x7.',
    eligibility: 'Any person issued a traffic challan or summons for a compoundable offence.',
    official_url: 'https://vcourts.gov.in/',
  },
  {
    id: 7,
    service_name: 'Certified Copy Application (eCourts)',
    category: 'CERTIFIED_COPY',
    category_display: 'Certified Copy Application',
    department: 'Department of Justice, Ministry of Law & Justice',
    state: null,
    description:
      'Citizens and advocates can apply online for certified copies of court orders, judgments, and other judicial records through the eCourts Services portal.',
    eligibility: 'Parties to the case or their advocates.',
    official_url: 'https://services.ecourts.gov.in/ecourtindia_v6/',
  },
  {
    id: 8,
    service_name: 'TELE-LAW – Legal Aid via Common Service Centres',
    category: 'LEGAL_AID',
    category_display: 'Free Legal Aid (NALSA / SLSA / DLSA)',
    department: 'Department of Justice, Ministry of Law & Justice / NALSA',
    state: null,
    description:
      'Tele-Law connects citizens in rural areas with empanelled lawyers via video conferencing at Common Service Centres (CSCs) across India for pre-litigation legal advice.',
    eligibility: 'Marginalized communities, rural citizens, women, SC/ST communities.',
    official_url: 'https://tele-law.in/',
  },
  {
    id: 9,
    service_name: 'National Judicial Data Grid (NJDG)',
    category: 'CASE_STATUS',
    category_display: 'eCourts Case Status & Cause List',
    department: 'Department of Justice, Ministry of Law & Justice',
    state: null,
    description:
      'The National Judicial Data Grid provides aggregated data on case pendency, institution, and disposal across High Courts and District/Taluka Courts in India.',
    eligibility: 'Open to all. No registration required.',
    official_url: 'https://njdg.ecourts.gov.in/',
  },
  {
    id: 10,
    service_name: 'Supreme Court of India – Judgment Search (JUDIS)',
    category: 'CASE_STATUS',
    category_display: 'eCourts Case Status & Cause List',
    department: 'Supreme Court of India',
    state: null,
    description:
      'JUDIS (Judgment Information System) is the official repository of Supreme Court of India judgments from 1950 onwards, with comprehensive full-text search.',
    eligibility: 'Open to all. No registration required.',
    official_url: 'https://judis.nic.in/',
  },
];

const CATEGORY_MAP = {
  ALL: { label: 'All Services', icon: Building2 },
  CASE_STATUS: { label: 'Case Status & eCourts', icon: Search },
  E_FILING: { label: 'e-Filing Portals', icon: FileText },
  LEGAL_AID: { label: 'Free Legal Aid (NALSA)', icon: Scale },
  CERTIFIED_COPY: { label: 'Certified Copies', icon: BookOpen },
  CONSUMER_FORUM: { label: 'Consumer Disputes', icon: Shield },
  TRAFFIC_CHALLAN: { label: 'Virtual Courts', icon: Gavel },
};

export default function ServicesPage() {
  const [rawServices, setRawServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [jurisdictionFilter, setJurisdictionFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // CNR Quick Tracker states
  const [cnrNumber, setCnrNumber] = useState('');
  const [cnrPortal, setCnrPortal] = useState('ecourts');
  const [cnrCopied, setCnrCopied] = useState(false);
  const [showCnrHelp, setShowCnrHelp] = useState(false);
  const [showLegalAidHelp, setShowLegalAidHelp] = useState(false);

  // Link copy feedback
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    async function fetchServices() {
      setLoading(true);
      try {
        const data = await servicesApi.getServices();
        const list = Array.isArray(data) ? data : data?.results || [];
        if (list.length > 0) {
          setRawServices(list);
        } else {
          setRawServices(DEFAULT_SERVICES);
        }
      } catch (err) {
        console.warn('Falling back to default judicial services:', err);
        setRawServices(DEFAULT_SERVICES);
      } finally {
        setLoading(false);
      }
    }
    fetchServices();
  }, []);

  // Normalize data records to ensure field resilience
  const normalizedServices = useMemo(() => {
    return rawServices.map((svc) => ({
      id: svc.id,
      title: svc.service_name || svc.title || svc.name || 'Judicial Service',
      category: svc.category || 'OTHER',
      categoryDisplay: svc.category_display || svc.category || 'Official Portal',
      department: svc.department || 'Ministry of Law & Justice / Indian Judiciary',
      state: svc.state || null,
      description: svc.description || svc.short_description || '',
      eligibility: svc.eligibility || 'Open to all citizens and advocates.',
      url: svc.official_url || svc.url || svc.portal_url || '#',
    }));
  }, [rawServices]);

  // Extract unique jurisdictions for filtering
  const availableJurisdictions = useMemo(() => {
    const states = new Set();
    normalizedServices.forEach((s) => {
      if (s.state) states.add(s.state);
    });
    return Array.from(states).sort();
  }, [normalizedServices]);

  // Filtered services
  const filteredServices = useMemo(() => {
    return normalizedServices.filter((svc) => {
      // Category filter
      if (activeCategory !== 'ALL' && svc.category !== activeCategory) {
        return false;
      }
      // Jurisdiction filter
      if (jurisdictionFilter === 'CENTRAL' && svc.state !== null) {
        return false;
      }
      if (
        jurisdictionFilter !== 'ALL' &&
        jurisdictionFilter !== 'CENTRAL' &&
        svc.state !== jurisdictionFilter
      ) {
        return false;
      }
      // Text search
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const inTitle = svc.title.toLowerCase().includes(q);
        const inDesc = svc.description.toLowerCase().includes(q);
        const inDept = svc.department.toLowerCase().includes(q);
        const inElig = svc.eligibility.toLowerCase().includes(q);
        const inCat = svc.categoryDisplay.toLowerCase().includes(q);
        return inTitle || inDesc || inDept || inElig || inCat;
      }
      return true;
    });
  }, [normalizedServices, activeCategory, jurisdictionFilter, searchQuery]);

  // Handle Copy URL
  const handleCopyUrl = (id, url) => {
    navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Handle CNR Search Submit
  const handleCnrSubmit = (e) => {
    e.preventDefault();
    const cleanCnr = cnrNumber.trim().toUpperCase();
    if (!cleanCnr) return;

    let targetUrl = 'https://services.ecourts.gov.in/ecourtindia_v6/';
    if (cnrPortal === 'njdg') {
      targetUrl = 'https://njdg.ecourts.gov.in/';
    } else if (cnrPortal === 'sci') {
      targetUrl = 'https://main.sci.gov.in/case-status';
    }

    // Open portal in new tab
    window.open(targetUrl, '_blank', 'noopener,noreferrer');
  };

  const handleCopyCnr = () => {
    if (!cnrNumber) return;
    navigator.clipboard.writeText(cnrNumber.trim().toUpperCase());
    setCnrCopied(true);
    setTimeout(() => setCnrCopied(false), 2000);
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'CASE_STATUS':
        return Search;
      case 'E_FILING':
        return FileText;
      case 'LEGAL_AID':
        return Scale;
      case 'CERTIFIED_COPY':
        return BookOpen;
      case 'CONSUMER_FORUM':
        return Shield;
      case 'TRAFFIC_CHALLAN':
        return Gavel;
      default:
        return Building2;
    }
  };

  return (
    <AppLayout>
      <div className="services-page-container">
        {/* Page Top Header */}
        <header className="services-hero-header">
          <div className="services-hero-content">
            <div className="services-hero-badge">
              <Shield className="h-3.5 w-3.5 text-[#FFA425]" />
              <span>National Judicial Infrastructure Access Hub</span>
            </div>
            <h1 className="services-hero-title">Judicial &amp; Government Services</h1>
            <p className="services-hero-desc">
              Direct, verified digital access to official Indian court portals, eCourts CNR case tracking, 
              electronic filing registries, free statutory legal aid (NALSA), and virtual court adjudication.
            </p>
          </div>

          <div className="services-hero-stats">
            <div className="services-stat-card">
              <span className="services-stat-num">10+</span>
              <span className="services-stat-label">Verified Portals</span>
            </div>
            <div className="services-stat-card">
              <span className="services-stat-num">24x7</span>
              <span className="services-stat-label">Digital Access</span>
            </div>
            <div className="services-stat-card">
              <span className="services-stat-num">100%</span>
              <span className="services-stat-label">Free Legal Aid</span>
            </div>
          </div>
        </header>

        {/* Interactive CNR Quick Case Tracker */}
        <section className="services-cnr-panel" aria-labelledby="cnr-panel-title">
          <div className="services-cnr-header">
            <div className="flex items-center gap-2">
              <div className="services-cnr-icon-box">
                <Search className="h-5 w-5 text-[#FFA425]" />
              </div>
              <div>
                <h2 id="cnr-panel-title" className="services-cnr-title">
                  eCourts CNR Quick Case Tracker
                </h2>
                <p className="services-cnr-subtitle">
                  Directly track any case across District Courts, High Courts, and Supreme Court using your 16-character Case Record Number.
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowCnrHelp(!showCnrHelp)}
              className="services-help-toggle-btn"
              aria-expanded={showCnrHelp}
            >
              <HelpCircle className="h-4 w-4" />
              <span>{showCnrHelp ? 'Hide CNR Guide' : 'What is a CNR Number?'}</span>
            </button>
          </div>

          {/* Expandable CNR Guidance */}
          {showCnrHelp && (
            <div className="services-cnr-guide-box">
              <div className="flex items-start gap-2">
                <Info className="h-4 w-4 text-[#11486B] mt-0.5 shrink-0" />
                <div className="text-xs leading-relaxed space-y-1">
                  <p className="font-semibold text-[var(--text-primary)]">
                    Understanding Your 16-Digit CNR (Case Record Number)
                  </p>
                  <p className="text-[var(--text-muted)]">
                    A CNR is an alphanumeric identifier uniquely assigned to every petition filed under the eCourts umbrella. 
                    Format example: <strong className="font-mono text-[var(--primary-navy)]">DLHC01-001234-2024</strong> (Court Code [4 chars] + Court Complex [2 chars] + Case Number [6 chars] + Year [4 chars]).
                  </p>
                  <p className="text-[var(--text-muted)]">
                    It can be found stamped at the top of your official filing receipt, court summons, daily order-sheet, or cause list entry.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* CNR Tracking Form */}
          <form onSubmit={handleCnrSubmit} className="services-cnr-form">
            <div className="services-cnr-input-group">
              <label htmlFor="cnr-input" className="sr-only">Enter 16-Character CNR Number</label>
              <input
                id="cnr-input"
                type="text"
                value={cnrNumber}
                onChange={(e) => setCnrNumber(e.target.value.toUpperCase())}
                placeholder="Enter 16-character CNR number (e.g. DLHC010012342024)"
                maxLength={18}
                className="services-cnr-input font-mono"
              />
              {cnrNumber && (
                <button
                  type="button"
                  onClick={handleCopyCnr}
                  className="services-cnr-copy-btn"
                  title="Copy CNR to clipboard"
                >
                  {cnrCopied ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-emerald-600" />
                      <span className="text-emerald-600 text-xs">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      <span className="text-xs">Copy</span>
                    </>
                  )}
                </button>
              )}
            </div>

            <div className="services-cnr-destinations">
              <label className="services-destination-label">Target Judicial System:</label>
              <div className="services-destination-radios">
                <label className={`services-dest-chip ${cnrPortal === 'ecourts' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="cnrPortal"
                    value="ecourts"
                    checked={cnrPortal === 'ecourts'}
                    onChange={() => setCnrPortal('ecourts')}
                    className="sr-only"
                  />
                  <span>eCourts Services (District/HC)</span>
                </label>
                <label className={`services-dest-chip ${cnrPortal === 'njdg' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="cnrPortal"
                    value="njdg"
                    checked={cnrPortal === 'njdg'}
                    onChange={() => setCnrPortal('njdg')}
                    className="sr-only"
                  />
                  <span>NJDG National Grid</span>
                </label>
                <label className={`services-dest-chip ${cnrPortal === 'sci' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="cnrPortal"
                    value="sci"
                    checked={cnrPortal === 'sci'}
                    onChange={() => setCnrPortal('sci')}
                    className="sr-only"
                  />
                  <span>Supreme Court Portal</span>
                </label>
              </div>
            </div>

            <div className="services-cnr-actions">
              <button
                type="submit"
                className="services-cnr-launch-btn"
              >
                <span>Track on Official Portal</span>
                <ExternalLink className="h-4 w-4" />
              </button>
            </div>
          </form>
        </section>

        {/* Free Legal Aid Entitlement Banner */}
        <section className="services-legal-aid-banner">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="services-aid-icon-box">
                <Scale className="h-5 w-5 text-[#FFA425]" />
              </div>
              <div>
                <h3 className="services-aid-title">Free Legal Aid Entitlement (NALSA / Section 12)</h3>
                <p className="services-aid-desc">
                  Under the Legal Services Authorities Act, 1987, eligible citizens receive 100% free legal representation and advisory.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 self-stretch sm:self-auto shrink-0">
              <button
                type="button"
                onClick={() => setShowLegalAidHelp(!showLegalAidHelp)}
                className="services-aid-criteria-btn"
              >
                <span>{showLegalAidHelp ? 'Close Criteria' : 'Check Eligibility'}</span>
                <Info className="h-4 w-4" />
              </button>
              <a
                href="https://nalsa.gov.in/"
                target="_blank"
                rel="noopener noreferrer"
                className="services-aid-apply-btn"
              >
                <span>Apply on NALSA</span>
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </div>
          </div>

          {showLegalAidHelp && (
            <div className="services-legal-aid-breakdown">
              <h4 className="font-semibold text-xs text-[var(--navy-900)] mb-2 uppercase tracking-wider">
                Eligible Categories Under Section 12, Legal Services Authorities Act, 1987:
              </h4>
              <ul className="services-aid-list">
                <li><CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" /> <span>Women and Children (Automatic eligibility; no income limitation)</span></li>
                <li><CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" /> <span>Members of Scheduled Castes (SC) and Scheduled Tribes (ST)</span></li>
                <li><CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" /> <span>Industrial Workmen / Laborers</span></li>
                <li><CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" /> <span>Persons with disabilities or mental illness</span></li>
                <li><CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" /> <span>Victims of trafficking, beggar system, or caste violence</span></li>
                <li><CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" /> <span>Persons in judicial or police custody, or juvenile reform homes</span></li>
                <li><CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" /> <span>Low-income citizens earning under ₹3,00,000 annually (as notified by State authorities)</span></li>
              </ul>
            </div>
          )}
        </section>

        {/* Filter Controls Row: Category Tabs + Search + Jurisdiction Dropdown */}
        <div className="services-filter-toolbar">
          {/* Search Box */}
          <div className="services-search-box">
            <Search className="h-4 w-4 text-[var(--text-muted)] shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search judicial services, portals, departments, or eligibility criteria..."
              className="services-search-input"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                aria-label="Clear search query"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Jurisdiction Dropdown */}
          <div className="services-jurisdiction-box">
            <MapPin className="h-4 w-4 text-[#FFA425] shrink-0" />
            <select
              value={jurisdictionFilter}
              onChange={(e) => setJurisdictionFilter(e.target.value)}
              className="services-jurisdiction-select"
              aria-label="Filter by Jurisdiction"
            >
              <option value="ALL">All Jurisdictions (Central &amp; States)</option>
              <option value="CENTRAL">Central / All-India Portals</option>
              {availableJurisdictions.map((st) => (
                <option key={st} value={st}>
                  {st} State / High Court
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Category Filter Pills Bar */}
        <div className="services-category-tabs-container">
          <div className="services-category-tabs" role="tablist" aria-label="Service Categories">
            {Object.entries(CATEGORY_MAP).map(([key, item]) => {
              const Icon = item.icon;
              const isActive = activeCategory === key;
              const count = key === 'ALL'
                ? normalizedServices.length
                : normalizedServices.filter((s) => s.category === key).length;

              return (
                <button
                  key={key}
                  type="button"
                  role="tab"
                  aria-selected={isActive}
                  onClick={() => setActiveCategory(key)}
                  className={`services-category-pill ${isActive ? 'active' : ''}`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{item.label}</span>
                  <span className="services-category-count">{count}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Active Results Summary */}
        <div className="services-results-meta">
          <p className="services-results-count">
            Showing <strong>{filteredServices.length}</strong> official judicial {filteredServices.length === 1 ? 'service' : 'services'}
            {activeCategory !== 'ALL' && ` in ${CATEGORY_MAP[activeCategory]?.label}`}
            {jurisdictionFilter !== 'ALL' && ` (${jurisdictionFilter})`}
            {searchQuery && ` matching "${searchQuery}"`}
          </p>
          {(activeCategory !== 'ALL' || jurisdictionFilter !== 'ALL' || searchQuery) && (
            <button
              type="button"
              onClick={() => {
                setActiveCategory('ALL');
                setJurisdictionFilter('ALL');
                setSearchQuery('');
              }}
              className="services-reset-filters-btn"
            >
              Reset Filters
            </button>
          )}
        </div>

        {/* Services Cards Grid */}
        {loading ? (
          <ServicesSkeleton count={6} />
        ) : filteredServices.length === 0 ? (
          <div className="services-empty-state">
            <Building2 className="h-10 w-10 text-[var(--text-light)] mb-2" />
            <h3 className="text-base font-bold text-[var(--text-primary)]">No judicial services found</h3>
            <p className="text-xs text-[var(--text-muted)] max-w-sm mt-1">
              No government services match your current query. Try adjusting your search keywords or switching category filters.
            </p>
            <button
              type="button"
              onClick={() => {
                setActiveCategory('ALL');
                setJurisdictionFilter('ALL');
                setSearchQuery('');
              }}
              className="mt-3 px-3 py-1.5 text-xs font-semibold bg-[#11486B] text-white rounded-md"
            >
              View All Services
            </button>
          </div>
        ) : (
          <div className="services-grid">
            {filteredServices.map((svc) => {
              const Icon = getCategoryIcon(svc.category);
              const isCopied = copiedId === svc.id;

              return (
                <article key={svc.id} className="service-card" aria-labelledby={`svc-title-${svc.id}`}>
                  <div className="service-card-top">
                    {/* Header: Icon + Category Badge + Jurisdiction */}
                    <div className="service-card-meta-row">
                      <div className="service-icon-box">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="service-badges-wrap">
                        <span className={`service-cat-badge cat-${svc.category.toLowerCase()}`}>
                          {svc.categoryDisplay}
                        </span>
                        {svc.state ? (
                          <span className="service-state-badge">
                            <MapPin className="h-3 w-3" />
                            {svc.state}
                          </span>
                        ) : (
                          <span className="service-central-badge">
                            All-India / Central
                          </span>
                        )}
                        <span className="service-verified-badge" title="Verified Government Portal">
                          <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                          <span>Gov.in</span>
                        </span>
                      </div>
                    </div>

                    {/* Title & Department */}
                    <div className="service-title-block">
                      <h3 id={`svc-title-${svc.id}`} className="service-title">
                        {svc.title}
                      </h3>
                      <p className="service-department">
                        <Building2 className="h-3.5 w-3.5 shrink-0" />
                        <span>{svc.department}</span>
                      </p>
                    </div>

                    {/* Description */}
                    <p className="service-desc">{svc.description}</p>

                    {/* Eligibility / Target Citizens Block */}
                    {svc.eligibility && (
                      <div className="service-eligibility-box">
                        <div className="flex items-start gap-1.5">
                          <Info className="h-3.5 w-3.5 text-[#11486B] shrink-0 mt-0.5" />
                          <div className="text-xs">
                            <span className="font-semibold text-[var(--text-primary)]">Eligibility &amp; Access: </span>
                            <span className="text-[var(--text-muted)]">{svc.eligibility}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Card Actions Footer */}
                  <div className="service-card-footer">
                    <button
                      type="button"
                      onClick={() => handleCopyUrl(svc.id, svc.url)}
                      className="service-action-secondary-btn"
                      title="Copy official portal URL"
                    >
                      {isCopied ? (
                        <>
                          <Check className="h-3.5 w-3.5 text-emerald-600" />
                          <span className="text-emerald-600">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-3.5 w-3.5" />
                          <span>Copy Link</span>
                        </>
                      )}
                    </button>

                    <a
                      href={svc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="service-action-primary-btn"
                    >
                      <span>Launch Official Portal</span>
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </article>
              );
            })}
          </div>
        )}

        {/* Emergency & Citizen Judicial Helplines Panel */}
        <section className="services-helplines-strip" aria-labelledby="helplines-title">
          <div className="services-helplines-header">
            <PhoneCall className="h-4 w-4 text-[#FFA425]" />
            <h2 id="helplines-title" className="services-helplines-title">
              Official Judicial &amp; Citizen Helplines
            </h2>
          </div>

          <div className="services-helplines-grid">
            <div className="services-helpline-card">
              <span className="services-helpline-tag">Free Legal Advisory</span>
              <p className="services-helpline-number">15100</p>
              <p className="services-helpline-desc">National Legal Services Authority (NALSA) 24x7 Toll-Free Support</p>
            </div>

            <div className="services-helpline-card">
              <span className="services-helpline-tag">Rural Video Consultation</span>
              <p className="services-helpline-number">14417</p>
              <p className="services-helpline-desc">Tele-Law Pre-Litigation Advisory via Common Service Centres</p>
            </div>

            <div className="services-helpline-card">
              <span className="services-helpline-tag">eCourts SMS Pull</span>
              <p className="services-helpline-number">8448446699</p>
              <p className="services-helpline-desc">SMS: <strong className="font-mono">ECOURTS &lt;CNR&gt;</strong> for automated hearing updates</p>
            </div>

            <div className="services-helpline-card">
              <span className="services-helpline-tag">Consumer Grievances</span>
              <p className="services-helpline-number">1915</p>
              <p className="services-helpline-desc">National Consumer Helpline (NCH) / WhatsApp 8800001915</p>
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  );
}
