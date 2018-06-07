

# Append dict item in list if not exist
def append_dependency_to_list(cursor):
    dependencies = []
    dependencies_set = set()
    for item in cursor:
        if item['dependency'] not in dependencies_set:
            dependencies.append(item['dependency'])
            dependencies_set.add(item['dependency'])
    return dependencies
