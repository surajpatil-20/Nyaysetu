import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Mail, AlertCircle, CheckCircle2, RotateCcw, ArrowRight, Terminal } from 'lucide-react';
import './AuthPages.css';

export default function VerifyOtpPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { verifyOtp, resendOtp } = useAuth();

  const initialEmail = location.state?.email || '';
  const [email, setEmail] = useState(initialEmail);
  const [isEditingEmail, setIsEditingEmail] = useState(!initialEmail);

  // 6 digits state
  const [digits, setDigits] = useState(['', '', '', '', '', '']);
  const inputRefs = useRef([]);

  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // 5-minute expiry countdown (300 seconds)
  const [timeLeft, setTimeLeft] = useState(300);

  // 30-second resend cooldown
  const [cooldown, setCooldown] = useState(30);

  useEffect(() => {
    // 5-minute countdown timer
    if (timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => Math.max(prev - 1, 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  useEffect(() => {
    // 30-second cooldown timer for Resend button
    if (cooldown <= 0) return;
    const timer = setInterval(() => {
      setCooldown((prev) => Math.max(prev - 1, 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleDigitChange = (index, value) => {
    if (!/^\d*$/.test(value)) return;

    const newDigits = [...digits];
    newDigits[index] = value.slice(-1);
    setDigits(newDigits);
    setError('');

    // Auto-advance to next box if filled
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').trim();
    if (/^\d{6}$/.test(pasted)) {
      const newDigits = pasted.split('');
      setDigits(newDigits);
      inputRefs.current[5]?.focus();
    }
  };

  const handleVerify = async (e) => {
    if (e) e.preventDefault();
    const fullOtp = digits.join('');
    if (fullOtp.length !== 6) {
      setError('Please enter the complete 6-digit OTP code.');
      return;
    }
    if (!email.trim()) {
      setError('Please provide the email address used for registration.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMsg('');

    try {
      await verifyOtp(email.trim(), fullOtp);
      navigate('/login', {
        state: { message: 'Account verified successfully. Please log in.' },
        replace: true,
      });
    } catch (err) {
      setError(err.message || 'OTP verification failed. Please check the code.');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (cooldown > 0 || resending) return;
    if (!email.trim()) {
      setError('Please provide the email address to resend the OTP.');
      return;
    }

    setResending(true);
    setError('');
    setSuccessMsg('');

    try {
      await resendOtp(email.trim());
      setSuccessMsg('A new 6-digit OTP has been generated. Check your backend terminal.');
      setCooldown(30);
      setTimeLeft(300);
      setDigits(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } catch (err) {
      setError(err.message || 'Failed to resend OTP. Please try again.');
    } finally {
      setResending(false);
    }
  };

  const isExpired = timeLeft === 0;

  return (
    <div className="auth-page-container">
      <div className="auth-card">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-brand-icon-box">
            <ShieldCheck className="h-7 w-7" />
          </div>
          <h2 className="auth-title">Verify Your Email</h2>
          <p className="auth-subtitle">
            Enter the 6-digit verification code sent to your email.
          </p>
        </div>

        {/* Email verification target */}
        <div style={{ backgroundColor: '#f8fafc', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '0.75rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0 }}>
            <Mail className="h-4 w-4 text-slate-400 shrink-0" />
            {isEditingEmail ? (
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="citizen@example.com"
                style={{ backgroundColor: '#ffffff', border: '1px solid var(--border-medium)', borderRadius: 'var(--radius-xs)', padding: '0.25rem 0.5rem', fontSize: '0.75rem', color: 'var(--text-primary)', outline: 'none' }}
              />
            ) : (
              <span style={{ fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {email || 'No email provided'}
              </span>
            )}
          </div>
          <button
            type="button"
            onClick={() => setIsEditingEmail(!isEditingEmail)}
            style={{ fontSize: '0.6875rem', color: 'var(--primary-navy)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 700 }}
          >
            {isEditingEmail ? 'Done' : 'Change'}
          </button>
        </div>

        {/* Terminal Hint Banner */}
        <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 'var(--radius-md)', padding: '0.75rem', fontSize: '0.6875rem', color: '#1e3a8a', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
          <Terminal className="h-4 w-4 text-blue-600 shrink-0 mt-0.5" />
          <div style={{ lineHeight: 1.4 }}>
            <strong>Development Notice:</strong> View the 6-digit OTP printed in your Django backend terminal.
          </div>
        </div>

        {/* Notifications */}
        {error && (
          <div className="auth-banner-error">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="auth-banner-success">
            <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5 text-emerald-600" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* 6-Digit Boxes Form */}
        <form onSubmit={handleVerify} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="otp-inputs-grid" onPaste={handlePaste}>
            {digits.map((digit, idx) => (
              <input
                key={idx}
                ref={(el) => (inputRefs.current[idx] = el)}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleDigitChange(idx, e.target.value)}
                onKeyDown={(e) => handleKeyDown(idx, e)}
                disabled={loading || isExpired}
                className="otp-box-input"
              />
            ))}
          </div>

          {/* Expiry Countdown */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>
              Code expires in:{' '}
              <span style={{ fontFamily: 'monospace', fontWeight: 700, color: isExpired ? '#dc2626' : 'var(--text-primary)' }}>
                {formatTime(timeLeft)}
              </span>
            </span>

            {isExpired && (
              <span style={{ fontSize: '0.6875rem', color: '#dc2626', fontWeight: 700 }}>
                OTP Expired
              </span>
            )}
          </div>

          {/* Verify Button */}
          <button
            type="submit"
            disabled={loading || isExpired || digits.join('').length !== 6}
            className="auth-submit-btn"
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.375rem' }}
          >
            <span>{loading ? 'Verifying OTP...' : 'Verify OTP'}</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        {/* Resend OTP Button with Cooldown */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #f1f5f9', paddingTop: '0.875rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span>Didn&rsquo;t receive the code?</span>
          <button
            type="button"
            onClick={handleResend}
            disabled={cooldown > 0 || resending}
            style={{ color: cooldown > 0 ? '#94a3b8' : 'var(--primary-navy)', background: 'none', border: 'none', cursor: cooldown > 0 ? 'not-allowed' : 'pointer', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}
          >
            <RotateCcw className={`h-3.5 w-3.5 ${resending ? 'animate-spin' : ''}`} />
            <span>
              {resending
                ? 'Sending...'
                : cooldown > 0
                ? `Resend in ${cooldown}s`
                : 'Resend OTP'}
            </span>
          </button>
        </div>

        <p className="auth-footer-text">
          <Link to="/login" className="auth-footer-link">
            Back to Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
