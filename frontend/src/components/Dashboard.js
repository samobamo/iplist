import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_tasks: 0,
    completed_tasks: 0,
    pending_tasks: 0,
    overdue_tasks: 0,
    today_tasks: 0
  });
  const [recentTasks, setRecentTasks] = useState([]);
  const [upcomingTasks, setUpcomingTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, recentResponse, upcomingResponse] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/dashboard/recent-tasks`),
        axios.get(`${API}/dashboard/upcoming-tasks`)
      ]);

      setStats(statsResponse.data);
      setRecentTasks(recentResponse.data);
      setUpcomingTasks(upcomingResponse.data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "No due date";
    return new Date(dateString).toLocaleDateString();
  };

  const getPriorityClass = (priority) => {
    const classes = {
      low: "priority-low",
      medium: "priority-medium",
      high: "priority-high"
    };
    return `priority-badge ${classes[priority] || classes.medium}`;
  };

  const getStatusClass = (status) => {
    const classes = {
      todo: "status-todo",
      in_progress: "status-in-progress",
      completed: "status-completed"
    };
    return `status-badge ${classes[status] || classes.todo}`;
  };

  const getTaskCardClass = (status) => {
    const classes = {
      todo: "task-card-todo",
      in_progress: "task-card-in-progress",
      completed: "task-card-completed"
    };
    return `task-card ${classes[status] || classes.todo}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 fade-in">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="stats-card stats-card-total">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm font-medium">Total Tasks</p>
              <p className="text-3xl font-bold text-white">{stats.total_tasks}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-full">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
        </div>

        <div className="stats-card stats-card-completed">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm font-medium">Completed</p>
              <p className="text-3xl font-bold text-white">{stats.completed_tasks}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-full">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </div>

        <div className="stats-card stats-card-pending">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm font-medium">Pending</p>
              <p className="text-3xl font-bold text-white">{stats.pending_tasks}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-full">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="stats-card stats-card-overdue">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm font-medium">Overdue</p>
              <p className="text-3xl font-bold text-white">{stats.overdue_tasks}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-full">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.96-.833-2.73 0L3.084 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="stats-card stats-card-today">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm font-medium">Due Today</p>
              <p className="text-3xl font-bold text-white">{stats.today_tasks}</p>
            </div>
            <div className="p-3 bg-white/20 rounded-full">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2-2v16a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Recent and Upcoming Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Tasks */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Recent Tasks</h2>
            <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="space-y-4">
            {recentTasks.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No recent tasks found</p>
            ) : (
              recentTasks.map((task) => (
                <div key={task.id} className={getTaskCardClass(task.status)}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800 mb-1">{task.title}</h3>
                      {task.description && (
                        <p className="text-gray-600 text-sm mb-2">{task.description}</p>
                      )}
                      <div className="flex items-center space-x-2">
                        <span className={getPriorityClass(task.priority)}>
                          {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                        </span>
                        <span className={getStatusClass(task.status)}>
                          {task.status.replace('_', ' ').charAt(0).toUpperCase() + task.status.replace('_', ' ').slice(1)}
                        </span>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      <p>{formatDate(task.due_date)}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Upcoming Tasks */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Upcoming Tasks</h2>
            <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2-2v16a2 2 0 002 2z" />
            </svg>
          </div>
          <div className="space-y-4">
            {upcomingTasks.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No upcoming tasks found</p>
            ) : (
              upcomingTasks.map((task) => (
                <div key={task.id} className={getTaskCardClass(task.status)}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800 mb-1">{task.title}</h3>
                      {task.description && (
                        <p className="text-gray-600 text-sm mb-2">{task.description}</p>
                      )}
                      <div className="flex items-center space-x-2">
                        <span className={getPriorityClass(task.priority)}>
                          {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                        </span>
                        <span className={getStatusClass(task.status)}>
                          {task.status.replace('_', ' ').charAt(0).toUpperCase() + task.status.replace('_', ' ').slice(1)}
                        </span>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      <p>{formatDate(task.due_date)}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;