import cv2
import numpy as np
import os

def split_images_in_folder(folder_path):
    # Controlla se la cartella esiste
    if not os.path.exists(folder_path):
        print("La cartella specificata non esiste.")
        return
    
    # Crea una cartella di output se non esiste
    output_folder = os.path.join(folder_path, "output")
    os.makedirs(output_folder, exist_ok=True)
    
    # Ottieni la lista di file nella cartella
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            
            # Carica l'immagine
            img = cv2.imread(image_path)
            if img is None:
                print(f"Errore nel caricamento dell'immagine {filename}.")
                continue
            
            # Ottieni le dimensioni dell'immagine
            height, width, _ = img.shape
            
            # Calcola l'altezza di ogni segmento
            segment_height = width // 3
            
            # Dividi l'immagine in tre parti
            part1 = img[:, 0:segment_height]
            part2 = img[:, segment_height:2*segment_height]
            part3 = img[:, 2*segment_height:]
            
            # Salva le tre parti
            base_name, ext = os.path.splitext(filename)
            cv2.imwrite(os.path.join(output_folder, f"{base_name}_part1{ext}"), part1)
            cv2.imwrite(os.path.join(output_folder, f"{base_name}_part2{ext}"), part2)
            cv2.imwrite(os.path.join(output_folder, f"{base_name}_part3{ext}"), part3)
            
            print(f"{filename} divisa e salvata in {output_folder}")

def resize_images_in_folder(folder_path, scale=0.1):
    # Controlla se la cartella esiste
    if not os.path.exists(folder_path):
        print("La cartella specificata non esiste.")
        return
    
    # Crea una cartella di output se non esiste
    output_folder = os.path.join(folder_path, "resized")
    os.makedirs(output_folder, exist_ok=True)
    
    # Ottieni la lista di file nella cartella
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            
            # Carica l'immagine
            img = cv2.imread(image_path)
            if img is None:
                print(f"Errore nel caricamento dell'immagine {filename}.")
                continue
            
            # Ottieni le dimensioni e ridimensiona l'immagine
            height, width = img.shape[:2]
            new_dimensions = (int(width * scale), int(height * scale))
            resized_img = cv2.resize(img, new_dimensions, interpolation=cv2.INTER_AREA)
            
            # Salva l'immagine ridimensionata
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, resized_img)
            print(f"{filename} ridimensionata e salvata in {output_folder}")
