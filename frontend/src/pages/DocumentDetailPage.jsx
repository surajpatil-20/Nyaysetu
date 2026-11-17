import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { documentsApi } from '../api/documents';
import AppLayout from '../components/AppLayout';
import {
  FileText,
  ChevronRight,
  Trash2,
  CheckCircle2,
  Clock,
  AlertCircle,
  Copy,
  Check,
  Download,
  BookOpen
} from 'lucide-react';
import './DocumentDetailPage.css';

export default function DocumentDetailPage() {
  const { id } = useParams();
  const [doc, setDoc] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchDoc() {
      setLoading(true);
      setError(null);
      try {
        const [docData, summaryData] = await Promise.all([
          documentsApi.getDocumentDetail(id),
          documentsApi.getDocumentSummary(id).catch(() => null),
        ]);
        setDoc(docData);
        setSummary(summaryData);
      } catch (err) {
        setError(err.message || 'Failed to load document analysis.');
      } finally {
        setLoading(false);
      }
    }
    fetchDoc();
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    try {
      await documentsApi.deleteDocument(id);
      navigate('/documents');
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const copyText = () => {
    if (doc?.extracted_text) {
      navigator.clipboard.writeText(doc.extracted_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="p-16 text-center space-y-3">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-slate-500 text-xs">Analyzing document extraction & chunks...</p>
        </div>
      </AppLayout>
    );
  }

  if (error || !doc) {
    return (
      <AppLayout>
        <div className="p-12 max-w-lg mx-auto text-center space-y-4">
          <AlertCircle className="h-10 w-10 text-rose-500 mx-auto" />
          <h2 className="text-lg font-bold text-slate-800">Document Not Found</h2>
          <p className="text-xs text-slate-500">{error || 'This document could not be retrieved.'}</p>
          <Link
            to="/documents"
            className="inline-flex items-center text-xs font-semibold px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <span>Return to Documents</span>
          </Link>
        </div>
      </AppLayout>
    );
  }

  const isCompleted = doc.status === 'COMPLETED';

  return (
    <AppLayout>
      <div className="p-6 max-w-5xl mx-auto space-y-6">
        {/* Breadcrumb Navigation */}
        <nav className="flex items-center space-x-1.5 text-xs text-slate-500">
          <Link to="/documents" className="hover:text-blue-600 transition">My Documents</Link>
          <ChevronRight className="h-3 w-3 text-slate-400" />
          <span className="font-semibold text-slate-800 truncate max-w-[240px]">{doc.title}</span>
        </nav>

        {/* Header Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="p-3 bg-rose-50 text-rose-600 rounded-xl">
              <FileText className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                {doc.title?.endsWith('.pdf') ? doc.title : `${doc.title}.pdf`}
              </h1>
              <div className="flex items-center space-x-2 mt-1 text-xs text-slate-500">
                <span>{doc.file_size ? `${(doc.file_size / (1024 * 1024)).toFixed(2)} MB` : 'PDF Document'}</span>
                <span>•</span>
                <span>{doc.page_count || 1} pages</span>
                <span>•</span>
                <span className={`px-2 py-0.5 rounded-full font-semibold text-[11px] ${
                  isCompleted ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-blue-50 text-blue-700 border border-blue-200'
                }`}>
                  {doc.status}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2.5">
            {doc.file && (
              <a
                href={doc.file}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-xs transition"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Download PDF</span>
              </a>
            )}
            <button
              type="button"
              onClick={handleDelete}
              className="p-2 text-slate-400 hover:text-rose-600 hover:bg-slate-100 rounded-lg transition"
              title="Delete Document"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* AI Summary Card (if available) */}
        {summary && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-3">
            <h3 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
              <BookOpen className="h-4 w-4 text-blue-600" />
              <span>Automated Legal Analysis & Abstract</span>
            </h3>
            <p className="text-xs text-slate-700 leading-relaxed font-serif bg-slate-50 p-4 rounded-lg border-l-2 border-blue-500">
              {summary.summary || summary.text || 'Document analysis successfully indexed into private vector space.'}
            </p>
          </div>
        )}

        {/* Extracted Text Pane */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-sm">Extracted Text Content</h3>
            <button
              type="button"
              onClick={copyText}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Text'}</span>
            </button>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 max-h-96 overflow-y-auto text-xs text-slate-700 font-mono whitespace-pre-wrap leading-relaxed">
            {doc.extracted_text || 'No extracted text available yet.'}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
