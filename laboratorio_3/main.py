# main.py

import os
import platform
import time
from datetime import datetime

import matplotlib
import numpy as np
import pandas as pd

from experimentos.benchmark import Benchmark
from experimentos.graficador import Graficador
from experimentos.informe import generar_informe


def _informacion_equipo():
    cpu = ''
    if os.path.exists('/proc/cpuinfo'):
        with open('/proc/cpuinfo', encoding='utf-8') as archivo:
            for linea in archivo:
                if linea.lower().startswith('model name'):
                    cpu = linea.split(':', 1)[1].strip()
                    break

    try:
        memoria = (
            os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024 ** 3)
        )
    except (ValueError, OSError):
        memoria = 0.0

    return {
        'cpu': cpu or platform.processor() or 'No disponible',
        'nucleos': os.cpu_count() or 0,
        'memoria_gib': memoria,
    }

def main():
    inicio = time.perf_counter()
    print("=== Iniciando Experimentos del Laboratorio 3 ===")
    print(f"Python: {platform.python_version()} | Sistema: {platform.platform()}")
    
    # Parámetros del experimento
    k_repeticiones = 5
    rangos_m = [1000, 2500, 5000]
    rangos_n = [100, 500, 1000, 2500, 5000, 10000]
    semilla = 2026
    bench = Benchmark(
        k_repeticiones=k_repeticiones,
        m_busquedas=max(rangos_m),
        semilla=semilla,
    )
    print(
        f"K={k_repeticiones}, N={rangos_n}, M={rangos_m}, semilla={semilla}"
    )
    datos_crudos = bench.ejecutar_experimentos(rangos_n, rangos_m)
    resumen = bench.calcular_resumen(datos_crudos)

    os.makedirs("resultados", exist_ok=True)
    datos_crudos.to_csv("resultados/datos_crudos.csv", index=False)
    resumen.to_csv("resultados/resumen_estadistico.csv", index=False)
    print("✓ Mediciones guardadas en 'resultados/datos_crudos.csv'")
    print("✓ Estadísticas guardadas en 'resultados/resumen_estadistico.csv'")

    graficador = Graficador()
    graficador.generar_todas(resumen)
    print("✓ Seis gráficas temáticas guardadas en 'resultados/graficas/'")

    duracion = time.perf_counter() - inicio
    metadatos = {
        **_informacion_equipo(),
        'fecha': datetime.now().astimezone().isoformat(timespec='seconds'),
        'sistema': platform.platform(),
        'python': platform.python_version(),
        'numpy': np.__version__,
        'pandas': pd.__version__,
        'matplotlib': matplotlib.__version__,
        'rangos_n': rangos_n,
        'rangos_m': rangos_m,
        'semilla': semilla,
        'duracion_s': duracion,
    }
    generar_informe(resumen, metadatos, 'resultados/informe_experimento.md')
    print("✓ Informe guardado en 'resultados/informe_experimento.md'")
    print(f"Duración total (benchmark, CSV y gráficas): {duracion:.2f} s ({duracion / 60:.2f} min)")
    if not 1 <= duracion <= 300:
        print("ADVERTENCIA: la duración queda fuera del intervalo recomendado de 1 a 300 segundos.")
    print("\n¡Experimento completado con éxito!")

if __name__ == "__main__":
    main()