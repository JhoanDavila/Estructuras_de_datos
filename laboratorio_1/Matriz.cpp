/**
 * Laboratorio 1:
 * 
 * TÉCNICAS CLAVE USADAS :
 * 1. Bitpacking: En lugar de guardar cada valor (0 o 1) en un 'bool' o 'int' de 1 a 4 bytes,
 *    empaquetamos 8 celdas dentro de 1 solo byte de memoria.
 * 2. Estructura por Registros (Doble Header + Tail): Cada fila tiene sus dos marcadores
 *    de control al inicio (Header 1 = ID de fila, Header 2 = Cantidad de Columnas) y su
 *    delimitador de cierre 0xFF al final.
 * 3. Mapeo a Memoria Virtual (mmap): Permite interactuar con el archivo en disco como si estuviera
 *    en RAM, sin cargarlo completo físicamente y saltando a cualquier byte en 0 milisegundos.
 */

#include <iostream>
#include <fstream>
#include <fcntl.h>     // Para llamadas del sistema de archivos de Linux (open, O_RDWR, etc.)
#include <unistd.h>    // Para llamadas POSIX como ftruncate, sysconf y close
#include <sys/mman.h>  // Para gestionar la memoria virtual con mmap y munmap
#include <sys/stat.h>
#include <cstdint>     // Para tipos de datos con tamaño garantizado (ej. uint32_t)
#include <cstring>     // Para manipulación rápida de memoria (memcpy, memset)
#include <chrono>      // Para medir el tiempo de ejecución en milisegundos y segundos
#include <vector>

// --- DIMENSIONES Y ESTRUCTURA MATEMÁTICA DE LA MATRIZ ---
const size_t FILAS = 100000;
const size_t COLS = 100000;

// Como agrupamos 8 columnas en 1 solo byte, dividimos 100,000 / 8 = 12,500 bytes por fila
const size_t BYTES_DATOS = COLS / 8; 

// --- ARQUITECTURA DE DOBLE HEADER POR FILA + DELIMITADOR ---
// Header 1: ID de la Fila actual (4 bytes)
const size_t BYTES_HEADER_ROW_ID = sizeof(uint32_t); 

// Header 2: Total de Columnas de la Fila (4 bytes)
const size_t BYTES_HEADER_COLS   = sizeof(uint32_t); 

// Suma total de cabeceras al inicio = 8 bytes
const size_t BYTES_HEADER_TOTAL  = BYTES_HEADER_ROW_ID + BYTES_HEADER_COLS; 

// Delimitador (Fin): Un byte con valor Hexadecimal 0xFF (255 en decimal) para marcar el final exacto de la fila
const unsigned char DELIMITADOR_FIN = 0xFF;           

// Tamaño total de 1 registro = Header 1 (4 B) + Header 2 (4 B) + Datos (12,500 B) + Delimitador (1 B) = 12,509 Bytes
const size_t TAMANO_REGISTRO = BYTES_HEADER_TOTAL + BYTES_DATOS + 1; 

// Tamaño final del archivo en disco: 100,000 filas * 12,509 bytes = ~1.25 GB
const size_t TAMANO_TOTAL_ARCHIVO = FILAS * TAMANO_REGISTRO; 

const char* NOMBRE_ARCHIVO = "matriz_estructurada_100k.bin";

/**
 * 1. CREACIÓN Y ESCRITURA RÁPIDA DE LA MATRIZ
 * Genera el archivo binario en disco mapeando en memoria virtual.
 */
void crear_matriz_optimizada() {
    std::cout << "========================================================\n";
    std::cout << "[1] CREANDO MATRIZ BINARIA EN DISCO (" << TAMANO_TOTAL_ARCHIVO / (1024 * 1024) << " MB)\n";
    std::cout << "========================================================\n";
    
    auto inicio = std::chrono::high_resolution_clock::now();

    int fd = open(NOMBRE_ARCHIVO, O_RDWR | O_CREAT | O_TRUNC, (mode_t)0600);
    if (fd == -1) { perror("Error abriendo archivo"); exit(1); }

    if (ftruncate(fd, TAMANO_TOTAL_ARCHIVO) == -1) {
        perror("Error en ftruncate"); close(fd); exit(1);
    }

    unsigned char* mapa = (unsigned char*)mmap(NULL, TAMANO_TOTAL_ARCHIVO, 
                                               PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (mapa == MAP_FAILED) { perror("Error en mmap"); close(fd); exit(1); }

    // Rellenamos el archivo fila por fila directamente con la estructura de doble header
    for (uint32_t f = 0; f < FILAS; ++f) {
        size_t offset_fila = (size_t)f * TAMANO_REGISTRO;

        // A) HEADER 1: ID de Fila (4 bytes)
        std::memcpy(&mapa[offset_fila], &f, sizeof(uint32_t));

        // B) HEADER 2: Total de Columnas (4 bytes)
        uint32_t num_cols = COLS;
        std::memcpy(&mapa[offset_fila + BYTES_HEADER_ROW_ID], &num_cols, sizeof(uint32_t));

        // C) PAYLOAD: 12,500 bytes de datos bitpacked
        std::memset(&mapa[offset_fila + BYTES_HEADER_TOTAL], 0xAA, BYTES_DATOS); 

        // D) DELIMITADOR: Byte de cierre 0xFF al final de la fila
        mapa[offset_fila + BYTES_HEADER_TOTAL + BYTES_DATOS] = DELIMITADOR_FIN;
    }

    msync(mapa, TAMANO_TOTAL_ARCHIVO, MS_SYNC);
    munmap(mapa, TAMANO_TOTAL_ARCHIVO);
    close(fd);

    auto fin = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> duracion = fin - inicio;
    std::cout << ">>> Matriz creada exitosamente en: " << duracion.count() / 1000.0 << " segundos.\n\n";
}

/**
 * DEBUG 1: CONSULTA DE UN DATO INDIVIDUAL [Fila, Columna]
 */
void leer_dato_especifico(uint32_t fila, uint32_t col) {
    std::cout << "--- [DEBUG 1] LECTURA DE DATO INDIVIDUAL [" << fila << ", " << col << "] ---\n";
    auto inicio = std::chrono::high_resolution_clock::now();

    int fd = open(NOMBRE_ARCHIVO, O_RDONLY);

    off_t offset_directo = (off_t)fila * TAMANO_REGISTRO;

    // Alineación POSIX
    long page_size = sysconf(_SC_PAGE_SIZE);
    off_t offset_alineado = (offset_directo / page_size) * page_size;
    size_t dif = offset_directo - offset_alineado;
    size_t tamano_mapeo = TAMANO_REGISTRO + dif;

    unsigned char* mapa = (unsigned char*)mmap(NULL, tamano_mapeo, PROT_READ, MAP_PRIVATE, fd, offset_alineado);

    unsigned char* registro = mapa + dif;

    size_t byte_rel = col / 8;
    int bit_off = col % 8;
    
    // Saltamos los 8 bytes de cabecera total para llegar al payload
    bool valor = (registro[BYTES_HEADER_TOTAL + byte_rel] >> bit_off) & 1;

    munmap(mapa, tamano_mapeo);
    close(fd);

    auto fin = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> duracion = fin - inicio;

    std::cout << "-> Valor en [" << fila << "][" << col << "]: " << valor << "\n";
    std::cout << "-> Tiempo de consulta: " << duracion.count() << " ms\n\n";
}

/**
 * DEBUG 2: CARGA Y VERIFICACIÓN DE INTEGRIDAD DE UNA FILA (VERIFICA AMBOS HEADERS Y EL TAIL)
 */
void cargar_fila_entera_y_verificar(uint32_t fila) {
    std::cout << "--- [DEBUG 2] CARGAR FILA ENTERA (" << fila << ") Y VERIFICAR ESTRUCTURA ---\n";
    auto inicio = std::chrono::high_resolution_clock::now();

    int fd = open(NOMBRE_ARCHIVO, O_RDONLY);
    off_t offset_directo = (off_t)fila * TAMANO_REGISTRO;

    long page_size = sysconf(_SC_PAGE_SIZE);
    off_t offset_alineado = (offset_directo / page_size) * page_size;
    size_t dif = offset_directo - offset_alineado;
    size_t tamano_mapeo = TAMANO_REGISTRO + dif;

    unsigned char* mapa = (unsigned char*)mmap(NULL, tamano_mapeo, PROT_READ, MAP_PRIVATE, fd, offset_alineado);

    unsigned char* registro = mapa + dif;

    // A) VALIDACIÓN DE LOS DOS HEADERS
    uint32_t id_fila_leido = *(uint32_t*)(registro);
    uint32_t total_cols_leido = *(uint32_t*)(registro + BYTES_HEADER_ROW_ID);

    // B) VERIFICACIÓN DE LONGITUD DE DATOS
    size_t contador_bits = 0;
    for (size_t i = 0; i < BYTES_DATOS; ++i) {
        contador_bits += 8;
    }

    // C) VALIDACIÓN DEL DELIMITADOR DE CIERRE
    unsigned char delimitador = registro[BYTES_HEADER_TOTAL + BYTES_DATOS];

    munmap(mapa, tamano_mapeo);
    close(fd);

    auto fin = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> duracion = fin - inicio;

    std::cout << "-> Header 1 (Row-ID): " << id_fila_leido << "\n";
    std::cout << "-> Header 2 (Total Columnas): " << total_cols_leido << "\n";
    std::cout << "-> Total de columnas contadas hasta el delimitador: " << contador_bits << " bits\n";
    std::cout << "-> Delimitador de cierre hallado: 0x" << std::hex << (int)delimitador << std::dec << "\n";
    std::cout << "-> Tiempo de proceso de fila: " << duracion.count() << " ms\n\n";
}

/**
 * DEBUG 3: EXTRACCIÓN DE UNA COLUMNA ENTERA EN LAS 100,000 FILAS
 */
void cargar_columna_entera(uint32_t columna_deseada) {
    std::cout << "--- [DEBUG 3] LECTURA DE COLUMNA ENTERA (" << columna_deseada << ") EN LAS 100,000 FILAS ---\n";
    auto inicio = std::chrono::high_resolution_clock::now();

    int fd = open(NOMBRE_ARCHIVO, O_RDONLY);
    
    unsigned char* mapa = (unsigned char*)mmap(NULL, TAMANO_TOTAL_ARCHIVO, PROT_READ, MAP_PRIVATE, fd, 0);

    size_t byte_relativo = columna_deseada / 8;
    int bit_offset = columna_deseada % 8;

    std::vector<bool> columna_extraida(FILAS);

    // BARRIDO VERTICAL considerando el desplazamiento de los 8 bytes de cabecera total
    for (size_t f = 0; f < FILAS; ++f) {
        size_t offset_registro = f * TAMANO_REGISTRO;
        unsigned char byte_val = mapa[offset_registro + BYTES_HEADER_TOTAL + byte_relativo];
        columna_extraida[f] = (byte_val >> bit_offset) & 1;
    }

    munmap(mapa, TAMANO_TOTAL_ARCHIVO);
    close(fd);

    auto fin = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> duracion = fin - inicio;

    std::cout << "-> Total elementos recolectados en la columna: " << columna_extraida.size() << "\n";
    std::cout << "-> Muestra (Fila 0, 1, 2, 3): [" 
              << columna_extraida[0] << ", " << columna_extraida[1] << ", " 
              << columna_extraida[2] << ", " << columna_extraida[3] << "]\n";
    std::cout << "-> Tiempo de extraccion de columna: " << duracion.count() << " ms\n\n";
}

/**
 * PUNTO DE ENTRADA DEL PROGRAMA
 */
int main() {
    crear_matriz_optimizada();

    leer_dato_especifico(50000, 25000);   
    cargar_fila_entera_y_verificar(75000); 
    cargar_columna_entera(12345);         

    return 0;
}