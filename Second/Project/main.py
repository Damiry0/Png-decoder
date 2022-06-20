from tkinter import Tk, Label, Button, Frame, font
from tkinter.filedialog import askopenfilename
from chunk_processor import PNGChunkProcessor
from PIL import Image, ImageTk

gui = Tk()


def choose_photo_ecb():
    img_path = askopenfilename(filetypes=[("PNG Files", "*.png")])
    chunk_processor = PNGChunkProcessor()
    img_source = open(img_path, 'rb')
    chunk_processor.save_chunks(img_source)
    chunk_processor.IHDR_chunk_processor()
    chunk_processor.IDAT_chunk_processor_ecb()
    chunk_processor.IEND_chunk_processor()
    chunk_processor.create_ecb_image()
    chunk_processor.create_ecb_library_image()
    chunk_processor.create_decrypted_image_ecb()
   # display_photo(chunk_processor)


def choose_photo_cbc():
    img_path = askopenfilename(filetypes=[("PNG Files", "*.png")])
    chunk_processor = PNGChunkProcessor()
    img_source = open(img_path, 'rb')
    chunk_processor.save_chunks(img_source)
    chunk_processor.IHDR_chunk_processor()
    chunk_processor.IDAT_chunk_processor_cbc()
    chunk_processor.IEND_chunk_processor()
    chunk_processor.create_cbc_image()
    chunk_processor.create_decrypted_image_cbc()
    display_photo(chunk_processor)


def display_photo(chunk_processor):
    filename = chunk_processor.create_new_image()
    path = "./images/{}".format(filename)
    img = Image.open(path)
    img = ImageTk.PhotoImage(Image.open(path).resize((round(400 / img.height * img.width), round(400))))
    label = Label(gui, image=img)
    label.image = img
    label.grid(row=2, column=0)


def main():
    myFont = font.Font(family='Helvetica')
    gui.title("CIPHER PNG")
    window_width = 500
    window_height = 500
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    gui.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    frame = Frame(gui)

    # label = Label(gui, text="Choose an option", font=('Helvetica 15 bold'))
    # def on_click():
    #    label["text"] = "Work in progress..."
    #    b["state"] = "disabled"


    b_ecb = Button(frame, bg="#9AC791", width=15, height=2, text="Cipher with ECB", command=choose_photo_ecb)
    b_ecb['font'] = myFont
    b_cbc = Button(frame, bg="#9AC791", width=15, height=2, text="Cipher with CBC", command=choose_photo_cbc)
    b_cbc['font'] = myFont
    frame.grid(row=0, column=0, columnspan=1, pady=10, padx=10, ipadx=175)
    b_ecb.pack(side="top")
    b_cbc.pack(side="top")
    # label.pack(side="bottom")

    gui.mainloop()


if __name__ == "__main__":
    main()
