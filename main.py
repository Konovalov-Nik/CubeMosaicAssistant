import customtkinter

import numpy as np

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter

IMAGE_PATH = None

ORIGINAL_TK_IMAGE = None
ORIGNINAL_IMAGE_LBL = None

SELECTION_WIDTH = 100
SELECTION_HEIGHT = 100

SELECTION_OFFSET_X = None
SELECTION_OFFSET_Y = None

TARGET_WIDTH = 30
TARGET_HEIGHT = 30

PROCESSED_PREVIEW_WIDTH = 150
PROCESSED_PREVIEW_HEIGHT = 150

OUTPUT_MODE = 5

# outer_bounds are always 0 and 255
GREY_DEFAULT_LEVELS = {6: [42, 84, 126, 168, 210], 5: [51, 102, 153, 204]}
GREY_DEFAULT_DOWNCOLOR_TARGETS = {6: [0, 51, 102, 153, 204, 255],
                                  5: [0, 63, 127, 191, 255]}

SLIDERS_FRAME = None
GREY_SLIDERS = []
GREY_SLIDER_VALUES = []

# 0: blue, 1: green, 2: red, 3: orange, 4: yellow, 5: white
RUBIC_CUBE_COLORS = {6: [(0, 70, 173), (0, 155, 72), (183, 18, 52), (255, 88, 0), (255, 213, 0), (255, 255, 255)],
                     5: [(0, 70, 173), (183, 18, 52), (255, 88, 0), (255, 213, 0), (255, 255, 255)]}

# SCALE_FACTOR = 2

APP = None

DEFAULT_PREVIEW_WIDTH = 300
DEFAULT_PREVIEW_HEIGHT = 500
PIL_BLANK_IMAGE = Image.new(
    "RGB", (DEFAULT_PREVIEW_WIDTH, int(DEFAULT_PREVIEW_WIDTH * 1.3)), color=(255, 255, 255))
PIL_IMAGE_DISPLAY = PIL_BLANK_IMAGE.copy()
PIL_IMAGE_CLEAN = PIL_BLANK_IMAGE.copy()

PIL_GREYSCALE_IMAGE = None
GREYSCALE_TK_IMAGE = None

PIL_GREYSCALE_BLURED_IMAGE = None
GREYSCALE_BLURED_TK_IMAGE = None
BLUR_RADIUS = None

PIL_GREYSCALE_DOWNCOLORED_IMAGE = None
GREYSCALE_DOWNCLORED_TK_IMAGE = None

PIL_RUBICKS_IMAGE = None
RUBICKS_TK_IMAGE = None


def set_default_image():
    global IMAGE_PATH
    IMAGE_PATH = "demo_photo.jpg"

    SELECTION_OFFSET_X.set(298)
    SELECTION_OFFSET_Y.set(340)
    SELECTION_WIDTH.set(330)
    SELECTION_HEIGHT.set(330)

    BLUR_RADIUS.set(0)

    refresh_all_chain(reload_original=True)


def set_test_gradient_image():
    global IMAGE_PATH
    IMAGE_PATH = "test_gradient.jpg"
    SELECTION_OFFSET_X.set(0)
    SELECTION_OFFSET_Y.set(0)
    SELECTION_WIDTH.set(300)
    SELECTION_HEIGHT.set(300)

    refresh_all_chain(reload_original=True)


def load_image():
    global IMAGE_PATH
    IMAGE_PATH = customtkinter.filedialog.askopenfilename(
        initialdir=".", title="Select file", filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png"), ("all files", "*.*")))

    refresh_all_chain(reload_original=True)


def refresh_original_image(reload=False):
    global IMAGE_PATH
    global PIL_IMAGE_CLEAN
    global PIL_IMAGE_DISPLAY

    if reload:
        if IMAGE_PATH:
            PIL_IMAGE_CLEAN = Image.open(IMAGE_PATH)
        else:
            PIL_IMAGE_CLEAN = PIL_BLANK_IMAGE

        PIL_IMAGE_DISPLAY = PIL_IMAGE_CLEAN.copy()

    w, h = scale_to_fit(
        PIL_IMAGE_DISPLAY.width, PIL_IMAGE_DISPLAY.height, DEFAULT_PREVIEW_WIDTH, DEFAULT_PREVIEW_HEIGHT)
    global ORIGINAL_TK_IMAGE
    ORIGINAL_TK_IMAGE.configure(light_image=PIL_IMAGE_DISPLAY, size=(w, h))


def scale_to_fit(w, h, target_width, target_height):
    if w / h > target_width / target_height:
        return (target_width, int(target_width * h / w))
    else:
        return (int(target_height * w / h), target_height)


def handle_mouse_click(event):
    global SELECTION_OFFSET_X
    global SELECTION_OFFSET_Y

    global PIL_IMAGE_DISPLAY

    e_x = event.x
    e_y = event.y

    preview_scale = PIL_IMAGE_DISPLAY.width / ORIGINAL_TK_IMAGE.cget("size")[0]

    SELECTION_OFFSET_X.set(int(e_x * preview_scale) -
                           int(SELECTION_WIDTH.get() / 2))
    SELECTION_OFFSET_Y.set(int(e_y * preview_scale) -
                           int(SELECTION_HEIGHT.get() / 2))

    refresh_all_chain()


def reset_sliders():
    for s in GREY_SLIDERS:
        if s:
            s.destroy()
    GREY_SLIDERS.clear()
    GREY_SLIDER_VALUES.clear()

    for i in range(OUTPUT_MODE.get() - 1):
        GREY_SLIDER_VALUES.append(customtkinter.IntVar(
            value=GREY_DEFAULT_LEVELS[OUTPUT_MODE.get()][i]))
        GREY_SLIDER_VALUES[i].trace_add(
            "write", lambda *args: refresh_all_chain())
        GREY_SLIDERS.append(customtkinter.CTkSlider(
            master=SLIDERS_FRAME, variable=GREY_SLIDER_VALUES[i], from_=0, to=255))
        GREY_SLIDERS[i].grid(row=i+1, column=0, padx=10, pady=10, columnspan=2)


def reset_blur():
    BLUR_RADIUS.set(5)


def draw_selection_rect():
    global PIL_IMAGE_DISPLAY
    PIL_IMAGE_DISPLAY = PIL_IMAGE_CLEAN.copy()
    draw = ImageDraw.Draw(PIL_IMAGE_DISPLAY)

    draw.rectangle(
        (SELECTION_OFFSET_X.get(), SELECTION_OFFSET_Y.get(),
         SELECTION_OFFSET_X.get() + SELECTION_WIDTH.get(), SELECTION_OFFSET_Y.get() + SELECTION_HEIGHT.get()),
        outline="red", width=2)

    ORIGINAL_TK_IMAGE.configure(light_image=PIL_IMAGE_DISPLAY)


def refresh_all_chain(reload_original=False):
    refresh_original_image(reload=reload_original)
    draw_selection_rect()
    draw_greyscale_cut_image()
    draw_greyscale_blured_image()
    draw_greyscale_downcolored_image()
    draw_rubicks_image()


def draw_greyscale_cut_image():
    global PIL_GREYSCALE_IMAGE

    PIL_GREYSCALE_IMAGE = PIL_IMAGE_CLEAN.copy() \
        .crop((SELECTION_OFFSET_X.get(), SELECTION_OFFSET_Y.get(),
               SELECTION_OFFSET_X.get() + SELECTION_WIDTH.get(), SELECTION_OFFSET_Y.get() + SELECTION_HEIGHT.get())) \
        .resize((TARGET_WIDTH.get(), TARGET_HEIGHT.get()))

    w, h = scale_to_fit(
        PIL_GREYSCALE_IMAGE.width, PIL_GREYSCALE_IMAGE.height,
        PROCESSED_PREVIEW_WIDTH, PROCESSED_PREVIEW_HEIGHT)

    PIL_GREYSCALE_IMAGE = PIL_GREYSCALE_IMAGE.convert("L")
    GREYSCALE_TK_IMAGE.configure(light_image=PIL_GREYSCALE_IMAGE, size=(w, h))


def draw_greyscale_blured_image():
    global PIL_GREYSCALE_BLURED_IMAGE

    PIL_GREYSCALE_BLURED_IMAGE = PIL_GREYSCALE_IMAGE.copy()
    PIL_GREYSCALE_BLURED_IMAGE = PIL_GREYSCALE_BLURED_IMAGE.filter(
        ImageFilter.GaussianBlur(radius=BLUR_RADIUS.get()))

    w, h = scale_to_fit(
        PIL_GREYSCALE_BLURED_IMAGE.width, PIL_GREYSCALE_BLURED_IMAGE.height,
        PROCESSED_PREVIEW_WIDTH, PROCESSED_PREVIEW_HEIGHT)

    GREYSCALE_BLURED_TK_IMAGE.configure(
        light_image=PIL_GREYSCALE_BLURED_IMAGE, size=(w, h))


def draw_greyscale_downcolored_image():
    global PIL_GREYSCALE_DOWNCOLORED_IMAGE
    np_downclored_image = np.array(PIL_GREYSCALE_BLURED_IMAGE)
    grey_slider_values = [s.get() for s in GREY_SLIDER_VALUES]
    grey_targerts = [0] + grey_slider_values

    for i in range(len(grey_slider_values)):
        np_downclored_image = np.where(
            (np_downclored_image >= grey_targerts[i]) & (
                np_downclored_image < grey_targerts[i+1]),
            grey_targerts[i], np_downclored_image)

    PIL_GREYSCALE_DOWNCOLORED_IMAGE = Image.fromarray(np_downclored_image)
    w, h = scale_to_fit(
        PIL_GREYSCALE_DOWNCOLORED_IMAGE.width, PIL_GREYSCALE_DOWNCOLORED_IMAGE.height,
        PROCESSED_PREVIEW_WIDTH, PROCESSED_PREVIEW_HEIGHT)

    GREYSCALE_DOWNCLORED_TK_IMAGE.configure(
        light_image=PIL_GREYSCALE_DOWNCOLORED_IMAGE, size=(w, h))


def draw_rubicks_image():
    global PIL_RUBICKS_IMAGE

    PIL_RUBICKS_IMAGE = PIL_GREYSCALE_DOWNCOLORED_IMAGE.copy()
    PIL_RUBICKS_IMAGE = PIL_RUBICKS_IMAGE.convert("RGB")

    downcolored_data = list(PIL_GREYSCALE_DOWNCOLORED_IMAGE.getdata())
    target_tmp_image = []
    grey_slider_values = [s.get() for s in GREY_SLIDER_VALUES]
    grey_targerts = [0] + grey_slider_values + [255]
    target_colors = RUBIC_CUBE_COLORS[OUTPUT_MODE.get()]
    grey_to_target = dict(zip(grey_targerts, target_colors))

    for p in downcolored_data:
        target_tmp_image.append(grey_to_target.get(p, target_colors[-1]))

    PIL_RUBICKS_IMAGE.putdata(target_tmp_image)
    w, h = scale_to_fit(
        PIL_RUBICKS_IMAGE.width, PIL_RUBICKS_IMAGE.height,
        PROCESSED_PREVIEW_WIDTH, PROCESSED_PREVIEW_HEIGHT)
    RUBICKS_TK_IMAGE.configure(light_image=PIL_RUBICKS_IMAGE, size=(w, h))


def export_simple():
    save_file_path = customtkinter.filedialog.asksaveasfilename(
        initialdir="./", title="Select file",
        filetypes=(("PNG files", "*.png"), ("all files", "*.*")))
    PIL_RUBICKS_IMAGE.save(save_file_path)


def export_upscaled_with_grid():
    save_file_path = customtkinter.filedialog.asksaveasfilename(
        initialdir="./", title="Select file",
        filetypes=(("PNG files", "*.png"), ("all files", "*.*")))

    PIL_RUBICKS_IMAGE_UPSCALED = PIL_RUBICKS_IMAGE.copy()
    PIL_RUBICKS_IMAGE_UPSCALED = PIL_RUBICKS_IMAGE_UPSCALED.resize(
        (PIL_RUBICKS_IMAGE_UPSCALED.width * 5,
         PIL_RUBICKS_IMAGE_UPSCALED.height * 5), resample=Image.NEAREST)
    # draw line every 5 pixels
    draw = ImageDraw.Draw(PIL_RUBICKS_IMAGE_UPSCALED)
    for i in range(0, PIL_RUBICKS_IMAGE_UPSCALED.width, 5):
        line = ((i, 0), (i, PIL_RUBICKS_IMAGE_UPSCALED.height))
        draw.line(line, fill="black")
    for i in range(0, PIL_RUBICKS_IMAGE_UPSCALED.height, 5):
        line = ((0, i), (PIL_RUBICKS_IMAGE_UPSCALED.width, i))
        draw.line(line, fill="black")

    PIL_RUBICKS_IMAGE_UPSCALED.save(save_file_path)


def main():

    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    global APP
    APP = customtkinter.CTk()
    APP.geometry("1100x900")

    original_image_frame = customtkinter.CTkFrame(
        master=APP, width=DEFAULT_PREVIEW_WIDTH, height=DEFAULT_PREVIEW_HEIGHT)
    original_image_frame.grid(row=0, column=0, padx=10, pady=10)

    load_user_image_button = customtkinter.CTkButton(
        master=original_image_frame, text="Open image", command=load_image)
    load_user_image_button.grid(row=0, column=0, padx=10, pady=10)

    load_default_image_button = customtkinter.CTkButton(
        master=original_image_frame, text="Load Example Image", command=set_default_image)
    load_default_image_button.grid(row=0, column=1, padx=10, pady=10)

    load_test_gradient_image_button = customtkinter.CTkButton(
        master=original_image_frame, text="Load Test Gradient", command=set_test_gradient_image)
    load_test_gradient_image_button.grid(row=0, column=2, padx=10, pady=10)

    w, h = scale_to_fit(
        PIL_IMAGE_DISPLAY.width, PIL_IMAGE_DISPLAY.height,
        DEFAULT_PREVIEW_WIDTH, DEFAULT_PREVIEW_HEIGHT)
    global ORIGINAL_TK_IMAGE
    ORIGINAL_TK_IMAGE = customtkinter.CTkImage(
        light_image=PIL_IMAGE_DISPLAY, size=(w, h))
    global ORIGNINAL_IMAGE_LBL
    ORIGNINAL_IMAGE_LBL = customtkinter.CTkLabel(
        master=original_image_frame, image=ORIGINAL_TK_IMAGE, text="")
    ORIGNINAL_IMAGE_LBL.grid(row=1, column=0, padx=0, pady=0, columnspan=3)

    selection_frame = customtkinter.CTkFrame(
        master=original_image_frame, width=DEFAULT_PREVIEW_WIDTH)
    selection_frame.grid(row=2, column=0, padx=10, pady=10, columnspan=3)

    global SELECTION_OFFSET_X
    SELECTION_OFFSET_X = customtkinter.IntVar(value=0)
    SELECTION_OFFSET_X.trace_add("write", lambda *args: refresh_all_chain())
    selection_offset_x_label = customtkinter.CTkLabel(
        master=selection_frame, text="Selection X:")
    selection_offset_x_label.grid(row=0, column=0, padx=5, pady=10)
    selection_offset_x = customtkinter.CTkEntry(
        master=selection_frame, textvariable=SELECTION_OFFSET_X)
    selection_offset_x.grid(row=0, column=1, padx=5, pady=10)

    global SELECTION_OFFSET_Y
    SELECTION_OFFSET_Y = customtkinter.IntVar(value=0)
    SELECTION_OFFSET_Y.trace_add("write", lambda *args: refresh_all_chain())
    selection_offset_y_label = customtkinter.CTkLabel(
        master=selection_frame, text="Selection Y:")
    selection_offset_y_label.grid(row=0, column=2, padx=5, pady=10)
    selection_offset_y = customtkinter.CTkEntry(
        master=selection_frame, textvariable=SELECTION_OFFSET_Y)
    selection_offset_y.grid(row=0, column=3, padx=5, pady=10)

    global SELECTION_WIDTH
    SELECTION_WIDTH = customtkinter.IntVar(value=100)
    SELECTION_WIDTH.trace_add("write", lambda *args: refresh_all_chain())
    selection_width_label = customtkinter.CTkLabel(
        master=selection_frame, text="Width:")
    selection_width_label.grid(row=1, column=0, padx=5, pady=10)
    selection_width = customtkinter.CTkEntry(
        master=selection_frame, textvariable=SELECTION_WIDTH)
    selection_width.grid(row=1, column=1, padx=5, pady=10)

    global SELECTION_HEIGHT
    SELECTION_HEIGHT = customtkinter.IntVar(value=100)
    SELECTION_HEIGHT.trace_add("write", lambda *args: refresh_all_chain())
    selection_height_label = customtkinter.CTkLabel(
        master=selection_frame, text="Height:")
    selection_height_label.grid(row=1, column=2, padx=5, pady=10)
    selection_height = customtkinter.CTkEntry(
        master=selection_frame, textvariable=SELECTION_HEIGHT)
    selection_height.grid(row=1, column=3, padx=5, pady=10)

    global TARGET_WIDTH
    TARGET_WIDTH = customtkinter.IntVar(value=30)
    TARGET_WIDTH.trace_add("write", lambda *args: refresh_all_chain())
    target_width_label = customtkinter.CTkLabel(
        master=selection_frame, text="Target Width:")
    target_width_label.grid(row=2, column=0, padx=5, pady=10)
    target_width = customtkinter.CTkEntry(
        master=selection_frame, textvariable=TARGET_WIDTH)
    target_width.grid(row=2, column=1, padx=5, pady=10)

    global TARGET_HEIGHT
    TARGET_HEIGHT = customtkinter.IntVar(value=30)
    TARGET_HEIGHT.trace_add("write", lambda *args: refresh_all_chain())
    target_height_label = customtkinter.CTkLabel(
        master=selection_frame, text="Target Height:")
    target_height_label.grid(row=2, column=2, padx=5, pady=10)
    target_height = customtkinter.CTkEntry(
        master=selection_frame, textvariable=TARGET_HEIGHT)
    target_height.grid(row=2, column=3, padx=5, pady=10)

    global OUTPUT_MODE
    OUTPUT_MODE = customtkinter.IntVar(value=5)
    OUTPUT_MODE.trace_add(
        "write", lambda *args: (reset_sliders(), refresh_all_chain()))
    output_mode_label = customtkinter.CTkLabel(
        master=selection_frame, text="Output Mode:")
    output_mode_label.grid(row=3, column=0, padx=5, pady=10)
    mode_6 = customtkinter.CTkRadioButton(
        master=selection_frame, text="6 - colored", variable=OUTPUT_MODE, value=6)
    mode_6.grid(row=3, column=1, padx=5, pady=10)
    mode_5 = customtkinter.CTkRadioButton(
        master=selection_frame, text="5 - colored", variable=OUTPUT_MODE, value=5)
    mode_5.grid(row=3, column=2, padx=5, pady=10)

    processed_image_frame = customtkinter.CTkFrame(master=APP, width=200)
    processed_image_frame.grid(row=0, column=1, padx=10, pady=10)

    global GREYSCALE_TK_IMAGE
    GREYSCALE_TK_IMAGE = customtkinter.CTkImage(
        light_image=PIL_BLANK_IMAGE, size=(PROCESSED_PREVIEW_WIDTH, PROCESSED_PREVIEW_HEIGHT))
    greyscale_cut_header = customtkinter.CTkLabel(
        master=processed_image_frame, text="Greyscale Cut Image")
    greyscale_cut_header.grid(row=0, column=0, padx=10, pady=10)
    greyscale_cut_image_lbl = customtkinter.CTkLabel(
        master=processed_image_frame, image=GREYSCALE_TK_IMAGE, text="")
    greyscale_cut_image_lbl.grid(row=1, column=0, padx=10, pady=0)

    global GREYSCALE_BLURED_TK_IMAGE
    GREYSCALE_BLURED_TK_IMAGE = customtkinter.CTkImage(
        light_image=PIL_BLANK_IMAGE, size=(PROCESSED_PREVIEW_WIDTH, PROCESSED_PREVIEW_HEIGHT))
    greyscale_blured_header = customtkinter.CTkLabel(
        master=processed_image_frame, text="Greyscale Blured Image")
    greyscale_blured_header.grid(row=2, column=0, padx=10, pady=10)
    greyscale_blured_image_lbl = customtkinter.CTkLabel(
        master=processed_image_frame, image=GREYSCALE_BLURED_TK_IMAGE, text="")
    greyscale_blured_image_lbl.grid(row=3, column=0, padx=10, pady=0)

    global GREYSCALE_DOWNCLORED_TK_IMAGE
    GREYSCALE_DOWNCLORED_TK_IMAGE = customtkinter.CTkImage(
        light_image=PIL_BLANK_IMAGE, size=(PROCESSED_PREVIEW_WIDTH, PROCESSED_PREVIEW_HEIGHT))
    greyscale_downcolored_header = customtkinter.CTkLabel(
        master=processed_image_frame, text="Greyscale Downcolored Image")
    greyscale_downcolored_header.grid(row=4, column=0, padx=10, pady=10)
    greyscale_downcolored_image_lbl = customtkinter.CTkLabel(
        master=processed_image_frame, image=GREYSCALE_DOWNCLORED_TK_IMAGE, text="")
    greyscale_downcolored_image_lbl.grid(row=5, column=0, padx=10, pady=0)

    global RUBICKS_TK_IMAGE
    RUBICKS_TK_IMAGE = customtkinter.CTkImage(
        light_image=PIL_BLANK_IMAGE, size=(PROCESSED_PREVIEW_WIDTH, PROCESSED_PREVIEW_HEIGHT))
    rubicks_header = customtkinter.CTkLabel(
        master=processed_image_frame, text="Rubicks Image")
    rubicks_header.grid(row=6, column=0, padx=10, pady=10)
    rubicks_image_lbl = customtkinter.CTkLabel(
        master=processed_image_frame, image=RUBICKS_TK_IMAGE, text="")
    rubicks_image_lbl.grid(row=7, column=0, padx=10, pady=0)

    settings_frame = customtkinter.CTkFrame(master=APP, width=200)
    settings_frame.grid(row=0, column=2, padx=10, pady=10)

    blur_frame = customtkinter.CTkFrame(master=settings_frame, width=200)
    blur_frame.grid(row=0, column=0, padx=10, pady=10)

    global BLUR_RADIUS
    BLUR_RADIUS = customtkinter.IntVar(value=1)
    BLUR_RADIUS.trace_add("write", lambda *args: (refresh_all_chain()))
    blur_header = customtkinter.CTkLabel(
        master=blur_frame, text="Blur Radius")
    blur_header.grid(row=1, column=0, padx=10, pady=10)
    blur_reset_button = customtkinter.CTkButton(
        master=blur_frame, text="Reset", command=reset_blur)
    blur_reset_button.grid(row=1, column=1, padx=10, pady=10)
    blur_value_input = customtkinter.CTkEntry(
        master=blur_frame, textvariable=BLUR_RADIUS)
    blur_value_input.grid(row=2, column=0, padx=10, pady=10, columnspan=2)
    blur_slider = customtkinter.CTkSlider(
        master=blur_frame, from_=0, to=10, variable=BLUR_RADIUS)
    blur_slider.grid(row=3, column=0, padx=10, pady=10, columnspan=2)

    global SLIDERS_FRAME
    SLIDERS_FRAME = customtkinter.CTkFrame(master=settings_frame, width=200)
    SLIDERS_FRAME.grid(row=1, column=0, padx=10, pady=10)

    sliders_header = customtkinter.CTkLabel(
        master=SLIDERS_FRAME, text="Sensitivity Levels")
    sliders_header.grid(row=0, column=0, padx=10, pady=10)
    sliders_reset_button = customtkinter.CTkButton(
        master=SLIDERS_FRAME, text="Reset", command=lambda: (reset_sliders(), refresh_all_chain()))
    sliders_reset_button.grid(row=0, column=1, padx=10, pady=10)

    export_frame = customtkinter.CTkFrame(master=settings_frame, width=200)
    export_frame.grid(row=2, column=0, padx=10, pady=10)

    export_simple_button = customtkinter.CTkButton(
        master=export_frame, text="Export Simple", command=export_simple)
    export_simple_button.grid(row=0, column=0, padx=10, pady=10)

    export_upscaled_with_grid_button = customtkinter.CTkButton(
        master=export_frame, text="Export Upscaled With Grid", command=export_upscaled_with_grid)
    export_upscaled_with_grid_button.grid(row=1, column=0, padx=10, pady=10)

    reset_sliders()
    refresh_all_chain(reload_original=False)

    # bind mouse click event
    ORIGNINAL_IMAGE_LBL.bind("<Button-1>", handle_mouse_click)

    APP.mainloop()


if __name__ == "__main__":
    main()
