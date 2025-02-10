
import serial
import serial.tools.list_ports
from datetime import datetime

def log_serial_with_timestamp(port, baud_rate, output_file):
    """
    Enregistre les données reçues sur un port série dans un fichier, avec des timestamps.

    Args:
        port (str): Nom du port série 
        baud_rate (int): Taux de communication série 
        output_file (str): Nom du fichier de sortie.
    """
    try:
        # Ouvre le port série
        with serial.Serial(port, baud_rate, timeout=1) as ser, open(output_file, 'w') as file:
            print(f"Connexion au port {port} avec un baud rate de {baud_rate}.")
            print(f"Données sauvegardées dans {output_file}.")

            # Boucle pour lire et enregistrer les données
            while True:
                if ser.in_waiting > 0:  # Vérifie si des données sont disponibles
                    line = ser.readline().decode('utf-8').strip()  # Lit et décode une ligne
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Génère le timestamp
                    formatted_line = f"[{timestamp}] {line}"  # Format des données avec timestamp
                    print(formatted_line)  # Affiche dans le terminal
                    file.write(formatted_line + '\n')  # Écrit dans le fichier
    except KeyboardInterrupt:
        print("Enregistrement interrompu.")
    except serial.SerialException as e:
        print(f"Erreur série : {e}")
    except Exception as e:
        print(f"Erreur : {e}")

# Main
if __name__ == "__main__":
    #port="/dev/cu.usbmodem0010502101701" # premiere nordic
    port = "/dev/cu.usbmodem0010502471531" # deuxième nordic apolline
    baud_rate=115200
    output_file="arduino_output.txt"
    log_serial_with_timestamp(port, baud_rate, output_file)
