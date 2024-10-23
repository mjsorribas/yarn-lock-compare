import re

def parse_yarn_lock(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Usamos expresiones regulares para extraer dependencias y sus versiones
    #dependencies = re.findall(r'^(.*?@npm:.*?)\s*:\s*version\s*:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
    dependencies = re.findall(r'^(.*?@.*?):\s*version\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
    #return {remove_npm_prefix(name.strip()): extract_version(version.strip()) for name, version in dependencies}
    return {extract_name(name.strip()): extract_version(version.strip()) for name, version in dependencies}

def extract_name(dep_name):
    # Elimina cualquier parte después del primer '@' que se usa para la versión
    dep_name = dep_name.replace('"', '').replace("'", "")  # Remueve comillas
    if '@' in dep_name:
        return dep_name.split('@')[0].strip() + '@' + dep_name.split('@')[1].strip()
    return dep_name


def remove_npm_prefix(dep_name):
    # Elimina la parte '@npm:' de la dependencia
    return dep_name.replace('npm:', '')

def extract_version(version_str):
    # Extrae la versión, manejando diferentes formatos
    match = re.match(r'^\s*version\s*:\s*["\']?(.*?)["\']?$', version_str)
    if match:
        return match.group(1).strip()  # Remueve espacios en blanco alrededor
    
    # Si no se captura en el primer formato, intenta con el segundo
    match = re.match(r'^\s*["\']?(.*?)["\']?$', version_str)
    return (match.group(1).strip() if match else version_str.strip()).replace(':', '').strip()

def generate_lock_html(lock_file_path, output_file_name):
    dependencies = parse_yarn_lock(lock_file_path)

    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dependencias de {}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
    </style>
</head>
<body>
    <h1>Dependencias de {}</h1>
    <table>
        <tr>
            <th>Dependencia</th>
            <th>Versión</th>
        </tr>""".format(lock_file_path, lock_file_path)

    for dep, ver in dependencies.items():
        html_content += f"""
        <tr>
            <td>{dep}</td>
            <td>{ver}</td>
        </tr>"""

    html_content += """
    </table>
</body>
</html>"""

    with open(output_file_name, 'w') as file:
        file.write(html_content)

def compare_locks(yarn_lock, yarnold_lock):
    # Parsear las dependencias de ambos archivos
    yarn_dependencies = parse_yarn_lock(yarn_lock)
    yarnold_dependencies = parse_yarn_lock(yarnold_lock)

    differences = []
    print(yarnold_dependencies)
    # Comparar dependencias que están en ambos archivos
    for dep, old_ver in yarnold_dependencies.items():
        yarn_version = yarn_dependencies.get(dep)
        
        if yarn_version is not None and yarn_version != old_ver:
            differences.append((dep, old_ver, yarn_version))
        elif yarn_version is None:
            differences.append((dep, old_ver, 'N/A'))

    return differences

def generate_html(differences):
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diferencias en Dependencias</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
    </style>
</head>
<body>
    <h1>Diferencias entre yarn.lock y yarnold.lock</h1>
    <table>
        <tr>
            <th>Dependencia</th>
            <th>Versión en yarnold.lock</th>
            <th>Versión en yarn.lock</th>
        </tr>"""
    
    for dep, old_ver, new_ver in differences:
        html_content += f"""
        <tr>
            <td>{dep}</td>
            <td>{old_ver}</td>
            <td>{new_ver}</td>
        </tr>"""

    html_content += """
    </table>
</body>
</html>"""

    with open('diferencias_dependencias.html', 'w') as file:
        file.write(html_content)

if __name__ == "__main__":
    yarn_lock_path = 'yarn.lock'       # Ruta al archivo yarn.lock
    yarnold_lock_path = 'yarnold.lock'  # Ruta al archivo yarnold.lock
    
    differences = compare_locks(yarn_lock_path, yarnold_lock_path)
    generate_html(differences)
    
    if differences:
        print("Archivo HTML generado: diferencias_dependencias.html")
    else:
        print("No se encontraron diferencias de versiones entre los archivos.")

    # Generar HTML para cada archivo de bloqueo
    generate_lock_html(yarn_lock_path, 'dependencias_yarn.html')
    generate_lock_html(yarnold_lock_path, 'dependencias_yarnold.html')