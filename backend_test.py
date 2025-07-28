#!/usr/bin/env python3
"""
Backend API Testing for Time Management Application
Tests all CRUD operations, dashboard stats, calendar endpoints, and edge cases
"""

import requests
import json
from datetime import datetime, date, timedelta
import uuid
import sys

# Backend URL from environment
BACKEND_URL = "https://d04443a0-7860-4a98-b40f-49067dd77d82.preview.emergentagent.com/api"

class TimeManagementAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.created_task_ids = []
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_result(self, test_name, success, message=""):
        if success:
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED - {message}")
    
    def cleanup_created_tasks(self):
        """Clean up tasks created during testing"""
        for task_id in self.created_task_ids:
            try:
                requests.delete(f"{self.base_url}/tasks/{task_id}")
            except:
                pass
    
    def test_api_health(self):
        """Test if API is accessible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.log_result("API Health Check", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_result("API Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_task_crud_operations(self):
        """Test complete CRUD operations for tasks"""
        print("\n=== Testing Task CRUD Operations ===")
        
        # Test 1: Create task with all fields
        task_data = {
            "title": "Complete project proposal",
            "description": "Finalize the Q1 project proposal with budget details",
            "due_date": (date.today() + timedelta(days=7)).isoformat(),
            "priority": "high"
        }
        
        try:
            response = requests.post(f"{self.base_url}/tasks", json=task_data)
            if response.status_code == 200:
                task = response.json()
                self.created_task_ids.append(task['id'])
                self.log_result("Create Task (Full Data)", True, f"ID: {task['id']}")
                
                # Verify task structure
                required_fields = ['id', 'title', 'status', 'priority', 'created_at', 'updated_at']
                missing_fields = [field for field in required_fields if field not in task]
                if missing_fields:
                    self.log_result("Task Structure Validation", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Task Structure Validation", True)
                
                # Test 2: Read the created task
                get_response = requests.get(f"{self.base_url}/tasks/{task['id']}")
                if get_response.status_code == 200:
                    retrieved_task = get_response.json()
                    if retrieved_task['title'] == task_data['title']:
                        self.log_result("Read Single Task", True)
                    else:
                        self.log_result("Read Single Task", False, "Data mismatch")
                else:
                    self.log_result("Read Single Task", False, f"Status: {get_response.status_code}")
                
                # Test 3: Update task
                update_data = {
                    "status": "in_progress",
                    "description": "Updated description with progress notes"
                }
                update_response = requests.put(f"{self.base_url}/tasks/{task['id']}", json=update_data)
                if update_response.status_code == 200:
                    updated_task = update_response.json()
                    if updated_task['status'] == 'in_progress':
                        self.log_result("Update Task", True)
                    else:
                        self.log_result("Update Task", False, "Status not updated")
                else:
                    self.log_result("Update Task", False, f"Status: {update_response.status_code}")
                
            else:
                self.log_result("Create Task (Full Data)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Create Task (Full Data)", False, f"Exception: {str(e)}")
        
        # Test 4: Create task with minimal data
        minimal_task = {"title": "Review meeting notes"}
        try:
            response = requests.post(f"{self.base_url}/tasks", json=minimal_task)
            if response.status_code == 200:
                task = response.json()
                self.created_task_ids.append(task['id'])
                self.log_result("Create Task (Minimal Data)", True)
                
                # Verify defaults
                if task['status'] == 'todo' and task['priority'] == 'medium':
                    self.log_result("Default Values Check", True)
                else:
                    self.log_result("Default Values Check", False, f"Status: {task['status']}, Priority: {task['priority']}")
            else:
                self.log_result("Create Task (Minimal Data)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Create Task (Minimal Data)", False, f"Exception: {str(e)}")
        
        # Test 5: Get all tasks
        try:
            response = requests.get(f"{self.base_url}/tasks")
            if response.status_code == 200:
                tasks = response.json()
                if isinstance(tasks, list) and len(tasks) >= 2:
                    self.log_result("Get All Tasks", True, f"Found {len(tasks)} tasks")
                else:
                    self.log_result("Get All Tasks", False, f"Expected list with >=2 tasks, got {len(tasks) if isinstance(tasks, list) else 'non-list'}")
            else:
                self.log_result("Get All Tasks", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Get All Tasks", False, f"Exception: {str(e)}")
        
        # Test 6: Test error handling - invalid task ID
        try:
            response = requests.get(f"{self.base_url}/tasks/invalid-id")
            if response.status_code == 404:
                self.log_result("Error Handling (Invalid ID)", True)
            else:
                self.log_result("Error Handling (Invalid ID)", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling (Invalid ID)", False, f"Exception: {str(e)}")
        
        # Test 7: Delete task
        if self.created_task_ids:
            task_to_delete = self.created_task_ids[0]
            try:
                response = requests.delete(f"{self.base_url}/tasks/{task_to_delete}")
                if response.status_code == 200:
                    self.log_result("Delete Task", True)
                    self.created_task_ids.remove(task_to_delete)
                    
                    # Verify deletion
                    get_response = requests.get(f"{self.base_url}/tasks/{task_to_delete}")
                    if get_response.status_code == 404:
                        self.log_result("Verify Task Deletion", True)
                    else:
                        self.log_result("Verify Task Deletion", False, "Task still exists")
                else:
                    self.log_result("Delete Task", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Delete Task", False, f"Exception: {str(e)}")
    
    def test_dashboard_statistics(self):
        """Test dashboard statistics API"""
        print("\n=== Testing Dashboard Statistics ===")
        
        # Create test tasks with different statuses and dates
        test_tasks = [
            {
                "title": "Overdue task",
                "due_date": (date.today() - timedelta(days=2)).isoformat(),
                "status": "todo",
                "priority": "high"
            },
            {
                "title": "Today's task",
                "due_date": date.today().isoformat(),
                "status": "in_progress",
                "priority": "medium"
            },
            {
                "title": "Completed task",
                "due_date": (date.today() + timedelta(days=1)).isoformat(),
                "status": "completed",
                "priority": "low"
            },
            {
                "title": "Future task",
                "due_date": (date.today() + timedelta(days=5)).isoformat(),
                "status": "todo",
                "priority": "medium"
            }
        ]
        
        # Create test tasks
        created_for_stats = []
        for task_data in test_tasks:
            try:
                response = requests.post(f"{self.base_url}/tasks", json=task_data)
                if response.status_code == 200:
                    task = response.json()
                    created_for_stats.append(task['id'])
                    self.created_task_ids.append(task['id'])
            except Exception as e:
                print(f"Failed to create test task: {e}")
        
        # Test dashboard stats
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                required_stats = ['total_tasks', 'completed_tasks', 'pending_tasks', 'overdue_tasks', 'today_tasks']
                
                if all(stat in stats for stat in required_stats):
                    self.log_result("Dashboard Stats Structure", True)
                    
                    # Verify stats logic
                    if stats['total_tasks'] >= len(created_for_stats):
                        self.log_result("Total Tasks Count", True, f"Total: {stats['total_tasks']}")
                    else:
                        self.log_result("Total Tasks Count", False, f"Expected >= {len(created_for_stats)}, got {stats['total_tasks']}")
                    
                    if stats['completed_tasks'] >= 1:  # We created 1 completed task
                        self.log_result("Completed Tasks Count", True, f"Completed: {stats['completed_tasks']}")
                    else:
                        self.log_result("Completed Tasks Count", False, f"Expected >= 1, got {stats['completed_tasks']}")
                    
                    if stats['pending_tasks'] >= 3:  # We created 3 non-completed tasks
                        self.log_result("Pending Tasks Count", True, f"Pending: {stats['pending_tasks']}")
                    else:
                        self.log_result("Pending Tasks Count", False, f"Expected >= 3, got {stats['pending_tasks']}")
                    
                    if stats['overdue_tasks'] >= 1:  # We created 1 overdue task
                        self.log_result("Overdue Tasks Count", True, f"Overdue: {stats['overdue_tasks']}")
                    else:
                        self.log_result("Overdue Tasks Count", False, f"Expected >= 1, got {stats['overdue_tasks']}")
                    
                    if stats['today_tasks'] >= 1:  # We created 1 today task
                        self.log_result("Today Tasks Count", True, f"Today: {stats['today_tasks']}")
                    else:
                        self.log_result("Today Tasks Count", False, f"Expected >= 1, got {stats['today_tasks']}")
                        
                else:
                    missing_stats = [stat for stat in required_stats if stat not in stats]
                    self.log_result("Dashboard Stats Structure", False, f"Missing: {missing_stats}")
            else:
                self.log_result("Dashboard Stats API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Dashboard Stats API", False, f"Exception: {str(e)}")
    
    def test_recent_and_upcoming_tasks(self):
        """Test recent and upcoming tasks endpoints"""
        print("\n=== Testing Recent and Upcoming Tasks ===")
        
        # Test recent tasks
        try:
            response = requests.get(f"{self.base_url}/dashboard/recent-tasks")
            if response.status_code == 200:
                recent_tasks = response.json()
                if isinstance(recent_tasks, list):
                    self.log_result("Recent Tasks API", True, f"Found {len(recent_tasks)} recent tasks")
                    
                    # Verify limit (should be max 5)
                    if len(recent_tasks) <= 5:
                        self.log_result("Recent Tasks Limit", True)
                    else:
                        self.log_result("Recent Tasks Limit", False, f"Expected <= 5, got {len(recent_tasks)}")
                else:
                    self.log_result("Recent Tasks API", False, "Response is not a list")
            else:
                self.log_result("Recent Tasks API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Recent Tasks API", False, f"Exception: {str(e)}")
        
        # Test upcoming tasks
        try:
            response = requests.get(f"{self.base_url}/dashboard/upcoming-tasks")
            if response.status_code == 200:
                upcoming_tasks = response.json()
                if isinstance(upcoming_tasks, list):
                    self.log_result("Upcoming Tasks API", True, f"Found {len(upcoming_tasks)} upcoming tasks")
                    
                    # Verify limit (should be max 5)
                    if len(upcoming_tasks) <= 5:
                        self.log_result("Upcoming Tasks Limit", True)
                    else:
                        self.log_result("Upcoming Tasks Limit", False, f"Expected <= 5, got {len(upcoming_tasks)}")
                    
                    # Verify upcoming tasks are not completed and have future due dates
                    valid_upcoming = True
                    for task in upcoming_tasks:
                        if task.get('status') == 'completed':
                            valid_upcoming = False
                            break
                        if task.get('due_date'):
                            task_date = datetime.fromisoformat(task['due_date']).date()
                            if task_date < date.today():
                                valid_upcoming = False
                                break
                    
                    if valid_upcoming:
                        self.log_result("Upcoming Tasks Logic", True)
                    else:
                        self.log_result("Upcoming Tasks Logic", False, "Contains completed or past due tasks")
                        
                else:
                    self.log_result("Upcoming Tasks API", False, "Response is not a list")
            else:
                self.log_result("Upcoming Tasks API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Upcoming Tasks API", False, f"Exception: {str(e)}")
    
    def test_calendar_api(self):
        """Test calendar API endpoints"""
        print("\n=== Testing Calendar API ===")
        
        # Create tasks for specific months
        current_date = date.today()
        next_month = current_date.replace(day=15) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        
        calendar_tasks = [
            {
                "title": "Current month task",
                "due_date": current_date.replace(day=15).isoformat(),
                "priority": "medium"
            },
            {
                "title": "Next month task",
                "due_date": next_month.replace(day=10).isoformat(),
                "priority": "high"
            }
        ]
        
        # Create calendar test tasks
        for task_data in calendar_tasks:
            try:
                response = requests.post(f"{self.base_url}/tasks", json=task_data)
                if response.status_code == 200:
                    task = response.json()
                    self.created_task_ids.append(task['id'])
            except Exception as e:
                print(f"Failed to create calendar test task: {e}")
        
        # Test 1: Get current month tasks
        try:
            response = requests.get(f"{self.base_url}/calendar/tasks")
            if response.status_code == 200:
                tasks = response.json()
                if isinstance(tasks, list):
                    self.log_result("Calendar Tasks (Current Month)", True, f"Found {len(tasks)} tasks")
                else:
                    self.log_result("Calendar Tasks (Current Month)", False, "Response is not a list")
            else:
                self.log_result("Calendar Tasks (Current Month)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Calendar Tasks (Current Month)", False, f"Exception: {str(e)}")
        
        # Test 2: Get specific month tasks
        try:
            response = requests.get(f"{self.base_url}/calendar/tasks?month={next_month.month}&year={next_month.year}")
            if response.status_code == 200:
                tasks = response.json()
                if isinstance(tasks, list):
                    self.log_result("Calendar Tasks (Specific Month)", True, f"Found {len(tasks)} tasks for {next_month.month}/{next_month.year}")
                    
                    # Verify tasks are from the correct month
                    correct_month = True
                    for task in tasks:
                        if task.get('due_date'):
                            task_date = datetime.fromisoformat(task['due_date']).date()
                            if task_date.month != next_month.month or task_date.year != next_month.year:
                                correct_month = False
                                break
                    
                    if correct_month:
                        self.log_result("Calendar Month Filtering", True)
                    else:
                        self.log_result("Calendar Month Filtering", False, "Tasks from wrong month returned")
                        
                else:
                    self.log_result("Calendar Tasks (Specific Month)", False, "Response is not a list")
            else:
                self.log_result("Calendar Tasks (Specific Month)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Calendar Tasks (Specific Month)", False, f"Exception: {str(e)}")
        
        # Test 3: Test edge case - invalid month
        try:
            response = requests.get(f"{self.base_url}/calendar/tasks?month=13&year=2024")
            # This should either handle gracefully or return an error
            if response.status_code in [200, 400]:
                self.log_result("Calendar Invalid Month Handling", True, f"Status: {response.status_code}")
            else:
                self.log_result("Calendar Invalid Month Handling", False, f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Calendar Invalid Month Handling", False, f"Exception: {str(e)}")
    
    def test_edge_cases(self):
        """Test various edge cases"""
        print("\n=== Testing Edge Cases ===")
        
        # Test 1: Task without due date
        task_no_date = {
            "title": "Task without due date",
            "description": "This task has no specific deadline",
            "priority": "low"
        }
        
        try:
            response = requests.post(f"{self.base_url}/tasks", json=task_no_date)
            if response.status_code == 200:
                task = response.json()
                self.created_task_ids.append(task['id'])
                if task.get('due_date') is None:
                    self.log_result("Task Without Due Date", True)
                else:
                    self.log_result("Task Without Due Date", False, f"Expected null due_date, got {task.get('due_date')}")
            else:
                self.log_result("Task Without Due Date", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Task Without Due Date", False, f"Exception: {str(e)}")
        
        # Test 2: All priority levels
        priorities = ["low", "medium", "high"]
        for priority in priorities:
            task_data = {
                "title": f"Task with {priority} priority",
                "priority": priority
            }
            try:
                response = requests.post(f"{self.base_url}/tasks", json=task_data)
                if response.status_code == 200:
                    task = response.json()
                    self.created_task_ids.append(task['id'])
                    if task['priority'] == priority:
                        self.log_result(f"Priority Level ({priority})", True)
                    else:
                        self.log_result(f"Priority Level ({priority})", False, f"Expected {priority}, got {task['priority']}")
                else:
                    self.log_result(f"Priority Level ({priority})", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Priority Level ({priority})", False, f"Exception: {str(e)}")
        
        # Test 3: All status levels
        if self.created_task_ids:
            statuses = ["todo", "in_progress", "completed"]
            task_id = self.created_task_ids[-1]  # Use last created task
            
            for status in statuses:
                try:
                    response = requests.put(f"{self.base_url}/tasks/{task_id}", json={"status": status})
                    if response.status_code == 200:
                        task = response.json()
                        if task['status'] == status:
                            self.log_result(f"Status Update ({status})", True)
                        else:
                            self.log_result(f"Status Update ({status})", False, f"Expected {status}, got {task['status']}")
                    else:
                        self.log_result(f"Status Update ({status})", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.log_result(f"Status Update ({status})", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Time Management API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Check API health first
        if not self.test_api_health():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        try:
            # Run all test suites
            self.test_task_crud_operations()
            self.test_dashboard_statistics()
            self.test_recent_and_upcoming_tasks()
            self.test_calendar_api()
            self.test_edge_cases()
            
        finally:
            # Cleanup
            print("\n=== Cleaning Up Test Data ===")
            self.cleanup_created_tasks()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"  • {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = TimeManagementAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)