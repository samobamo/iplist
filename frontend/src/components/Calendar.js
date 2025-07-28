import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [tasks, setTasks] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    priority: "medium"
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCalendarTasks();
  }, [currentDate]);

  const fetchCalendarTasks = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/calendar/tasks`, {
        params: {
          month: currentDate.getMonth() + 1,
          year: currentDate.getFullYear()
        }
      });
      setTasks(response.data);
    } catch (error) {
      console.error("Error fetching calendar tasks:", error);
    } finally {
      setLoading(false);
    }
  };

  const createTask = async () => {
    if (!newTask.title.trim() || !selectedDate) return;

    try {
      await axios.post(`${API}/tasks`, {
        ...newTask,
        due_date: selectedDate.toISOString().split('T')[0]
      });
      
      setNewTask({ title: "", description: "", priority: "medium" });
      setShowTaskModal(false);
      setSelectedDate(null);
      fetchCalendarTasks();
    } catch (error) {
      console.error("Error creating task:", error);
    }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      const prevMonthDay = new Date(year, month, -startingDayOfWeek + i + 1);
      days.push({ date: prevMonthDay, isCurrentMonth: false });
    }
    
    // Add days of the current month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push({ date: new Date(year, month, day), isCurrentMonth: true });
    }
    
    // Add empty cells for days after the last day of the month
    const remainingCells = 42 - days.length; // 6 rows * 7 days
    for (let i = 1; i <= remainingCells; i++) {
      const nextMonthDay = new Date(year, month + 1, i);
      days.push({ date: nextMonthDay, isCurrentMonth: false });
    }
    
    return days;
  };

  const getTasksForDate = (date) => {
    const dateString = date.toISOString().split('T')[0];
    return tasks.filter(task => task.due_date === dateString);
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const handleDateClick = (date) => {
    if (!date.isCurrentMonth) return;
    setSelectedDate(date.date);
    setShowTaskModal(true);
  };

  const getTaskDotClass = (status) => {
    const classes = {
      todo: "calendar-task-dot-todo",
      in_progress: "calendar-task-dot-in-progress",
      completed: "calendar-task-dot-completed"
    };
    return `calendar-task-dot ${classes[status] || classes.todo}`;
  };

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <div className="space-y-6 fade-in">
      {/* Calendar Container */}
      <div className="calendar-container">
        {/* Calendar Header */}
        <div className="calendar-header">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigateMonth(-1)}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <h2 className="text-2xl font-bold">
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </h2>
            
            <button
              onClick={() => navigateMonth(1)}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="calendar-grid">
          {/* Day Headers */}
          {dayNames.map((day) => (
            <div key={day} className="calendar-day-header">
              {day}
            </div>
          ))}

          {/* Calendar Days */}
          {getDaysInMonth(currentDate).map((day, index) => {
            const dayTasks = getTasksForDate(day.date);
            const isCurrentDay = isToday(day.date);
            
            return (
              <div
                key={index}
                onClick={() => handleDateClick(day)}
                className={`calendar-day ${
                  isCurrentDay ? "calendar-day-today" : ""
                } ${!day.isCurrentMonth ? "calendar-day-other-month" : ""}`}
              >
                <div className="font-semibold text-sm mb-1">
                  {day.date.getDate()}
                </div>
                
                {/* Task indicators */}
                <div className="space-y-1">
                  {dayTasks.slice(0, 3).map((task) => (
                    <div key={task.id} className="text-xs truncate">
                      <span className={getTaskDotClass(task.status)}></span>
                      {task.title}
                    </div>
                  ))}
                  {dayTasks.length > 3 && (
                    <div className="text-xs text-gray-500">
                      +{dayTasks.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Loading Indicator */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
        </div>
      )}

      {/* Task Creation Modal */}
      {showTaskModal && (
        <div className="modal-overlay" onClick={() => setShowTaskModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-800">
                Add Task for {selectedDate?.toLocaleDateString()}
              </h3>
              <button
                onClick={() => setShowTaskModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="form-label">Task Title</label>
                <input
                  type="text"
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  className="form-input"
                  placeholder="Enter task title..."
                />
              </div>

              <div>
                <label className="form-label">Description (Optional)</label>
                <textarea
                  value={newTask.description}
                  onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  className="form-input"
                  rows={3}
                  placeholder="Enter task description..."
                />
              </div>

              <div>
                <label className="form-label">Priority</label>
                <select
                  value={newTask.priority}
                  onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                  className="form-select"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  onClick={createTask}
                  disabled={!newTask.title.trim()}
                  className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create Task
                </button>
                <button
                  onClick={() => setShowTaskModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar;