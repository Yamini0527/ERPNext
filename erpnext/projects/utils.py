# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import frappe


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def query_task(doctype, txt, searchfield, start, page_len, filters):
	from frappe.desk.reportview import build_match_conditions

	search_string = "%%%s%%" % txt
	order_by_string = "%s%%" % txt
	match_conditions = build_match_conditions("Task")
	match_conditions = ("and" + match_conditions) if match_conditions else ""

	return frappe.db.sql(
		"""select name, subject from `tabTask`
		where (`{}` like {} or `subject` like {}) {}
		order by
			case when `subject` like {} then 0 else 1 end,
			case when `{}` like {} then 0 else 1 end,
			`{}`,
			subject
		limit {} offset {}""".format(
			searchfield, "%s", "%s", match_conditions, "%s", searchfield, "%s", searchfield, "%s", "%s"
		),
		(search_string, search_string, order_by_string, order_by_string, page_len, start),
	)


@frappe.whitelist()
def create_sample_development_data():
	"""Create sample data for development project management module"""
	
	# Create sample project
	if not frappe.db.exists("Project", "DEV-2024-001"):
		project = frappe.get_doc({
			"doctype": "Project",
			"project_name": "E-Commerce Platform Development",
			"status": "Open",
			"priority": "High",
			"expected_start_date": "2024-01-15",
			"expected_end_date": "2024-06-30",
			"percent_complete_method": "Task Completion",
			"notes": "Development of a modern e-commerce platform with React frontend and Python backend"
		})
		project.insert()
		frappe.db.commit()
		project_name = project.name
	else:
		project_name = "DEV-2024-001"
	
	# Create sample tasks with dependencies and reviewers
	tasks_data = [
		{
			"subject": "Database Schema Design",
			"status": "Completed",
			"priority": "High",
			"exp_start_date": "2024-01-15 09:00:00",
			"exp_end_date": "2024-01-25 17:00:00",
			"progress": 100,
			"task_reviewer": "Administrator",
			"description": "Design the complete database schema for the e-commerce platform including users, products, orders, and payments tables."
		},
		{
			"subject": "Backend API Development",
			"status": "Working",
			"priority": "High",
			"exp_start_date": "2024-01-26 09:00:00",
			"exp_end_date": "2024-03-15 17:00:00",
			"progress": 60,
			"task_reviewer": "Administrator",
			"description": "Develop RESTful APIs for user management, product catalog, shopping cart, and order processing."
		},
		{
			"subject": "Frontend UI Development",
			"status": "Working",
			"priority": "High",
			"exp_start_date": "2024-02-01 09:00:00",
			"exp_end_date": "2024-04-15 17:00:00",
			"progress": 45,
			"task_reviewer": "Administrator",
			"description": "Build responsive React frontend with modern UI components and state management."
		},
		{
			"subject": "Payment Gateway Integration",
			"status": "Pending Review",
			"priority": "Medium",
			"exp_start_date": "2024-03-01 09:00:00",
			"exp_end_date": "2024-03-30 17:00:00",
			"progress": 90,
			"task_reviewer": "Administrator",
			"description": "Integrate Stripe payment gateway for secure online payments."
		},
		{
			"subject": "Testing and Quality Assurance",
			"status": "Open",
			"priority": "Medium",
			"exp_start_date": "2024-04-16 09:00:00",
			"exp_end_date": "2024-05-15 17:00:00",
			"progress": 0,
			"task_reviewer": "Administrator",
			"description": "Comprehensive testing including unit tests, integration tests, and user acceptance testing."
		},
		{
			"subject": "Deployment and Launch",
			"status": "Open",
			"priority": "High",
			"exp_start_date": "2024-05-16 09:00:00",
			"exp_end_date": "2024-06-30 17:00:00",
			"progress": 0,
			"task_reviewer": "Administrator",
			"description": "Deploy the application to production servers and launch the e-commerce platform."
		}
	]
	
	created_tasks = []
	
	for task_data in tasks_data:
		if not frappe.db.exists("Task", {"subject": task_data["subject"], "project": project_name}):
			task = frappe.get_doc({
				"doctype": "Task",
				"project": project_name,
				**task_data
			})
			task.insert()
			created_tasks.append(task.name)
	
	frappe.db.commit()
	
	# Set up dependencies
	dependencies = [
		("Backend API Development", "Database Schema Design"),
		("Frontend UI Development", "Database Schema Design"),
		("Payment Gateway Integration", "Backend API Development"),
		("Testing and Quality Assurance", "Frontend UI Development"),
		("Testing and Quality Assurance", "Payment Gateway Integration"),
		("Deployment and Launch", "Testing and Quality Assurance")
	]
	
	for dependent_task, parent_task in dependencies:
		dependent_task_name = frappe.db.get_value("Task", {"subject": dependent_task, "project": project_name}, "name")
		parent_task_name = frappe.db.get_value("Task", {"subject": parent_task, "project": project_name}, "name")
		
		if dependent_task_name and parent_task_name:
			task_doc = frappe.get_doc("Task", dependent_task_name)
			# Check if dependency already exists
			existing_deps = [d.task for d in task_doc.depends_on]
			if parent_task_name not in existing_deps:
				task_doc.append("depends_on", {"task": parent_task_name})
				task_doc.save()
	
	frappe.db.commit()
	
	return {
		"project": project_name,
		"tasks_created": created_tasks,
		"message": "Sample development project data created successfully!"
	}
