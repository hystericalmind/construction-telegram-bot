import gsheets_manager

# Удаляем все проекты из листа projects
projects = gsheets_manager.get_all_projects()
for project in projects:
    success, message = gsheets_manager.delete_project(project['name'])
    print(f"{project['name']}: {message}")

print("✅ Очистка завершена")