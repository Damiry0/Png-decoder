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


List_combo = []
# define the window layout
layout = [[sg.Text("Choose a file: "), sg.FileBrowse(key="-IN-")],
          [sg.Canvas(key='-CANVAS-'), sg.Multiline("", size=(15, 15), key='OUTPUT', visible=False, no_scrollbar=True)],
          [sg.Button('Decode'),
           sg.InputCombo(List_combo, key='chunk_names_combo', size=(5, 5), visible=False,
                         enable_events=True)]]

# create the form and show it without the plot
window = sg.Window('Png-decoder', layout, finalize=True,
                   element_justification='center', font='Helvetica 18')

fig, chunk_names, Width, Height, Bit_depth, Color_type, Gamma, SRGB, PHYs, CHRM, TIME, TEXT, Compression_method, Filter_method, Interlace_method = object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == "Decode":
        fig, chunk_names, Width, Height, Bit_depth, Color_type, Gamma, SRGB, PHYs, CHRM, TIME, TEXT, Compression_method, Filter_method, Interlace_method = png.open_png(
            values["-IN-"])
        fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
        window['OUTPUT'].update(
            f"Width:{Width} Height:{Height} Bit_depth:{Bit_depth} Color_type:{Color_type} Gamma:{Gamma} cHRM:{CHRM} sRGB:{SRGB} pHYs:{PHYs} date:{PHYs} text:{TEXT}",
            visible=True)
        List_combo = chunk_names
        window['chunk_names_combo'].update(values=List_combo, visible=True)
    elif event == 'chunk_names_combo':

        if values['chunk_names_combo'] == b"IHDR":
            window['OUTPUT'].update(f"Width:{Width} Height:{Height} Bit_depth:{Bit_depth} Color_type:{Color_type}")

        elif values['chunk_names_combo'] == b"gAMA":
            window['OUTPUT'].update(f"Gamma:{Gamma}", visible=True)

        elif values['chunk_names_combo'] == b"cHRM":
            window['OUTPUT'].update(f"cHRM:{CHRM}", visible=True)

        elif values['chunk_names_combo'] == b"sRGB":
            window['OUTPUT'].update(f"sRGB:{SRGB}", visible=True)

        elif values['chunk_names_combo'] == b"pHYs":
            window['OUTPUT'].update(f"pHYs:{PHYs}", visible=True)

        elif values['chunk_names_combo'] == b"IEND":
            window['OUTPUT'].update(f"IEND chunk loaded correctly", visible=True)

        elif values['chunk_names_combo'] == b"IDAT":
            window['OUTPUT'].update(f"IDAT chunk loaded correctly, results are shown on the left", visible=True)

        # elif values['chunk_names_combo'] == b"tIME":
        #     window['OUTPUT'].update(
        #         f"Width:{Width} Height:{Height} Bit_depth:{Bit_depth} Color_type:{Color_type} Gamma:{Gamma} cHRM:{CHRM} sRGB:{SRGB} pHYs:{PHYs} date:{PHYs} text:{TEXT}",
        #         visible=True)

        elif values['chunk_names_combo'] == b"tEXt":
            window['OUTPUT'].update(f"text:{TEXT}", visible=True)

        else:
            window['OUTPUT'].update(f"error")

window.close()
