import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Search,
  Bot,
  Network,
  Folder,
  Building2,
  Info,
  ArrowRight,
  Sparkles,
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
    "child witness testimony",
    "Section 302 IPC circumstantial evidence",
    "anticipatory bail Section 438",
    "speedy trial Article 21",
  ];

  const quickActions = [
    {
      title: "Search Cases",
      description: "Precedents, orders & rulings",
      icon: Search,
      link: "/search",
    },
    {
      title: "Ask Judicial AI",
      description: "Evidence-grounded answers",
      icon: Bot,
      link: isAuthenticated ? "/assistant" : "/login",
    },
    {
      title: "Knowledge Graph",
      description: "Connected cases, judges & acts",
      icon: Network,
      link: "/search",
    },
    {
      title: "Document Vault",
      description: "Private OCR & chunk analysis",
      icon: Folder,
      link: "/documents",
    },
    {
      title: "Official Services",
      description: "eCourts, NJDG & NALSA portals",
      icon: Building2,
      link: "/services",
    },
  ];

  return (
    <div className="home-page-container">
      {/* Hero Section with Supreme Court Background Image */}
      <section className="home-hero-section">
        {/* Supreme Court Watermark Background */}
        <div className="home-hero-watermark">
          <img
            src={heroImg}
            alt="Supreme Court of India"
            className="home-hero-watermark-img"
          />
          <div className="home-hero-vignette-overlay" />
          <div className="home-hero-radial-overlay" />
        </div>

        {/* Hero Foreground Content */}
        <div className="home-hero-content">
          {/* Pill Badge */}
          <div className="home-hero-pill">
            <Sparkles className="h-3.5 w-3.5" />
            <span>AI-Assisted Judicial Information Platform</span>
          </div>

          {/* Heading */}
          <div className="home-hero-title-group">
            <h1 className="home-hero-title">NYAYASETU</h1>
            <p className="home-hero-subtitle">
              Search real Supreme Court precedents, explore case relationships,
              and ask evidence-grounded legal questions.
            </p>
          </div>

          {/* Centered Large Search Bar */}
          <form onSubmit={handleSearch} className="home-search-form">
            <div className="home-search-box">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search cases, judgments, legal concepts..."
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

          {/* Quick Search Chips */}
          <div className="home-pills-row">
            <span className="home-pills-label hidden sm:inline">
              Try searching:
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

      {/* Main Content: 5 Clean Quick Action Cards */}
      <section className="home-content-section">
        {/* Quick Actions Grid */}
        <div className="home-actions-grid">
          {quickActions.map((action, idx) => {
            const Icon = action.icon;
            return (
              <Link
                key={idx}
                to={action.link}
                className="home-action-card"
              >
                <div className="home-action-icon-box">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="home-action-title">
                    {action.title}
                  </h3>
                  <p className="home-action-description">
                    {action.description}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Minimal Informational Note for Logged-Out Users */}
        {!isAuthenticated && (
          <div className="home-auth-banner">
            <div className="home-auth-banner-left">
              <div className="home-auth-icon-box">
                <Bot className="h-4 w-4" />
              </div>
              <div>
                <span className="home-auth-strong">
                  Sign in to use the NYAYASETU AI Assistant
                </span>
                <span className="home-auth-muted-info hidden sm:inline">
                  {" "}
                  — Evidence-grounded answers with Supreme Court citations
                  require an active account.
                </span>
              </div>
            </div>
            <Link
              to="/login"
              state={{ from: { pathname: "/assistant" } }}
              className="home-auth-btn-signin"
            >
              <span>Sign In</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        )}

        {/* Civic Disclaimer Alert Banner */}
        <div className="home-disclaimer-banner">
          <Info className="home-disclaimer-icon" />
          <span>
            NYAYASETU provides informational assistance based on available
            judicial records. It is not a substitute for professional legal
            advice and does not predict judicial outcomes or make judicial
            decisions.
          </span>
        </div>
      </section>
    </div>
  );
}
