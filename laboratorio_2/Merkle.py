import hashlib # liberia de python para poder crear los hash sha256


# --- 1. FUNCIÓN HASH ---
def sha256(texto): # Esta funcion se encarga de convertir el texto que se le manda en un hash sha256 y devolder ese valor hash
  return hashlib.sha256(texto.encode("utf-8")).hexdigest()


# --- 2. CONSTRUCTOR DEL ÁRBOL DE MERKLE ---
def construir_arbol(transacciones):
  # Construye el árbol desde las transacciones (hojas) hasta la cima (raíz).
  nivel_actual = [sha256(tx) for tx in transacciones]  # mete en esta variable nivel actual mediante un ciclo los valores hash sha256 de todos los datos de la variable transacciones
  niveles = [nivel_actual]  # se ingresa en la casilla 0 de niveles los hashes recién creados sobre las transacciones

  # Repetimos este proceso mientras nos quede más de un elemento; cuando quede solo uno, habremos llegado a la cima (la raíz)
  while len(nivel_actual) > 1:

    # REGLA DEL ÁRBOL: Si la cantidad de elementos en este nivel es impar...
    if (len(nivel_actual) % 2 != 0):  # ...duplicamos el último elemento agregándolo al final para que todos tengan su pareja
      nivel_actual.append(nivel_actual[-1])

    siguiente_nivel = ([])  # Creamos una lista vacía para guardar a los padres que vamos a ir formando en este nuevo piso

    # Recorremos la lista de dos en dos (saltando de 2 en 2 con el 'range')
    for i in range(0, len(nivel_actual), 2):
      izquierda = nivel_actual[i]  # El primer hijo de la pareja
      derecha = nivel_actual[i + 1]  # El segundo hijo que está justo al lado

      # Unimos los dos hashes hijos y los pasamos por la funcion sha256 para crear el hash del padre
      padre = sha256(izquierda + derecha)

      # Guardamos ese nuevo papá en el piso que estamos construyendo
      siguiente_nivel.append(padre)

    # Una vez terminamos el piso, el 'siguiente_nivel' se vuelve nuestro nuevo nivel actual para seguir subiendo
    nivel_actual = siguiente_nivel
    # Y guardamos este piso completo en nuestra lista de 'niveles' para no perderlo
    niveles.append(nivel_actual)

  return niveles  # Devuelve todos los pisos del árbol (las hojas abajo, la raíz arriba en el último nivel)

# --- 3. GENERAR PRUEBA DE INCLUSIÓN ---
def generar_prueba(niveles, indice_hoja):
  # Busca los 'vecinos' necesarios para comprobar que una hoja pertenece al árbol.
  prueba = []  # Aquí vamos a ir guardando las pistas
  indice = (indice_hoja)  # La posición exacta de nuestra transacción (ej: la posición 2)

  # Subimos piso por piso guardando el hash del hermano que nos acompaña
  for (nivel) in (niveles[:-1]):  # Recorremos todos los pisos, pero SIN contar la raíz (por eso el '[:-1]')

    # 1. ¿Estoy a la izquierda o a la derecha de mi pareja?
    # Si mi índice es par (0, 2, 4...), significa que estoy a la izquierda.
    es_par = indice % 2 == 0

    # 2. ¿Quién es mi hermano de pareja?
    # Si soy par (estoy a la izq), mi hermano está al lado derecho (+1).
    # Si soy impar (estoy a la der), mi hermano está al lado izquierdo (-1).
    indice_hermano = indice + 1 if es_par else indice - 1

    # 3. Guardamos al hermano si existe de verdad en ese nivel
    if indice_hermano < len(nivel):
      # Anotamos si ese hermano estaba a nuestra derecha o a nuestra izquierda
      posicion = "derecha" if es_par else "izquierda"
      # Guardamos una tupla: (el código hash del hermano, y de qué lado estaba)
      prueba.append((nivel[indice_hermano], posicion))

    # 4. Damos el salto al piso de arriba (al nivel del papá)
    # Como en el piso de arriba los nodos se reducen a la mitad, dividimos el índice entre 2 (// 2)
    indice = indice // 2

  return prueba  # Devolvemos la listita con todas las pistas necesarias para reconstruir la cima

# --- 4. VERIFICAR LA PRUEBA ---
def verificar_prueba(dato_hoja, prueba, raiz_esperada):
  # Reconstruye el camino hacia arriba usando el dato y las pistas de los vecinos para ver si llegamos a la misma raíz.

  # Paso A: Convertimos el texto de la transacción en su hash inicial (nuestro punto de partida abajo en las hojas)
  hash_actual = sha256(dato_hoja)

  # Paso B: Recorremos la lista de pistas (la prueba) para subir piso por piso hasta la cima
  for hermano, posicion in prueba:
    # Si el vecino estaba a nuestra derecha, nosotros vamos primero y el hermano después: (nosotros + hermano)
    if posicion == "derecha":
      hash_actual = sha256(hash_actual + hermano)
    # Si el vecino estaba a nuestra izquierda, el hermano va primero y nosotros después: (hermano + nosotros)
    else:
      hash_actual = sha256(hermano + hash_actual)

  # Paso C: Al terminar de subir todas las escalas, comparamos nuestro hash final con la raíz que nos entregaron.
  # Si son idénticos, devuelve True (el dato es legítimo); si no coinciden, devuelve False (es falso o fue alterado).
  return hash_actual == raiz_esperada


# ==========================================
# EJECUCIÓN DEL EXPERIMENTO
# ==========================================
if __name__ == "__main__":
  print("=" * 60)
  print(" LABORATORIO: ÁRBOLES DE MERKLE")
  print("=" * 60)

  # 1. Definimos las 5 transacciones de ejemplo que servirán como hojas base de nuestro árbol
  transacciones = [
      "Tx1: Ana paga 10 a Carlos",
      "Tx2: Carlos paga 5 a Sofia",
      "Tx3: Sofia paga 2 a Juan",
      "Tx4: Juan paga 20 a Diana",
      "Tx5: Diana paga 5 a Ana",
  ]

  # Mostramos en pantalla el listado inicial numerado de las transacciones
  print("\n[Paso 1] Transacciones originales:")
  for i, tx in enumerate(transacciones):
    print(f"  - Hoja {i}: {tx}")

  # Creamos el árbol original usando nuestra función y extraemos el único valor de la cima (la Raíz de Merkle)
  arbol_original = construir_arbol(transacciones)
  raiz_original = arbol_original[-1][0]
  # Imprimimos el hash raíz que representa de manera única a todo el conjunto de transacciones
  print(f"\n  -> Raíz del Árbol Original: {raiz_original}")

  # 2. Simulamos la modificación de una transacción para probar la seguridad
  print(
      "\n"
      + "-" * 60
      + "\n[Paso 2] Modificamos una transacción en secreto (Tx3)"
  )
  transacciones_modificadas = transacciones.copy()
  # Alteramos el monto de la transacción 3 (cambiamos '2' por '99')
  transacciones_modificadas[2] = ("Tx3: Sofia paga 99 a Juan")

  # Imprimimos ambas versiones para evidenciar el cambio exacto en los datos
  print(f"  - Original : {transacciones[2]}")
  print(f"  - Modificada: {transacciones_modificadas[2]}")

  # Construimos un nuevo árbol completo a partir de las transacciones modificadas y sacamos su nueva raíz
  arbol_modificado = construir_arbol(transacciones_modificadas)
  raiz_modificada = arbol_modificado[-1][0]

  # Mostramos la nueva raíz y comprobamos mediante un booleano si hubo un cambio drástico
  print(f"\n  -> Nueva Raíz (Modificada): {raiz_modificada}")
  print(
      f"  -> ¿La raíz cambió? {raiz_original != raiz_modificada} (Demuestra que"
      " cualquier cambio altera todo el bloque)"
  )

  # 3. Realizamos las pruebas de inclusión (Merkle Proof) sobre el árbol modificado
  print(
      "\n"
      + "-" * 60
      + "\n[Paso 3] Pruebas de validación sobre el árbol modificado"
  )

  indice_objetivo = 2  # Seleccionamos la Tx3 (que está en el índice 2) para verificarla
  # Generamos la lista de pistas (hermanos y posiciones) para esa hoja específica
  prueba = generar_prueba(arbol_modificado, indice_objetivo)

  # A. Prueba de validación con el DATO CORRECTO (el valor real ya modificado)
  dato_correcto = transacciones_modificadas[indice_objetivo]
  # Verificamos si al reconstruir el camino con este dato obtenemos la nueva raíz esperada
  es_valido = verificar_prueba(dato_correcto, prueba, raiz_modificada)
  print(f"\n  A) Probando con el dato correcto:")
  print(f"     Dato: '{dato_correcto}'")
  print(f"     Resultado -> {es_valido} (¡El sistema acepta que es verídico!)")

  # B. Prueba de validación con un DATO FALSO (intentando colar una trampa)
  dato_falso = "Tx3: Sofia paga 500 a Juan"  # Inventamos un valor distinto
  # Intentamos verificar ese dato falso usando la misma ruta de pruebas
  es_valido_trampa = verificar_prueba(dato_falso, prueba, raiz_modificada)
  print(f"\n  B) Probando con un dato falso (trampa):")
  print(f"     Dato: '{dato_falso}'")
  print(
      f"     Resultado -> {es_valido_trampa} (¡El sistema lo rechaza de"
      " inmediato!)"
  )

  # Mensaje de cierre de la ejecución
  print("\n" + "=" * 60)
  print(" ¡FIN DE LA PRUEBA!")
  print("=" * 60)