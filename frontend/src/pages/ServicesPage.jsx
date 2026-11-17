import { useState, useEffect } from 'react';
import { servicesApi } from '../api/services';
import AppLayout from '../components/AppLayout';
import {
  Building2,
  ExternalLink,
  Scale,
  Search,
  Shield,
  FileText
} from 'lucide-react';
import './ServicesPage.css';

export default function ServicesPage() {
  const [services, setServices] = useState([]);
  const [activeTab, setActiveTab] = useState('All');

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
      try {
        const data = await servicesApi.getServices();
        if (data && (data.results?.length > 0 || data.length > 0)) {
          setServices(data.results || data);
        } else {
          setServices(defaultServices);
        }
      } catch {
        setServices(defaultServices);
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
      <div className="services-page-container">
        {/* Header (Screen 7) */}
        <div className="services-header">
          <h1 className="services-title">Judicial &amp; Government Services</h1>
          <p className="services-subtitle">
            Access official judicial and legal services from trusted government sources.
          </p>
        </div>

        {/* Filter Pills (Screen 7) */}
        <div className="services-tabs-row">
          {filterTabs.map((tab) => {
            const isActive = activeTab === tab.value;
            return (
              <button
                key={tab.value}
                type="button"
                onClick={() => setActiveTab(tab.value)}
                className={`services-tab-btn ${isActive ? 'active' : ''}`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Services Grid (Screen 7 - 2x2 cards) */}
        <div className="services-grid">
          {filteredServices.map((svc, idx) => {
            const Icon = svc.icon || Building2;
            const title = svc.name || svc.title;
            const desc = svc.description || svc.short_description;
            const url = svc.url || svc.portal_url;

            return (
              <div key={svc.id || idx} className="service-card">
                <div className="service-card-top">
                  <div className="service-icon-box">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="service-title">{title}</h3>
                    <p className="service-desc">{desc}</p>
                  </div>
                </div>

                <div className="service-card-footer">
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="service-link"
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
