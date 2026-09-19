# Estudiante: Jhoan Sebastian Davila Hernandez.
# Registro de Archivos del Repositorio - Laboratorio.


Este repositorio contiene la implementación y pruebas de rendimiento para el manejo de una matriz binaria de gran escala ($100,000 \times 100,000$ celdas) mediante técnicas de optimización en C++.

## Archivos Contenidos

### main.cpp

Es el único archivo de código fuente del proyecto.
 

Contiene la lógica autocontenida para la generación del archivo binario y las pruebas de validación de lectura/escritura.

### El archivo implementa las siguientes funciones principales:

* crear_matriz_optimizada(): Genera el archivo binario en disco (matriz_estructurada_100k.bin) de ~1.25 GB mediante ftruncate y mapeo de memoria virtual (mmap). Aplica bitpacking para almacenar 8 celdas por byte. además cada 100000 bits pone el marcador (0xFF).
* leer_dato_especifico(fila, col): Accede a un bit individual en cualquier posición de la matriz calculando el offset exacto y aplicando operaciones a nivel de bit.
* cargar_fila_entera_y_verificar(fila): Lee una fila específica y valida la estructura de control compuesta por el Header 1 (ID de fila), Header 2 (Total de columnas) y el delimitador de cierre (0xFF).
* cargar_columna_entera(columna_deseada): Realiza un barrido vertical a través de las 100,000 filas para extraer los datos de una columna específica.
### Archivos Generados en Ejecuciónmatriz_estructurada_100k.bin

el archivo no se carga completo, lo primero que se hace es mirar los Header, el de las filas y el de las columnas, luego solo ignora los bits hasta llegar a la posicion y carga en la ram desde esa posicion.

Archivo binario creado automáticamente al ejecutar el programa. Representa la matriz estructurada en disco con una arquitectura por registro de 12,509 bytes por fila:

* Header 1: ID de fila (uint32_t, 4 bytes).
* Header 2: Total de columnas (uint32_t, 4 bytes).
* Datos empaquetados: 12,500 bytes (100,000 bits).
* Delimitador: 1 byte (0xFF). es el que marca el fin de cada columna.

### ejecutable desde la carpeta central de repositorio:
es nesesario tener el el compilador g++:
    g++ -O3 laboratorio_1/Matriz.cpp -o programa && ./programa
