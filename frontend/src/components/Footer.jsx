import { ShieldAlert, ExternalLink, Scale } from 'lucide-react';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer-root">
      <div className="footer-container">
        {/* Civic Judicial Information Notice */}
        <div className="footer-disclaimer-box">
          <ShieldAlert className="footer-disclaimer-icon" />
          <div>
            <span className="footer-disclaimer-title">Civic Judicial Information Notice:</span>
            <p className="footer-disclaimer-text">
              NYAYASETU provides informational assistance based on available judicial records. It is not a substitute for professional legal advice and does not predict judicial outcomes or make judicial decisions. Always consult an enrolled advocate or qualified legal practitioner for actionable legal representation.
            </p>
          </div>
        </div>

        {/* Data Attribution & Official Links */}
        <div className="footer-grid">
          <div>
            <div className="footer-brand-title">
              <Scale className="h-4 w-4 text-blue-500" />
              <span>NYAYASETU</span>
            </div>
            <p className="footer-text">
              AI-Assisted, Evidence-Oriented Judicial Information Platform. Real judicial case judgments are sourced from the Indian Supreme Court Judgments Open Dataset via the AWS Open Data Registry under CC BY 4.0.
            </p>
          </div>

          <div>
            <h4 className="footer-column-heading">Official Government Portals</h4>
            <ul className="footer-links-list">
              <li className="footer-link-item">
                <a
                  href="https://main.sci.gov.in/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span>Supreme Court of India</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li className="footer-link-item">
                <a
                  href="https://ecourts.gov.in/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span>eCourts Services Portal</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li className="footer-link-item">
                <a
                  href="https://nalsa.gov.in/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span>National Legal Services Authority (NALSA)</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="footer-column-heading">Technical Architecture</h4>
            <p className="footer-text">
              Evidence retrieval powered by PostgreSQL <code className="footer-code-tag">pgvector</code> HNSW cosine similarity, <code className="footer-code-tag">BAAI/bge-base-en-v1.5</code> dense embeddings, and Judicial Knowledge Graph exploration.
            </p>
          </div>
        </div>

        <div className="footer-bottom-row">
          <p>© {new Date().getFullYear()} NYAYASETU Platform. Public Legal Information Initiative.</p>
          <p>Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).</p>
        </div>
      </div>
    </footer>
  );
}
