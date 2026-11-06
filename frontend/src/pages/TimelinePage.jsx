import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { casesApi } from '../api/cases';
import AppLayout from '../components/AppLayout';
import {
  Calendar,
  ChevronRight,
  AlertCircle,
  FileText,
  CheckCircle2,
  Clock,
  ArrowLeft
} from 'lucide-react';

export default function TimelinePage() {
  const { id } = useParams();
  const [timelineData, setTimelineData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchTimeline() {
      setLoading(true);
      setError(null);
      try {
        const data = await casesApi.getCaseTimeline(id);
        setTimelineData(data);
      } catch (err) {
        setError(err.message || 'Failed to load case timeline.');
      } finally {
        setLoading(false);
      }
    }
    fetchTimeline();
  }, [id]);

  if (loading) {
    return (
      <AppLayout>
        <div className="p-16 text-center space-y-3">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-slate-500 text-xs">Building procedural case timeline...</p>
        </div>
      </AppLayout>
    );
  }

  if (error || !timelineData) {
    return (
      <AppLayout>
        <div className="p-12 max-w-lg mx-auto text-center space-y-4">
          <AlertCircle className="h-10 w-10 text-rose-500 mx-auto" />
          <h2 className="text-lg font-bold text-slate-800">Timeline Unavailable</h2>
          <p className="text-xs text-slate-500">{error || 'No chronological events recorded for this case.'}</p>
          <Link to={`/cases/${id}`} className="text-xs text-blue-600 hover:underline font-semibold">
            Return to Case Detail
          </Link>
        </div>
      </AppLayout>
    );
  }

  const { case_number, case_title, timeline } = timelineData;

  return (
    <AppLayout>
      <div className="p-6 max-w-5xl mx-auto space-y-6">
        {/* Breadcrumb Navigation */}
        <nav className="flex items-center space-x-1.5 text-xs text-slate-500">
          <Link to="/search" className="hover:text-blue-600 transition">Cases</Link>
          <ChevronRight className="h-3 w-3 text-slate-400" />
          <Link to={`/cases/${id}`} className="hover:text-blue-600 transition truncate max-w-[200px]">
            {case_title || case_number}
          </Link>
          <ChevronRight className="h-3 w-3 text-slate-400" />
          <span className="font-semibold text-slate-800">Timeline</span>
        </nav>

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Procedural Case Timeline</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Chronological milestones from filing to final judgment for {case_number}.
            </p>
          </div>
          <Link
            to={`/cases/${id}`}
            className="px-3 py-1.5 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-semibold flex items-center space-x-1 transition"
          >
            <ArrowLeft className="h-3 w-3" />
            <span>Case Detail</span>
          </Link>
        </div>

        {/* Timeline Events Container */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-xs">
          {timeline && timeline.length > 0 ? (
            <div className="relative border-l-2 border-blue-500 ml-4 space-y-8 pl-6">
              {timeline.map((item, idx) => (
                <div key={idx} className="relative group">
                  {/* Dot */}
                  <span className="absolute -left-[31px] top-1 h-3.5 w-3.5 rounded-full bg-blue-600 ring-4 ring-white"></span>

                  <div className="space-y-1">
                    <span className="inline-block px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-[11px] font-mono font-semibold">
                      {item.event_date || item.date}
                    </span>
                    <h3 className="font-bold text-slate-900 text-sm">
                      {item.event_title || item.title || item.event_type}
                    </h3>
                    <p className="text-xs text-slate-600 leading-relaxed max-w-xl">
                      {item.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-xs">
              No recorded timeline events for this case record.
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
