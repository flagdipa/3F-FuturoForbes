# Proposal: Sistema de Verificación E2E Multi-Agente con Orquestador

## What
Crear y modelar un flujo de pruebas End-to-End en el que diferentes instancias o agentes de IA asuman roles de "Workers" dedicados a auditar módulos específicos del sistema 3F de forma asíncrona o simultánea (Ej: un agente para Login, otro para Entidades, etc.). Se establecerá la figura de un "Agente Orquestador" que consolidará y organizará todos los problemas encontrados.

## Why
Probar exhaustivamente un sistema tan grande es complejo y puede abrumar ("sobrecargar el contexto") de un solo modelo. Dividir el trabajo entre varios asistentes virtuales que actúan de manera paralela o enfocada es muchísimo más eficiente. El Orquestador coordinará los hallazgos y evitará conflictos, armando finalmente un reporte maestro (`master_bug_report.md`) que sirva de base para las correcciones en todo el Frontend.

## Impact
- **Nivel Trabajo**: Paraleliza la ejecución visual y la validación en código, ahorrando tiempo.
- **Nivel Proyecto**: Produce reportes modulares y un reporte final consolidado de la salud del Frontend y Backend.
- **Escalabilidad**: Sienta el estándar sobre cómo distintos modelos pueden colaborar leyendo/escribiendo el mismo archivo de tareas (`tasks.md`).
