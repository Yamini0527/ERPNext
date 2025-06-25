# Copyright (c) 2024, Custom ERPNext Development
# License: GNU General Public License v3. See license.txt

import frappe
from erpnext.projects.utils import create_sample_development_data

def test_customizations():
	"""Test the customizations for development project management"""
	
	print("Testing ERPNext Project Management Customizations...")
	
	# Test 1: Create sample data
	print("\n1. Creating sample development project data...")
	try:
		result = create_sample_development_data()
		print(f"✓ Sample data created successfully!")
		print(f"  Project: {result['project']}")
		print(f"  Tasks created: {len(result['tasks_created'])}")
	except Exception as e:
		print(f"✗ Error creating sample data: {e}")
		return False
	
	# Test 2: Verify task reviewer field exists
	print("\n2. Testing task reviewer field...")
	try:
		task_doc = frappe.get_doc("Task", result['tasks_created'][0])
		if hasattr(task_doc, 'task_reviewer'):
			print("✓ Task reviewer field exists")
		else:
			print("✗ Task reviewer field not found")
			return False
	except Exception as e:
		print(f"✗ Error testing task reviewer field: {e}")
		return False
	
	# Test 3: Verify dependencies work
	print("\n3. Testing task dependencies...")
	try:
		# Get a task with dependencies
		tasks_with_deps = frappe.get_all("Task", 
			filters={"project": result['project'], "depends_on": ["!=", ""]}, 
			fields=["name", "subject", "depends_on_tasks"])
		
		if tasks_with_deps:
			task = frappe.get_doc("Task", tasks_with_deps[0].name)
			dependency_status = task.get_dependency_status()
			is_blocked = task.is_blocked_by_dependencies()
			print(f"✓ Dependencies working - Task '{task.subject}' has {len(dependency_status)} dependencies")
			print(f"  Blocked by dependencies: {is_blocked}")
		else:
			print("✗ No tasks with dependencies found")
			return False
	except Exception as e:
		print(f"✗ Error testing dependencies: {e}")
		return False
	
	# Test 4: Verify project and task structure
	print("\n4. Testing project and task structure...")
	try:
		project = frappe.get_doc("Project", result['project'])
		tasks = frappe.get_all("Task", filters={"project": result['project']}, fields=["name", "subject", "status", "task_reviewer"])
		
		print(f"✓ Project '{project.project_name}' created successfully")
		print(f"  Total tasks: {len(tasks)}")
		print(f"  Tasks with reviewers: {len([t for t in tasks if t.task_reviewer])}")
		
		# Show task breakdown
		status_counts = {}
		for task in tasks:
			status_counts[task.status] = status_counts.get(task.status, 0) + 1
		
		print("  Task status breakdown:")
		for status, count in status_counts.items():
			print(f"    {status}: {count}")
			
	except Exception as e:
		print(f"✗ Error testing project structure: {e}")
		return False
	
	print("\n✓ All customizations tested successfully!")
	return True

if __name__ == "__main__":
	test_customizations() 