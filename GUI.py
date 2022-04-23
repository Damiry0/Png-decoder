from matplotlib.ticker import NullFormatter
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
import png

matplotlib.use('TkAgg')
sg.theme('DarkAmber')


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# define the window layout
layout = [[sg.Text("Choose a file: "), sg.FileBrowse(key="-IN-")],
          [sg.Canvas(key='-CANVAS-'), sg.Multiline("", size=(15, 15), key='OUTPUT', visible=False, no_scrollbar=True)],
          [sg.Button('Decode')]]

# create the form and show it without the plot
window = sg.Window('Png-decoder', layout, finalize=True,
                   element_justification='center', font='Helvetica 18')

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == "Decode":
        fig, Width, Height, Bit_depth, Color_type, Gamma, SRGB, Compression_method, Filter_method, Interlace_method = png.open_png(
            values["-IN-"])
        fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
        window['OUTPUT'].update( f"Width:{Width} Height:{Height} Bit_depth:{Bit_depth} Color_type:{Color_type} Gamma:{Gamma} sRGB:{SRGB}",visible=True)

window.close()
