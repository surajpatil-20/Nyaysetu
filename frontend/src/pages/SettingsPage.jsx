import { useState } from 'react';
import AppLayout from '../components/AppLayout';
import { useTheme } from '../context/ThemeContext';
import {
  Sun,
  Moon,
  Type,
  Check,
  RotateCcw,
  Sparkles,
  Eye,
  SlidersHorizontal,
  CheckCircle2,
  FileText
} from 'lucide-react';
import './SettingsPage.css';

export default function SettingsPage() {
  const {
    theme,
    setTheme,
    toggleTheme,
    fontSize,
    setFontSize,
    fontSizes,
    fontSizeConfig,
    resetPreferences,
  } = useTheme();

  const [savedNotification, setSavedNotification] = useState('');

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    showNotice(`Theme updated to ${newTheme === 'dark' ? 'Judicial Dark Mode' : 'Civic Light Mode'}`);
  };

  const handleFontSizeChange = (newSize) => {
    setFontSize(newSize);
    const label = fontSizes[newSize]?.label || newSize;
    showNotice(`Judicial font size updated to ${label} (${fontSizes[newSize]?.badge})`);
  };

  const handleReset = () => {
    resetPreferences();
    showNotice('Preferences reset to default Light theme and Standard typography.');
  };

  const showNotice = (msg) => {
    setSavedNotification(msg);
    setTimeout(() => {
      setSavedNotification('');
    }, 3000);
  };

  return (
    <AppLayout>
      <div className="settings-container">
        {/* Header */}
        <div className="settings-header">
          <h1 className="settings-title">Settings &amp; Accessibility</h1>
          <p className="settings-subtitle">
            Configure platform appearance, theme mode, and reading typography across judicial records.
          </p>
        </div>

        {/* Live Notification Banner */}
        {savedNotification && (
          <div style={{
            backgroundColor: 'var(--success-bg)',
            border: '1px solid var(--success-border)',
            borderRadius: 'var(--radius-md)',
            padding: '0.75rem 1rem',
            fontSize: '0.8125rem',
            color: 'var(--success-text)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'all var(--transition-fast)'
          }}>
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{savedNotification}</span>
          </div>
        )}

        {/* ==================================================================
            Section 1: Appearance Mode (Dark / Light Mode)
            ================================================================== */}
        <div className="settings-section-card">
          <div className="settings-section-header">
            <h2 className="settings-section-title">
              <Sun className="h-4 w-4 text-[#FFA425]" />
              <span>Appearance &amp; Theme Mode</span>
            </h2>
            <p className="settings-section-subtitle">
              Choose between Clean Civic Light and Judicial Deep Navy Dark mode. You can also toggle this anytime directly from the top navigation bar.
            </p>
          </div>

          <div className="theme-options-grid">
            {/* Option 1: Light Mode */}
            <div
              className={`theme-card ${theme === 'light' ? 'active' : ''}`}
              onClick={() => handleThemeChange('light')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleThemeChange('light')}
            >
              <div className="theme-card-top">
                <div className="theme-card-icon-box">
                  <Sun className="h-5 w-5 text-[#FFA425]" />
                </div>
                <div className="theme-radio-indicator">
                  {theme === 'light' && <Check className="h-3 w-3 stroke-[3]" />}
                </div>
              </div>
              <div>
                <h3 className="theme-card-title">Light Mode (Civic White)</h3>
                <p className="theme-card-desc">
                  High-contrast crisp off-white surfaces designed for standard daytime research, citation printing, and civic transparency.
                </p>
              </div>
            </div>

            {/* Option 2: Dark Mode */}
            <div
              className={`theme-card ${theme === 'dark' ? 'active' : ''}`}
              onClick={() => handleThemeChange('dark')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleThemeChange('dark')}
            >
              <div className="theme-card-top">
                <div className="theme-card-icon-box">
                  <Moon className="h-5 w-5 text-[#38BDF8]" />
                </div>
                <div className="theme-radio-indicator">
                  {theme === 'dark' && <Check className="h-3 w-3 stroke-[3]" />}
                </div>
              </div>
              <div>
                <h3 className="theme-card-title">Dark Mode (Judicial Navy)</h3>
                <p className="theme-card-desc">
                  Deep navy `#11486B` and slate tones to reduce eye strain during intensive precedent review and late-night case research.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ==================================================================
            Section 2: Judicial Reading Font Size (Three Options)
            ================================================================== */}
        <div className="settings-section-card">
          <div className="settings-section-header">
            <h2 className="settings-section-title">
              <Type className="h-4 w-4 text-[#FFA425]" />
              <span>Judicial Typography &amp; Text Scale</span>
            </h2>
            <p className="settings-section-subtitle">
              Adjust base typography scale across case dossiers, judgments, statutory citations, and AI holding analyses. Select one of three options below.
            </p>
          </div>

          <div className="font-options-grid">
            {/* Option 1: Standard (16px) */}
            <div
              className={`font-card ${fontSize === 'normal' ? 'active' : ''}`}
              onClick={() => handleFontSizeChange('normal')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleFontSizeChange('normal')}
            >
              <div className="font-card-top">
                <span className="font-preview-insignia" style={{ fontSize: '1rem' }}>
                  Aa
                </span>
                <span className="font-scale-badge">16px • 100%</span>
              </div>
              <div>
                <h3 className="font-card-title">1. Standard</h3>
                <p className="font-card-desc">
                  Default balanced interface scale. Optimal for general navigation and standard laptop screens.
                </p>
              </div>
            </div>

            {/* Option 2: Medium (18px) */}
            <div
              className={`font-card ${fontSize === 'medium' ? 'active' : ''}`}
              onClick={() => handleFontSizeChange('medium')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleFontSizeChange('medium')}
            >
              <div className="font-card-top">
                <span className="font-preview-insignia" style={{ fontSize: '1.25rem' }}>
                  Aa
                </span>
                <span className="font-scale-badge">18px • 112%</span>
              </div>
              <div>
                <h3 className="font-card-title">2. Medium (Enhanced)</h3>
                <p className="font-card-desc">
                  Increased legibility for reading dense statutory provisions, deposition transcripts, and legal citations.
                </p>
              </div>
            </div>

            {/* Option 3: Large (20px) */}
            <div
              className={`font-card ${fontSize === 'large' ? 'active' : ''}`}
              onClick={() => handleFontSizeChange('large')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleFontSizeChange('large')}
            >
              <div className="font-card-top">
                <span className="font-preview-insignia" style={{ fontSize: '1.5rem' }}>
                  Aa
                </span>
                <span className="font-scale-badge">20px • 125%</span>
              </div>
              <div>
                <h3 className="font-card-title">3. Large (High Legibility)</h3>
                <p className="font-card-desc">
                  Magnified typography tailored for extensive reading of Supreme Court judgment dossiers and bench orders.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ==================================================================
            Section 3: Live Interactive Preview
            ================================================================== */}
        <div className="settings-section-card">
          <div className="settings-section-header">
            <h2 className="settings-section-title">
              <Eye className="h-4 w-4 text-[#FFA425]" />
              <span>Live Precedent Dossier Preview</span>
            </h2>
            <p className="settings-section-subtitle">
              Interactive preview illustrating how judgments and evidence quotes render with your selected theme ({theme.toUpperCase()}) and font scale ({fontSizeConfig.label} - {fontSizeConfig.badge}).
            </p>
          </div>

          <div className="settings-preview-box">
            <div className="settings-preview-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText className="h-4 w-4 text-[#FFA425]" />
                <h3 className="settings-preview-title">
                  Pradeep v. State of Haryana (2023 INSC 599)
                </h3>
              </div>
              <span className="settings-preview-pill">
                ✓ 94% Relevance Match
              </span>
            </div>

            <p className="settings-preview-snippet">
              &ldquo;...testimony of child witness – Sole basis of conviction – When not proper – Appellant along with co-accused convicted under s. 302/34, IPC based on PW-1 minor deposition...&rdquo;
            </p>

            <div className="settings-preview-footer">
              <span>Supreme Court of India</span>
              <span>•</span>
              <span>Coram: Hon&rsquo;ble Justice Abhay S. Oka</span>
              <span>•</span>
              <span style={{ color: 'var(--accent-gold)', fontWeight: 600 }}>Active Scale: {fontSizeConfig.scale}</span>
            </div>
          </div>
        </div>

        {/* Footer Reset Action */}
        <div className="settings-footer">
          <div className="settings-status-note">
            <Sparkles className="h-3.5 w-3.5 text-[#FFA425]" />
            <span>Preferences are automatically saved to your browser session.</span>
          </div>

          <button
            type="button"
            onClick={handleReset}
            className="settings-btn-reset"
            title="Reset theme and font size"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Restore Default Preferences</span>
          </button>
        </div>
      </div>
    </AppLayout>
  );
}
