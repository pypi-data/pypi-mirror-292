import os
import re
import subprocess
import json
import time
import chardet
import psutil
import copy
from Orange.data import Domain, StringVariable, Table
import ftfy

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.MetManagement import get_local_store_path
else:
    from orangecontrib.AAIT.utils.MetManagement import get_local_store_path


def open_gpt_4_all(table, progress_callback=None):
    modify_gpt4all_config()
    time.sleep(1)
    if table is None:
        return
    data = copy.deepcopy(table)
    attr_dom = list(data.domain.attributes)
    metas_dom = list(data.domain.metas)
    class_dom = list(data.domain.class_vars)

    """Launch the GPT4All application if not already running, and wait until it is fully launched."""
    user_profile_path = os.getenv('USERPROFILE')
    gpt4all_exe_path = os.path.join(user_profile_path, "gpt4all", "bin", "chat.exe")
    rows=None
    if os.path.exists(gpt4all_exe_path):
        if is_process_running("chat.exe"):
            print("GPT4All est déjà en cours d'exécution.")
        else:
            try:
                subprocess.Popen([gpt4all_exe_path], shell=True)
                print("GPT4All a été lancé avec succès.")
            except Exception as e:
                print(f"Erreur lors de l'ouverture de GPT4All : {e}")
                return False
        if is_process_running("chat.exe"):
            time.sleep(2)
            try:
                rows=generate_and_clean_response(data,progress_callback)
            except:
                try:
                    time.sleep(5)
                    rows=generate_and_clean_response(data, progress_callback)
                except (ValueError,TypeError) as e:

                    print("An error occurred when trying to generate an answer:", e)
                    return
        if rows is None:
            rows = generate_and_clean_response(data, progress_callback)
        # Generate new Domain to add to data
        answer_dom = [StringVariable("Answer")]

        # Create and return table
        domain = Domain(attributes=attr_dom, metas=metas_dom + answer_dom, class_vars=class_dom)
        out_data = Table.from_list(domain=domain, rows=rows)
        return out_data


def generate_and_clean_response(data, progress_callback):
    rows = []
    for i, row in enumerate(data):
        try:
            features = list(data[i])
            metas = list(data.metas[i])
            answer = call_completion_api("localhost:4891", str(row["prompt"]))
            answer = corriger_encodage(answer)
            answer = clean_response(answer)
            metas += [answer]
            rows.append(features + metas)
        except Exception as e:
            print(f"Error processing row {i}: {e}")
            continue

        if progress_callback is not None:
            progress_value = float(100 * (i + 1) / len(data))
            progress_callback(progress_value)

    if not rows:
        print("No valid rows generated.")

    return rows

def get_model_in_gpt4all():
    aait_store_path = get_local_store_path()
    dir_model_path = f"{aait_store_path}/Models/NLP/"
    for element in os.listdir(dir_model_path):
        if "solar" in element and ".gguf" in element:
            return element


def modify_gpt4all_config():
    """Modify the GPT4All configuration to set the GPU device, enable server mode, and configure network settings."""
    appdata_path = os.getenv('APPDATA')
    file_path = os.path.join(appdata_path, "nomic.ai", "GPT4All.ini")
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path))

    gpu_name = get_gpu_name()
    model_name = get_model_in_gpt4all()
    aait_store_path = get_local_store_path()
    dir_model_path = f"{aait_store_path}Models/NLP/"

    if gpu_name is not None and model_name is not None:
        try:
            lines = []
            if os.path.exists(file_path):
                # If the file exists, read it
                with open(file_path, 'r') as file:
                    lines = file.readlines()

            # Initialize flags to check if modifications have been made
            gpu_modified = False
            server_chat_modified = False
            user_default_model_modified = False
            found_general_section = False
            found_model_section = False
            found_network_section = False
            usage_stats_active = False
            is_active = False
            found_download_section = False
            model_path_modified = False

            # Read lines from the file
            # Iterate over lines to modify existing sections or add new ones
            for i, line in enumerate(lines):
                if line.strip() == "[General]":
                    found_general_section = True
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith("["):
                            break
                        if "device=" in lines[j]:
                            lines[j] = f"device={gpu_name}\n"
                            gpu_modified = True
                        if "serverChat=" in lines[j]:
                            lines[j] = "serverChat=true\n"
                            server_chat_modified = True
                        if "userDefaultModel=" in lines[j]:
                            lines[j] = f"userDefaultModel={model_name}\n"
                            user_default_model_modified = True
                        if "modelPath" in lines[j]:
                            lines[j] = f"modelPath={dir_model_path}\n"
                            model_path_modified = True
                    if not gpu_modified:
                        lines.insert(i + 1, f"device={gpu_name}\n")
                    if not server_chat_modified:
                        lines.insert(i + 1, "serverChat=true\n")
                    if not user_default_model_modified:
                        lines.insert(i + 1, f"userDefaultModel={model_name}\n")
                    if not model_path_modified:
                        lines.insert(i + 1, f"modelPath={dir_model_path}\n")

            # If [General] section is not found, create it
            if not found_general_section:
                lines.append(f"[General]\ndevice={gpu_name}\nserverChat=true\nuserDefaultModel={model_name}\nmodelPath={dir_model_path}\n")

            # Check for model-specific section and add it if not found
            for i, line in enumerate(lines):
                if f"[model-{model_name}]" in line:
                    found_model_section = True
                    break
            if not found_model_section:
                lines.append(f"\n[model-{model_name}]\nfilename={model_name}\n")
            for i, line in enumerate(lines):
                if f"[download]" in line:
                    found_download_section = True
                    break
            if not found_download_section:
                lines.append(f"[download]\nlastVersionStarted=3.2.1")
            # Check for [network] section and add it if not found
            for i, line in enumerate(lines):
                if line.strip() == "[network]":
                    found_network_section = True
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith("["):
                            break
                        if "usageStatsActive=" in lines[j]:
                            lines[j] = f"usageStatsActive=false\n"
                            usage_stats_active = True
                        if "isActive=" in lines[j]:
                            lines[j] = "isActive=false\n"
                            is_active = True
                    if not usage_stats_active:
                        lines.insert(i + 1, f"usageStatsActive=false\n")
                    if not is_active:
                        lines.insert(i + 1, f"isActive=false\n")
                    break
            if not found_network_section:
                lines.append(f"\n[network]\nusageStatsActive=false\nisActive=false\n")
            # Write the modified or newly created configuration back to the file
            print(lines)
            with open(file_path, 'w') as file:
                file.writelines(lines)
            print("GPT4All configuration updated successfully.")
        except Exception as e:
            print(f"Erreur lors de la modification ou de la création du fichier GPT4All.ini : {e}")

def is_process_running(process_name):
    """Check if a process with the given name is already running."""
    return any(process_name.lower() in proc.info['name'].lower() for proc in psutil.process_iter(['name']))


def call_completion_api(localhost, message_content):
    """Calls the GPT4All completion API and returns the response."""
    print(f"Sending message to GPT-4All: {message_content}")
    command = [
        "curl",
        "--location",
        f"http://{localhost}/v1/chat/completions",
        "--header",
        "Content-Type: application/json; charset=UTF-8",
        "--data",
        json.dumps({
            "temperature": 0.7,
            "model": "gpt-4-turbo",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": message_content}]
        })
    ]

    try:
        # Adding the `creationflags` parameter to suppress the CMD window
        response = subprocess.check_output(
            command,
            universal_newlines=True,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW  # Prevents the CMD window from appearing
        )
        return response
    except subprocess.CalledProcessError as e:
        print(f"Error during API call: {e}")
        return None


def get_gpu_name():
    try:
        # Vérification de la présence d'un GPU NVIDIA via la commande WMIC
        wmic_result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if "NVIDIA" not in wmic_result.stdout:
            return None

        # Si un GPU NVIDIA est trouvé, exécution de nvidia-smi pour obtenir le nom du GPU
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            gpu_name = result.stdout.strip()
            return "CUDA: " + gpu_name
        else:
            print(f"Error: {result.stderr}")
            return None
    except FileNotFoundError:
        print("nvidia-smi command not found. Make sure NVIDIA drivers are installed.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def clean_response(response_data):
    """Cleans the response text by removing special characters and correcting encoding issues."""
    try:
        data = json.loads(response_data)
        message_content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        # Clean the response by removing unwanted characters
        cleaned_text = re.sub(r'[^\w\s,.!?\'"àâçéèêëîïôûùüÿÀÂÇÉÈÊËÎÏÔÛÙÜŸ-]', '', message_content)
        cleaned_text = corriger_encodage(cleaned_text)
        return cleaned_text.strip()
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON: {str(e)}")
        return ""
def corriger_encodage(texte):
    """Uses ftfy to correct misencoded text."""
    texte_corrige = ftfy.fix_text(texte)
    return texte_corrige

def detect_encoding(file_path):
    """Detects file encoding using chardet."""
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']
def extract_text_from_file(file_path):
    """Extracts and returns text content from a file with proper encoding detection."""
    encodings = ['utf-8', 'latin-1', 'cp1252']  # Add other encodings as needed
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except (UnicodeDecodeError, IOError) as e:
            print(f"Erreur avec l'encodage {encoding} pour le fichier : {file_path}, Erreur: {str(e)}")
            continue
    print(f"Impossible de lire le fichier avec les encodages tentés : {file_path}")
    return ""


modify_gpt4all_config()