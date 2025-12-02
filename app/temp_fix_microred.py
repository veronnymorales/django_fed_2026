import sys

file_path = r'd:\2025\FED 2025-2026\django_fed_2026\app\s11_captacion_gestante\views.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Modificar las líneas específicas (índice 0-based, por lo que línea 1344 es índice 1343)
lines[1343] = "            'provincia': '',  # No filtrar por provincia\r\n"
lines[1344] = "            'distrito': '',   # No filtrar por distrito\r\n"
lines[1347] = "            'establecimiento': '',  # No filtrar por establecimiento\r\n"
lines[1348] = "            'cumple': '',     # No filtrar por cumple\r\n"

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Archivo modificado exitosamente')
print('Se han actualizado las líneas 1344, 1345, 1348 y 1349')
print('Ahora el reporte de microredes solo filtrará por RED y MICRORED')
