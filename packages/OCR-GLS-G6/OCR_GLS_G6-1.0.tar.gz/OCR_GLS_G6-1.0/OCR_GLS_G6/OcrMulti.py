import tempfile
import fitz  # PyMuPDF
from PIL import Image
import easyocr
import os
import gc
def pdf_to_images(pdf_path, dpi=300):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    images_paths = []
    temp = tempfile.mkdtemp(prefix="pre_",suffix="_suf")
    # Loop through all pages
    for page_number in range(len(pdf_document)):
        # Select the page
        page = pdf_document.load_page(page_number)
        # Convert page to a pixmap (image)
        zoom = dpi / 72  # DPI conversion factor
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        # Save the pixmap as an image
        img_path = f'{temp}\\page_{page_number+1}.png'
        pix.save(img_path)
        images_paths.append(img_path)
        #os.remove(image_path)
        del img_path
        del pix
    return images_paths

def crop_image(image_path, crop_box):
    # Open the image
    temp = tempfile.mkdtemp(prefix="pre_",suffix="_suf")
    with Image.open(image_path) as img:
        # Crop the image
        cropped_img = img.crop(crop_box)
        # Save the cropped image
        cropped_img_path = f'{temp}\\page.png'
        cropped_img.save(cropped_img_path, dpi=(img.info['dpi']))
        #os.remove(cropped_img_path)
        del cropped_img
    return cropped_img_path

# Example usagepy
class MultiPdf :
    def MultiOcr(pdf_path,crop_box,dpi=300):
        AllResult = []
        gc.enable()
        gc.set_threshold(600, 50, 50)
        reader = easyocr.Reader(['en'], gpu=True)
        images_paths = pdf_to_images(pdf_path, dpi)
        folder_path = os.path.dirname(images_paths[0])
        for image_path in images_paths:
            cropped_image_path = crop_image(image_path, crop_box)
            allResults = reader.readtext(cropped_image_path)
            AllResult.append(allResults)
            folder_image_path = os.path.dirname(cropped_image_path)
            os.remove(cropped_image_path)
            os.remove(image_path)
            del image_path
            del allResults
            del cropped_image_path
            if not os.listdir(folder_image_path):
                os.rmdir(folder_image_path)
        if not os.listdir(folder_path):
            os.rmdir(folder_path)
        gc.collect()
        gc.disable()
        return AllResult