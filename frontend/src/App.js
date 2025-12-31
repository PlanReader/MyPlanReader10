import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';
import { 
  Plus, 
  Search, 
  CheckSquare, 
  Square, 
  Edit3, 
  Trash2, 
  Calendar, 
  Flag, 
  Tag, 
  LayoutDashboard,
  List,
  X,
  Clock,
  AlertCircle,
  CheckCircle2,
  Circle,
  Loader2
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

const DEFAULT_CATEGORIES = ['General', 'Work', 'Personal', 'Shopping', 'Health', 'Finance'];

function App() {
  const [tasks, setTasks] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [activeView, setActiveView] = useState('tasks'); // 'tasks' or 'dashboard'
  const [categories, setCategories] = useState(DEFAULT_CATEGORIES);
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
    category: 'General',
    due_date: ''
  });

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  }, []);

  // Fetch dashboard data
  const fetchDashboard = useCallback(async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/dashboard`);
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  }, []);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/categories`);
      const fetchedCategories = response.data.categories;
      setCategories([...new Set([...DEFAULT_CATEGORIES, ...fetchedCategories])]);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  }, []);

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchTasks(), fetchDashboard(), fetchCategories()]);
      setLoading(false);
    };
    loadData();
  }, [fetchTasks, fetchDashboard, fetchCategories]);

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingTask) {
        await axios.put(`${BACKEND_URL}/api/tasks/${editingTask.id}`, formData);
      } else {
        await axios.post(`${BACKEND_URL}/api/tasks`, formData);
      }
      await fetchTasks();
      await fetchDashboard();
      closeModal();
    } catch (error) {
      console.error('Error saving task:', error);
    }
  };

  // Handle task deletion
  const handleDelete = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    try {
      await axios.delete(`${BACKEND_URL}/api/tasks/${taskId}`);
      await fetchTasks();
      await fetchDashboard();
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  // Handle task completion toggle
  const handleToggleComplete = async (task) => {
    try {
      await axios.patch(`${BACKEND_URL}/api/tasks/${task.id}/complete`);
      await fetchTasks();
      await fetchDashboard();
    } catch (error) {
      console.error('Error toggling task:', error);
    }
  };

  // Open modal for new task
  const openNewTaskModal = () => {
    setEditingTask(null);
    setFormData({
      title: '',
      description: '',
      status: 'todo',
      priority: 'medium',
      category: 'General',
      due_date: ''
    });
    setShowModal(true);
  };

  // Open modal for editing
  const openEditModal = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description || '',
      status: task.status,
      priority: task.priority,
      category: task.category || 'General',
      due_date: task.due_date || ''
    });
    setShowModal(true);
  };

  // Close modal
  const closeModal = () => {
    setShowModal(false);
    setEditingTask(null);
  };

  // Filter tasks
  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = filterStatus === 'all' || task.status === filterStatus;
    const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
    return matchesSearch && matchesStatus && matchesPriority;
  });

  // Check if task is overdue
  const isOverdue = (task) => {
    if (!task.due_date || task.status === 'completed') return false;
    return new Date(task.due_date) < new Date(new Date().toDateString());
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white" data-testid="loading-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-gray-400 animate-spin" />
          <p className="text-gray-500">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white" data-testid="app-container">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-60 bg-[#f7f6f3] border-r border-[#e3e2de] p-4" data-testid="sidebar">
        <div className="mb-8">
          <h1 className="text-xl font-semibold text-[#37352f] flex items-center gap-2">
            <CheckSquare className="w-6 h-6 text-blue-600" />
            TaskFlow
          </h1>
        </div>
        
        <nav className="space-y-1">
          <button
            onClick={() => setActiveView('tasks')}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
              activeView === 'tasks' ? 'bg-[#efefef] text-[#37352f] font-medium' : 'text-[#9b9a97] hover:bg-[#efefef]'
            }`}
            data-testid="nav-tasks"
          >
            <List className="w-4 h-4" />
            All Tasks
          </button>
          <button
            onClick={() => setActiveView('dashboard')}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
              activeView === 'dashboard' ? 'bg-[#efefef] text-[#37352f] font-medium' : 'text-[#9b9a97] hover:bg-[#efefef]'
            }`}
            data-testid="nav-dashboard"
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboard
          </button>
        </nav>

        {/* Quick Stats */}
        {dashboard && (
          <div className="mt-8 p-3 bg-white rounded-lg border border-[#e3e2de]" data-testid="quick-stats">
            <h3 className="text-xs font-medium text-[#9b9a97] uppercase tracking-wider mb-3">Quick Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[#9b9a97]">Total</span>
                <span className="font-medium text-[#37352f]">{dashboard.total_tasks}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#9b9a97]">Completed</span>
                <span className="font-medium text-green-600">{dashboard.status_breakdown.completed}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#9b9a97]">Overdue</span>
                <span className="font-medium text-red-600">{dashboard.overdue_count}</span>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="ml-60 p-8" data-testid="main-content">
        {activeView === 'tasks' ? (
          <TasksView
            tasks={filteredTasks}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            filterStatus={filterStatus}
            setFilterStatus={setFilterStatus}
            filterPriority={filterPriority}
            setFilterPriority={setFilterPriority}
            openNewTaskModal={openNewTaskModal}
            openEditModal={openEditModal}
            handleDelete={handleDelete}
            handleToggleComplete={handleToggleComplete}
            isOverdue={isOverdue}
            formatDate={formatDate}
          />
        ) : (
          <DashboardView dashboard={dashboard} formatDate={formatDate} />
        )}
      </main>

      {/* Task Modal */}
      {showModal && (
        <TaskModal
          formData={formData}
          setFormData={setFormData}
          editingTask={editingTask}
          categories={categories}
          handleSubmit={handleSubmit}
          closeModal={closeModal}
        />
      )}
    </div>
  );
}

// Tasks View Component
function TasksView({
  tasks,
  searchQuery,
  setSearchQuery,
  filterStatus,
  setFilterStatus,
  filterPriority,
  setFilterPriority,
  openNewTaskModal,
  openEditModal,
  handleDelete,
  handleToggleComplete,
  isOverdue,
  formatDate
}) {
  // Group tasks by status
  const tasksByStatus = {
    todo: tasks.filter(t => t.status === 'todo'),
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    completed: tasks.filter(t => t.status === 'completed')
  };

  return (
    <div data-testid="tasks-view">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold text-[#37352f]">Tasks</h2>
        <button
          onClick={openNewTaskModal}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          data-testid="new-task-btn"
        >
          <Plus className="w-4 h-4" />
          New Task
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#9b9a97]" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-[#e3e2de] rounded-md text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            data-testid="search-input"
          />
        </div>
        
        <div className="flex items-center gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-[#e3e2de] rounded-md text-sm bg-white"
            data-testid="filter-status"
          >
            <option value="all">All Status</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
          
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-3 py-2 border border-[#e3e2de] rounded-md text-sm bg-white"
            data-testid="filter-priority"
          >
            <option value="all">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Task Columns (Kanban-style) */}
      <div className="grid grid-cols-3 gap-6" data-testid="task-columns">
        {Object.entries(STATUSES).map(([status, config]) => {
          const StatusIcon = config.icon;
          const statusTasks = tasksByStatus[status];
          
          return (
            <div key={status} className="bg-[#f7f6f3] rounded-lg p-4" data-testid={`column-${status}`}>
              <div className="flex items-center gap-2 mb-4">
                <StatusIcon className={`w-4 h-4 ${status === 'todo' ? 'text-gray-500' : status === 'in_progress' ? 'text-blue-500' : 'text-green-500'}`} />
                <h3 className="font-medium text-[#37352f]">{config.label}</h3>
                <span className="text-xs text-[#9b9a97] bg-white px-2 py-0.5 rounded">{statusTasks.length}</span>
              </div>
              
              <div className="space-y-2">
                {statusTasks.map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    openEditModal={openEditModal}
                    handleDelete={handleDelete}
                    handleToggleComplete={handleToggleComplete}
                    isOverdue={isOverdue}
                    formatDate={formatDate}
                  />
                ))}
                {statusTasks.length === 0 && (
                  <p className="text-sm text-[#9b9a97] text-center py-8">No tasks</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Task Card Component
function TaskCard({ task, openEditModal, handleDelete, handleToggleComplete, isOverdue, formatDate }) {
  const priorityConfig = PRIORITIES[task.priority];
  const overdue = isOverdue(task);

  return (
    <div
      className="bg-white p-3 rounded-lg border border-[#e3e2de] task-card cursor-pointer group"
      data-testid={`task-card-${task.id}`}
    >
      <div className="flex items-start gap-3">
        <button
          onClick={(e) => { e.stopPropagation(); handleToggleComplete(task); }}
          className="mt-0.5 flex-shrink-0"
          data-testid={`toggle-complete-${task.id}`}
        >
          {task.status === 'completed' ? (
            <CheckSquare className="w-5 h-5 text-blue-600" />
          ) : (
            <Square className="w-5 h-5 text-[#9b9a97] hover:text-blue-600 transition-colors" />
          )}
        </button>
        
        <div className="flex-1 min-w-0">
          <h4 className={`font-medium text-sm ${task.status === 'completed' ? 'line-through text-[#9b9a97]' : 'text-[#37352f]'}`}>
            {task.title}
          </h4>
          
          {task.description && (
            <p className="text-xs text-[#9b9a97] mt-1 line-clamp-2">{task.description}</p>
          )}
          
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            {/* Priority Badge */}
            <span className={`text-xs px-2 py-0.5 rounded ${priorityConfig.color}`} data-testid={`priority-${task.id}`}>
              {priorityConfig.icon} {priorityConfig.label}
            </span>
            
            {/* Category Badge */}
            {task.category && (
              <span className="text-xs px-2 py-0.5 rounded bg-purple-50 text-purple-600" data-testid={`category-${task.id}`}>
                <Tag className="w-3 h-3 inline mr-1" />
                {task.category}
              </span>
            )}
            
            {/* Due Date */}
            {task.due_date && (
              <span className={`text-xs px-2 py-0.5 rounded flex items-center gap-1 ${
                overdue ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-600'
              }`} data-testid={`due-date-${task.id}`}>
                {overdue ? <AlertCircle className="w-3 h-3" /> : <Calendar className="w-3 h-3" />}
                {formatDate(task.due_date)}
              </span>
            )}
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => { e.stopPropagation(); openEditModal(task); }}
            className="p-1 hover:bg-[#efefef] rounded"
            data-testid={`edit-task-${task.id}`}
          >
            <Edit3 className="w-4 h-4 text-[#9b9a97]" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); handleDelete(task.id); }}
            className="p-1 hover:bg-red-50 rounded"
            data-testid={`delete-task-${task.id}`}
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      </div>
    </div>
  );
}

// Dashboard View Component
function DashboardView({ dashboard, formatDate }) {
  if (!dashboard) return null;

  const completionPercentage = dashboard.completion_rate || 0;

  return (
    <div data-testid="dashboard-view">
      <h2 className="text-3xl font-bold text-[#37352f] mb-8">Dashboard</h2>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8" data-testid="stats-cards">
        <StatCard
          label="Total Tasks"
          value={dashboard.total_tasks}
          icon={<List className="w-5 h-5 text-blue-600" />}
          color="bg-blue-50"
        />
        <StatCard
          label="To Do"
          value={dashboard.status_breakdown.todo}
          icon={<Circle className="w-5 h-5 text-gray-500" />}
          color="bg-gray-50"
        />
        <StatCard
          label="In Progress"
          value={dashboard.status_breakdown.in_progress}
          icon={<Clock className="w-5 h-5 text-orange-500" />}
          color="bg-orange-50"
        />
        <StatCard
          label="Completed"
          value={dashboard.status_breakdown.completed}
          icon={<CheckCircle2 className="w-5 h-5 text-green-600" />}
          color="bg-green-50"
        />
      </div>

      {/* Progress and Priority Row */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Completion Progress */}
        <div className="bg-white border border-[#e3e2de] rounded-lg p-6" data-testid="completion-progress">
          <h3 className="text-lg font-semibold text-[#37352f] mb-4">Completion Progress</h3>
          <div className="relative pt-1">
            <div className="flex mb-2 items-center justify-between">
              <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-green-600 bg-green-50">
                {completionPercentage}% Complete
              </span>
            </div>
            <div className="overflow-hidden h-4 mb-4 text-xs flex rounded-full bg-gray-100">
              <div
                style={{ width: `${completionPercentage}%` }}
                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-500 transition-all duration-500"
              ></div>
            </div>
          </div>
        </div>

        {/* Priority Breakdown */}
        <div className="bg-white border border-[#e3e2de] rounded-lg p-6" data-testid="priority-breakdown">
          <h3 className="text-lg font-semibold text-[#37352f] mb-4">Priority Breakdown</h3>
          <div className="space-y-3">
            <PriorityBar label="High" count={dashboard.priority_breakdown.high} total={dashboard.total_tasks} color="bg-red-500" />
            <PriorityBar label="Medium" count={dashboard.priority_breakdown.medium} total={dashboard.total_tasks} color="bg-orange-500" />
            <PriorityBar label="Low" count={dashboard.priority_breakdown.low} total={dashboard.total_tasks} color="bg-green-500" />
          </div>
        </div>
      </div>

      {/* Categories and Overdue */}
      <div className="grid grid-cols-2 gap-6">
        {/* Categories */}
        <div className="bg-white border border-[#e3e2de] rounded-lg p-6" data-testid="categories-breakdown">
          <h3 className="text-lg font-semibold text-[#37352f] mb-4">Categories</h3>
          <div className="space-y-2">
            {Object.entries(dashboard.categories || {}).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between py-2 border-b border-[#e3e2de] last:border-0">
                <span className="flex items-center gap-2">
                  <Tag className="w-4 h-4 text-purple-500" />
                  <span className="text-sm text-[#37352f]">{category}</span>
                </span>
                <span className="text-sm font-medium text-[#9b9a97]">{count}</span>
              </div>
            ))}
            {Object.keys(dashboard.categories || {}).length === 0 && (
              <p className="text-sm text-[#9b9a97]">No categories yet</p>
            )}
          </div>
        </div>

        {/* Overdue Tasks */}
        <div className="bg-white border border-[#e3e2de] rounded-lg p-6" data-testid="overdue-tasks">
          <h3 className="text-lg font-semibold text-[#37352f] mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            Overdue Tasks ({dashboard.overdue_count})
          </h3>
          <div className="space-y-2">
            {dashboard.overdue_tasks && dashboard.overdue_tasks.length > 0 ? (
              dashboard.overdue_tasks.map(task => (
                <div key={task.id} className="flex items-center justify-between py-2 border-b border-[#e3e2de] last:border-0">
                  <span className="text-sm text-[#37352f]">{task.title}</span>
                  <span className="text-xs text-red-500">{formatDate(task.due_date)}</span>
                </div>
              ))
            ) : (
              <p className="text-sm text-green-600 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                No overdue tasks! 🎉
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({ label, value, icon, color }) {
  return (
    <div className={`${color} rounded-lg p-4 border border-[#e3e2de]`} data-testid={`stat-${label.toLowerCase().replace(' ', '-')}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-2xl font-bold text-[#37352f]">{value}</p>
          <p className="text-sm text-[#9b9a97]">{label}</p>
        </div>
        {icon}
      </div>
    </div>
  );
}

// Priority Bar Component
function PriorityBar({ label, count, total, color }) {
  const percentage = total > 0 ? (count / total) * 100 : 0;
  
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-[#9b9a97] w-16">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${percentage}%` }}></div>
      </div>
      <span className="text-sm font-medium text-[#37352f] w-8 text-right">{count}</span>
    </div>
  );
}

// Task Modal Component
function TaskModal({ formData, setFormData, editingTask, categories, handleSubmit, closeModal }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 modal-backdrop" data-testid="task-modal">
      <div className="bg-white rounded-lg w-full max-w-lg p-6 modal-content" data-testid="modal-content">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-[#37352f]">
            {editingTask ? 'Edit Task' : 'New Task'}
          </h3>
          <button onClick={closeModal} className="p-1 hover:bg-[#efefef] rounded" data-testid="close-modal">
            <X className="w-5 h-5 text-[#9b9a97]" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-[#37352f] mb-1">Title *</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border border-[#e3e2de] rounded-md text-sm"
              placeholder="What needs to be done?"
              required
              data-testid="input-title"
            />
          </div>
          
          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-[#37352f] mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-[#e3e2de] rounded-md text-sm resize-none"
              rows={3}
              placeholder="Add more details..."
              data-testid="input-description"
            />
          </div>
          
          {/* Status and Priority Row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-[#37352f] mb-1">
                <Flag className="w-4 h-4 inline mr-1" />
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                className="w-full px-3 py-2 border border-[#e3e2de] rounded-md text-sm bg-white"
                data-testid="select-status"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-[#37352f] mb-1">
                <Flag className="w-4 h-4 inline mr-1" />
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full px-3 py-2 border border-[#e3e2de] rounded-md text-sm bg-white"
                data-testid="select-priority"
              >
                <option value="low">🟢 Low</option>
                <option value="medium">🟠 Medium</option>
                <option value="high">🔴 High</option>
              </select>
            </div>
          </div>
          
          {/* Category and Due Date Row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-[#37352f] mb-1">
                <Tag className="w-4 h-4 inline mr-1" />
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 border border-[#e3e2de] rounded-md text-sm bg-white"
                data-testid="select-category"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-[#37352f] mb-1">
                <Calendar className="w-4 h-4 inline mr-1" />
                Due Date
              </label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="w-full px-3 py-2 border border-[#e3e2de] rounded-md text-sm"
                data-testid="input-due-date"
              />
            </div>
          </div>
          
          {/* Submit Button */}
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={closeModal}
              className="px-4 py-2 text-sm text-[#9b9a97] hover:bg-[#efefef] rounded-md transition-colors"
              data-testid="cancel-btn"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              data-testid="submit-task-btn"
            >
              {editingTask ? 'Save Changes' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
