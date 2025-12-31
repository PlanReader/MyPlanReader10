import React, { useState, useEffect, useCallback } from 'react';
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
  Lock
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

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

// Trade configurations
const TRADES = {
  'Drywall': { color: 'text-amber-700 bg-amber-50', icon: '🧱', measurementFields: [
    { key: 'length_ft', label: 'Wall Length (ft)', type: 'number', placeholder: '12.5' },
    { key: 'height_ft', label: 'Wall Height (ft)', type: 'number', placeholder: '8', default: 8 }
  ]},
  'Painting': { color: 'text-pink-700 bg-pink-50', icon: '🎨', measurementFields: [
    { key: 'sq_ft', label: 'Surface Area (sq ft)', type: 'number', placeholder: '850' },
    { key: 'coats', label: 'Number of Coats', type: 'number', placeholder: '2', default: 2 }
  ]},
  'Stucco': { color: 'text-stone-700 bg-stone-50', icon: '🏗️', measurementFields: [
    { key: 'sq_ft', label: 'Surface Area (sq ft)', type: 'number', placeholder: '500' }
  ]},
  'Exterior Paint': { color: 'text-teal-700 bg-teal-50', icon: '🏠', measurementFields: [
    { key: 'sq_ft', label: 'Surface Area (sq ft)', type: 'number', placeholder: '800' },
    { key: 'coats', label: 'Number of Coats', type: 'number', placeholder: '2', default: 2 }
  ]},
  'HVAC': { color: 'text-cyan-700 bg-cyan-50', icon: '❄️', measurementFields: [
    { key: 'sq_ft_coverage', label: 'Coverage Area (sq ft)', type: 'number', placeholder: '1500' },
    { key: 'num_vents', label: 'Number of Vents', type: 'number', placeholder: '4', default: 1 }
  ]},
  'Electrical': { color: 'text-yellow-700 bg-yellow-50', icon: '⚡', measurementFields: [
    { key: 'num_outlets', label: 'Number of Outlets', type: 'number', placeholder: '10' },
    { key: 'num_switches', label: 'Number of Switches', type: 'number', placeholder: '5' },
    { key: 'wire_runs_ft', label: 'Wire Runs (ft)', type: 'number', placeholder: '200' }
  ]},
  'Plumbing': { color: 'text-blue-700 bg-blue-50', icon: '🔧', measurementFields: [
    { key: 'pipe_runs_ft', label: 'Pipe Runs (ft)', type: 'number', placeholder: '100' },
    { key: 'num_fixtures', label: 'Number of Fixtures', type: 'number', placeholder: '3' }
  ]},
  'General': { color: 'text-gray-700 bg-gray-50', icon: '🔨', measurementFields: [] }
};

const DEFAULT_CATEGORIES = ['General', 'Work', 'Personal', 'Shopping', 'Health', 'Finance'];
const DEFAULT_TRADES = ['Drywall', 'Painting', 'Stucco', 'Exterior Paint', 'HVAC', 'Electrical', 'Plumbing', 'General'];

const formatMaterialName = (name) => {
  return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

function App() {
  const [tasks, setTasks] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [shoppingList, setShoppingList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterTrade, setFilterTrade] = useState('all');
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [activeView, setActiveView] = useState('upload'); // Default to Upload portal
  const [categories, setCategories] = useState(DEFAULT_CATEGORIES);
  const [trades, setTrades] = useState(DEFAULT_TRADES);
  const [showAddTradeModal, setShowAddTradeModal] = useState(false);
  const [newTradeName, setNewTradeName] = useState('');
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
    category: 'General',
    trade: '',
    due_date: '',
    measurements: {}
  });

  // Fetch functions
  const fetchTasks = useCallback(async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  }, []);

  const fetchDashboard = useCallback(async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/dashboard`);
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  }, []);

  const fetchShoppingList = useCallback(async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/shopping-list`);
      setShoppingList(response.data);
    } catch (error) {
      console.error('Error fetching shopping list:', error);
    }
  }, []);

  const fetchCategories = useCallback(async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/categories`);
      const fetchedCategories = response.data.categories;
      setCategories([...new Set([...DEFAULT_CATEGORIES, ...fetchedCategories])]);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  }, []);

  const fetchTrades = useCallback(async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/trades`);
      setTrades(response.data.trades || DEFAULT_TRADES);
    } catch (error) {
      setTrades(DEFAULT_TRADES);
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchTasks(), fetchDashboard(), fetchCategories(), fetchTrades(), fetchShoppingList()]);
      setLoading(false);
    };
    loadData();
  }, [fetchTasks, fetchDashboard, fetchCategories, fetchTrades, fetchShoppingList]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = { ...formData };
      if (Object.keys(submitData.measurements).length === 0) {
        delete submitData.measurements;
      }
      
      if (editingTask) {
        await axios.put(`${BACKEND_URL}/api/tasks/${editingTask.id}`, submitData);
      } else {
        await axios.post(`${BACKEND_URL}/api/tasks`, submitData);
      }
      await fetchTasks();
      await fetchDashboard();
      await fetchTrades();
      await fetchShoppingList();
      closeModal();
    } catch (error) {
      console.error('Error saving task:', error);
    }
  };

  const handleDelete = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    try {
      await axios.delete(`${BACKEND_URL}/api/tasks/${taskId}`);
      await fetchTasks();
      await fetchDashboard();
      await fetchShoppingList();
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const handleToggleComplete = async (task) => {
    try {
      await axios.patch(`${BACKEND_URL}/api/tasks/${task.id}/complete`);
      await fetchTasks();
      await fetchDashboard();
    } catch (error) {
      console.error('Error toggling task:', error);
    }
  };

  const handleExportShoppingList = () => {
    window.open(`${BACKEND_URL}/api/export/shopping-list`, '_blank');
  };

  const handleExportTasks = () => {
    window.open(`${BACKEND_URL}/api/export/tasks`, '_blank');
  };

  const handleAddTrade = () => {
    if (newTradeName.trim() && !trades.includes(newTradeName.trim())) {
      const tradeName = newTradeName.trim();
      setTrades([...trades, tradeName]);
      if (!TRADES[tradeName]) {
        TRADES[tradeName] = { color: 'text-indigo-700 bg-indigo-50', icon: '🔧', measurementFields: [] };
      }
      setNewTradeName('');
      setShowAddTradeModal(false);
    }
  };

  const handleBlueprintProcessed = async () => {
    await fetchTasks();
    await fetchDashboard();
    await fetchShoppingList();
    setActiveView('shopping');
  };

  const openNewTaskModal = () => {
    setEditingTask(null);
    setFormData({
      title: '', description: '', status: 'todo', priority: 'medium',
      category: 'General', trade: '', due_date: '', measurements: {}
    });
    setShowModal(true);
  };

  const openEditModal = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title, description: task.description || '', status: task.status,
      priority: task.priority, category: task.category || 'General',
      trade: task.trade || '', due_date: task.due_date || '',
      measurements: task.measurements || {}
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingTask(null);
  };

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = filterStatus === 'all' || task.status === filterStatus;
    const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
    const matchesTrade = filterTrade === 'all' || task.trade === filterTrade;
    return matchesSearch && matchesStatus && matchesPriority && matchesTrade;
  });

  const isOverdue = (task) => {
    if (!task.due_date || task.status === 'completed') return false;
    return new Date(task.due_date) < new Date(new Date().toDateString());
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800" data-testid="loading-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
          <p className="text-slate-400 text-lg">Loading PlanReader Pro...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white" data-testid="app-container">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-60 bg-slate-900 border-r border-slate-700 p-4 overflow-y-auto" data-testid="sidebar">
        <div className="mb-8">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-6 h-6 text-blue-500" />
            PlanReader Pro
          </h1>
          <p className="text-xs text-slate-500 mt-1">Blueprint Material Calculator</p>
        </div>
        
        <nav className="space-y-1">
          <button
            onClick={() => setActiveView('upload')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeView === 'upload' ? 'bg-blue-600 text-white font-medium' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
            }`}
            data-testid="nav-upload"
          >
            <Upload className="w-4 h-4" />
            Upload Plans
          </button>
          <button
            onClick={() => setActiveView('shopping')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeView === 'shopping' ? 'bg-blue-600 text-white font-medium' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
            }`}
            data-testid="nav-shopping"
          >
            <ShoppingCart className="w-4 h-4" />
            Shopping List
          </button>
          <button
            onClick={() => setActiveView('tasks')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeView === 'tasks' ? 'bg-blue-600 text-white font-medium' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
            }`}
            data-testid="nav-tasks"
          >
            <List className="w-4 h-4" />
            All Tasks
          </button>
          <button
            onClick={() => setActiveView('dashboard')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeView === 'dashboard' ? 'bg-blue-600 text-white font-medium' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
            }`}
            data-testid="nav-dashboard"
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboard
          </button>
        </nav>

        {/* Quick Stats */}
        {dashboard && (
          <div className="mt-8 p-3 bg-slate-800 rounded-lg border border-slate-700" data-testid="quick-stats">
            <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3">Project Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Tasks</span>
                <span className="font-medium text-white">{dashboard.total_tasks}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Completed</span>
                <span className="font-medium text-green-500">{dashboard.status_breakdown.completed}</span>
              </div>
            </div>
          </div>
        )}

        {/* Materials Summary */}
        {shoppingList && shoppingList.total_items > 0 && (
          <div className="mt-4 p-3 bg-emerald-900/30 rounded-lg border border-emerald-700/50" data-testid="materials-summary">
            <h3 className="text-xs font-medium text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Package className="w-3 h-3" />
              Materials Ready
            </h3>
            <p className="text-lg text-emerald-300 font-bold">{shoppingList.total_items} items</p>
            <p className="text-xs text-emerald-500">{shoppingList.tasks_included} takeoffs processed</p>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="ml-60 min-h-screen bg-slate-50" data-testid="main-content">
        {activeView === 'upload' ? (
          <UploadPortal onProcessed={handleBlueprintProcessed} />
        ) : activeView === 'shopping' ? (
          <ShoppingListView 
            shoppingList={shoppingList} 
            handleExportShoppingList={handleExportShoppingList}
            handleExportTasks={handleExportTasks}
          />
        ) : activeView === 'tasks' ? (
          <TasksView
            tasks={filteredTasks}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            filterStatus={filterStatus}
            setFilterStatus={setFilterStatus}
            filterPriority={filterPriority}
            setFilterPriority={setFilterPriority}
            filterTrade={filterTrade}
            setFilterTrade={setFilterTrade}
            trades={trades}
            openNewTaskModal={openNewTaskModal}
            openEditModal={openEditModal}
            handleDelete={handleDelete}
            handleToggleComplete={handleToggleComplete}
            isOverdue={isOverdue}
            formatDate={formatDate}
          />
        ) : (
          <DashboardView dashboard={dashboard} formatDate={formatDate} tasks={tasks} />
        )}
      </main>

      {/* Task Modal */}
      {showModal && (
        <TaskModal
          formData={formData}
          setFormData={setFormData}
          editingTask={editingTask}
          categories={categories}
          trades={trades}
          handleSubmit={handleSubmit}
          closeModal={closeModal}
          onAddTrade={() => setShowAddTradeModal(true)}
        />
      )}

      {/* Add Trade Modal */}
      {showAddTradeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-full max-w-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Wrench className="w-5 h-5 text-blue-600" />
                Add New Trade
              </h3>
              <button onClick={() => { setShowAddTradeModal(false); setNewTradeName(''); }} className="p-1 hover:bg-slate-100 rounded">
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>
            <input
              type="text"
              value={newTradeName}
              onChange={(e) => setNewTradeName(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm mb-4"
              placeholder="e.g., Carpentry, Roofing..."
              autoFocus
              onKeyPress={(e) => e.key === 'Enter' && handleAddTrade()}
            />
            <div className="flex justify-end gap-3">
              <button onClick={() => { setShowAddTradeModal(false); setNewTradeName(''); }} className="px-4 py-2 text-sm text-slate-500 hover:bg-slate-100 rounded-md">
                Cancel
              </button>
              <button onClick={handleAddTrade} disabled={!newTradeName.trim()} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
                Add Trade
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================
// UPLOAD PORTAL COMPONENT
// ============================================
function UploadPortal({ onProcessed }) {
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
  
  const addOns = [
    { id: 'Painting', label: 'Painting', price: ADDON_PRICE },
    { id: 'Stucco', label: 'Stucco', price: ADDON_PRICE },
    { id: 'Exterior Paint', label: 'Exterior Paint', price: ADDON_PRICE }
  ];

  const totalPrice = BASE_PRICE + addOns.filter(a => selectedTrades.includes(a.id)).length * ADDON_PRICE;

  // Initialize Stripe
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

  // Check for payment success on mount (returning from Stripe)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const paymentId = urlParams.get('payment_id');
    
    if (sessionId && paymentId) {
      verifyPaymentAndProcess(paymentId, sessionId);
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const verifyPaymentAndProcess = async (paymentId, sessionId) => {
    setIsProcessing(true);
    setProcessingStep('Verifying payment...');
    setProgress(10);
    
    try {
      const verifyResponse = await axios.get(`${BACKEND_URL}/api/verify-payment/${paymentId}?session_id=${sessionId}`);
      
      if (verifyResponse.data.verified) {
        setPaymentSuccess(true);
        setProcessingStep('Payment confirmed! Processing blueprint...');
        setProgress(30);
        
        // Process the blueprint
        const steps = [
          'Parsing divisions...',
          'Extracting measurements...',
          'Calculating whole-unit quantities...',
          'Generating shopping list...'
        ];
        
        for (let i = 0; i < steps.length; i++) {
          setProcessingStep(steps[i]);
          setProgress(30 + ((i + 1) * 15));
          await new Promise(r => setTimeout(r, 600));
        }
        
        await axios.post(`${BACKEND_URL}/api/process-blueprint`, {
          filename: verifyResponse.data.filename || 'Blueprint.pdf',
          page_count: verifyResponse.data.page_count || 10,
          selected_trades: verifyResponse.data.selected_trades || ['Drywall'],
          total_fee: verifyResponse.data.total_amount / 100
        });
        
        setProgress(100);
        setProcessingStep('Complete! Redirecting to shopping list...');
        await new Promise(r => setTimeout(r, 1000));
        
        onProcessed();
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
    if (!selectedFile || !stripePromise) return;
    
    setIsCheckingOut(true);
    
    try {
      const response = await axios.post(`${BACKEND_URL}/api/create-checkout-session`, {
        filename: selectedFile.name,
        page_count: pageCount,
        selected_trades: selectedTrades,
        total_amount: totalPrice * 100, // Convert to cents
        success_url: window.location.href,
        cancel_url: window.location.href
      });
      
      // Redirect to Stripe Checkout
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
      alert('Error initiating payment. Please try again.');
    }
    
    setIsCheckingOut(false);
  };

  // Demo mode - process without payment
  const handleDemoProcess = async () => {
    if (!selectedFile) return;
    
    setIsProcessing(true);
    setProgress(0);
    
    const steps = [
      'Uploading blueprint...',
      'Parsing divisions...',
      'Extracting measurements...',
      'Calculating whole-unit quantities...',
      'Generating shopping list...'
    ];
    
    for (let i = 0; i < steps.length; i++) {
      setProcessingStep(steps[i]);
      setProgress((i + 1) * 20);
      await new Promise(r => setTimeout(r, 800));
    }
    
    try {
      await axios.post(`${BACKEND_URL}/api/process-blueprint`, {
        filename: selectedFile.name,
        page_count: pageCount,
        selected_trades: selectedTrades,
        total_fee: totalPrice
      });
      
      setProgress(100);
      setProcessingStep('Complete! Redirecting to shopping list...');
      await new Promise(r => setTimeout(r, 1000));
      
      onProcessed();
    } catch (error) {
      console.error('Error processing blueprint:', error);
      setProcessingStep('Error processing file. Please try again.');
    }
    
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 p-8" data-testid="upload-portal">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
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
          <div className="fixed inset-0 bg-white/95 flex items-center justify-center z-50" data-testid="processing-overlay">
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
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-gray-500">{progress}%</p>
            </div>
          </div>
        )}

        {/* Upload Zone - Clean Light Design */}
        <div
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all mb-8 bg-white shadow-sm ${
            isDragging 
              ? 'border-blue-500 bg-blue-50' 
              : selectedFile 
                ? 'border-green-500 bg-green-50' 
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          data-testid="upload-zone"
        >
          <input
            id="file-input"
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={handleFileSelect}
          />
          
          {selectedFile ? (
            <div className="flex flex-col items-center py-4">
              <CheckCircle2 className="w-12 h-12 text-green-600 mb-3" />
              <p className="text-lg font-semibold text-gray-800 mb-1">{selectedFile.name}</p>
              <p className="text-gray-500 text-sm">{pageCount} pages detected</p>
              <button 
                onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                className="mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Choose different file
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center py-4">
              <p className="text-gray-500 text-sm mb-4">Drag & drop your PDF here, or</p>
              
              {/* Compact Blue Upload Button */}
              <button
                onClick={() => document.getElementById('file-input').click()}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 shadow-md hover:shadow-lg"
                data-testid="upload-btn"
              >
                <Upload className="w-5 h-5" />
                Upload PDF Blueprint
              </button>
              
              <p className="text-xs text-gray-400 mt-4">
                Max 25 pages for single use
              </p>
            </div>
          )}
        </div>

        {/* Trade Selection - High Contrast Light Theme */}
        <div className="bg-white rounded-2xl p-6 mb-6 shadow-sm border border-gray-200" data-testid="trade-selector">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Wrench className="w-5 h-5 text-blue-600" />
            Trade Selection
          </h2>
          
          {/* Base Trade */}
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
          
          {/* Add-ons */}
          <p className="text-sm text-gray-600 mb-3 font-medium">Add more trades:</p>
          <div className="space-y-3">
            {addOns.map(addon => (
              <label
                key={addon.id}
                className={`flex items-center justify-between p-4 rounded-xl cursor-pointer transition-all border-2 ${
                  selectedTrades.includes(addon.id)
                    ? 'bg-blue-50 border-blue-300'
                    : 'bg-gray-50 border-gray-200 hover:border-gray-300 hover:bg-gray-100'
                }`}
                data-testid={`addon-${addon.id.toLowerCase().replace(' ', '-')}`}
              >
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={selectedTrades.includes(addon.id)}
                    onChange={() => toggleAddOn(addon.id)}
                    className="w-5 h-5 rounded border-gray-400 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-gray-800 font-medium">
                    {TRADES[addon.id]?.icon} {addon.label}
                  </span>
                </div>
                <span className="text-gray-600 font-semibold">+${addon.price}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Pricing Summary Footer - High Contrast */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-200 sticky bottom-4" data-testid="pricing-summary">
          <div className="flex items-center justify-between mb-5">
            <div>
              <p className="text-gray-500 text-sm font-medium">Total Fee</p>
              <p className="text-4xl font-bold text-gray-900 flex items-center">
                <DollarSign className="w-9 h-9 text-green-600" />
                {totalPrice}
              </p>
            </div>
            <div className="text-right text-sm text-gray-600">
              <p>Base: <span className="font-semibold">${BASE_PRICE}</span></p>
              <p>Add-ons: <span className="font-semibold">${totalPrice - BASE_PRICE}</span></p>
            </div>
          </div>
          
          {/* Payment Button */}
          <button
            onClick={handleCheckout}
            disabled={!selectedFile || isCheckingOut || !stripePromise}
            className="w-full py-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:text-gray-500 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 mb-3 shadow-md"
            data-testid="checkout-btn"
          >
            {isCheckingOut ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Redirecting to payment...
              </>
            ) : (
              <>
                <CreditCard className="w-5 h-5" />
                Pay ${totalPrice} & Process Blueprint
              </>
            )}
          </button>

          {/* Demo Mode Button */}
          <button
            onClick={handleDemoProcess}
            disabled={!selectedFile || isProcessing}
            className="w-full py-3 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 text-gray-700 font-medium rounded-xl transition-colors flex items-center justify-center gap-2 text-sm border border-gray-300"
            data-testid="demo-btn"
          >
            <FileText className="w-4 h-4" />
            Demo Mode (Skip Payment)
          </button>
          
          <div className="flex items-center justify-center gap-2 mt-4 text-xs text-gray-500">
            <Lock className="w-3 h-3" />
            <span>Secure payment powered by Stripe</span>
          </div>
          
          <p className="text-center text-xs text-gray-400 mt-2">
            All material quantities rounded UP to whole numbers
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================
// SHOPPING LIST VIEW
// ============================================
function ShoppingListView({ shoppingList, handleExportShoppingList, handleExportTasks }) {
  if (!shoppingList) {
    return (
      <div className="p-8" data-testid="shopping-list-view">
        <h2 className="text-3xl font-bold text-slate-800 mb-8">Shopping List</h2>
        <p className="text-slate-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="p-8" data-testid="shopping-list-view">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-slate-800">Shopping List</h2>
          <p className="text-sm text-slate-500 mt-1">All quantities are whole numbers (rounded UP)</p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleExportShoppingList} className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700" data-testid="export-shopping-btn">
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          <button onClick={handleExportTasks} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" data-testid="export-tasks-btn">
            <Download className="w-4 h-4" />
            Export Tasks
          </button>
        </div>
      </div>

      {/* Aggregated Materials */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 mb-8 shadow-sm" data-testid="aggregated-list">
        <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <ShoppingCart className="w-5 h-5 text-emerald-600" />
          Aggregated Materials ({shoppingList.total_items} items)
        </h3>
        
        {Object.keys(shoppingList.shopping_list).length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {Object.entries(shoppingList.shopping_list).map(([item, qty]) => (
              <div key={item} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-100" data-testid={`material-${item}`}>
                <span className="text-sm text-slate-700">{formatMaterialName(item)}</span>
                <span className="text-xl font-bold text-emerald-700">{qty}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Upload className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No materials calculated yet.</p>
            <p className="text-sm text-slate-400">Upload a blueprint to generate your shopping list.</p>
          </div>
        )}
      </div>

      {/* Breakdown by Task */}
      {shoppingList.breakdown_by_task && shoppingList.breakdown_by_task.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm" data-testid="breakdown-by-task">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Package className="w-5 h-5 text-blue-600" />
            Materials by Takeoff
          </h3>
          <div className="space-y-4">
            {shoppingList.breakdown_by_task.map((task, idx) => (
              <div key={idx} className="border border-slate-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <h4 className="font-medium text-slate-800">{task.task_title}</h4>
                  {task.trade && TRADES[task.trade] && (
                    <span className={`text-xs px-2 py-0.5 rounded ${TRADES[task.trade].color}`}>
                      {TRADES[task.trade].icon} {task.trade}
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {Object.entries(task.materials).map(([item, qty]) => (
                    typeof qty === 'number' && (
                      <div key={item} className="text-sm">
                        <span className="text-slate-500">{formatMaterialName(item)}:</span>{' '}
                        <span className="font-medium text-slate-800">{qty}</span>
                      </div>
                    )
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================
// REMAINING COMPONENTS (Tasks, Dashboard, etc.)
// ============================================
function TasksView({ tasks, searchQuery, setSearchQuery, filterStatus, setFilterStatus, filterPriority, setFilterPriority, filterTrade, setFilterTrade, trades, openNewTaskModal, openEditModal, handleDelete, handleToggleComplete, isOverdue, formatDate }) {
  const tasksByStatus = {
    todo: tasks.filter(t => t.status === 'todo'),
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    completed: tasks.filter(t => t.status === 'completed')
  };
  const hasActiveTradeFilter = filterTrade !== 'all';

  return (
    <div className="p-8" data-testid="tasks-view">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-slate-800">Tasks</h2>
          {hasActiveTradeFilter && (
            <p className="text-sm text-blue-600 mt-1 flex items-center gap-1">
              <Wrench className="w-4 h-4" />
              Filtered by: {filterTrade}
              <button onClick={() => setFilterTrade('all')} className="ml-2 text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </p>
          )}
        </div>
        <button onClick={openNewTaskModal} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" data-testid="new-task-btn">
          <Plus className="w-4 h-4" />
          New Task
        </button>
      </div>

      <div className="flex items-center gap-4 mb-6 flex-wrap">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input type="text" placeholder="Search tasks..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-sm" data-testid="search-input" />
        </div>
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white" data-testid="filter-status">
          <option value="all">All Status</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
        <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)} className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white" data-testid="filter-priority">
          <option value="all">All Priorities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select value={filterTrade} onChange={(e) => setFilterTrade(e.target.value)} className={`px-3 py-2 border rounded-lg text-sm bg-white ${hasActiveTradeFilter ? 'border-blue-500 ring-1 ring-blue-500' : 'border-slate-300'}`} data-testid="filter-trade">
          <option value="all">All Trades</option>
          {trades.map(trade => (<option key={trade} value={trade}>{TRADES[trade]?.icon || '🔨'} {trade}</option>))}
        </select>
      </div>

      <div className="grid grid-cols-3 gap-6" data-testid="task-columns">
        {Object.entries(STATUSES).map(([status, config]) => {
          const StatusIcon = config.icon;
          const statusTasks = tasksByStatus[status];
          return (
            <div key={status} className="bg-slate-100 rounded-xl p-4" data-testid={`column-${status}`}>
              <div className="flex items-center gap-2 mb-4">
                <StatusIcon className={`w-4 h-4 ${status === 'todo' ? 'text-slate-500' : status === 'in_progress' ? 'text-blue-500' : 'text-green-500'}`} />
                <h3 className="font-medium text-slate-800">{config.label}</h3>
                <span className="text-xs text-slate-500 bg-white px-2 py-0.5 rounded">{statusTasks.length}</span>
              </div>
              <div className="space-y-2">
                {statusTasks.map(task => (
                  <TaskCard key={task.id} task={task} openEditModal={openEditModal} handleDelete={handleDelete} handleToggleComplete={handleToggleComplete} isOverdue={isOverdue} formatDate={formatDate} />
                ))}
                {statusTasks.length === 0 && <p className="text-sm text-slate-400 text-center py-8">No tasks</p>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function TaskCard({ task, openEditModal, handleDelete, handleToggleComplete, isOverdue, formatDate }) {
  const priorityConfig = PRIORITIES[task.priority];
  const tradeConfig = task.trade ? TRADES[task.trade] || TRADES['General'] : null;
  const overdue = isOverdue(task);
  const hasMaterials = task.materials && Object.keys(task.materials).length > 0;

  return (
    <div className="bg-white p-3 rounded-lg border border-slate-200 hover:border-slate-300 cursor-pointer group" data-testid={`task-card-${task.id}`}>
      <div className="flex items-start gap-3">
        <button onClick={(e) => { e.stopPropagation(); handleToggleComplete(task); }} className="mt-0.5 flex-shrink-0" data-testid={`toggle-complete-${task.id}`}>
          {task.status === 'completed' ? <CheckSquare className="w-5 h-5 text-blue-600" /> : <Square className="w-5 h-5 text-slate-400 hover:text-blue-600" />}
        </button>
        <div className="flex-1 min-w-0">
          <h4 className={`font-medium text-sm ${task.status === 'completed' ? 'line-through text-slate-400' : 'text-slate-800'}`}>{task.title}</h4>
          {task.description && <p className="text-xs text-slate-500 mt-1 line-clamp-2">{task.description}</p>}
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <span className={`text-xs px-2 py-0.5 rounded ${priorityConfig.color}`}>{priorityConfig.icon} {priorityConfig.label}</span>
            {task.trade && tradeConfig && <span className={`text-xs px-2 py-0.5 rounded ${tradeConfig.color}`}>{tradeConfig.icon} {task.trade}</span>}
            {hasMaterials && <span className="text-xs px-2 py-0.5 rounded bg-emerald-50 text-emerald-700"><Package className="w-3 h-3 inline mr-1" />Materials</span>}
            {task.due_date && <span className={`text-xs px-2 py-0.5 rounded ${overdue ? 'bg-red-50 text-red-600' : 'bg-slate-100 text-slate-600'}`}>{overdue ? <AlertCircle className="w-3 h-3 inline mr-1" /> : <Calendar className="w-3 h-3 inline mr-1" />}{formatDate(task.due_date)}</span>}
          </div>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100">
          <button onClick={(e) => { e.stopPropagation(); openEditModal(task); }} className="p-1 hover:bg-slate-100 rounded" data-testid={`edit-task-${task.id}`}><Edit3 className="w-4 h-4 text-slate-400" /></button>
          <button onClick={(e) => { e.stopPropagation(); handleDelete(task.id); }} className="p-1 hover:bg-red-50 rounded" data-testid={`delete-task-${task.id}`}><Trash2 className="w-4 h-4 text-red-500" /></button>
        </div>
      </div>
    </div>
  );
}

function DashboardView({ dashboard, formatDate, tasks }) {
  if (!dashboard) return null;
  const completionPercentage = dashboard.completion_rate || 0;
  const tradeBreakdown = {};
  tasks.forEach(task => { if (task.trade) tradeBreakdown[task.trade] = (tradeBreakdown[task.trade] || 0) + 1; });

  return (
    <div className="p-8" data-testid="dashboard-view">
      <h2 className="text-3xl font-bold text-slate-800 mb-8">Dashboard</h2>
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Tasks" value={dashboard.total_tasks} icon={<List className="w-5 h-5 text-blue-600" />} color="bg-blue-50" />
        <StatCard label="To Do" value={dashboard.status_breakdown.todo} icon={<Circle className="w-5 h-5 text-slate-500" />} color="bg-slate-50" />
        <StatCard label="In Progress" value={dashboard.status_breakdown.in_progress} icon={<Clock className="w-5 h-5 text-orange-500" />} color="bg-orange-50" />
        <StatCard label="Completed" value={dashboard.status_breakdown.completed} icon={<CheckCircle2 className="w-5 h-5 text-green-600" />} color="bg-green-50" />
      </div>
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Completion Progress</h3>
          <div className="flex mb-2 items-center justify-between">
            <span className="text-xs font-semibold py-1 px-2 rounded-full text-green-600 bg-green-50">{completionPercentage}% Complete</span>
          </div>
          <div className="h-4 rounded-full bg-slate-100">
            <div style={{ width: `${completionPercentage}%` }} className="h-4 rounded-full bg-green-500 transition-all"></div>
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Trade Breakdown</h3>
          <div className="space-y-2">
            {Object.entries(tradeBreakdown).length > 0 ? Object.entries(tradeBreakdown).map(([trade, count]) => (
              <div key={trade} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                <span className="flex items-center gap-2"><span>{TRADES[trade]?.icon || '🔨'}</span><span className="text-sm text-slate-700">{trade}</span></span>
                <span className="text-sm font-medium text-slate-500">{count}</span>
              </div>
            )) : <p className="text-sm text-slate-400">No trades assigned yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color }) {
  return (
    <div className={`${color} rounded-xl p-4 border border-slate-200`}>
      <div className="flex items-center justify-between">
        <div><p className="text-2xl font-bold text-slate-800">{value}</p><p className="text-sm text-slate-500">{label}</p></div>
        {icon}
      </div>
    </div>
  );
}

function TaskModal({ formData, setFormData, editingTask, categories, trades, handleSubmit, closeModal, onAddTrade }) {
  const selectedTrade = formData.trade ? TRADES[formData.trade] : null;
  const measurementFields = selectedTrade?.measurementFields || [];
  const handleMeasurementChange = (key, value) => { setFormData({ ...formData, measurements: { ...formData.measurements, [key]: value ? parseFloat(value) : undefined } }); };
  const handleTradeChange = (e) => { const value = e.target.value; if (value === '__add_new__') { onAddTrade(); } else { setFormData({ ...formData, trade: value, measurements: {} }); } };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-slate-800">{editingTask ? 'Edit Task' : 'New Task'}</h3>
          <button onClick={closeModal} className="p-1 hover:bg-slate-100 rounded"><X className="w-5 h-5 text-slate-400" /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Title *</label>
            <input type="text" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm" placeholder="Task title" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
            <textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm resize-none" rows={2} placeholder="Details..." />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
              <select value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white">
                <option value="todo">To Do</option><option value="in_progress">In Progress</option><option value="completed">Completed</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Priority</label>
              <select value={formData.priority} onChange={(e) => setFormData({ ...formData, priority: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white">
                <option value="low">🟢 Low</option><option value="medium">🟠 Medium</option><option value="high">🔴 High</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
              <select value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white">
                {categories.map(cat => (<option key={cat} value={cat}>{cat}</option>))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Trade</label>
              <select value={formData.trade} onChange={handleTradeChange} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white">
                <option value="">No Trade</option>
                {trades.map(trade => (<option key={trade} value={trade}>{TRADES[trade]?.icon || '🔨'} {trade}</option>))}
                <option value="__add_new__">➕ Add Trade...</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Due Date</label>
            <input type="date" value={formData.due_date} onChange={(e) => setFormData({ ...formData, due_date: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm" />
          </div>
          {measurementFields.length > 0 && (
            <div className="border-t border-slate-200 pt-4">
              <h4 className="text-sm font-medium text-slate-700 mb-3 flex items-center gap-2"><Ruler className="w-4 h-4 text-emerald-600" />Measurements</h4>
              <p className="text-xs text-slate-500 mb-3">All quantities rounded UP to whole numbers</p>
              <div className="grid grid-cols-2 gap-3">
                {measurementFields.map(field => (
                  <div key={field.key}>
                    <label className="block text-xs text-slate-500 mb-1">{field.label}</label>
                    <input type="number" step="0.1" value={formData.measurements[field.key] || ''} onChange={(e) => handleMeasurementChange(field.key, e.target.value)} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm" placeholder={field.placeholder} />
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="flex justify-end gap-3 pt-4">
            <button type="button" onClick={closeModal} className="px-4 py-2 text-sm text-slate-500 hover:bg-slate-100 rounded-lg">Cancel</button>
            <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">{editingTask ? 'Save Changes' : 'Create Task'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
