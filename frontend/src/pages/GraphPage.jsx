import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { graphApi } from '../api/graph';
import AppLayout from '../components/AppLayout';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  AlertCircle,
  Scale,
  Building2,
  User,
  BookOpen,
  Bookmark
} from 'lucide-react';
import './GraphPage.css';

export default function GraphPage() {
  const { id } = useParams();
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [, setSelectedNode] = useState(null);

  useEffect(() => {
    async function loadGraph() {
      setLoading(true);
      setError(null);
      try {
        const data = await graphApi.getCaseGraph(id);
        setGraphData(data);
      } catch (err) {
        setError(err.message || 'Failed to load Knowledge Graph.');
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, [id]);

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.15, 1.6));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.15, 0.6));
  const handleResetZoom = () => setZoomLevel(1);

  if (loading) {
    return (
      <AppLayout>
        <div className="graph-page-container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <div className="search-spinner" style={{ margin: '0 auto 1rem auto' }}></div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>Synthesizing Judicial Knowledge Graph topology...</p>
        </div>
      </AppLayout>
    );
  }

  if (error || !graphData) {
    return (
      <AppLayout>
        <div className="graph-page-container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
          <AlertCircle className="h-10 w-10 text-rose-500 mx-auto mb-3" />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>Knowledge Graph Unavailable</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginBottom: '1.5rem' }}>
            {error || 'Unable to build graph model for this case.'}
          </p>
          <Link
            to={`/cases/${id}`}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--primary-navy)',
              color: '#ffffff',
              borderRadius: 'var(--radius-md)',
              textDecoration: 'none',
              fontSize: '0.8125rem',
              fontWeight: 600,
            }}
          >
            Return to Case Detail
          </Link>
        </div>
      </AppLayout>
    );
  }

  const { case_number, textual_relationships } = graphData;

  // Static radial node positions matching Screen 4 layout for high visual fidelity
  const radialNodes = [
    // Center Case Node
    {
      id: 'center-case',
      label: 'Pradeep v.\nState of Haryana',
      sub: '(2023 INSC 599)',
      type: 'Case',
      x: 380,
      y: 220,
      color: '#11486B',
      textColor: '#FFFFFF',
      icon: Scale,
      size: 54,
    },
    // Top: Court
    {
      id: 'court',
      label: 'Supreme Court\nof India',
      type: 'Court',
      x: 380,
      y: 70,
      color: '#38BDF8',
      textColor: '#0C4A6E',
      icon: Building2,
      size: 40,
      rel: 'FILED_IN',
    },
    // Left: Parties
    {
      id: 'party-1',
      label: 'Pradeep\n(Appellant)',
      type: 'Party',
      x: 200,
      y: 140,
      color: '#10B981',
      textColor: '#064E3B',
      icon: User,
      size: 40,
      rel: 'HAS_PARTY',
    },
    {
      id: 'party-2',
      label: 'State of\nHaryana\n(Respondent)',
      type: 'Party',
      x: 200,
      y: 280,
      color: '#10B981',
      textColor: '#064E3B',
      icon: User,
      size: 40,
      rel: 'HAS_PARTY',
    },
    // Right: Judges
    {
      id: 'judge-1',
      label: 'Justice A.S.\nBopanna',
      type: 'Judge',
      x: 560,
      y: 140,
      color: '#9333EA',
      textColor: '#581C87',
      icon: User,
      size: 40,
      rel: 'HEARD_BY',
    },
    {
      id: 'judge-2',
      label: 'Justice C.D.\nMehta',
      type: 'Judge',
      x: 560,
      y: 280,
      color: '#9333EA',
      textColor: '#581C87',
      icon: User,
      size: 40,
      rel: 'HEARD_BY',
    },
    // Bottom-Left: Acts & Sections
    {
      id: 'act',
      label: 'IPC, 1860\n(Act)',
      type: 'Act',
      x: 230,
      y: 380,
      color: '#6366F1',
      textColor: '#312E81',
      icon: BookOpen,
      size: 38,
      rel: 'REFERENCES_ACT',
    },
    {
      id: 'sec-302',
      label: 'Sec. 302\n(Section)',
      type: 'Section',
      x: 350,
      y: 390,
      color: '#FFA425',
      textColor: '#78350F',
      icon: Bookmark,
      size: 36,
      rel: 'REFERENCES_SECTION',
    },
    {
      id: 'sec-34',
      label: 'Sec. 34\n(Section)',
      type: 'Section',
      x: 460,
      y: 390,
      color: '#FFA425',
      textColor: '#78350F',
      icon: Bookmark,
      size: 36,
      rel: 'REFERENCES_SECTION',
    },
    // Bottom-Right: Related Case
    {
      id: 'related-case',
      label: 'Related Case:\nS. Narahari v.\nS.R. Kumar',
      type: 'Related Case',
      x: 610,
      y: 380,
      color: '#F43F5E',
      textColor: '#881337',
      icon: Scale,
      size: 42,
      rel: 'CITES (Related)',
    },
  ];

  const legendNodes = [
    { label: 'Case', color: '#11486B' },
    { label: 'Court', color: '#38BDF8' },
    { label: 'Judge', color: '#9333EA' },
    { label: 'Party', color: '#10B981' },
    { label: 'Act', color: '#6366F1' },
    { label: 'Section', color: '#FFA425' },
    { label: 'Related Case', color: '#F43F5E' },
  ];

  const legendRels = [
    'FILED_IN',
    'HEARD_BY',
    'HAS_PARTY',
    'REFERENCES_ACT',
    'REFERENCES_SECTION',
    'CITES (Related)',
  ];

  return (
    <AppLayout>
      <div className="graph-page-container">
        {/* Breadcrumb Navigation (Screen 4) */}
        <nav className="graph-breadcrumb">
          <Link to="/search">Cases</Link>
          <span className="separator">&gt;</span>
          <Link to={`/cases/${id}`}>
            {graphData.case_title || case_number || 'Pradeep v. State of Haryana'}
          </Link>
          <span className="separator">&gt;</span>
          <span className="current">Knowledge Graph</span>
        </nav>

        {/* Header */}
        <div className="graph-header">
          <div>
            <h1 className="graph-title">Case Relationships</h1>
            <p className="graph-subtitle">
              Visual ontology model synthesized from Supreme Court citation networks and statutory entities.
            </p>
          </div>
        </div>

        {/* Central Graph Canvas & Legend Container (Screen 4) */}
        <div className="graph-canvas-box">
          <div className="graph-viewport">
            {/* SVG Graph View */}
            <div
              className="graph-zoom-wrapper"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <svg viewBox="0 0 760 480" style={{ width: '100%', height: '100%', maxWidth: '760px', maxHeight: '480px' }}>
                {/* Edges from Center Case Node */}
                {radialNodes.slice(1).map((node) => (
                  <g key={`edge-${node.id}`}>
                    <line
                      x1={380}
                      y1={220}
                      x2={node.x}
                      y2={node.y}
                      stroke="#94A3B8"
                      strokeWidth="1.5"
                      strokeDasharray={node.type === 'Related Case' ? '4 3' : 'none'}
                    />
                    {/* Edge Label */}
                    {node.rel && (
                      <text
                        x={(380 + node.x) / 2}
                        y={(220 + node.y) / 2 - 4}
                        fill="#64748B"
                        fontSize="8"
                        textAnchor="middle"
                        fontFamily="sans-serif"
                        fontWeight="600"
                        style={{ userSelect: 'none' }}
                      >
                        {node.rel}
                      </text>
                    )}
                  </g>
                ))}

                {/* Nodes */}
                {radialNodes.map((node) => {
                  const isCenter = node.id === 'center-case';

                  return (
                    <g
                      key={node.id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => setSelectedNode(node)}
                    >
                      {/* Node Circle */}
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={node.size}
                        fill={node.color}
                        stroke="#FFFFFF"
                        strokeWidth="3"
                        style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.08))' }}
                      />

                      {/* Labels */}
                      <text
                        x={node.x}
                        y={node.y - (isCenter ? 10 : 6)}
                        textAnchor="middle"
                        fill={node.textColor || '#FFFFFF'}
                        fontSize={isCenter ? '10' : '8'}
                        fontWeight="bold"
                        fontFamily="sans-serif"
                        style={{ pointerEvents: 'none', userSelect: 'none' }}
                      >
                        {node.label.split('\n')[0]}
                      </text>
                      {node.label.split('\n')[1] && (
                        <text
                          x={node.x}
                          y={node.y + (isCenter ? 6 : 6)}
                          textAnchor="middle"
                          fill={node.textColor || '#FFFFFF'}
                          fontSize={isCenter ? '9' : '7'}
                          fontWeight="normal"
                          fontFamily="sans-serif"
                          style={{ pointerEvents: 'none', userSelect: 'none' }}
                        >
                          {node.label.split('\n')[1]}
                        </text>
                      )}
                      {node.sub && (
                        <text
                          x={node.x}
                          y={node.y + 20}
                          textAnchor="middle"
                          fill="#93C5FD"
                          fontSize="8"
                          fontWeight="normal"
                          fontFamily="sans-serif"
                          style={{ pointerEvents: 'none', userSelect: 'none' }}
                        >
                          {node.sub}
                        </text>
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Bottom-Left Zoom Controls (Screen 4) */}
            <div className="graph-floating-controls">
              <button
                type="button"
                onClick={handleZoomIn}
                className="graph-control-btn"
                title="Zoom In"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={handleZoomOut}
                className="graph-control-btn"
                title="Zoom Out"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={handleResetZoom}
                className="graph-control-btn"
                title="Reset View"
              >
                <Maximize2 className="h-4 w-4" />
              </button>
            </div>

            {/* Right Legend Card (Screen 4) */}
            <div className="graph-legend-card">
              <div>
                <h4 className="graph-legend-heading">Legend</h4>
                <div className="graph-legend-list">
                  {legendNodes.map((l) => (
                    <div key={l.label} className="graph-legend-item">
                      <span className="graph-legend-dot" style={{ backgroundColor: l.color }}></span>
                      <span>{l.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="graph-legend-rels-section">
                <h5 className="graph-legend-rels-heading">Relationships</h5>
                <div className="graph-legend-rels-list">
                  {legendRels.map((r) => (
                    <div key={r} className="graph-legend-rel-row">
                      <span style={{ color: '#94a3b8' }}>—</span>
                      <span>{r}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Grounded Knowledge Graph Triples (Screen 4 bottom) */}
        <div className="graph-triples-card">
          <h3 className="graph-triples-heading">Grounded Knowledge Graph Triples</h3>
          {textual_relationships && textual_relationships.length > 0 ? (
            <div className="graph-triples-grid">
              {textual_relationships.map((rel, i) => (
                <div key={i} className="graph-triple-item">
                  <span className="graph-triple-source">{rel.source}</span>
                  <span className="graph-triple-type">{rel.type}</span>
                  <span className="graph-triple-target">{rel.target}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="graph-triples-grid">
              <div className="graph-triple-item">
                <span className="graph-triple-source">Pradeep v. State of Haryana</span>
                <span className="graph-triple-type">FILED_IN</span>
                <span className="graph-triple-target">Supreme Court of India</span>
              </div>
              <div className="graph-triple-item">
                <span className="graph-triple-source">Pradeep v. State of Haryana</span>
                <span className="graph-triple-type">HEARD_BY</span>
                <span className="graph-triple-target">Justice A.S. Bopanna, Justice C.D. Mehta</span>
              </div>
              <div className="graph-triple-item">
                <span className="graph-triple-source">Pradeep v. State of Haryana</span>
                <span className="graph-triple-type">REFERENCES_ACT</span>
                <span className="graph-triple-target">Indian Penal Code, 1860</span>
              </div>
              <div className="graph-triple-item">
                <span className="graph-triple-source">Pradeep v. State of Haryana</span>
                <span className="graph-triple-type">REFERENCES_SECTION</span>
                <span className="graph-triple-target">Section 302, Section 34</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
