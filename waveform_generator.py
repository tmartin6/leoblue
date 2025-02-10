import numpy as np
import math
from math import  sqrt, pi
from scipy.special import erf
import matplotlib.pyplot as plt


def ble_waveform_generator(message, mode, sps, channel_index, access_address):
    """Génère la forme d'onde BLE."""
    preamble = generate_preamble(mode, access_address)
    whitened_message = whitening_ble(message, channel_index)
    phy_frame = preamble + access_address + whitened_message.tolist()
    bitstream = phy_frame
    waveform = gmsk_modulate(phy_frame, sps)
    return waveform, bitstream


def generate_preamble(mode, access_address):
    """Génération d'un préambule BLE."""
    return [0, 1, 0, 1, 0, 1, 0, 1]  if mode == 'LE1M' else '1010' * 16


def whitening_ble(bits, channel):
    """
    Applique le whitening BLE à une séquence de bits, en utilisant un LFSR.

    Args:
        bits (list[int]): Liste des bits d'entrée (0 ou 1).
        channel (int): Index du canal BLE (0 à 39).

    Returns:
        np.array: Séquence de bits whitened.
    """

    # Définition du polynôme de whitening x^7 + x^4 + 1
    polynomial = [0] * 8  # Création d'un vecteur de taille 8 initialisé à 0
    exponents = [0, 4, 7]  # Positions des termes dans le polynôme (x^7 + x^4 + 1)

    for x in exponents:
        polynomial[x] = 1  # Configuration du polynôme en LFSR

    working_poly = np.array(polynomial[:-1])  # On exclut le terme x^8 (non utilisé)

    # Configuration du registre de whitening avec l'index du canal (6 bits)
    # La spécification BLE demande d'ajouter un MSB de valeur 1 au canal
    channel_array = [int(x) for x in format(channel, "06b")]  # Convertir en binaire sur 6 bits
    state = np.array([1] + channel_array, dtype=int)  # Ajouter MSB = 1

    out_array = np.array([], dtype=int)

    # Boucle LFSR
    for bit in bits:
        # Le bit de sortie est XORé avec le premier bit de l'état (D0)
        out_bit = state[-1]  # Prendre le bit D0 (LSB)
        whitened_bit = bit ^ out_bit  # XOR avec le bit courant d'entrée
        out_array = np.append(out_array, whitened_bit)

        # Décalage du registre LFSR vers la droite
        state = np.insert(state[:-1], 0, 0)  # Ajouter un 0 au début (D6)

        # Application du feedback en fonction du polynôme
        xor_array = out_bit * working_poly  # XOR avec le polynôme actif
        state = np.bitwise_xor(state, xor_array)  # Appliquer le XOR à l'état LFSR

    return out_array





def gmsk_modulate(data, sps):
    """
    Modulation GMSK d'un signal binaire.

    Args:
        data (list): Séquence binaire.
        Tb (float): Durée d'un bit.
        samples (int): Symbols per sample.

    Returns:
        np.ndarray: Signal modulé GMSK.
    """
    pulse_len = 1
    bt_prod = 0.3
    # Étape 1 : Convertir les données en format NRZ (-1, +1)
    nrz_data = 2 * np.array(data) - 1  # Conversion 0->-1, 1->+1
    
    # Étape 2 : Suréchantillonnage

    upsampled_data = np.zeros(len(nrz_data) * sps)
    upsampled_data[::sps] = nrz_data
    
    # Étape 3 : Appliquer le filtre gaussien
    gauss_filter = gaussian_pulse(bt_prod, pulse_len, sps)
    conv_rect_gauss = np.convolve(upsampled_data, gauss_filter, mode='same')
    
    # Étape 4 : Intégration du signal filtré
    integrated_signal = np.cumsum(conv_rect_gauss)


    # Étape 5 : Génération des composantes en phase et en quadrature
    m_filtered2_real = np.cos(integrated_signal)
    m_filtered2_imag = np.sin(integrated_signal)
    m_filtered2 = m_filtered2_real + 1j * m_filtered2_imag
    

    
    return np.transpose(m_filtered2)

import numpy as np

def gaussian_pulse(BT, T, sps):
    """
    Génère un filtre gaussien pour la modulation GMSK.

    Args:
        T (float): Durée d'un bit.
        sps (int): Nombre d'échantillons par bit.

    Returns:
        np.ndarray: Filtre gaussien normalisé.
    """

    # Génération du vecteur de temps équivalent à (-1.5*T:T/sps:1.5*T)
    t = np.arange(-1.5 * T, 1.5 * T + T / sps, T / sps)

    # Paramètre de largeur de bande-temporalité (BT)
    BT = 0.3  # T = 1

    # Calcul de la réponse impulsionnelle du filtre gaussien
    h = (BT * np.sqrt((2 * np.pi) / np.log(2))) * np.exp(-((2 * np.pi**2) * (BT**2) * t**2) / np.log(2))

    # Mise à l'échelle du filtre pour un changement de phase de pi/2 par bit
    K = np.pi / 2 / np.sum(h)
    gfilter = K * h

    # Option de normalisation supplémentaire (décommenter si nécessaire)
    # gfilter = gfilter / np.sqrt(np.sum(gfilter))

    # Tracé du filtre (décommenter si nécessaire)
    # import matplotlib.pyplot as plt
    # plt.plot(gfilter)
    # plt.title('Gaussian Filter')
    # plt.xlabel('Samples')
    # plt.ylabel('Amplitude')
    # plt.show()

    return gfilter


def qfun(t):
    """
    Complementary error function approximation.

    Args:
        t (np.ndarray): Input values.

    Returns:
        np.ndarray: Q function output.
    """
    return 0.5 * (1 - erf(t / np.sqrt(2)))