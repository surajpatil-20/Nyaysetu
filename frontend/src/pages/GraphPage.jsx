import { useState, useEffect, useMemo } from 'react';
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
  Bookmark,
  FileText
} from 'lucide-react';
import { GraphSkeleton } from '../components/Skeleton';
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

  // Compute dynamic radial layout from actual backend graph data
  const { centerNode, outerNodes, edges } = useMemo(() => {
    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
      return { centerNode: null, outerNodes: [], edges: [] };
    }

    const rawNodes = graphData.nodes;
    const rawLinks = graphData.links || [];

    // Find or create central case node
    let center = rawNodes.find((n) => n.type === 'Case');
    const others = rawNodes.filter((n) => n !== center);

    const caseTitle = center?.data?.title || graphData.case_title || graphData.case_number || `Case #${id}`;
    const caseDocket = center?.data?.case_number || graphData.case_number || '';

    const centerNodeFormatted = {
      id: center?.id || `case_${id}`,
      label: caseTitle.length > 30 ? `${caseTitle.slice(0, 28)}...` : caseTitle,
      sub: caseDocket,
      type: 'Case',
      x: 380,
      y: 220,
      color: '#11486B',
      textColor: '#FFFFFF',
      icon: Scale,
      size: 52,
    };

    // Arrange other nodes evenly in an ellipse around (380, 220)
    const count = others.length;
    const rx = 210;
    const ry = 140;

    const typeColors = {
      Court: { color: '#38BDF8', text: '#0C4A6E', icon: Building2 },
      Judge: { color: '#9333EA', text: '#581C87', icon: User },
      Party: { color: '#10B981', text: '#064E3B', icon: User },
      Act: { color: '#6366F1', text: '#312E81', icon: BookOpen },
      Section: { color: '#FFA425', text: '#78350F', icon: Bookmark },
      Document: { color: '#64748B', text: '#0F172A', icon: FileText },
      'Related Case': { color: '#F43F5E', text: '#881337', icon: Scale },
    };

    const outerNodesFormatted = others.map((node, i) => {
      // Angle offset so top node starts at top
      const angle = (2 * Math.PI * i) / Math.max(count, 1) - Math.PI / 2;
      const x = Math.round(380 + rx * Math.cos(angle));
      const y = Math.round(220 + ry * Math.sin(angle));

      const typeMeta = typeColors[node.type] || { color: '#94A3B8', text: '#1E293B', icon: Bookmark };

      // Find relational link connecting this node to case
      const link = rawLinks.find(
        (l) => l.target === node.id || l.source === node.id
      );

      const label = node.label || node.data?.name || node.data?.title || node.id;
      const splitLabel = label.length > 22 ? `${label.slice(0, 20)}...` : label;

      return {
        id: node.id,
        label: splitLabel,
        type: node.type,
        x,
        y,
        color: typeMeta.color,
        textColor: typeMeta.text,
        icon: typeMeta.icon,
        size: 38,
        rel: link?.type || node.type.toUpperCase(),
      };
    });

    return {
      centerNode: centerNodeFormatted,
      outerNodes: outerNodesFormatted,
      edges: outerNodesFormatted,
    };
  }, [graphData, id]);

  if (loading) {
    return (
      <AppLayout>
        <div className="graph-page-container">
          <nav className="graph-breadcrumb">
            <Link to="/search">Cases</Link>
            <span className="separator">&gt;</span>
            <Link to={`/cases/${id}`}>Case #{id}</Link>
            <span className="separator">&gt;</span>
            <span className="current">Knowledge Graph</span>
          </nav>
          <div className="graph-header">
            <div>
              <h1 className="graph-title">Case Relationships</h1>
              <p className="graph-subtitle">
                Synthesizing knowledge graph ontology and precedent citation networks...
              </p>
            </div>
          </div>
          <GraphSkeleton />
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

  const { case_number, case_title, textual_relationships } = graphData;

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
        {/* Breadcrumb Navigation */}
        <nav className="graph-breadcrumb">
          <Link to="/search">Cases</Link>
          <span className="separator">&gt;</span>
          <Link to={`/cases/${id}`} style={{ maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {case_title || case_number || `Case #${id}`}
          </Link>
          <span className="separator">&gt;</span>
          <span className="current">Knowledge Graph</span>
        </nav>

        {/* Header */}
        <div className="graph-header">
          <div>
            <h1 className="graph-title">Case Relationships</h1>
            <p className="graph-subtitle">
              Visual ontology model synthesized from precedent citation networks and statutory entities for {case_number || case_title}.
            </p>
          </div>
        </div>

        {/* Central Graph Canvas & Legend Container */}
        <div className="graph-canvas-box">
          <div className="graph-viewport">
            {/* SVG Graph View */}
            <div
              className="graph-zoom-wrapper"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <svg viewBox="0 0 760 480" style={{ width: '100%', height: '100%', maxWidth: '760px', maxHeight: '480px' }}>
                {/* Edges from Center Case Node */}
                {edges.map((node) => (
                  <g key={`edge-${node.id}`}>
                    <line
                      x1={380}
                      y1={220}
                      x2={node.x}
                      y2={node.y}
                      stroke="#CBD5E1"
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

                {/* Outer Nodes */}
                {outerNodes.map((node) => (
                  <g
                    key={node.id}
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedNode(node)}
                  >
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={node.size}
                      fill={node.color}
                      stroke="#FFFFFF"
                      strokeWidth="3"
                      style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.08))' }}
                    />
                    <text
                      x={node.x}
                      y={node.y - 2}
                      textAnchor="middle"
                      fill={node.textColor || '#FFFFFF'}
                      fontSize="8"
                      fontWeight="bold"
                      fontFamily="sans-serif"
                      style={{ pointerEvents: 'none', userSelect: 'none' }}
                    >
                      {node.label}
                    </text>
                    <text
                      x={node.x}
                      y={node.y + 9}
                      textAnchor="middle"
                      fill={node.textColor || '#FFFFFF'}
                      fontSize="7"
                      fontWeight="normal"
                      fontFamily="sans-serif"
                      style={{ pointerEvents: 'none', userSelect: 'none', opacity: 0.85 }}
                    >
                      {node.type}
                    </text>
                  </g>
                ))}

                {/* Center Case Node */}
                {centerNode && (
                  <g
                    key={centerNode.id}
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedNode(centerNode)}
                  >
                    <circle
                      cx={centerNode.x}
                      cy={centerNode.y}
                      r={centerNode.size}
                      fill={centerNode.color}
                      stroke="#FFFFFF"
                      strokeWidth="4"
                      style={{ filter: 'drop-shadow(0 3px 8px rgba(17,72,107,0.3))' }}
                    />
                    <text
                      x={centerNode.x}
                      y={centerNode.y - 4}
                      textAnchor="middle"
                      fill={centerNode.textColor}
                      fontSize="9"
                      fontWeight="bold"
                      fontFamily="sans-serif"
                      style={{ pointerEvents: 'none', userSelect: 'none' }}
                    >
                      {centerNode.label}
                    </text>
                    {centerNode.sub && (
                      <text
                        x={centerNode.x}
                        y={centerNode.y + 12}
                        textAnchor="middle"
                        fill="#93C5FD"
                        fontSize="8"
                        fontWeight="normal"
                        fontFamily="sans-serif"
                        style={{ pointerEvents: 'none', userSelect: 'none' }}
                      >
                        {centerNode.sub}
                      </text>
                    )}
                  </g>
                )}
              </svg>
            </div>

            {/* Bottom-Left Zoom Controls */}
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

            {/* Right Legend Card */}
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

        {/* Grounded Knowledge Graph Triples */}
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
            <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
              No explicit citation triples registered for this record. Relational nodes are mapped directly from judicial database entities.
            </p>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
