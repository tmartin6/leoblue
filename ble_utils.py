import numpy as np
def access_address_bytes_to_bits(hex_list):
    """Convertit une liste d'hexadécimaux en bits."""
    binary_list = hex_cell_to_binary_matrix(hex_list)
    rotated_binary_matrix = np.rot90(np.array(binary_list),2)
    flattened_bits = rotated_binary_matrix.reshape(-1).tolist()
    
    return flattened_bits



def swap_rows_two_by_two(matrix):
    """
    Échange les lignes de la matrice deux par deux.
    'matrix' est une liste de listes, où matrix[i] correspond à la i-ème ligne.
    """
    swapped_matrix = [row[:] for row in matrix]  # copie superficielle
    num_rows = len(swapped_matrix)

    # On boucle de 0 à num_rows-1 par pas de 2
    # (car MATLAB: i=1:2:num_rows-1 => en Python on décale de -1 pour le 0-based)
    for i in range(0, num_rows-1, 2):
        # Échanger les lignes i et i+1
        tmp = swapped_matrix[i]
        swapped_matrix[i] = swapped_matrix[i+1]
        swapped_matrix[i+1] = tmp

    return swapped_matrix

def hex_cell_to_binary_matrix(hex_list):
    """
    Convertit une liste de chaînes hexadécimales en une "matrice" (liste de listes) binaire.
    Chaque élément de 'hex_list' est une chaîne hex (ex: '1A'), 
    et on crée une ligne de bits (0/1) pour chaque hex string.
    """
    binary_matrix = []

    for hex_seq in hex_list:
        binary_row = []
        for char in hex_seq:
            # Convertir un caractère hex (ex: 'F') en entier 0..15
            val = int(char, 16)
            # Convertir en binaire 4 bits (ex: '1111')
            bin_str = format(val, '04b')
            # Convertir la chaîne en liste d'entiers (0/1)
            for b in bin_str:
                binary_row.append(int(b))
                
        # Ajouter la ligne à la matrice
        binary_matrix.append(binary_row)

    return binary_matrix

def packet_bytes_to_bits(hex_packet):
    """
    Reproduit la logique MATLAB : 
      1) Convertit le hex_packet en matrice binaire
      2) fliplr
      3) swap_rows_two_by_two
      4) transpose + reshape en une seule colonne
    Renvoie une liste 1D de bits.
    """
    # 1) Conversion en matrice binaire
    binary_matrix = hex_cell_to_binary_matrix(hex_packet)

    # 2) fliplr => renverser chaque ligne
    # En MATLAB, fliplr(...) renverse l'ordre des colonnes
    for row in binary_matrix:
        row.reverse()  # in-place

    # 3) swap_rows_two_by_two
    swapped_mat = swap_rows_two_by_two(binary_matrix)

    # 4) Reshape(packet_bits', [], 1)
    matrix = np.array(swapped_mat)
    flattened_bits = matrix.reshape(-1).tolist()
    
    return flattened_bits
