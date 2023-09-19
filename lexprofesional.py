import getpass
import os
import psutil
import socket
import shutil
import subprocess
import mimetypes

# Parola corectă (criptată sau salvată într-un mediu securizat în producție)
parola_corecta = "sun12"

# Directorul curent
director_curent = os.getcwd()

# Director pentru copierea resurselor
director_copiere = os.path.join(os.getcwd(), "copiere_temporara")

# Resursa copiată
resursa_copiata = None

# Numărul maxim de încercări greșite permise
max_incercari = 3
numar_incercari = 0

# Funcție pentru completarea comenzii la apăsarea tastei Tab
def completeaza_comanda(comanda_partiala):
    potriviri = [comanda for comanda in comenzi_disponibile if comanda.startswith(comanda_partiala)]
    if len(potriviri) == 1:
        return potriviri[0]
    return comanda_partiala

# Funcție pentru a obține culoarea corespunzătoare în funcție de tipul de fișier
def get_color_for_file(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        if mime_type.startswith("text"):
            return "\033[1;33;40m"  # Culoarea galbenă pentru fișierele de tip text
        elif mime_type.startswith("image"):
            return "\033[1;35;40m"  # Culoarea mov pentru imagini
        elif mime_type.startswith("audio"):
            return "\033[1;34;40m"  # Culoarea albastră pentru fișiere audio
        elif mime_type.startswith("video"):
            return "\033[1;31;40m"  # Culoarea roșie pentru fișiere video
    return ""  # Returnează culoarea implicită

# Interfață personalizată a comenzii
def afisare_comanda():
    return input(f"\033[1;32;40m{getpass.getuser()}\033[0m@\033[1;34;40mlex-linux\033[0m:\033[1;36;40m{os.path.basename(director_curent)}\033[0m$ ")

# Comenzile disponibile
comenzi_disponibile = [
    "all", "cd", "edit", "manager", "kill", "ip", "rm", "cp", "paste", "clear", "nano", "read", "-t", "-d", "exit"
]

# Întrebăm utilizatorul să introducă parola corectă
while numar_incercari < max_incercari:
    parola_intrata = getpass.getpass("Introduceți parola: ")

    if parola_intrata == parola_corecta:
        print("Parola corectă. Acces permis.")
        break
    else:
        numar_incercari += 1
        print("Parolă incorectă. Mai aveți", max_incercari - numar_incercari, "încercări rămase.")

if numar_incercari == max_incercari:
    print("Prea multe încercări eșuate. Accesul este blocat.")
else:
    # Acum suntem în consolă și putem executa comenzile
    while True:
        command = afisare_comanda()

        if command == "exit":
            print("Consola se închide.")
            break
        elif command == "all":
            continut_director = os.listdir(director_curent)
            print("Conținutul directorului curent:")
            for element in continut_director:
                culoare = get_color_for_file(element)
                afisare_element = f"{culoare}{element}\033[0m"
                print(afisare_element)
        elif command.startswith("cd "):
            try:
                director_nou = command.split("cd ")[1]
                os.chdir(director_nou)
                director_curent = os.getcwd()
            except Exception as e:
                print("Eroare la schimbarea directorului:", str(e))
        elif command.startswith("edit "):
            nume_fisier = command.split("edit ")[1]
            try:
                with open(nume_fisier, 'r') as fisier_text:
                    continut = fisier_text.read()
                print(f"Editarea fișierului {nume_fisier}:\n")
                nou_continut = input("Introduceți sau editați conținutul:\n")
                with open(nume_fisier, 'w') as fisier_text:
                    fisier_text.write(nou_continut)
                print(f"Fișierul {nume_fisier} a fost actualizat cu succes.")
            except Exception as e:
                print("Eroare la editarea fișierului:", str(e))
        elif command == "manager":
            print("Afișare procese și resurse sistem:")
            print("=" * 50)
            procese = psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
            for proc in procese:
                try:
                    pid = proc.info['pid']
                    name = proc.info['name']
                    cpu_percent = proc.info['cpu_percent']
                    memory_percent = proc.info['memory_percent']
                    print(f"PID: {pid}, Nume: {name}, CPU: {cpu_percent}%, Memorie: {memory_percent}%")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            print("=" * 50)
        # Restul codului neschimbat
        elif command.startswith("-t "):
            nume_fisier = command.split("-t ")[1]
            try:
                with open(nume_fisier, 'w') as fisier_text:
                    print(f"Fișierul {nume_fisier} a fost creat.")
            except Exception as e:
                print("Eroare la crearea fișierului:", str(e))
        elif command.startswith("-d "):
            nume_folder = command.split("-d ")[1]
            try:
                os.mkdir(nume_folder)
                print(f"Directorul {nume_folder} a fost creat.")
            except Exception as e:
                print("Eroare la crearea directorului:", str(e))

        elif command.startswith("kill "):
            pid_to_kill = command.split("kill ")[1]
            try:
                pid_to_kill = int(pid_to_kill)
                process = psutil.Process(pid_to_kill)
                process.terminate()
                print(f"Procesul cu PID {pid_to_kill} a fost oprit.")
            except ValueError:
                print("PID-ul introdus nu este valid.")
            except psutil.NoSuchProcess:
                print(f"Nu există proces cu PID-ul {pid_to_kill}.")
        elif command == "ip":
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            print(f"Numele calculatorului: {hostname}")
            print(f"Adresa IP: {ip_address}")
        elif command.startswith("rm "):
            nume_resursa = command.split("rm ")[1]
            try:
                if os.path.isfile(nume_resursa):
                    os.remove(nume_resursa)
                    print(f"Fișierul {nume_resursa} a fost șters cu succes.")
                elif os.path.isdir(nume_resursa):
                    shutil.rmtree(nume_resursa)
                    print(f"Directorul {nume_resursa} a fost șters cu succes.")
                else:
                    print(f"{nume_resursa} nu există sau nu poate fi șters.")
            except Exception as e:
                print("Eroare la ștergerea resursei:", str(e))
        elif command.startswith("cp "):
            resursa_sursa = command.split("cp ")[1]
            try:
                if os.path.exists(resursa_sursa):
                    if os.path.isfile(resursa_sursa):
                        if not os.path.exists(director_copiere):
                            os.makedirs(director_copiere)
                        resursa_destinatie = os.path.join(director_copiere, os.path.basename(resursa_sursa))
                        shutil.copy2(resursa_sursa, resursa_destinatie)
                        resursa_copiata = resursa_destinatie
                        print(f"Fișierul {resursa_sursa} a fost copiat în {resursa_destinatie}.")
                    elif os.path.isdir(resursa_sursa):
                        resursa_destinatie = os.path.join(director_copiere, os.path.basename(resursa_sursa))
                        shutil.copytree(resursa_sursa, resursa_destinatie)
                        resursa_copiata = resursa_destinatie
                        print(f"Directorul {resursa_sursa} a fost copiat în {resursa_destinatie}.")
                else:
                    print(f"{resursa_sursa} nu există sau nu poate fi copiat.")
            except Exception as e:
                print("Eroare la copierea resursei:", str(e))
        elif command == "paste":
            if resursa_copiata:
                try:
                    if os.path.isfile(resursa_copiata):
                        shutil.copy2(resursa_copiata, director_curent)
                        print(f"Fișierul copiat {resursa_copiata} a fost pus în directorul curent.")
                    elif os.path.isdir(resursa_copiata):
                        destinatie = os.path.join(director_curent, os.path.basename(resursa_copiata))
                        shutil.copytree(resursa_copiata, destinatie)
                        print(f"Directorul copiat {resursa_copiata} a fost pus în directorul curent.")
                except Exception as e:
                    print("Eroare la paste:", str(e))
            else:
                print("Nu există resursă copiată pentru a face paste.")
        elif command.startswith("nano "):
            nume_fisier = command.split("nano ")[1]
            try:
                subprocess.run(["nano", nume_fisier])
            except Exception as e:
                print("Eroare la deschiderea fișierului în nano:", str(e))
        elif command.startswith("read "):
            nume_fisier = command.split("read ")[1]
            try:
                with open(nume_fisier, 'r') as fisier_text:
                    continut = fisier_text.read()
                    print(f"Conținutul fișierului {nume_fisier}:\n")
                    print(continut)
            except Exception as e:
                print("Eroare la citirea fișierului:", str(e))
        elif command == "clear":
            if os.name == "posix":
                os.system("clear")
            elif os.name == "nt":
                os.system("cls")
            else:
                print("Funcția clear nu este suportată pe acest sistem de operare.")
        else:
            completare = completeaza_comanda(command)
            print(f"Comandă necunoscută. Ați vrut să scrieți: {completare}")
