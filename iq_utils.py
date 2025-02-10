import numpy as np
import subprocess
import time



def transmit_iq_hackrf(filename, frequency, sample_rate, gain, interval_ms):
    """
    Transmet un fichier IQ avec la HackRF en boucle toutes les 20ms.

    Parameters:
    - filename : str (nom du fichier IQ)
    - frequency : int (fréquence de transmission en Hz, ex: 2.4 GHz)
    - sample_rate : int (taux d'échantillonnage en Hz, ex: 2 MHz)
    - gain : int (gain de transmission en dB)
    - interval_ms : int (intervalle entre chaque transmission en millisecondes)
    """
    print(f"Transmission IQ depuis {filename} à {frequency/1e6} MHz toutes les {interval_ms} ms...")

    try:
        while True:
            # Exécuter la commande hackrf_transfer pour envoyer le fichier IQ
            cmd = [
                "hackrf_transfer",
                "-t", filename,
                "-f", str(frequency),
                "-s", str(sample_rate),
                "-x", str(gain),
                "-a", "1",  # Activer l'amplificateur d'antenne
                "-p", "1",  # Activer le PA
                "-R"
            ]
            subprocess.run(cmd, check=True)
            
            # Attente entre les transmissions
            time.sleep(interval_ms / 1000.0)

    except KeyboardInterrupt:
        print("\nTransmission arrêtée.")


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
