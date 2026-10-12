# experimentos/graficador.py

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd


def _entero_es(valor):
    return f'{int(valor):,}'.replace(',', '.')


class Graficador:
    def __init__(self, ruta_salida: str = "resultados/graficas"):
        self.ruta_salida = ruta_salida
        os.makedirs(self.ruta_salida, exist_ok=True)
        plt.rcParams.update({'font.size': 8, 'axes.titlesize': 9, 'axes.labelsize': 8})

    def generar_todas(self, df: pd.DataFrame):
        graficas_anteriores = [
            '1_complejidad_teorica_busqueda.png',
            '2_degeneracion_abb.png',
            '3_altura_vs_tiempo.png',
            '4_costos_constantes_n_pequeno.png',
            '5_evaluacion_insercion.png',
            '6_evaluacion_listado.png',
            'resumen_experimentos.png',
        ]
        for nombre in graficas_anteriores:
            ruta = os.path.join(self.ruta_salida, nombre)
            if os.path.exists(ruta):
                os.remove(ruta)
            m_maximo = int(df.loc[df['Operacion'] == 'Busqueda', 'M'].max())
        self._grafica_vs_n(df, 'Busqueda', 'Busqueda_vs_N.png',
                       'Búsqueda: cómo escala con N', m_maximo)
        self._grafica_vs_n(df, 'Insercion', 'Insercion_vs_N.png',
                           'Inserción: cómo escala con N')
        self._grafica_vs_n(df, 'Listado', 'Listado_vs_N.png',
                           'Listado ordenado: cómo escala con N')
        self._grafica_vs_m(df, 'Busqueda_vs_M.png')
        self._grafica_variabilidad(df, 'Variabilidad_busqueda.png')
        self._grafica_altura_tiempo(df, 'Altura_vs_busqueda_ABB.png')

    def _grafica_vs_n(self, df, operacion, archivo, titulo, m_busquedas=0):
        datos = df[(df['Operacion'] == operacion) & (df['M'] == m_busquedas)]
        estructuras = ['Lista', 'ABB', 'BPlus']
        colores = {'Lista': '#d55e00', 'ABB': '#0072b2', 'BPlus': '#009e73'}
        casos = [('aleatorio', 'IDs aleatorios'), ('ordenado', 'IDs ordenados')]
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

        for ax, (caso, etiqueta) in zip(axes, casos):
            for estructura in estructuras:
                sub = datos[(datos['Caso'] == caso) & (datos['Estructura'] == estructura)].sort_values('N')
                if sub.empty:
                    continue
                self._dibujar_promedio(ax, sub, 'N', colores[estructura], estructura)
            ax.set_title(etiqueta, fontweight='bold')
            ax.set_xlabel('Estudiantes (N)')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.grid(True, which='both', linestyle=':', alpha=0.45)

        axes[0].set_ylabel('Tiempo promedio (s)')
        handles = [plt.Line2D([0], [0], color=colores[n], marker='o', label=n)
                   for n in estructuras]
        fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False,
                   bbox_to_anchor=(0.5, 0.92))
        k = int(datos['Repeticiones'].min()) if not datos.empty else 0
        subtitulo = f'K={k} corridas | barras: desviación estándar'
        if operacion == 'Busqueda':
            subtitulo += f' | M={m_busquedas} búsquedas por corrida'
        fig.suptitle(titulo, fontsize=15, fontweight='bold', y=0.99)
        fig.text(0.5, 0.04, subtitulo, ha='center', fontsize=9)
        fig.tight_layout(rect=[0.04, 0.08, 0.98, 0.84])
        fig.savefig(os.path.join(self.ruta_salida, archivo), dpi=220)
        plt.close(fig)

    @staticmethod
    def _dibujar_promedio(ax, sub, eje_x, color, etiqueta):
        promedio = sub['Promedio_s'].to_numpy()
        desviacion = sub['Desviacion_estandar_s'].to_numpy()
        error_inferior = (promedio - np.minimum(desviacion, promedio * 0.95))
        ax.errorbar(
            sub[eje_x], promedio, yerr=[error_inferior, desviacion],
            color=color, marker='o', linewidth=1.8, markersize=4,
            capsize=2, label=etiqueta,
        )

    def _grafica_vs_m(self, df, archivo):
        datos = df[(df['Operacion'] == 'Busqueda') & (df['N'] == df['N'].max())]
        estructuras = ['Lista', 'ABB', 'BPlus']
        colores = {'Lista': '#d55e00', 'ABB': '#0072b2', 'BPlus': '#009e73'}
        casos = [('aleatorio', 'IDs aleatorios'), ('ordenado', 'IDs ordenados')]
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

        for ax, (caso, etiqueta) in zip(axes, casos):
            for estructura in estructuras:
                sub = datos[(datos['Caso'] == caso) & (datos['Estructura'] == estructura)].sort_values('M')
                if sub.empty:
                    continue
                self._dibujar_promedio(ax, sub, 'M', colores[estructura], estructura)
            ax.set_title(etiqueta, fontweight='bold')
            ax.set_xlabel('Búsquedas por corrida (M)')
            ax.set_xticks(sorted(datos['M'].unique()))
            ax.set_yscale('log')
            ax.grid(True, which='both', linestyle=':', alpha=0.45)

        axes[0].set_ylabel('Tiempo total de búsqueda (s)')
        handles = [plt.Line2D([0], [0], color=colores[n], marker='o', label=n)
                   for n in estructuras]
        fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False,
                   bbox_to_anchor=(0.5, 0.92))
        k = int(datos['Repeticiones'].min()) if not datos.empty else 0
        fig.suptitle(f'Efecto de M en la búsqueda (N={int(df["N"].max()):,})'.replace(',', '.'),
                     fontsize=15, fontweight='bold', y=0.99)
        fig.text(0.5, 0.04, f'K={k} corridas | barras: desviación estándar',
                 ha='center', fontsize=9)
        fig.tight_layout(rect=[0.04, 0.08, 0.98, 0.84])
        fig.savefig(os.path.join(self.ruta_salida, archivo), dpi=220)
        plt.close(fig)

    def _grafica_variabilidad(self, df, archivo):
        n_maximo = df['N'].max()
        m_maximo = df.loc[df['Operacion'] == 'Busqueda', 'M'].max()
        datos = df[
            (df['Operacion'] == 'Busqueda')
            & (df['N'] == n_maximo)
            & (df['M'] == m_maximo)
        ]
        estructuras = ['Lista', 'ABB', 'BPlus']
        colores = {'Lista': '#d55e00', 'ABB': '#0072b2', 'BPlus': '#009e73'}
        casos = [('aleatorio', 'IDs aleatorios'), ('ordenado', 'IDs ordenados')]
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)

        for ax, (caso, etiqueta) in zip(axes, casos):
            sub = datos[datos['Caso'] == caso].set_index('Estructura')
            valores = [sub.loc[n, 'CV_pct'] for n in estructuras]
            barras = ax.bar(
                estructuras, valores,
                color=[colores[n] for n in estructuras], width=0.62,
            )
            ax.bar_label(barras, fmt='%.1f%%', padding=3, fontsize=8)
            ax.set_title(etiqueta, fontweight='bold')
            ax.set_xlabel('Estructura')
            ax.grid(axis='y', linestyle=':', alpha=0.45)
            ax.set_axisbelow(True)

        max_cv = datos['CV_pct'].max()
        axes[0].set_ylim(0, max_cv * 1.2)
        axes[0].set_ylabel('Coeficiente de variación (%)')
        fig.suptitle(
            f'Estabilidad de las búsquedas (N={_entero_es(n_maximo)}, M={_entero_es(m_maximo)})',
            fontsize=14, fontweight='bold', y=0.99,
        )
        k = int(datos['Repeticiones'].min()) if not datos.empty else 0
        fig.text(0.5, 0.03, f'CV = desviación estándar / promedio × 100 | K={k} corridas',
                 ha='center', fontsize=9)
        fig.tight_layout(rect=[0.04, 0.08, 0.98, 0.90])
        fig.savefig(os.path.join(self.ruta_salida, archivo), dpi=220)
        plt.close(fig)

    def _grafica_altura_tiempo(self, df, archivo):
        datos = df[
            (df['Operacion'] == 'Busqueda')
            & (df['M'] == df['M'].max())
            & (df['Estructura'] == 'ABB')
        ]
        colores = {'aleatorio': '#0072b2', 'ordenado': '#d55e00'}
        casos = [('aleatorio', 'IDs aleatorios'), ('ordenado', 'IDs ordenados')]
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

        for ax, (caso, etiqueta) in zip(axes, casos):
            sub = datos[datos['Caso'] == caso].sort_values('N')
            if sub.empty:
                continue
            ax.errorbar(
                sub['Altura_promedio'], sub['Promedio_s'],
                yerr=[
                    sub['Promedio_s'] - (sub['Promedio_s'] - sub['Desviacion_estandar_s']).clip(lower=sub['Promedio_s'] * 0.05),
                    sub['Desviacion_estandar_s'],
                ],
                color=colores[caso], marker='o', linestyle='none', capsize=2,
            )
            desplazamientos = [(6, 7), (6, -10), (6, 9), (6, -12), (6, 12), (6, -14)]
            for indice, (_, fila) in enumerate(sub.iterrows()):
                ax.annotate(f"N={int(fila['N']):,}".replace(',', '.'),
                            (fila['Altura_promedio'], fila['Promedio_s']),
                            xytext=desplazamientos[indice % len(desplazamientos)],
                            textcoords='offset points', fontsize=7)
            ax.set_title(etiqueta, fontweight='bold')
            ax.set_xscale('linear' if caso == 'aleatorio' else 'log')
            ax.set_yscale('log')
            ax.set_xlabel('Altura promedio (niveles)')
            ax.grid(True, which='both', linestyle=':', alpha=0.45)

        axes[0].set_ylabel(f"Tiempo para M={int(datos['M'].max()):,} búsquedas (s)".replace(',', '.'))
        fig.suptitle('ABB: altura del árbol y tiempo de búsqueda',
                     fontsize=15, fontweight='bold', y=0.99)
        fig.text(0.5, 0.04, 'Cada punto indica N; las barras muestran una desviación estándar',
                 ha='center', fontsize=9)
        fig.tight_layout(rect=[0.04, 0.08, 0.98, 0.91])
        fig.savefig(os.path.join(self.ruta_salida, archivo), dpi=220)
        plt.close(fig)

    def _figura_resumen(self, df: pd.DataFrame):
        estructuras = ['Lista', 'ABB', 'BPlus']
        casos = [('aleatorio', '-', 'IDs aleatorios'), ('ordenado', '--', 'IDs ordenados')]
        colores = {'Lista': '#d55e00', 'ABB': '#0072b2', 'BPlus': '#009e73'}
        operaciones = [
            ('Insercion', 'Inserción de N estudiantes'),
            ('Busqueda', 'Búsqueda de M IDs'),
            ('Listado', 'Listado ascendente por ID'),
        ]

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Laboratorio 3 | Rendimiento de las estructuras de búsqueda',
                     fontsize=17, fontweight='bold', y=0.98)

        for ax, (metrica, titulo) in zip(axes.flat[:3], operaciones):
            for estructura in estructuras:
                for caso, estilo, etiqueta_caso in casos:
                    sub = df[(df['Estructura'] == estructura) & (df['Caso'] == caso)].sort_values('N')
                    if sub.empty:
                        continue
                    ax.errorbar(
                        sub['N'], sub[f'{metrica}_Mean'] * 1000,
                        yerr=sub[f'{metrica}_Std'] * 1000,
                        color=colores[estructura], linestyle=estilo, marker='o',
                        markersize=4, linewidth=1.6, capsize=2,
                    )
            ax.set_title(titulo, loc='left', fontweight='bold')
            ax.set_xlabel('Cantidad de estudiantes (N)')
            ax.set_ylabel('Tiempo (milisegundos)')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda valor, _: f'{valor:g}'))
            ax.grid(True, which='both', linestyle=':', alpha=0.45)

        ax_altura = axes.flat[3]
        for estructura in estructuras:
            for caso, estilo, etiqueta_caso in casos:
                sub = df[(df['Estructura'] == estructura) & (df['Caso'] == caso)].sort_values('N')
                if sub.empty:
                    continue
                ax_altura.plot(
                    sub['N'], sub['Altura_Mean'], color=colores[estructura],
                    linestyle=estilo, marker='o', markersize=4, linewidth=1.6,
                )
        ax_altura.set_title('Altura promedio de la estructura', loc='left', fontweight='bold')
        ax_altura.set_xlabel('Cantidad de estudiantes (N)')
        ax_altura.set_ylabel('Altura (niveles)')
        ax_altura.set_xscale('log')
        ax_altura.grid(True, which='both', linestyle=':', alpha=0.45)

        leyenda_estructuras = [
            plt.Line2D([0], [0], color=colores[nombre], marker='o', label=nombre)
            for nombre in estructuras
        ]
        leyenda_casos = [
            plt.Line2D([0], [0], color='#444444', linestyle=estilo, label=etiqueta)
            for _, estilo, etiqueta in casos
        ]
        fig.legend(handles=leyenda_estructuras + leyenda_casos, loc='upper center',
                   bbox_to_anchor=(0.5, 0.94), ncol=5, frameon=False)

        n_valores = ', '.join(f'{int(n):,}'.replace(',', '.') for n in sorted(df['N'].unique()))
        k = int(df['Ejecuciones'].iloc[0]) if 'Ejecuciones' in df else '?'
        m = int(df['M'].iloc[0]) if 'M' in df else '?'
        semilla = int(df['Semilla'].iloc[0]) if 'Semilla' in df else '?'
        fig.text(0.5, 0.015,
             f'Metodología: {k} corridas por punto | M = {m} búsquedas | semilla = {semilla} | '
             f'N = {n_valores} | punto = promedio; barras = desviación estándar',
                 ha='center', fontsize=9)
        fig.tight_layout(rect=[0.04, 0.05, 0.98, 0.89])
        fig.savefig(os.path.join(self.ruta_salida, 'resumen_experimentos.png'), dpi=220)
        plt.close(fig)

    def _crear_grid_base(self, titulo_general: str):
        fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True)
        fig.suptitle(titulo_general, fontsize=12, fontweight='bold', y=0.98)
        return fig, axes

    def _fig1_complejidad_teorica(self, df: pd.DataFrame):
        """ PREGUNTA: ¿Los resultados se comportan como predice la complejidad teórica? """
        fig, axes = self._crear_grid_base('Figura 1: Validación de Complejidad Teórica en Búsqueda (M búsquedas)')
        estructuras = ['Lista', 'ABB', 'BPlus']
        casos = [('ordenado', 'IDs Ordenados', 0), ('aleatorio', 'IDs Aleatorios', 1)]
        colores = {'Lista': '#d95f02', 'ABB': '#7570b3', 'BPlus': '#1b9e77'}

        for caso_key, caso_label, fila in casos:
            for col, est in enumerate(estructuras):
                ax = axes[fila, col]
                sub = df[(df['Estructura'] == est) & (df['Caso'] == caso_key)]
                if not sub.empty:
                    ax.errorbar(sub['N'], sub['Busqueda_Mean'], yerr=sub['Busqueda_Std'],
                                fmt='-o', color=colores[est], ecolor='gray', capsize=3)
                ax.set_yscale('log')
                ax.set_title(f'{est} - {caso_label}')
                ax.grid(True, which="both", ls="--", alpha=0.5)
                if fila == 1: ax.set_xlabel('Tamaño N')
                if col == 0: ax.set_ylabel('Tiempo (s) [log]')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.ruta_salida, "1_complejidad_teorica_busqueda.png"), dpi=300)
        plt.close()

    def _fig2_degeneracion_abb(self, df: pd.DataFrame):
        """ PREGUNTA: ¿En qué situaciones el árbol binario deja de comportarse como O(logN)? """
        fig, axes = self._crear_grid_base('Figura 2: Degeneración del ABB (IDs Ordenados vs Aleatorios)')
        estructuras = ['Lista', 'ABB', 'BPlus']

        for col, est in enumerate(estructuras):
            # Fila 0: Tiempo de Inserción
            ax_ins = axes[0, col]
            sub_ord = df[(df['Estructura'] == est) & (df['Caso'] == 'ordenado')]
            sub_ale = df[(df['Estructura'] == est) & (df['Caso'] == 'aleatorio')]

            ax_ins.plot(sub_ord['N'], sub_ord['Insercion_Mean'], 'r-o', label='Ordenado O(N)')
            ax_ins.plot(sub_ale['N'], sub_ale['Insercion_Mean'], 'b--s', label='Aleatorio')
            ax_ins.set_title(f'Inserción en {est}')
            ax_ins.grid(True, ls="--", alpha=0.5)
            ax_ins.legend(fontsize=7)
            if col == 0: ax_ins.set_ylabel('Tiempo Inserción (s)')

            # Fila 1: Tiempo de Búsqueda
            ax_bus = axes[1, col]
            ax_bus.plot(sub_ord['N'], sub_ord['Busqueda_Mean'], 'r-o', label='Ordenado')
            ax_bus.plot(sub_ale['N'], sub_ale['Busqueda_Mean'], 'b--s', label='Aleatorio')
            ax_bus.set_yscale('log')
            ax_bus.set_title(f'Búsqueda en {est}')
            ax_bus.grid(True, which="both", ls="--", alpha=0.5)
            ax_bus.legend(fontsize=7)
            ax_bus.set_xlabel('Tamaño N')
            if col == 0: ax_bus.set_ylabel('Tiempo Búsqueda (s) [log]')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.ruta_salida, "2_degeneracion_abb.png"), dpi=300)
        plt.close()

    def _fig3_altura_vs_tiempo(self, df: pd.DataFrame):
        """ PREGUNTA: ¿Qué relación existe entre la altura del árbol y el tiempo de búsqueda? """
        fig, axes = plt.subplots(2, 3, figsize=(14, 8))
        fig.suptitle('Figura 3: Relación entre Altura de la Estructura (H) y Tiempo de Búsqueda', fontsize=12, fontweight='bold', y=0.98)
        estructuras = ['Lista', 'ABB', 'BPlus']
        casos = [('ordenado', 'IDs Ordenados', 0), ('aleatorio', 'IDs Aleatorios', 1)]

        for caso_key, caso_label, fila in casos:
            for col, est in enumerate(estructuras):
                ax = axes[fila, col]
                sub = df[(df['Estructura'] == est) & (df['Caso'] == caso_key)]
                if not sub.empty:
                    ax.scatter(sub['Altura_Mean'], sub['Busqueda_Mean'], color='#8c564b', s=40)
                    for _, row in sub.iterrows():
                        ax.annotate(f"N={int(row['N'])}", (row['Altura_Mean'], row['Busqueda_Mean']), fontsize=6)
                ax.set_yscale('log')
                ax.set_title(f'{est} - {caso_label}')
                ax.grid(True, which="both", ls="--", alpha=0.5)
                ax.set_xlabel('Altura (H)')
                if col == 0: ax.set_ylabel('Tiempo (s) [log]')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.ruta_salida, "3_altura_vs_tiempo.png"), dpi=300)
        plt.close()

    def _fig4_costos_constantes_n_pequeno(self, df: pd.DataFrame):
        """ PREGUNTA: ¿Existen costos constantes que hagan que dos algoritmos tengan tiempos similares para N pequeños? """
        fig, axes = plt.subplots(2, 3, figsize=(14, 8))
        fig.suptitle('Figura 4: Análisis de Overhead / Costos Constantes en Entradas Pequeñas (N <= 1000)', fontsize=12, fontweight='bold', y=0.98)
        
        # Filtrar solo entradas pequeñas
        df_small = df[df['N'] <= 1000]
        estructuras = ['Lista', 'ABB', 'BPlus']
        casos = [('ordenado', 'IDs Ordenados', 0), ('aleatorio', 'IDs Aleatorios', 1)]

        for caso_key, caso_label, fila in casos:
            for col, est in enumerate(estructuras):
                ax = axes[fila, col]
                sub = df_small[(df_small['Estructura'] == est) & (df_small['Caso'] == caso_key)]
                if not sub.empty:
                    ax.plot(sub['N'], sub['Insercion_Mean'], 'g-o', label='Inserción')
                    ax.plot(sub['N'], sub['Busqueda_Mean'], 'm--s', label='Búsqueda')
                ax.set_title(f'{est} - {caso_label}')
                ax.grid(True, ls="--", alpha=0.5)
                ax.legend(fontsize=7)
                ax.set_xlabel('Tamaño N (Pequeños)')
                if col == 0: ax.set_ylabel('Tiempo (s)')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.ruta_salida, "4_costos_constantes_n_pequeno.png"), dpi=300)
        plt.close()

    def _fig5_operacion_insercion(self, df: pd.DataFrame):
        """ EVALUACIÓN: Operación de Inserción (Construcción con N elementos) """
        fig, axes = self._crear_grid_base('Figura 5: Evaluación de la Operación de Inserción (N Estudiantes)')
        estructuras = ['Lista', 'ABB', 'BPlus']
        casos = [('ordenado', 'IDs Ordenados', 0), ('aleatorio', 'IDs Aleatorios', 1)]

        for caso_key, caso_label, fila in casos:
            for col, est in enumerate(estructuras):
                ax = axes[fila, col]
                sub = df[(df['Estructura'] == est) & (df['Caso'] == caso_key)]
                if not sub.empty:
                    ax.errorbar(sub['N'], sub['Insercion_Mean'], yerr=sub['Insercion_Std'],
                                fmt='-s', color='#1f77b4', ecolor='red', capsize=3)
                ax.set_title(f'{est} - {caso_label}')
                ax.grid(True, ls="--", alpha=0.5)
                if fila == 1: ax.set_xlabel('Tamaño N')
                if col == 0: ax.set_ylabel('Tiempo Inserción (s)')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.ruta_salida, "5_evaluacion_insercion.png"), dpi=300)
        plt.close()

    def _fig6_operacion_listado(self, df: pd.DataFrame):
        """ EVALUACIÓN: Operación de Listado Ascendente por ID """
        fig, axes = self._crear_grid_base('Figura 6: Evaluación del Listado Ascendente por ID')
        estructuras = ['Lista', 'ABB', 'BPlus']
        casos = [('ordenado', 'IDs Ordenados', 0), ('aleatorio', 'IDs Aleatorios', 1)]

        for caso_key, caso_label, fila in casos:
            for col, est in enumerate(estructuras):
                ax = axes[fila, col]
                sub = df[(df['Estructura'] == est) & (df['Caso'] == caso_key)]
                if not sub.empty:
                    ax.errorbar(sub['N'], sub['Listado_Mean'], yerr=sub['Listado_Std'],
                                fmt='-^', color='#2ca02c', ecolor='gray', capsize=3)
                ax.set_title(f'{est} - {caso_label}')
                ax.grid(True, ls="--", alpha=0.5)
                if fila == 1: ax.set_xlabel('Tamaño N')
                if col == 0: ax.set_ylabel('Tiempo Listado (s)')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.ruta_salida, "6_evaluacion_listado.png"), dpi=300)
        plt.close()