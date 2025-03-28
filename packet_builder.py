import time

def build_legacy_ad_data():
    """Construit les données publicitaires BLE en mode legacy."""
    max_length = 31
    adv_data = []

    while True:
        remaining = max_length - len(adv_data) // 2
        print(f'Octets utilisés : {len(adv_data)//2}/{max_length}. Restants : {remaining}')

        if remaining <= 0:
            print("Plus de place disponible. Fin.")
            break

        ad_type_str = input("Entrez un AD Type en hexa (ex: 09) ou '0' pour terminer: ")
        if ad_type_str == '0':
            break

        if ad_type_str == '01':
            user_hex = input("Entrez la valeur des Flags en hexa (ex: 06): ")
            data_bytes = user_hex
        elif ad_type_str in ['08', '09']:
            user_str = input("Entrez le nom (ASCII): ")
            data_bytes = ascii_to_hex(user_str)
        else:
            user_hex = input("Entrez Data en hex (ex: 010203): ")
            data_bytes = user_hex

        len_val = 1 + len(data_bytes) // 2
        if len_val > 255 or len(adv_data) // 2 + 1 + len_val > max_length:
            print("Pas assez de place pour ajouter cette structure.")
            continue

        adv_data.append(f'{len_val:02X}{ad_type_str}{data_bytes}')

    print(f"Hex = {''.join(adv_data)}")
    result = list(''.join(adv_data))
    return result


def generate_packet_header_legacy(payload, new_header):
    """Génère l'entête du paquet Legacy."""
    print('Payload',payload)
    if len(payload) // 8 > 37:
        raise ValueError("Le payload est trop grand pour un paquet Legacy (> 37 octets).")
    
    return new_header + payload

def ascii_to_hex(ascii_str):
    """
    Convertit une chaîne ASCII en une chaîne hexadécimale.

    Args:
        ascii_str (str): La chaîne de caractères ASCII à convertir.

    Returns:
        str: La représentation hexadécimale de la chaîne ASCII.
    """
    hex_str = ascii_str.encode('utf-8').hex().upper()
    return hex_str

def build_fixed_legacy_ad_data():
    """Construit un paquet publicitaire BLE en mode legacy avec des données fixes."""
    adv_data = []

    # Ajout d'un Flag (AD Type = 01, valeur = 06 pour BLE Général Discoverable + BR/EDR non supporté)
    adv_data.append("020106")

    # Ajout d'un nom complet (AD Type = 09)
    nom = "MonAppareil"
    nom_hex = ascii_to_hex(nom)
    len_nom = 1 + len(nom_hex) // 2
    adv_data.append(f"{len_nom:02X}09{nom_hex}")

    hex_result = ''.join(adv_data)
    print(f"Hex = {hex_result}")
    return list(hex_result)


def build_dynamic_legacy_ad_data():
    """Construit un paquet publicitaire BLE en mode legacy avec des données fixes."""
    adv_data = []

    # Ajout d'un Flag (AD Type = 01, valeur = 06 pour BLE Général Discoverable + BR/EDR non supporté)
    adv_data.append("020106")

     # Récupération de l'heure actuelle au format HH:MM:SS
    prefix = "Leo: "
    current_time = time.strftime("%H:%M:%S", time.localtime())
    full_str = prefix + current_time
    full_hex = ascii_to_hex(full_str) # Convertir en hex

    len_data = 1 + len(full_hex) // 2
    if len_data > 31:  # Vérifier la limite BLE (31 octets max)
        print("Données trop longues pour un paquet BLE !")
        return []
    
    adv_data.append(f"{len_data:02X}09{full_hex}")

    hex_result = ''.join(adv_data)
    print(f"Hex = {hex_result}")
    return list(hex_result)
