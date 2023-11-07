import os
import math
import struct
import gzip
import binascii
import tkinter as tk
from tkinter import filedialog, messagebox

def pack_character_to_font(font_file_path):
    print("Start create font file")
    folder_path = 'fonts'
    file_names = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.tga'):
            file_names.append(filename)

    header = "544E4F4628000000280000000400000018000000"
    with open(font_file_path, "wb") as file:
        binary_data = bytes.fromhex(header)
        file.write(binary_data)
        file.write(struct.pack("<i", len(file_names)))
        offsets=len(file_names)*8+24
        offset=offsets
        all_size=0
        for filename in file_names:
            parts = filename.split('_')
            number, char, k_left, k_top, k_right_with_extension = parts
            k_right = os.path.splitext(k_right_with_extension)[0]
            file.write(struct.pack("<i", int(char)))
            file.write(struct.pack("<i", offset))

            with open("fonts/"+filename, 'rb') as char_image_file:
                char_image_file.seek(12)
                width = struct.unpack("<H", char_image_file.read(2))[0]
                height = struct.unpack("<H", char_image_file.read(2))[0]
                char_image_file.seek(18)
                image_data = char_image_file.read(width * height * 4)
                size=width * height
                all_size += size+5
                offset=offsets+all_size

        for filename in file_names:
            parts = filename.split('_')
            number, char, k_left, k_top, k_right_with_extension = parts
            k_left = int(k_left)
            k_top = int(k_top)
            k_right = int(os.path.splitext(k_right_with_extension)[0])
            print(f'Number={number}, Char={chr(int(char))}, Kerning left={k_left}, Kerning top={k_top}, Kerning right={k_right}')
            with open("fonts/"+filename, 'rb') as char_image_file:
                char_image_file.seek(12)
                width = struct.unpack("<H", char_image_file.read(2))[0]
                height = struct.unpack("<H", char_image_file.read(2))[0]
                char_image_file.seek(18)
                image_data = char_image_file.read(width * height * 4)
                file.write(struct.pack('B', width))
                file.write(struct.pack('B', height))
                file.write(struct.pack('B', k_left))    # kerning from left
                file.write(struct.pack('B', k_top))     # kerning from top
                file.write(struct.pack('B', k_right))   # kerning from right
                for i in range(width * height):
                    alpha = image_data[i*4 + 3]
                    file.write(struct.pack('B', alpha))
    output_file="MGS_Font_nht.raw.gz"
    target_exe="METAL GEAR SOLID3.exe"
    with open(font_file_path, 'rb') as f_in:
        data = f_in.read()
    with gzip.open(output_file, 'wb', compresslevel=9) as f_out:
        f_out.write(data)
    
    compressed_size = os.path.getsize(output_file)
    if compressed_size > 967298 * 1024:
        print("Error: The compressed file size is too large.")
    else:
        with open(target_exe, 'rb') as exe_file:
            exe_data = exe_file.read()
        hex_pattern = binascii.unhexlify("0400000082C20E000000000000000000")
        offset = exe_data.find(hex_pattern)
        if offset != -1:
            with open(output_file, 'rb') as gz_file:
                compressed_data = gz_file.read()
            with open(target_exe, 'r+b') as exe_file:
                exe_file.seek(offset + len(hex_pattern))
                exe_file.write(compressed_data)
            print("The compressed file was successfully added to", target_exe)
        else:
            print("Hexadecimal pattern not found in", target_exe)

def main(font_file_path):
    pack_character_to_font(font_file_path)

def main_ex(font_file_path):
    os.system("cls")
    f = open(font_file_path, 'rb')
    if not os.path.exists("fonts"):
        os.makedirs("fonts")
    magic		= struct.unpack("L", f.read(4))[0]
    unk0		= struct.unpack("L", f.read(4))[0]
    unk1		= struct.unpack("L", f.read(4))[0]
    unk2		= struct.unpack("L", f.read(4))[0]
    unk3		= struct.unpack("L", f.read(4))[0]
    charsCount	= struct.unpack("L", f.read(4))[0]

    for h in range(charsCount):
        f.seek(24 + h * 8)
        char	= struct.unpack("L", f.read(4))[0]
        offset	= struct.unpack("L", f.read(4))[0]

        f.seek(offset)
        width	= struct.unpack("B", f.read(1))[0]
        height	= struct.unpack("B", f.read(1))[0]
        k_left	= struct.unpack("B", f.read(1))[0] # kerning from left
        k_top	= struct.unpack("B", f.read(1))[0] # kerning from top
        k_right	= struct.unpack("B", f.read(1))[0] # kerning from right
        #f.read(3)

        save	= open("fonts/"+str(h).zfill(6)+"_"+str(char)+"_"+str(k_left)+"_"+str(k_top)+"_"+str(k_right)+".tga","wb")
        save.write(struct.pack('B', 0))
        save.write(struct.pack('B', 0))			# is mapped?
        save.write(struct.pack('B', 2))			# 
        save.write(struct.pack('H', 0))			# first color index
        save.write(struct.pack('H', 0))			# number of colors
        save.write(struct.pack('B', 32))		# bits per color
        save.write(struct.pack('H', 0))			# x-origin
        save.write(struct.pack('H', 0))			# y-origin
        save.write(struct.pack('H', width))	    # width
        save.write(struct.pack('H', height))	# height
        save.write(struct.pack('B', 32))		# bits per pixel
        save.write(struct.pack('B', 32))
    
        for i in range(width*height):
            save.write(struct.pack('B', 0))
            save.write(struct.pack('B', 0))
            save.write(struct.pack('B', 0))
            save.write(f.read(1))


def open_font_file():
    font_file_path = filedialog.askopenfilename(title="Open Font File", filetypes=[("Raw files", "*.raw")])
    if font_file_path:
        try:
            print(f"Font file selected: {font_file_path}")
            main(font_file_path)
            messagebox.showinfo("Success", "Characters packed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            print(f"An error occurred: {e}")

def open_font_file_ex():
    font_file_path = filedialog.askopenfilename(title="Open Font File", filetypes=[("Raw files", "*.raw")])
    if font_file_path:
        try:
            print(f"Font file selected: {font_file_path}")
            main_ex(font_file_path)
            messagebox.showinfo("Success", "Characters extract successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            print(f"An error occurred: {e}")

root = tk.Tk()
root.title("Font Extract\Packer")

open_button_ex = tk.Button(root, text="Extract Font File", command=open_font_file_ex)
open_button_ex.pack(pady=20)
open_button = tk.Button(root, text="Pack Font File", command=open_font_file)
open_button.pack(pady=20)

root.mainloop()
