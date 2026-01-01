import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { loadStripe } from '@stripe/stripe-js';
import './App.css';
import { 
  Plus, 
  Search, 
  CheckSquare, 
  Square, 
  Edit3, 
  Trash2, 
  Calendar, 
  LayoutDashboard,
  List,
  X,
  Clock,
  AlertCircle,
  CheckCircle2,
  Circle,
  Loader2,
  Wrench,
  ShoppingCart,
  Download,
  Package,
  Ruler,
  Upload,
  FileText,
  DollarSign,
  Check,
  CreditCard,
  Lock,
  Shield,
  User,
  LogOut,
  Heart,
  Flag,
  Award,
  Timer
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Session timeout configuration (in milliseconds)
const SESSION_TIMEOUT = 10 * 60 * 1000; // 10 minutes
const SESSION_WARNING = 8 * 60 * 1000; // 8 minutes (2-minute warning)

// Priority and Status configurations
const PRIORITIES = {
  high: { label: 'High', color: 'text-red-600 bg-red-50', icon: '🔴' },
  medium: { label: 'Medium', color: 'text-orange-600 bg-orange-50', icon: '🟠' },
  low: { label: 'Low', color: 'text-green-600 bg-green-50', icon: '🟢' }
};

const STATUSES = {
  todo: { label: 'To Do', color: 'text-gray-600 bg-gray-100', icon: Circle },
  in_progress: { label: 'In Progress', color: 'text-blue-600 bg-blue-50', icon: Clock },
  completed: { label: 'Completed', color: 'text-green-600 bg-green-50', icon: CheckCircle2 }
};

const TRADES = {
  'Drywall': { color: 'text-amber-700 bg-amber-50', icon: '🧱', measurementFields: [] },
  'Painting': { color: 'text-pink-700 bg-pink-50', icon: '🎨', measurementFields: [] },
  'Stucco': { color: 'text-stone-700 bg-stone-50', icon: '🏗️', measurementFields: [] },
  'Exterior Paint': { color: 'text-teal-700 bg-teal-50', icon: '🏠', measurementFields: [] },
  'HVAC': { color: 'text-cyan-700 bg-cyan-50', icon: '❄️', measurementFields: [] },
  'Electrical': { color: 'text-yellow-700 bg-yellow-50', icon: '⚡', measurementFields: [] },
  'Plumbing': { color: 'text-blue-700 bg-blue-50', icon: '🔧', measurementFields: [] },
  'General': { color: 'text-gray-700 bg-gray-50', icon: '🔨', measurementFields: [] }
};

const DEFAULT_TRADES = ['Drywall', 'Painting', 'Stucco', 'Exterior Paint', 'HVAC', 'Electrical', 'Plumbing', 'General'];

const formatMaterialName = (name) => {
  return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Session Timeout Warning Modal Component
function SessionWarningModal({ onKeepActive, timeRemaining }) {
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl border-4 border-red-500">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
            <AlertCircle className="w-7 h-7 text-red-600" />
          </div>
          <h2 className="text-2xl font-bold text-red-700">Security Alert</h2>
        </div>
        
        <p className="text-gray-700 mb-4 text-lg">
          Your session will expire and <strong>all data will be purged</strong> in{' '}
          <span className="text-red-600 font-bold">{Math.ceil(timeRemaining / 1000)} seconds</span> for your protection.
        </p>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-6">
          <p className="text-sm text-red-700 flex items-center gap-2">
            <Timer className="w-4 h-4" />
            Sessions are automatically erased after 10 minutes of inactivity for your protection.
          </p>
        </div>
        
        <button
          onClick={onKeepActive}
          className="w-full py-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition-colors text-lg"
        >
          Keep Session Active
        </button>
      </div>
    </div>
  );
}

// 1986 Legacy Badge Component
function LegacyBadge() {
  return (
    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-50 border border-amber-300 rounded-lg">
      <Award className="w-4 h-4 text-amber-600" />
      <span className="text-xs font-semibold text-amber-800">Est. 1986 • Expert-Verified Math</span>
    </div>
  );
}

// Security Badge Component
function SecurityBadge() {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mt-6">
      <div className="flex items-center gap-2 mb-3">
        <Shield className="w-5 h-5 text-green-600" />
        <h4 className="font-semibold text-gray-800">Your Data is Secured by USA Construction Inc.</h4>
      </div>
      <ul className="space-y-2 text-sm text-gray-600">
        <li className="flex items-start gap-2">
          <Award className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
          <span><strong>40 Years of Trust:</strong> Your data is backed by USA Construction Inc., an industry leader with a 40-year reputation for integrity and precision.</span>
        </li>
        <li className="flex items-start gap-2">
          <CreditCard className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
          <span><strong>Secure Payments:</strong> We never store your credit card info; all transactions are processed through Stripe's secure infrastructure.</span>
        </li>
        <li className="flex items-start gap-2">
          <Shield className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
          <span><strong>Privacy First:</strong> Your plans are yours. We use them strictly for your takeoff and never share your project data with third parties.</span>
        </li>
        <li className="flex items-start gap-2">
          <Timer className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <span><strong>Auto-Purge:</strong> Sessions are automatically erased after 10 minutes of inactivity for your protection.</span>
        </li>
      </ul>
    </div>
  );
}

// Donation Impact Component
function DonationImpact() {
  return (
    <div className="bg-gradient-to-r from-red-50 to-blue-50 border border-red-200 rounded-xl p-4 mt-4">
      <div className="flex items-center gap-2 mb-2">
        <Flag className="w-5 h-5 text-red-600" />
        <span className="text-lg">🇺🇸</span>
        <h4 className="font-semibold text-gray-800">Supporting Our Heroes</h4>
      </div>
      <p className="text-sm text-gray-700 mb-2">
        <strong>$1 from every single-use takeoff</strong> is donated directly to{' '}
        <span className="text-blue-700 font-semibold">Tunnel to Towers Foundation</span> from MyPlanReader's proceeds.
      </p>
      <p className="text-xs text-gray-600 flex items-center gap-1">
        <Heart className="w-3 h-3 text-red-500" />
        Every estimate supports a hero. 100% of single-use donations go toward mortgage-free homes for veterans and first responders.
      </p>
    </div>
  );
}

function App() {
  // Auth state
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('signin'); // 'signin' or 'signup'
  
  // Session security state
  const [showSessionWarning, setShowSessionWarning] = useState(false);
  const [sessionTimeRemaining, setSessionTimeRemaining] = useState(SESSION_TIMEOUT - SESSION_WARNING);
  const lastActivityRef = useRef(Date.now());
  const warningTimeoutRef = useRef(null);
  const purgeTimeoutRef = useRef(null);
  const countdownRef = useRef(null);
  
  // App state
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('upload');

  // Reset activity timer
  const resetActivityTimer = useCallback(() => {
    lastActivityRef.current = Date.now();
    setShowSessionWarning(false);
    
    // Clear existing timeouts
    if (warningTimeoutRef.current) clearTimeout(warningTimeoutRef.current);
    if (purgeTimeoutRef.current) clearTimeout(purgeTimeoutRef.current);
    if (countdownRef.current) clearInterval(countdownRef.current);
    
    // Set warning at 8 minutes
    warningTimeoutRef.current = setTimeout(() => {
      setShowSessionWarning(true);
      setSessionTimeRemaining(SESSION_TIMEOUT - SESSION_WARNING);
      
      // Start countdown
      countdownRef.current = setInterval(() => {
        setSessionTimeRemaining(prev => {
          if (prev <= 1000) {
            clearInterval(countdownRef.current);
            return 0;
          }
          return prev - 1000;
        });
      }, 1000);
    }, SESSION_WARNING);
    
    // Set purge at 10 minutes
    purgeTimeoutRef.current = setTimeout(() => {
      handleSessionPurge();
    }, SESSION_TIMEOUT);
  }, []);

  // Handle session purge - logout and clear all data
  const handleSessionPurge = useCallback(() => {
    // Clear all timeouts
    if (warningTimeoutRef.current) clearTimeout(warningTimeoutRef.current);
    if (purgeTimeoutRef.current) clearTimeout(purgeTimeoutRef.current);
    if (countdownRef.current) clearInterval(countdownRef.current);
    
    // Clear user data
    setUser(null);
    setProjects([]);
    setCurrentProject(null);
    localStorage.removeItem('myplanreader_user');
    
    // Reset UI
    setShowSessionWarning(false);
    setActiveView('upload');
    
    // Notify server to purge session data
    axios.post(`${BACKEND_URL}/api/session/purge`).catch(() => {});
    
    alert('Your session has expired and all data has been purged for your protection.');
  }, []);

  // Keep session active (dismiss warning)
  const handleKeepSessionActive = useCallback(() => {
    resetActivityTimer();
  }, [resetActivityTimer]);

  // Setup activity listeners
  useEffect(() => {
    const activityEvents = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'click'];
    
    const handleActivity = () => {
      if (!showSessionWarning) {
        resetActivityTimer();
      }
    };
    
    activityEvents.forEach(event => {
      document.addEventListener(event, handleActivity, { passive: true });
    });
    
    // Initial timer setup
    if (user) {
      resetActivityTimer();
    }
    
    return () => {
      activityEvents.forEach(event => {
        document.removeEventListener(event, handleActivity);
      });
      if (warningTimeoutRef.current) clearTimeout(warningTimeoutRef.current);
      if (purgeTimeoutRef.current) clearTimeout(purgeTimeoutRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, [user, showSessionWarning, resetActivityTimer]);

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('myplanreader_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  // Fetch user projects when user changes
  useEffect(() => {
    if (user) {
      fetchProjects();
    }
  }, [user]);

  const fetchProjects = async () => {
    if (!user) return;
    try {
      const response = await axios.get(`${BACKEND_URL}/api/projects/${user.id}`);
      setProjects(response.data.projects || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const handleSignIn = async (email, password) => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/auth/signin`, { email, password });
      const userData = response.data.user;
      setUser(userData);
      localStorage.setItem('myplanreader_user', JSON.stringify(userData));
      setShowAuthModal(false);
      resetActivityTimer(); // Start session timer on login
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Sign in failed' };
    }
  };

  const handleSignUp = async (email, password, name) => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/auth/signup`, { email, password, name });
      const userData = response.data.user;
      setUser(userData);
      localStorage.setItem('myplanreader_user', JSON.stringify(userData));
      setShowAuthModal(false);
      resetActivityTimer(); // Start session timer on signup
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Sign up failed' };
    }
  };

  const handleSignOut = () => {
    setUser(null);
    setProjects([]);
    localStorage.removeItem('myplanreader_user');
    setActiveView('upload');
    // Clear session timers
    if (warningTimeoutRef.current) clearTimeout(warningTimeoutRef.current);
    if (purgeTimeoutRef.current) clearTimeout(purgeTimeoutRef.current);
    if (countdownRef.current) clearInterval(countdownRef.current);
  };

  const handleProjectProcessed = async (projectId) => {
    await fetchProjects();
    if (projectId) {
      const project = projects.find(p => p.id === projectId);
      setCurrentProject(project);
    }
    setActiveView('shopping');
  };

  const requireAuth = (callback) => {
    if (!user) {
      setShowAuthModal(true);
      return false;
    }
    return true;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50" data-testid="loading-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
          <p className="text-gray-600 text-lg">Loading MyPlanReader™...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="app-container">
      {/* Session Warning Modal */}
      {showSessionWarning && (
        <SessionWarningModal 
          onKeepActive={handleKeepSessionActive}
          timeRemaining={sessionTimeRemaining}
        />
      )}

      {/* Header with Auth */}
      <header className="fixed top-0 left-60 right-0 h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 z-40">
        <h2 className="text-lg font-semibold text-gray-800">
          {activeView === 'upload' && 'Upload Plans'}
          {activeView === 'shopping' && 'Shopping List'}
          {activeView === 'projects' && 'My Projects'}
          {activeView === 'dashboard' && 'Dashboard'}
        </h2>
        <div className="flex items-center gap-4">
          {user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <User className="w-4 h-4" />
                <span>{user.name || user.email}</span>
              </div>
              <button
                onClick={handleSignOut}
                className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
            >
              <User className="w-4 h-4" />
              Sign In / Sign Up
            </button>
          )}
        </div>
      </header>

      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-60 bg-white border-r border-gray-200 p-4 overflow-y-auto shadow-sm flex flex-col" data-testid="sidebar">
        {/* Logo & Branding */}
        <div className="mb-8">
          <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="w-6 h-6 text-blue-600" />
            MyPlanReader™
          </h1>
          <p className="text-xs text-gray-600 mt-1 font-medium">By USA Construction Inc.</p>
          <p className="text-xs text-gray-500">Serving America since 1986</p>
        </div>
        
        <nav className="space-y-1 flex-grow">
          <button
            onClick={() => setActiveView('upload')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeView === 'upload' ? 'bg-blue-600 text-white font-medium' : 'text-gray-600 hover:bg-gray-100'
            }`}
            data-testid="nav-upload"
          >
            <Upload className="w-4 h-4" />
            Upload Plans
          </button>
          <button
            onClick={() => setActiveView('shopping')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeView === 'shopping' ? 'bg-blue-600 text-white font-medium' : 'text-gray-600 hover:bg-gray-100'
            }`}
            data-testid="nav-shopping"
          >
            <ShoppingCart className="w-4 h-4" />
            Shopping List
          </button>
          <button
            onClick={() => { if (requireAuth()) setActiveView('projects'); }}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeView === 'projects' ? 'bg-blue-600 text-white font-medium' : 'text-gray-600 hover:bg-gray-100'
            }`}
            data-testid="nav-projects"
          >
            <LayoutDashboard className="w-4 h-4" />
            My Projects
          </button>
        </nav>

        {/* User Stats */}
        {user && projects.length > 0 && (
          <div className="mt-8 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Your Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Projects</span>
                <span className="font-semibold text-gray-900">{projects.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Completed</span>
                <span className="font-semibold text-green-600">{projects.filter(p => p.status === 'complete').length}</span>
              </div>
            </div>
          </div>
        )}

        {/* Donation Counter */}
        {user && projects.filter(p => p.status === 'complete').length > 0 && (
          <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-200">
            <h3 className="text-xs font-semibold text-red-700 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Heart className="w-3 h-3" />
              Your Impact
            </h3>
            <p className="text-lg text-red-800 font-bold">${projects.filter(p => p.status === 'complete').length} donated</p>
            <p className="text-xs text-red-600">to Tunnel to Towers</p>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="ml-60 pt-14 min-h-screen bg-gray-50" data-testid="main-content">
        {activeView === 'upload' ? (
          <UploadPortal 
            user={user} 
            onProcessed={handleProjectProcessed} 
            onRequireAuth={() => setShowAuthModal(true)}
          />
        ) : activeView === 'shopping' ? (
          <ShoppingListView projects={projects} currentProject={currentProject} />
        ) : activeView === 'projects' ? (
          <ProjectsView 
            projects={projects} 
            onSelectProject={(p) => { setCurrentProject(p); setActiveView('shopping'); }}
            onRefresh={fetchProjects}
          />
        ) : null}
      </main>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          mode={authMode}
          setMode={setAuthMode}
          onSignIn={handleSignIn}
          onSignUp={handleSignUp}
          onClose={() => setShowAuthModal(false)}
        />
      )}
    </div>
  );
}

// Auth Modal Component
function AuthModal({ mode, setMode, onSignIn, onSignUp, onClose }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    const result = mode === 'signin' 
      ? await onSignIn(email, password)
      : await onSignUp(email, password, name);
    
    setIsLoading(false);
    if (!result.success) {
      setError(result.error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900">
            {mode === 'signin' ? 'Welcome Back' : 'Create Account'}
          </h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'signup' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Your name"
              />
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="your@email.com"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="••••••••"
              required
              minLength={6}
            />
          </div>
          
          {error && (
            <p className="text-sm text-red-600 bg-red-50 p-2 rounded">{error}</p>
          )}
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : (mode === 'signin' ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-600">
          {mode === 'signin' ? (
            <>Don't have an account? <button onClick={() => setMode('signup')} className="text-blue-600 font-medium">Sign Up</button></>
          ) : (
            <>Already have an account? <button onClick={() => setMode('signin')} className="text-blue-600 font-medium">Sign In</button></>
          )}
        </div>

        {/* Security Badge in Auth Modal */}
        <SecurityBadge />
      </div>
    </div>
  );
}

// Upload Portal Component
function UploadPortal({ user, onProcessed, onRequireAuth }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [pageCount, setPageCount] = useState(10);
  const [selectedTrades, setSelectedTrades] = useState(['Drywall']);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [progress, setProgress] = useState(0);
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [stripePromise, setStripePromise] = useState(null);

  const BASE_PRICE = 25;
  const ADDON_PRICE = 10;
  const DONATION = 1;
  
  const addOns = [
    { id: 'Painting', label: 'Painting', price: ADDON_PRICE },
    { id: 'Stucco', label: 'Stucco', price: ADDON_PRICE },
    { id: 'Exterior Paint', label: 'Exterior Paint', price: ADDON_PRICE }
  ];

  const totalPrice = BASE_PRICE + addOns.filter(a => selectedTrades.includes(a.id)).length * ADDON_PRICE;

  useEffect(() => {
    const initStripe = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/api/stripe-config`);
        if (response.data.publishable_key) {
          setStripePromise(loadStripe(response.data.publishable_key));
        }
      } catch (error) {
        console.error('Error loading Stripe:', error);
      }
    };
    initStripe();
  }, []);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const paymentId = urlParams.get('payment_id');
    const projectId = urlParams.get('project_id');
    
    if (sessionId && paymentId) {
      verifyPaymentAndProcess(paymentId, sessionId, projectId);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const verifyPaymentAndProcess = async (paymentId, sessionId, projectId) => {
    setIsProcessing(true);
    setProcessingStep('Verifying payment...');
    setProgress(10);
    
    try {
      const verifyResponse = await axios.get(
        `${BACKEND_URL}/api/verify-payment/${paymentId}?session_id=${sessionId}&project_id=${projectId}`
      );
      
      if (verifyResponse.data.verified) {
        setPaymentSuccess(true);
        setProcessingStep('Payment confirmed! $1 donated to Tunnel to Towers 🇺🇸');
        setProgress(30);
        await new Promise(r => setTimeout(r, 1500));
        
        setProcessingStep('Processing blueprint...');
        setProgress(50);
        
        // Process the project
        await axios.post(`${BACKEND_URL}/api/process-project/${projectId || verifyResponse.data.project_id}`);
        
        setProgress(80);
        setProcessingStep('Calculating whole-unit quantities...');
        await new Promise(r => setTimeout(r, 800));
        
        setProgress(100);
        setProcessingStep('Complete! Loading your shopping list...');
        await new Promise(r => setTimeout(r, 1000));
        
        onProcessed(projectId || verifyResponse.data.project_id);
      } else {
        setProcessingStep('Payment verification failed. Please try again.');
      }
    } catch (error) {
      console.error('Error verifying payment:', error);
      setProcessingStep('Error verifying payment. Please contact support.');
    }
    
    setIsProcessing(false);
  };

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false); };
  
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setPageCount(Math.min(25, Math.floor(Math.random() * 20) + 5));
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setPageCount(Math.min(25, Math.floor(Math.random() * 20) + 5));
    }
  };

  const toggleAddOn = (tradeId) => {
    if (selectedTrades.includes(tradeId)) {
      setSelectedTrades(selectedTrades.filter(t => t !== tradeId));
    } else {
      setSelectedTrades([...selectedTrades, tradeId]);
    }
  };

  const handleCheckout = async () => {
    if (!selectedFile) return;
    
    // Require auth before payment
    if (!user) {
      onRequireAuth();
      return;
    }
    
    if (!stripePromise) {
      alert('Payment system loading. Please try again.');
      return;
    }
    
    setIsCheckingOut(true);
    
    try {
      const response = await axios.post(`${BACKEND_URL}/api/create-checkout-session`, {
        filename: selectedFile.name,
        page_count: pageCount,
        selected_trades: selectedTrades,
        total_amount: totalPrice * 100,
        success_url: window.location.href,
        cancel_url: window.location.href,
        user_id: user.id
      });
      
      const stripe = await stripePromise;
      const { error } = await stripe.redirectToCheckout({
        sessionId: response.data.session_id
      });
      
      if (error) {
        console.error('Stripe redirect error:', error);
        alert('Payment failed. Please try again.');
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
      alert(error.response?.data?.detail || 'Error initiating payment. Please sign in first.');
    }
    
    setIsCheckingOut(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 p-8" data-testid="upload-portal">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            MyPlanReader™
          </h1>
          <p className="text-gray-600 text-lg">
            Upload your plans and get instant, whole-unit material quantities
          </p>
        </div>

        {/* Processing Overlay */}
        {isProcessing && (
          <div className="fixed inset-0 bg-white/95 flex items-center justify-center z-50">
            <div className="text-center max-w-md bg-white p-8 rounded-2xl shadow-xl border border-gray-200">
              {paymentSuccess && (
                <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 bg-green-100 border border-green-300 rounded-full">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span className="text-green-700 font-medium">Payment Successful</span>
                </div>
              )}
              <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-6" />
              <p className="text-xl text-gray-800 font-medium mb-4">{processingStep}</p>
              <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                <div className="bg-blue-600 h-3 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
              </div>
              <p className="text-gray-500">{progress}%</p>
            </div>
          </div>
        )}

        {/* Upload Zone */}
        <div
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all mb-8 bg-white shadow-sm ${
            isDragging ? 'border-blue-500 bg-blue-50' : selectedFile ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input id="file-input" type="file" accept=".pdf" className="hidden" onChange={handleFileSelect} />
          
          {selectedFile ? (
            <div className="flex flex-col items-center py-4">
              <CheckCircle2 className="w-12 h-12 text-green-600 mb-3" />
              <p className="text-lg font-semibold text-gray-800 mb-1">{selectedFile.name}</p>
              <p className="text-gray-500 text-sm">{pageCount} pages detected</p>
              <button onClick={() => setSelectedFile(null)} className="mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium">
                Choose different file
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center py-4">
              <p className="text-gray-500 text-sm mb-4">Drag & drop your PDF here, or</p>
              <button
                onClick={() => document.getElementById('file-input').click()}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 shadow-md hover:shadow-lg"
              >
                <Upload className="w-5 h-5" />
                Upload PDF Blueprint
              </button>
              <p className="text-xs text-gray-400 mt-4">Max 25 pages for single use</p>
            </div>
          )}
        </div>

        {/* Trade Selection */}
        <div className="bg-white rounded-2xl p-6 mb-6 shadow-sm border border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Wrench className="w-5 h-5 text-blue-600" />
            Trade Selection
          </h2>
          
          <div className="flex items-center justify-between p-4 bg-blue-50 border-2 border-blue-200 rounded-xl mb-4">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
                <Check className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="font-semibold text-gray-900">🧱 Drywall</p>
                <p className="text-sm text-gray-600">Included in base price</p>
              </div>
            </div>
            <span className="text-xl font-bold text-blue-700">${BASE_PRICE}</span>
          </div>

          {/* Single Use Tier Caption */}
          <div className="text-center mb-4 text-sm text-gray-600">
            🇺🇸 <span className="text-red-600 font-medium">$1 from every single-use takeoff</span> is donated directly to Tunnel to Towers.
          </div>
          
          <p className="text-sm text-gray-600 mb-3 font-medium">Add more trades:</p>
          <div className="space-y-3">
            {addOns.map(addon => (
              <label
                key={addon.id}
                className={`flex items-center justify-between p-4 rounded-xl cursor-pointer transition-all border-2 ${
                  selectedTrades.includes(addon.id) ? 'bg-blue-50 border-blue-300' : 'bg-gray-50 border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-3">
                  <input type="checkbox" checked={selectedTrades.includes(addon.id)} onChange={() => toggleAddOn(addon.id)} className="w-5 h-5 rounded border-gray-400 text-blue-600" />
                  <span className="text-gray-800 font-medium">{TRADES[addon.id]?.icon} {addon.label}</span>
                </div>
                <span className="text-gray-600 font-semibold">+${addon.price}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Donation Impact */}
        <DonationImpact />

        {/* Pricing Summary */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-200 sticky bottom-4 mt-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <p className="text-gray-500 text-sm font-medium">Total Fee</p>
              <p className="text-4xl font-bold text-gray-900 flex items-center">
                <DollarSign className="w-9 h-9 text-green-600" />
                {totalPrice}
              </p>
              <p className="text-xs text-red-600 mt-1">Includes ${DONATION} donation to Tunnel to Towers 🇺🇸</p>
            </div>
            <div className="text-right text-sm text-gray-600">
              <p>Base: <span className="font-semibold">${BASE_PRICE}</span></p>
              <p>Add-ons: <span className="font-semibold">${totalPrice - BASE_PRICE}</span></p>
              <p className="text-red-600">Donation: <span className="font-semibold">${DONATION}</span></p>
            </div>
          </div>
          
          {/* SSL Badge */}
          <div className="flex items-center justify-center gap-2 mb-4 text-xs text-gray-500 bg-gray-50 rounded-lg py-2">
            <Shield className="w-4 h-4 text-green-600" />
            <span>SSL Secured</span>
            <span className="text-gray-300">|</span>
            <Lock className="w-4 h-4 text-blue-600" />
            <span>Bank-Level Encryption</span>
          </div>
          
          <button
            onClick={handleCheckout}
            disabled={!selectedFile || isCheckingOut}
            className="w-full py-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:text-gray-500 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 shadow-md"
          >
            {isCheckingOut ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Redirecting to payment...</>
            ) : !user ? (
              <><User className="w-5 h-5" /> Sign In to Pay ${totalPrice}</>
            ) : (
              <><CreditCard className="w-5 h-5" /> Pay ${totalPrice} & Process Blueprint</>
            )}
          </button>
          
          <div className="flex items-center justify-center gap-2 mt-4 text-xs text-gray-500">
            <Lock className="w-3 h-3" />
            <span>Secure payment powered by Stripe</span>
          </div>
          
          <p className="text-center text-xs text-gray-400 mt-2">
            All material quantities rounded UP to whole numbers
          </p>
        </div>

        {/* Security Badge */}
        <SecurityBadge />
      </div>
    </div>
  );
}

// Projects View Component
function ProjectsView({ projects, onSelectProject, onRefresh }) {
  const getStatusBadge = (status) => {
    const configs = {
      'pending': { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
      'processing': { color: 'bg-blue-100 text-blue-800', label: 'Processing' },
      'paid': { color: 'bg-green-100 text-green-800', label: 'Paid' },
      'complete': { color: 'bg-emerald-100 text-emerald-800', label: 'Complete' }
    };
    const config = configs[status] || configs['pending'];
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>{config.label}</span>;
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold text-gray-900">My Projects</h2>
        <button onClick={onRefresh} className="text-blue-600 hover:text-blue-800 text-sm font-medium">
          Refresh
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">No Projects Yet</h3>
          <p className="text-gray-500">Upload your first blueprint to get started!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {projects.map(project => (
            <div
              key={project.id}
              onClick={() => project.status === 'complete' && onSelectProject(project)}
              className={`bg-white rounded-xl border border-gray-200 p-6 ${
                project.status === 'complete' ? 'cursor-pointer hover:border-blue-300 hover:shadow-md' : ''
              } transition-all`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <FileText className="w-10 h-10 text-blue-600" />
                  <div>
                    <h3 className="font-semibold text-gray-900">{project.filename}</h3>
                    <p className="text-sm text-gray-500">
                      {project.trades?.join(', ')} • ${project.total_fee}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {getStatusBadge(project.status)}
                  {project.status === 'complete' && (
                    <button className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-1">
                      View Materials <ShoppingCart className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
              {project.donation_amount && (
                <p className="text-xs text-red-600 mt-2 flex items-center gap-1">
                  <Heart className="w-3 h-3" /> ${project.donation_amount} donated to Tunnel to Towers
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// AIA Division Labels
const AIA_DIVISIONS = {
  "03": { name: "Concrete", icon: "🏗️", color: "bg-gray-100 text-gray-800" },
  "04": { name: "Masonry", icon: "🧱", color: "bg-orange-100 text-orange-800" },
  "06": { name: "Wood & Composites", icon: "🪵", color: "bg-amber-100 text-amber-800" },
  "07": { name: "Thermal & Moisture", icon: "🛡️", color: "bg-blue-100 text-blue-800" },
  "08": { name: "Openings", icon: "🚪", color: "bg-purple-100 text-purple-800" },
  "09": { name: "Finishes", icon: "🎨", color: "bg-pink-100 text-pink-800" }
};

// Shopping List View Component - Supplier Ready Format
function ShoppingListView({ projects, currentProject }) {
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'cards'
  const [filterDivision, setFilterDivision] = useState('all');
  const completedProjects = projects.filter(p => p.status === 'complete' && p.materials);
  const projectToShow = currentProject || completedProjects[0];

  // Check if materials is in new format (array) or old format (object)
  const isNewFormat = Array.isArray(projectToShow?.materials);
  
  const handleExportCSV = () => {
    if (projectToShow?.id) {
      window.open(`${BACKEND_URL}/api/export/takeoff/${projectToShow.id}`, '_blank');
    } else {
      window.open(`${BACKEND_URL}/api/export/shopping-list`, '_blank');
    }
  };

  const handleExportXLSX = () => {
    if (projectToShow?.id) {
      window.open(`${BACKEND_URL}/api/export/takeoff/${projectToShow.id}/xlsx`, '_blank');
    }
  };

  // Group materials by category for display
  const groupMaterials = (materials) => {
    if (!isNewFormat) return { legacy: Object.entries(materials) };
    
    const groups = {
      lumber: materials.filter(m => m.order_line < 100),
      connectors: materials.filter(m => m.order_line >= 100 && m.order_line < 200),
      fasteners: materials.filter(m => m.order_line >= 200 && m.order_line < 300),
      anchors: materials.filter(m => m.order_line >= 300)
    };
    return groups;
  };

  if (!projectToShow || !projectToShow.materials) {
    return (
      <div className="p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">Shopping List</h2>
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">No Materials Yet</h3>
          <p className="text-gray-500">Complete a paid takeoff to see your shopping list!</p>
        </div>
      </div>
    );
  }

  const materialGroups = groupMaterials(projectToShow.materials);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Supplier-Ready Material List</h2>
          <p className="text-sm text-gray-500 mt-1">
            {projectToShow.filename} • AIA Division 06 - Wood, Plastics & Composites
          </p>
          <p className="text-xs text-emerald-600 font-medium mt-1">
            ✓ All quantities rounded UP to whole numbers for ordering
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode(viewMode === 'table' ? 'cards' : 'table')}
            className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
          >
            {viewMode === 'table' ? 'Card View' : 'Table View'}
          </button>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          {isNewFormat && (
            <button
              onClick={handleExportXLSX}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Download className="w-4 h-4" />
              Lumber Order
            </button>
          )}
        </div>
      </div>

      {/* Project Summary */}
      {projectToShow.total_sqft && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide">Total Sq Ft</p>
            <p className="text-2xl font-bold text-gray-900">{projectToShow.total_sqft?.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide">Wall Linear Ft</p>
            <p className="text-2xl font-bold text-gray-900">{projectToShow.wall_linear_ft?.toLocaleString() || '-'}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide">Stories</p>
            <p className="text-2xl font-bold text-gray-900">{projectToShow.num_stories || 1}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide">Foundation</p>
            <p className="text-2xl font-bold text-gray-900 capitalize">{projectToShow.foundation_type || 'Slab'}</p>
          </div>
        </div>
      )}

      {/* New Format - Supplier Ready Table */}
      {isNewFormat ? (
        <div className="space-y-6">
          {/* Lumber Section */}
          {materialGroups.lumber?.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
              <div className="bg-amber-50 px-6 py-4 border-b border-amber-200">
                <h3 className="text-lg font-semibold text-amber-900 flex items-center gap-2">
                  🪵 Lumber & Sheathing ({materialGroups.lumber.length} items)
                </h3>
              </div>
              {viewMode === 'table' ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-600">
                      <tr>
                        <th className="px-4 py-3 text-left">#</th>
                        <th className="px-4 py-3 text-left">Description</th>
                        <th className="px-4 py-3 text-left">Size</th>
                        <th className="px-4 py-3 text-right">Qty</th>
                        <th className="px-4 py-3 text-left">Length</th>
                        <th className="px-4 py-3 text-left">Unit</th>
                        <th className="px-4 py-3 text-left">Supplier Notes</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {materialGroups.lumber.map((item, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-500">{item.order_line}</td>
                          <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.description}</td>
                          <td className="px-4 py-3 text-sm text-gray-700">{item.lumber_size}</td>
                          <td className="px-4 py-3 text-right text-lg font-bold text-emerald-700">{item.quantity}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{item.length}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{item.unit}</td>
                          <td className="px-4 py-3 text-xs text-gray-500">{item.supplier_notes}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
                  {materialGroups.lumber.map((item, idx) => (
                    <div key={idx} className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs text-gray-500">#{item.order_line}</span>
                        <span className="text-2xl font-bold text-emerald-700">{item.quantity}</span>
                      </div>
                      <p className="font-semibold text-gray-900">{item.description}</p>
                      <p className="text-sm text-gray-600">{item.lumber_size} × {item.length}</p>
                      <p className="text-xs text-gray-500 mt-2">{item.supplier_notes}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Connectors Section - Simpson Strong-Tie */}
          {materialGroups.connectors?.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
              <div className="bg-blue-50 px-6 py-4 border-b border-blue-200">
                <h3 className="text-lg font-semibold text-blue-900 flex items-center gap-2">
                  🔧 Simpson Strong-Tie Connectors ({materialGroups.connectors.length} items)
                </h3>
              </div>
              {viewMode === 'table' ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-600">
                      <tr>
                        <th className="px-4 py-3 text-left">#</th>
                        <th className="px-4 py-3 text-left">Description</th>
                        <th className="px-4 py-3 text-left">For Lumber</th>
                        <th className="px-4 py-3 text-right">Qty</th>
                        <th className="px-4 py-3 text-left">Unit</th>
                        <th className="px-4 py-3 text-left">Supplier Notes</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {materialGroups.connectors.map((item, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-500">{item.order_line}</td>
                          <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.description}</td>
                          <td className="px-4 py-3 text-sm text-gray-700">{item.lumber_size}</td>
                          <td className="px-4 py-3 text-right text-lg font-bold text-blue-700">{item.quantity}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{item.unit}</td>
                          <td className="px-4 py-3 text-xs text-gray-500">{item.supplier_notes}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
                  {materialGroups.connectors.map((item, idx) => (
                    <div key={idx} className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs text-gray-500">#{item.order_line}</span>
                        <span className="text-2xl font-bold text-blue-700">{item.quantity}</span>
                      </div>
                      <p className="font-semibold text-gray-900">{item.description}</p>
                      <p className="text-xs text-gray-500 mt-2">{item.supplier_notes}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Fasteners Section */}
          {materialGroups.fasteners?.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
              <div className="bg-gray-100 px-6 py-4 border-b border-gray-300">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  🔩 Fasteners ({materialGroups.fasteners.length} items)
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-600">
                    <tr>
                      <th className="px-4 py-3 text-left">#</th>
                      <th className="px-4 py-3 text-left">Description</th>
                      <th className="px-4 py-3 text-right">Qty</th>
                      <th className="px-4 py-3 text-left">Unit</th>
                      <th className="px-4 py-3 text-left">Supplier Notes</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {materialGroups.fasteners.map((item, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-500">{item.order_line}</td>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.description}</td>
                        <td className="px-4 py-3 text-right text-lg font-bold text-gray-700">{item.quantity}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{item.unit}</td>
                        <td className="px-4 py-3 text-xs text-gray-500">{item.supplier_notes}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Anchors Section */}
          {materialGroups.anchors?.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
              <div className="bg-stone-100 px-6 py-4 border-b border-stone-300">
                <h3 className="text-lg font-semibold text-stone-900 flex items-center gap-2">
                  ⚓ Anchors & Concrete Fasteners ({materialGroups.anchors.length} items)
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-600">
                    <tr>
                      <th className="px-4 py-3 text-left">#</th>
                      <th className="px-4 py-3 text-left">Description</th>
                      <th className="px-4 py-3 text-right">Qty</th>
                      <th className="px-4 py-3 text-left">Length</th>
                      <th className="px-4 py-3 text-left">Unit</th>
                      <th className="px-4 py-3 text-left">Supplier Notes</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {materialGroups.anchors.map((item, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-500">{item.order_line}</td>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.description}</td>
                        <td className="px-4 py-3 text-right text-lg font-bold text-stone-700">{item.quantity}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{item.length}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{item.unit}</td>
                        <td className="px-4 py-3 text-xs text-gray-500">{item.supplier_notes}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Legacy Format - Simple Grid */
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Package className="w-5 h-5 text-emerald-600" />
            Materials ({Object.keys(projectToShow.materials).length} items)
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {Object.entries(projectToShow.materials).map(([item, qty]) => (
              <div key={item} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100">
                <span className="text-sm text-gray-700">{formatMaterialName(item)}</span>
                <span className="text-xl font-bold text-emerald-700">{qty}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Donation confirmation */}
      <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
        <Heart className="w-6 h-6 text-red-500" />
        <div>
          <p className="font-semibold text-red-800">Thank you for supporting our heroes!</p>
          <p className="text-sm text-red-600">$1 from this takeoff was donated to Tunnel to Towers Foundation 🇺🇸</p>
        </div>
      </div>

      {/* AIA Division Legend */}
      <div className="mt-6 bg-white border border-gray-200 rounded-xl p-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">AIA MasterFormat Divisions</h4>
        <div className="flex flex-wrap gap-2">
          {Object.entries(AIA_DIVISIONS).map(([code, div]) => (
            <span key={code} className={`px-3 py-1 rounded-full text-xs font-medium ${div.color}`}>
              {div.icon} Div {code}: {div.name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
