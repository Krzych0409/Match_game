from PIL import Image, ImageOps
import os


def find_all_image(dir_name):
    # Do list with all file in directory
    list_files = os.listdir(rf'{dir_name}')
    # Images list
    list_img_text = []

    # Delete all files except image files
    for file in list_files:
        file_type = file.lower().split('.')[-1]
        if file_type == 'png' or file_type == 'jpg' or file_type == 'jpeg':
            # Add image to images list
            list_img_text.append(file)

    return list_img_text

def resize_images(list_img_text, dir_name, new_dir_name, max_px: int):
    max_length_vertical = 0
    max_length_horizontal = 0
    for img_text in list_img_text:
        # Load image with orientation
        image = ImageOps.exif_transpose(Image.open(rf'./{dir_name}/{img_text}'))

        width_img, height_img = image.size

        # Do new directory
        if not os.path.isdir(rf'.\images\{new_dir_name}'):
            os.mkdir(rf'.\images\{new_dir_name}')

        # Check position image
        if width_img > height_img:
            scale = width_img / max_px
            width_img_resize = max_px
            height_img_resize = int(height_img / scale)
            if height_img_resize > max_length_vertical:
                max_length_vertical = height_img_resize
            if width_img_resize > max_length_horizontal:
                max_length_horizontal = width_img_resize

            img_resize = image.resize((width_img_resize, height_img_resize))
            img_resize.save(rf'.\images\{new_dir_name}\{img_text.split(".")[0]}.png')

        else:
            scale = height_img / max_px
            height_img_resize = max_px
            width_img_resize = int(width_img / scale)
            if height_img_resize > max_length_vertical:
                max_length_vertical = height_img_resize
            if width_img_resize > max_length_horizontal:
                max_length_horizontal = width_img_resize

            img_resize = image.resize((width_img_resize, height_img_resize))
            img_resize.save(rf'.\images\{new_dir_name}\{img_text.split(".")[0]}.png')

    img_default = Image.open(rf'.\images\0.png').resize((max_length_horizontal, max_length_vertical))
    img_default.save(rf'.\images\{new_dir_name}\0.png')

if __name__ == "__main__":
    max_px = 400
    dir_img = 'my_img'
    new_dir_name = 'max400'
    list_img_text = find_all_image(dir_img)
    list_img_obj = resize_images(list_img_text, dir_img, new_dir_name, max_px)

