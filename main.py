from packet_builder import *
from waveform_generator import ble_waveform_generator
from ble_utils import access_address_bytes_to_bits, packet_bytes_to_bits
from crc_utils import append_crc
from iq_utils import  transmit_iq_hackrf, save_signal_to_file
from scipy.io import savemat
import os
import signal
# Parameters
channel_packet = 'Primary'
packet_mode = 'Legacy'
ble_mode = 'LE1M'
default_CRC_init = '555555'
sps = 8
channel_index = 37
length_preamble = 8
length_access_address = 32
frequency=2402000000
sample_rate=8000000
interval_ms=20
gain = 32

access_address_hex = ['8', 'E', '8', '9', 'B', 'E', 'D', '6']
advA_hex = ['E', 'D', '8', '8', '3', 'C', '9', 'B', 'B', '6', 'D', 'B']
nb_bits_length_header = 8
PDU_type = [0, 0, 0, 0]
RxAdd = 0
TxAdd = 1
Chsel = 1
RFU = 0


# while True: 
#     # Build payload
#     #payload_hex = build_legacy_ad_data()
#     #payload_hex = build_fixed_legacy_ad_data()
#     payload_hex = build_dynamic_legacy_ad_data()

#     #payload_hex = ['0', '2', '0','1', '0', '6', '0', '8', '0', '9', '6', 'C', '6', '5', '6', 'F', '6', '2', '6', 'C', '7', '5', '6', '5']
#     #payload_hex = ['0', '2', '0','1', '0', '6']
#     #payload_hex = ['0', '2', '0', '1', '0', '6','0', '8', '0', '9', '4', 'C','6', '5', '6', 'F', '4', '2', '6', 'C', '7', '5', '6', '5', '0', 'A', '1', '6', '0', 'D', '1', '8', '0', '0', '1', 'D', '1', '0','4','6','4','9','5','2','4','5']
#     print('Complete payload',payload_hex)
#     length_payload = (len(payload_hex) + len(advA_hex)) // 2
#     length_payload_bit = bin(length_payload)[2:].zfill(nb_bits_length_header)
#     length_payload_bits = list(map(int, length_payload_bit[::-1]))

#     # Define header and PDU
#     new_header_LEG = PDU_type + [RxAdd, TxAdd, Chsel, RFU] + list(map(int, length_payload_bits))

#     advA = list(map(int,packet_bytes_to_bits(advA_hex)))

#     payload = list(map(int,packet_bytes_to_bits(payload_hex)))

#     access_address = list(map(int,access_address_bytes_to_bits(access_address_hex)))


#     # Generate header and append CRC
#     data_to_send = generate_packet_header_legacy(advA + payload, new_header_LEG)

#     sig_crc = append_crc(data_to_send, default_CRC_init)


#     # Generate waveform
#     tx_waveform, bitstream_complete = ble_waveform_generator(sig_crc, ble_mode, sps, channel_index, access_address)

#     print("Transmission waveform generated successfully!")

#     # Définir un dictionnaire avec des noms de variables
#     mat_dict = {'my_array': tx_waveform}

#     # Sauvegarder dans un fichier .mat
#     savemat('tx_waveform_python.mat', mat_dict)

#     # Sauvegarder le signal IQ dans un fichier binaire
#     filename = save_signal_to_file(tx_waveform, ble_mode, packet_mode)
#     print(f"Fichier généré : {filename}")

#     # Transmettre le signal toutes les 20ms
#     transmit_iq_hackrf(filename, frequency, sample_rate, gain, interval_ms)

#     # Attente avant la prochaine mise à jour
#     time.sleep(interval_ms / 1000)  # Convertir ms en secondes


def transmit_ble():
    """Met à jour l'heure et relance la transmission IQ sans bloquer."""
    process = None  # Stocke le processus hackrf_transfer

    try:
        while True:
            # Générer le payload avec l'heure actuelle
            payload_hex = build_dynamic_legacy_ad_data()

            if not payload_hex:
                print("Erreur lors de la génération du payload, on saute cette transmission.")
                continue

            # Construire la trame BLE
            length_payload = (len(payload_hex) + len(advA_hex)) // 2
            length_payload_bit = bin(length_payload)[2:].zfill(nb_bits_length_header)
            length_payload_bits = list(map(int, length_payload_bit[::-1]))

            new_header_LEG = PDU_type + [RxAdd, TxAdd, Chsel, RFU] + list(map(int, length_payload_bits))

            advA = list(map(int, packet_bytes_to_bits(advA_hex)))
            payload = list(map(int, packet_bytes_to_bits(payload_hex)))
            access_address = list(map(int, access_address_bytes_to_bits(access_address_hex)))

            # Générer header et CRC
            data_to_send = generate_packet_header_legacy(advA + payload, new_header_LEG)
            sig_crc = append_crc(data_to_send, default_CRC_init)

            # Générer la forme d'onde
            tx_waveform, bitstream_complete = ble_waveform_generator(sig_crc, ble_mode, sps, channel_index, access_address)

            # Sauvegarder le fichier IQ
            filename = save_signal_to_file(tx_waveform, ble_mode, packet_mode)
            print(f"📡 Transmission BLE mise à jour : {filename}")

            # Si une transmission est en cours, l'arrêter avant de relancer
            if process:
                os.kill(process.pid, signal.SIGTERM)  # Arrêter proprement hackrf_transfer
                print("⏹️ Transmission précédente stoppée.")

            # Démarrer une nouvelle transmission
            process = transmit_iq_hackrf(filename, frequency, sample_rate, gain)

            # Attendre avant la prochaine mise à jour
            time.sleep(interval_ms / 1000)

    except KeyboardInterrupt:
        print("Arrêt de la transmission.")
        if process:
            os.kill(process.pid, signal.SIGTERM)  # Arrêter HackRF avant de quitter

# Lancer la transmission en boucle
transmit_ble()