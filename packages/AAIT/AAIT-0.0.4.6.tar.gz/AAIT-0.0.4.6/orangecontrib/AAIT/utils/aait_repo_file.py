import os
import json
import zipfile
from zipfile import ZipFile

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
    from Orange.widgets.orangecontrib.AAIT.utils import MetManagement, SimpleDialogQt
else:
    from orangecontrib.AAIT.utils import MetManagement, SimpleDialogQt

def generate_listing_json(directory_to_list):
    output_json_file = directory_to_list+'/files_info.json'
    if os.path.isfile(output_json_file):
        os.remove(output_json_file)

    def list_files_recursive(directory):
        files_info = {}

        for root, dirs, files in os.walk(directory):
            for file in files:

                file_path = os.path.join(root, file).replace("\\","/")
                file_size = os.path.getsize(file_path)
                file_path=file_path[len(directory)+1:]
                files_info[file_path]=file_size

        return files_info

    def save_to_json(data, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    files_info = list_files_recursive(directory_to_list)
    save_to_json(files_info, output_json_file)
    return files_info

def add_file_to_zip_file(folder,file_in,zip_file):
    path_in=folder+file_in
    with open(path_in, 'rb') as f:
        contenu = f.read()
    with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(file_in, contenu)

def create_index_file(in_repo_file,out_repo_file):
    if not os.path.isfile(in_repo_file):
        raise Exception("The specified path is not a file "+in_repo_file)
    if 0!=MetManagement.get_size(in_repo_file):
        raise Exception("The file " + in_repo_file+ " need to be empty to use this functions")
    print(MetManagement.get_size(in_repo_file))
    folder_to_process=os.path.dirname(in_repo_file).replace("\\","/")
    file_info=generate_listing_json(folder_to_process)
    # remove repo file if exist
    # if os.path.isfile(out_repo_file):
    #     os.remove(out_repo_file)
    #
    # folder_to_process+="/"
    # for element in file_info:
    #     print(element)
    #     add_file_to_zip_file(folder_to_process, element, out_repo_file)

    return

def decode(repo_file,file_to_read):
    if os.path.isfile(repo_file)==False:
        return None
    file_to_read=os.path.splitext(os.path.basename(repo_file))[0]+"/"+file_to_read
    with zipfile.ZipFile(repo_file, 'r') as zip_ref:
        with zip_ref.open(file_to_read) as file:
            content = file.read()
            return content.decode('utf-8')
    return None
def decode_to_file(zip_path, target_path, output_path):
    target_path=os.path.splitext(os.path.basename(zip_path))[0]+"/"+target_path
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        target_path = target_path.rstrip('/')
        files_to_extract = [f for f in zip_ref.namelist() if f.startswith(target_path)]

        if len(files_to_extract) == 0:
            raise FileNotFoundError(f"{target_path} not found in the archive.")

        if len(files_to_extract) == 1 and not files_to_extract[0].endswith('/'):
            # Cible est un fichier unique
            output_file_path = output_path
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with zip_ref.open(files_to_extract[0]) as source, open(output_file_path, 'wb') as target:
                target.write(source.read())
        else:
            # Cible est un dossier ou plusieurs fichiers
            for file in files_to_extract:
                relative_path = os.path.relpath(file, start=target_path)
                destination_path = os.path.join(output_path, relative_path)

                if file.endswith('/'):
                    os.makedirs(destination_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    with zip_ref.open(file) as source, open(destination_path, 'wb') as target:
                        target.write(source.read())


if __name__ == "__main__":
    in_repo_file="G:/Mon Drive/AAIT_resources/repository.aait"
    out_repo_file="C:/a_supp/toto.aait"
    create_index_file(in_repo_file, out_repo_file)

