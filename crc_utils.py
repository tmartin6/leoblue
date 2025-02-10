def append_crc(pdu, crc_init):
    """
    Ajoute un CRC à une trame PDU en utilisant le polynôme Bluetooth.
    
    Args:
        pdu (list of int): Liste binaire représentant la PDU
        crc_init (str): Valeur d'initialisation du CRC sous forme de chaîne hexadécimale
    
    Returns:
        list: Codeword (PDU + CRC) sous forme de liste binaire.
    """

    # Polynôme CRC Bluetooth (x^24 + x^10 + x^9 + x^6 + x^4 + x^3 + x + 1)
    CRC_POLYNOMIAL = 0x100065B  # Correspond au polynôme standard de 24 bits

    # Convertir crc_init de l'hexadécimal à un entier
    crc_value = int(crc_init, 16)

    # Calculer le CRC sur la PDU
    for bit in pdu:
        msb = (crc_value >> 23) & 1  # Extraire le bit de poids fort
        crc_value = (crc_value << 1) & 0xFFFFFF  # Décalage de 1 bit (garder sur 24 bits)
        
        if bit ^ msb:
            crc_value ^= CRC_POLYNOMIAL  # XOR avec le polynôme si nécessaire

    # Extraire les 24 bits du CRC calculé
    crc_bits = [(crc_value >> i) & 1 for i in range(23, -1, -1)]

    # Retourner la PDU concaténée avec le CRC
    return pdu + crc_bits
