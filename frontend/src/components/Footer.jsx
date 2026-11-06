import { ShieldAlert, BookOpen, ExternalLink, Scale } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-[#0A192F] border-t border-[#1E293B] text-slate-400 text-xs py-10 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Civic Judicial Information Notice */}
        <div className="bg-[#0D213F] border border-blue-900/50 rounded-xl p-4 flex items-start space-x-3 text-slate-300">
          <ShieldAlert className="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold text-white">Civic Judicial Information Notice:</span>
            <p className="leading-relaxed text-slate-300">
              NYAYASETU provides informational assistance based on available judicial records. It is not a substitute for professional legal advice and does not predict judicial outcomes or make judicial decisions. Always consult an enrolled advocate or qualified legal practitioner for actionable legal representation.
            </p>
          </div>
        </div>

        {/* Data Attribution & Official Links */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-2">
          <div>
            <div className="flex items-center space-x-2 text-white font-bold text-sm mb-3">
              <Scale className="h-4 w-4 text-blue-500" />
              <span>NYAYASETU</span>
            </div>
            <p className="leading-relaxed text-slate-400">
              AI-Assisted, Evidence-Oriented Judicial Information Platform. Real judicial case judgments are sourced from the Indian Supreme Court Judgments Open Dataset via the AWS Open Data Registry under CC BY 4.0.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-white text-sm mb-3">Official Government Portals</h4>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://main.sci.gov.in/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-400 flex items-center space-x-1.5 transition"
                >
                  <span>Supreme Court of India</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://ecourts.gov.in/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-400 flex items-center space-x-1.5 transition"
                >
                  <span>eCourts Services Portal</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://nalsa.gov.in/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-400 flex items-center space-x-1.5 transition"
                >
                  <span>National Legal Services Authority (NALSA)</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-white text-sm mb-3">Technical Architecture</h4>
            <p className="leading-relaxed text-slate-400">
              Evidence retrieval powered by PostgreSQL <code className="text-blue-300 bg-slate-800 px-1 py-0.5 rounded">pgvector</code> HNSW cosine similarity, <code className="text-blue-300 bg-slate-800 px-1 py-0.5 rounded">BAAI/bge-base-en-v1.5</code> dense embeddings, and Judicial Knowledge Graph exploration.
            </p>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 flex flex-col sm:flex-row justify-between items-center text-slate-500 text-[11px] gap-2">
          <p>© {new Date().getFullYear()} NYAYASETU Platform. Public Legal Information Initiative.</p>
          <p>Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).</p>
        </div>
      </div>
    </footer>
  );
}
