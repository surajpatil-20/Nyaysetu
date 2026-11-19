import { ShieldAlert, ExternalLink, Scale, Database, Network } from 'lucide-react';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer-root">
      <div className="footer-container">

        {/* Information Notice */}
        <div className="footer-notice">
          <ShieldAlert className="footer-notice-icon" />
          <div>
            <strong>Civic Judicial Information Notice</strong>
            <p>
              NYAYASETU provides informational assistance based on available
              judicial records and does not replace professional legal advice
              or predict judicial outcomes.
            </p>
          </div>
        </div>

        {/* Main Footer */}
        <div className="footer-main">

          {/* Brand */}
          <div className="footer-brand">
            <div className="footer-brand-title">
              <Scale size={18} />
              <span>NYAYASETU</span>
            </div>

            <p>
              AI-Assisted, Evidence-Oriented Judicial Information Platform.
              Built around authentic Indian Supreme Court judgments and
              evidence-grounded information retrieval.
            </p>

            <span className="footer-license">
              Data: Supreme Court Judgments Open Dataset · CC BY 4.0
            </span>
          </div>

          {/* Official Portals */}
          <div className="footer-column">
            <h4>Official Portals</h4>

            <a
              href="https://main.sci.gov.in/"
              target="_blank"
              rel="noopener noreferrer"
            >
              Supreme Court of India
              <ExternalLink size={13} />
            </a>

            <a
              href="https://ecourts.gov.in/"
              target="_blank"
              rel="noopener noreferrer"
            >
              eCourts Services
              <ExternalLink size={13} />
            </a>

            <a
              href="https://nalsa.gov.in/"
              target="_blank"
              rel="noopener noreferrer"
            >
              NALSA
              <ExternalLink size={13} />
            </a>
          </div>

          {/* Technology */}
          <div className="footer-column">
            <h4>Platform Technology</h4>

            <div className="footer-tech-item">
              <Database size={15} />
              <span>PostgreSQL + pgvector</span>
            </div>

            <div className="footer-tech-item">
              <Network size={15} />
              <span>HNSW Semantic Search</span>
            </div>

            <div className="footer-tech-item">
              <span className="footer-tech-dot" />
              <span>BGE Embeddings + Knowledge Graph</span>
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} NYAYASETU Platform</span>

          <span>
            Public Legal Information Initiative · CC BY 4.0
          </span>
        </div>

      </div>
    </footer>
  );
}