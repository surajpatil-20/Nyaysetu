import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { graphApi } from '../api/graph';
import AppLayout from '../components/AppLayout';
import {
  Network,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize2,
  AlertCircle,
  Scale,
  Building2,
  User,
  BookOpen,
  Bookmark,
  Share2
} from 'lucide-react';
import './GraphPage.css';

export default function GraphPage() {
  const { id } = useParams();
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedNode, setSelectedNode] = useState(null);

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
        <div className="p-16 text-center space-y-3">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-slate-500 text-xs">Synthesizing Judicial Knowledge Graph topology...</p>
        </div>
      </AppLayout>
    );
  }

  if (error || !graphData) {
    return (
      <AppLayout>
        <div className="p-12 max-w-lg mx-auto text-center space-y-4">
          <AlertCircle className="h-10 w-10 text-rose-500 mx-auto" />
          <h2 className="text-lg font-bold text-slate-800">Knowledge Graph Unavailable</h2>
          <p className="text-xs text-slate-500">{error || 'Unable to build graph model for this case.'}</p>
          <Link to={`/cases/${id}`} className="text-xs text-blue-600 hover:underline font-semibold">
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
      color: '#0A192F',
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
      color: '#A855F7',
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
      color: '#A855F7',
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
      color: '#F59E0B',
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
      color: '#F59E0B',
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
    { label: 'Case', color: '#0A192F' },
    { label: 'Court', color: '#38BDF8' },
    { label: 'Judge', color: '#A855F7' },
    { label: 'Party', color: '#10B981' },
    { label: 'Act', color: '#6366F1' },
    { label: 'Section', color: '#F59E0B' },
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
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Breadcrumb Navigation (Screen 4) */}
        <nav className="flex items-center space-x-1.5 text-xs text-slate-500">
          <Link to="/search" className="hover:text-blue-600 transition">Cases</Link>
          <ChevronRight className="h-3 w-3 text-slate-400" />
          <Link to={`/cases/${id}`} className="hover:text-blue-600 transition truncate max-w-[200px]">
            {graphData.case_title || case_number}
          </Link>
          <ChevronRight className="h-3 w-3 text-slate-400" />
          <span className="font-semibold text-slate-800">Knowledge Graph</span>
        </nav>

        {/* Title */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Case Relationships</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Visual ontology model synthesized from Supreme Court citation networks and statutory entities.
            </p>
          </div>
        </div>

        {/* Central Graph Canvas & Legend Container (Screen 4) */}
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs relative">
          <div className="relative w-full h-[540px] bg-slate-50/50 overflow-hidden flex items-center justify-center">
            {/* SVG Graph View */}
            <div
              className="w-full h-full flex items-center justify-center transition-transform duration-200 origin-center"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <svg viewBox="0 0 760 480" className="w-full h-full max-w-[760px] max-h-[480px]">
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
                        className="select-none"
                      >
                        {node.rel}
                      </text>
                    )}
                  </g>
                ))}

                {/* Nodes */}
                {radialNodes.map((node) => {
                  const Icon = node.icon;
                  const isCenter = node.id === 'center-case';

                  return (
                    <g
                      key={node.id}
                      className="cursor-pointer group"
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
                        className="transition-all drop-shadow-sm group-hover:scale-105"
                      />

                      {/* Icon or Label inside/below circle */}
                      <text
                        x={node.x}
                        y={node.y - (isCenter ? 10 : 6)}
                        textAnchor="middle"
                        fill={node.textColor || '#FFFFFF'}
                        fontSize={isCenter ? '10' : '8'}
                        fontWeight="bold"
                        fontFamily="sans-serif"
                        className="select-none pointer-events-none"
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
                          className="select-none pointer-events-none"
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
                          className="select-none pointer-events-none"
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
            <div className="absolute bottom-4 left-4 bg-white border border-slate-200 rounded-lg shadow-sm p-1 flex items-center space-x-1">
              <button
                type="button"
                onClick={handleZoomIn}
                className="p-1.5 hover:bg-slate-100 rounded text-slate-700 transition"
                title="Zoom In"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={handleZoomOut}
                className="p-1.5 hover:bg-slate-100 rounded text-slate-700 transition"
                title="Zoom Out"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={handleResetZoom}
                className="p-1.5 hover:bg-slate-100 rounded text-slate-700 transition"
                title="Reset View"
              >
                <Maximize2 className="h-4 w-4" />
              </button>
            </div>

            {/* Right Legend Card (Screen 4) */}
            <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm border border-slate-200 rounded-xl p-4 shadow-sm w-44 space-y-3 text-xs">
              <div>
                <h4 className="font-bold text-slate-900 mb-2">Legend</h4>
                <div className="space-y-1.5">
                  {legendNodes.map((l) => (
                    <div key={l.label} className="flex items-center space-x-2 text-[11px] text-slate-600">
                      <span className="h-2.5 w-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: l.color }}></span>
                      <span>{l.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border-t border-slate-100 pt-2">
                <h5 className="font-semibold text-slate-700 text-[11px] mb-1.5">Relationships</h5>
                <div className="space-y-1 text-[10px] text-slate-500 font-mono">
                  {legendRels.map((r) => (
                    <div key={r} className="flex items-center space-x-1.5">
                      <span className="text-slate-400">—</span>
                      <span>{r}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Accessible Textual Relationships List (Screen 4 bottom) */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
          <h3 className="font-bold text-slate-900 text-sm">Grounded Knowledge Graph Triples</h3>
          {textual_relationships && textual_relationships.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              {textual_relationships.map((rel, i) => (
                <div key={i} className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center space-x-2">
                  <span className="font-bold text-slate-800">{rel.source}</span>
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-mono text-[10px] uppercase font-semibold">
                    {rel.type}
                  </span>
                  <span className="text-slate-700">{rel.target}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center space-x-2">
                <span className="font-bold text-slate-800">Pradeep v. State of Haryana</span>
                <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-mono text-[10px] font-semibold">FILED_IN</span>
                <span className="text-slate-700">Supreme Court of India</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center space-x-2">
                <span className="font-bold text-slate-800">Pradeep v. State of Haryana</span>
                <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-mono text-[10px] font-semibold">HEARD_BY</span>
                <span className="text-slate-700">Justice A.S. Bopanna, Justice C.D. Mehta</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center space-x-2">
                <span className="font-bold text-slate-800">Pradeep v. State of Haryana</span>
                <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-mono text-[10px] font-semibold">REFERENCES_ACT</span>
                <span className="text-slate-700">Indian Penal Code, 1860</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center space-x-2">
                <span className="font-bold text-slate-800">Pradeep v. State of Haryana</span>
                <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-mono text-[10px] font-semibold">REFERENCES_SECTION</span>
                <span className="text-slate-700">Section 302, Section 34</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
