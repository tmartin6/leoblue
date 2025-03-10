import numpy as np
import subprocess
import time



import subprocess
import time

def transmit_iq_hackrf(filename, frequency, sample_rate, gain):
    """
    Lance hackrf_transfer en arrière-plan et met à jour le fichier IQ à chaque cycle.
    """
    print(f"Transmission IQ depuis {filename} à {frequency/1e6} MHz...")

    cmd = [
        "hackrf_transfer",
        "-t", filename,
        "-f", str(frequency),
        "-s", str(sample_rate),
        "-x", str(gain),
        "-a", "1",
        "-p", "1",
        "-R"
    ]
    
    # Lancer HackRF en arrière-plan (processus non bloquant)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return process  # Retourner le processus pour pouvoir l'arrêter si besoin



def save_signal_to_file(tx_waveform_doppler, ble_mode, packet_mode):
    """
    Enregistre le signal IQ dans un fichier binaire compatible avec HackRF.

    Args:
        tx_waveform_doppler (np.ndarray): Signal complexe à sauvegarder.
        ble_mode (str): Mode BLE utilisé.
        packet_mode (str): Mode de paquet utilisé.

    Returns:
        str: Nom du fichier généré.
    """

    # Extraction des parties réelle et imaginaire
    env_I_synthetic = np.real(tx_waveform_doppler).T  # Transposition pour correspondre à MATLAB
    env_Q_synthetic = np.imag(tx_waveform_doppler).T

    # Concatenation des composantes I et Q
    mat_env_formatIQ_synthetic = np.vstack((env_I_synthetic, env_Q_synthetic))

    # Mise à l'échelle à 64 pour HackRF (8 bits ADC)
    env_formatIQ_synthetic = (64 * mat_env_formatIQ_synthetic.flatten(order='F')).astype(np.float32)

    # Création du nom de fichier
    filename = f'B{ble_mode}_{packet_mode}.bin'

    # Sauvegarde des données dans un fichier binaire
    with open(filename, 'wb') as file:  # Ouvre le fichier en mode écriture binaire
        file.write(env_formatIQ_synthetic.astype(np.int8).tobytes())  # Convertit en octets et écrit

    return filename
