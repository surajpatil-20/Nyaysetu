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
    // Take the last character typed
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
      // Focus previous input on backspace
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
      // Navigate to login with success flash message
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
      // Reset cooldown and timer
      setCooldown(30);
      setTimeLeft(300);
      // Clear entered digits
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
    <div className="min-h-[calc(100vh-140px)] flex items-center justify-center px-4 py-12 bg-[#F8FAFC]">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-sm border border-slate-200 p-8 space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 bg-[#0A192F] rounded-xl text-blue-400 shadow-xs">
            <ShieldCheck className="h-7 w-7" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Verify Your Email</h2>
          <p className="text-xs text-slate-500">
            Enter the 6-digit verification code sent to your email.
          </p>
        </div>

        {/* Email verification target */}
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2 min-w-0">
            <Mail className="h-4 w-4 text-slate-400 flex-shrink-0" />
            {isEditingEmail ? (
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="citizen@example.com"
                className="bg-white border border-slate-300 rounded px-2 py-1 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            ) : (
              <span className="font-semibold text-slate-800 truncate">{email || 'No email provided'}</span>
            )}
          </div>
          <button
            type="button"
            onClick={() => setIsEditingEmail(!isEditingEmail)}
            className="text-[11px] text-blue-600 hover:underline font-semibold ml-2 flex-shrink-0"
          >
            {isEditingEmail ? 'Done' : 'Change'}
          </button>
        </div>

        {/* Terminal Hint Banner */}
        <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-3 text-xs text-blue-900 flex items-start space-x-2.5">
          <Terminal className="h-4 w-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="leading-relaxed text-[11px]">
            <strong>Development Notice:</strong> View the 6-digit OTP printed in your Django backend terminal.
          </div>
        </div>

        {/* Notifications */}
        {error && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-3.5 text-rose-800 text-xs flex items-start space-x-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3.5 text-emerald-800 text-xs flex items-start space-x-2">
            <CheckCircle2 className="h-4 w-4 flex-shrink-0 mt-0.5 text-emerald-600" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* 6-Digit Boxes Form */}
        <form onSubmit={handleVerify} className="space-y-5">
          <div className="flex justify-between gap-2 on-paste" onPaste={handlePaste}>
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
                className="w-12 h-14 text-center text-xl font-bold font-mono rounded-xl border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-2xs transition disabled:bg-slate-100 disabled:text-slate-400"
              />
            ))}
          </div>

          {/* Expiry Countdown */}
          <div className="flex items-center justify-between text-xs pt-1">
            <span className="text-slate-500">
              Code expires in:{' '}
              <span className={`font-mono font-bold ${isExpired ? 'text-rose-600' : 'text-slate-800'}`}>
                {formatTime(timeLeft)}
              </span>
            </span>

            {isExpired && (
              <span className="text-[11px] text-rose-600 font-semibold">
                OTP Expired
              </span>
            )}
          </div>

          {/* Verify Button */}
          <button
            type="submit"
            disabled={loading || isExpired || digits.join('').length !== 6}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-xs transition flex items-center justify-center space-x-1.5 disabled:opacity-50"
          >
            <span>{loading ? 'Verifying OTP...' : 'Verify OTP'}</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        {/* Resend OTP Button with Cooldown */}
        <div className="pt-2 text-center text-xs text-slate-500 border-t border-slate-100 flex items-center justify-between">
          <span>Didn&rsquo;t receive the code?</span>
          <button
            type="button"
            onClick={handleResend}
            disabled={cooldown > 0 || resending}
            className="text-blue-600 font-semibold hover:underline disabled:text-slate-400 disabled:no-underline flex items-center space-x-1 transition"
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

        <div className="text-center text-xs text-slate-500">
          <Link to="/login" className="text-slate-600 hover:underline">
            Back to Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}

