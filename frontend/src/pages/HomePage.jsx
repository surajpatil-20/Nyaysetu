import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Search,
  Bot,
  Network,
  Scale,
  FileText,
  Info,
  ArrowRight,
  ShieldCheck,
  BookOpen,
  Sparkles
} from "lucide-react";
import heroImg from "../assets/hero.png";
import "./HomePage.css";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const quickPills = [
    "Child witness testimony in Pradeep v State of Haryana",
    "Section 302 IPC circumstantial evidence",
    "Anticipatory bail Section 438",
    "Speedy trial Article 21",
  ];

  const capabilityCards = [
    {
      title: "Judicial Case Search",
      description: "Full-text Boolean keyword and dense pgvector semantic search across indexed Supreme Court precedents.",
      icon: Search,
      link: "/search",
    },
    {
      title: "Evidence-Grounded AI",
      description: "Judicial holding extraction, ratio decidendi analysis, and strict page-level evidence citations.",
      icon: Bot,
      link: isAuthenticated ? "/assistant" : "/login",
    },
    {
      title: "Case Intelligence",
      description: "Comprehensive dossiers detailing coram bench judges, parties, statutory sections, and timelines.",
      icon: FileText,
      link: "/search",
    },
    {
      title: "Judicial Knowledge Graph",
      description: "Multi-relational graph mapping precedent networks, presiding judges, enactments, and citations.",
      icon: Network,
      link: "/graph",
    },
  ];

  return (
    <div className="home-page-container">
      {/* Hero Section */}
      <section className="home-hero-section">
        {/* Supreme Court Watermark Background */}
        <div className="home-hero-watermark">
          <img
            src={heroImg}
            alt="Supreme Court of India"
            className="home-hero-watermark-img"
          />
          <div className="home-hero-vignette-overlay" />
        </div>

        {/* Hero Foreground Content */}
        <div className="home-hero-content">
          {/* Insignia Tag */}
          <div className="home-hero-tag-badge">
            <Scale className="h-3.5 w-3.5 text-[#FFA425]" />
            <span>Explore India's Judicial Knowledge</span>
          </div>

          {/* Heading */}
          <div className="home-hero-title-group">
            <h1 className="home-hero-title">NYAYASETU</h1>
            <p className="home-hero-subtitle">
              AI-Assisted, Evidence-Oriented Judicial Information Platform
            </p>
          </div>

          {/* Large Main Search Box */}
          <form onSubmit={handleSearch} className="home-search-form">
            <div className="home-search-box">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search cases, judgments, courts, judges, acts or legal concepts..."
                className="home-search-input"
              />
              <button
                type="submit"
                className="home-search-submit"
                title="Search Precedents"
              >
                <Search className="h-5 w-5" />
              </button>
            </div>
          </form>

          {/* Primary & Secondary Action CTAs */}
          <div className="home-cta-row">
            <Link to="/search" className="home-cta-btn-primary">
              <span>Explore Cases</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to={isAuthenticated ? "/assistant" : "/login"}
              className="home-cta-btn-secondary"
            >
              <Bot className="h-4 w-4 text-[#FFA425]" />
              <span>Ask AI Assistant</span>
            </Link>
          </div>

          {/* Quick Search Chips */}
          <div className="home-pills-row">
            <span className="home-pills-label hidden sm:inline">
              Suggested Precedents:
            </span>
            {quickPills.map((pill, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() =>
                  navigate(`/search?q=${encodeURIComponent(pill)}`)
                }
                className="home-pill-chip"
              >
                {pill}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* 4 Capability Cards Section */}
      <section className="home-capabilities-section">
        <div className="home-capabilities-grid">
          {capabilityCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <Link
                key={idx}
                to={card.link}
                className="home-capability-card"
              >
                <div className="home-capability-icon-box">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="home-capability-title">
                    <span>{card.title}</span>
                    <ArrowRight className="h-3.5 w-3.5 text-slate-400 group-hover:text-[#FFA425]" />
                  </h3>
                  <p className="home-capability-desc">
                    {card.description}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Explanation Section: Search. Understand. Verify. */}
      <section className="home-methodology-section">
        <div className="home-methodology-card">
          <div className="home-methodology-header">
            <h2 className="home-methodology-title">Search. Understand. Verify.</h2>
            <p className="home-methodology-subtitle">
              A principled, citation-backed legal research paradigm engineered for legal scholars, advocates, researchers, and citizens.
            </p>
          </div>

          <div className="home-methodology-pillars">
            <div className="home-pillar-item">
              <span className="home-pillar-num">01 / RETRIEVE</span>
              <h3 className="home-pillar-heading">Search Precedents</h3>
              <p className="home-pillar-desc">
                Execute hybrid search fusing PostgreSQL lexical filtering and dense pgvector cosine distance across 2,058 indexed Supreme Court document chunks.
              </p>
            </div>

            <div className="home-pillar-item">
              <span className="home-pillar-num">02 / SYNTHESIZE</span>
              <h3 className="home-pillar-heading">Understand Holdings</h3>
              <p className="home-pillar-desc">
                Review structured judicial dossiers breaking rulings into executive holdings, ratio decidendi principles, statutory provisions, and bench coram.
              </p>
            </div>

            <div className="home-pillar-item">
              <span className="home-pillar-num">03 / GROUND</span>
              <h3 className="home-pillar-heading">Verify Grounding</h3>
              <p className="home-pillar-desc">
                Every proposition is strictly tied to verifiable [Evidence N] tags with exact PDF page coordinates and direct links to official open judicial repositories.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Civic Disclaimer Bottom Banner */}
      <div className="home-disclaimer-wrapper">
        <div className="home-disclaimer-box">
          <Info className="home-disclaimer-icon" />
          <span>
            <strong>Civic Notice:</strong> NYAYASETU provides informational assistance based on available official judicial records. It is not a substitute for professional legal counsel and does not make judicial determinations or predict litigation outcomes.
          </span>
        </div>
      </div>
    </div>
  );
}
