import { useState, useEffect } from 'react';
import { servicesApi } from '../api/services';
import AppLayout from '../components/AppLayout';
import {
  Building2,
  ExternalLink,
  Scale,
  Search,
  BookOpen,
  Shield,
  FileText
} from 'lucide-react';
import './ServicesPage.css';

export default function ServicesPage() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('All');
  const [error, setError] = useState(null);

  const filterTabs = [
    { label: 'All', value: 'All' },
    { label: 'eCourts', value: 'eCourts' },
    { label: 'Supreme Court', value: 'Supreme Court' },
    { label: 'Case Status', value: 'Case Status' },
    { label: 'Legal Aid', value: 'Legal Aid' },
  ];

  // Default government judicial services matching Screen 7
  const defaultServices = [
    {
      id: 1,
      title: 'eCourts Services',
      description: 'Case status, orders, and cause lists from eCourts.',
      url: 'https://ecourts.gov.in/',
      category: 'eCourts',
      icon: Building2,
    },
    {
      id: 2,
      title: 'Supreme Court of India',
      description: 'Official website, judgments, cause lists and more.',
      url: 'https://main.sci.gov.in/',
      category: 'Supreme Court',
      icon: Scale,
    },
    {
      id: 3,
      title: 'Case Status (NJDG)',
      description: 'Track your case using CNR number.',
      url: 'https://njdg.ecourts.gov.in/',
      category: 'Case Status',
      icon: Search,
    },
    {
      id: 4,
      title: 'Legal Aid Services',
      description: 'Free legal aid and assistance under NALSA.',
      url: 'https://nalsa.gov.in/',
      category: 'Legal Aid',
      icon: Shield,
    },
    {
      id: 5,
      title: 'e-Filing 3.0 Portal',
      description: 'Electronic filing of judicial plaints, appeals, and petitions.',
      url: 'https://efiling.ecourts.gov.in/',
      category: 'eCourts',
      icon: FileText,
    },
    {
      id: 6,
      title: 'Virtual Courts Portal',
      description: 'Online adjudication and digital payment of traffic challans.',
      url: 'https://vcourts.gov.in/',
      category: 'Case Status',
      icon: Building2,
    },
  ];

  useEffect(() => {
    async function fetchServices() {
      setLoading(true);
      setError(null);
      try {
        const data = await servicesApi.getServices();
        if (data && (data.results?.length > 0 || data.length > 0)) {
          setServices(data.results || data);
        } else {
          setServices(defaultServices);
        }
      } catch (err) {
        // Fallback to default verified services
        setServices(defaultServices);
      } finally {
        setLoading(false);
      }
    }
    fetchServices();
  }, []);

  const filteredServices = activeTab === 'All'
    ? services
    : services.filter((s) => {
        const cat = s.category?.toLowerCase() || '';
        const title = s.name?.toLowerCase() || s.title?.toLowerCase() || '';
        const filter = activeTab.toLowerCase();
        return cat.includes(filter) || title.includes(filter);
      });

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Header (Screen 7) */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Judicial & Government Services
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Access official judicial and legal services from trusted government sources.
          </p>
        </div>

        {/* Filter Pills (Screen 7) */}
        <div className="flex space-x-2 overflow-x-auto pb-1 text-xs">
          {filterTabs.map((tab) => {
            const isActive = activeTab === tab.value;
            return (
              <button
                key={tab.value}
                onClick={() => setActiveTab(tab.value)}
                className={`px-4 py-2 rounded-lg font-semibold transition ${
                  isActive
                    ? 'bg-[#0A192F] text-white shadow-xs'
                    : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Services Grid (Screen 7) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredServices.map((svc, idx) => {
            const Icon = svc.icon || Building2;
            const title = svc.name || svc.title;
            const desc = svc.description || svc.short_description;
            const url = svc.url || svc.portal_url;

            return (
              <div
                key={svc.id || idx}
                className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs hover:shadow-md transition flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl w-fit">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 text-base">{title}</h3>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                      {desc}
                    </p>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100">
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 transition"
                  >
                    <span>Visit Official Site</span>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AppLayout>
  );
}
