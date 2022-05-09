from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib.image as img
import matplotlib
import png
import fourier

matplotlib.use('TkAgg')
sg.theme('DarkAmber')


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


List_combo = []
# define the window layout
layout = [[sg.Text("Choose a file: "),
           sg.FileBrowse(key="-IN-")],

          [sg.Canvas(key='palette'), sg.Canvas(key='fourier'), sg.Canvas(key='-CANVAS-'),
           sg.Multiline("", size=(20, 15), key='OUTPUT', visible=False, no_scrollbar=True)],

          [sg.Button('Decode'),
           sg.InputCombo(List_combo, key='chunk_names_combo', size=(5, 5), visible=False, enable_events=True)],

          [sg.InputText(key='File to Save', default_text='filename', enable_events=True, visible=False),
           sg.InputText(key='Save As', do_not_clear=False, enable_events=True, visible=False),
           sg.FileSaveAs(key='saveButton', initial_folder='/tmp', visible=False)]]

# create the form and show it without the plot
window = sg.Window('Png-decoder', layout, finalize=True,
                   element_justification='center', font='Helvetica 18')

fig, chunk_names, Width, Height, Bit_depth, Color_type, Gamma, SRGB, PHYs, CHRM, TIME, TEXT, Compression_method, Filter_method, Interlace_method, anomizated_chunks, PLTE = object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object(), object()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == "Decode":
        fig, chunk_names, Width, Height, Bit_depth, Color_type, Gamma, SRGB, PHYs, CHRM, TIME, TEXT, Compression_method, Filter_method, Interlace_method, anomizated_chunks, PLTE = png.open_png(
            values["-IN-"])
        fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
        fig_canvas_fourier = draw_figure(window['fourier'].TKCanvas, fourier.show_plots(values["-IN-"]))
        window['OUTPUT'].update(
            f"",
            visible=True)
        List_combo = chunk_names
        window['chunk_names_combo'].update(values=List_combo, visible=True)
        window['File to Save'].update(visible=True)
        window['saveButton'].update(visible=True)
    elif event == 'chunk_names_combo':

        if values['chunk_names_combo'] == b"IHDR":
            match Color_type:
                case 0:
                    Color_type = "Each pixel is a grayscale sample."
                case 2:
                    Color_type = "Each pixel is an R,G,B triple."
                case 3:
                    Color_type = "Each pixel is a palette index a PLTE chunk must appear."
                case 4:
                    Color_type = "Each pixel is a grayscale sample, followed by an alpha sample."
                case 6:
                    Color_type = "Each pixel is an R,G,B triple, followed by an alpha sample."
            match Interlace_method:
                case 0:
                    Interlace_method = "no interlace"
                case 1:
                    Interlace_method = "Adam7 interlace"

            window['OUTPUT'].update(
                f"Width:{Width}px"f"Height:{Height}px"f"Bit_depth:{Bit_depth}"f"Color_type:{Color_type}"f"Interlace Method:{Interlace_method}")

        elif values['chunk_names_combo'] == b"gAMA":
            window['OUTPUT'].update(f"Gamma:{Gamma}", visible=True)

        elif values['chunk_names_combo'] == b"PLTE":
            draw_figure(window['palette'].TKCanvas, PLTE)
            window['OUTPUT'].update(f"Gamma:{Gamma}", visible=True)

        elif values['chunk_names_combo'] == b"cHRM":
            CHRM = [i for sub in CHRM for i in sub]
            CHRM = ''.join(str(CHRM).split("'"))
            CHRM = ''.join(str(CHRM).split(","))
            window['OUTPUT'].update(f"cHRM:{CHRM}", visible=True)

        elif values['chunk_names_combo'] == b"sRGB":
            window['OUTPUT'].update(f"sRGB:{SRGB}", visible=True)

        elif values['chunk_names_combo'] == b"pHYs":
            window['OUTPUT'].update(f"pHYs:{PHYs}", visible=True)

        elif values['chunk_names_combo'] == b"IEND":
            window['OUTPUT'].update(f"IEND chunk loaded correctly", visible=True)

        elif values['chunk_names_combo'] == b"IDAT":
            window['OUTPUT'].update(f"IDAT chunk loaded correctly, results are shown on the left", visible=True)

        elif values['chunk_names_combo'] == b"tIME":
            window['OUTPUT'].update(f"tIME:{TIME}", visible=True)

        elif values['chunk_names_combo'] == b"tEXt":
            window['OUTPUT'].update(f"\n".join("{}\t{}".format(k, v) for k, v in TEXT.items()), visible=True)

        else:
            window['OUTPUT'].update(f"error, chunk not supported")
    elif event == 'Save As':
        filename = values['Save As']
        if filename:
            window['File to Save'].update(value=filename)
            f = open(filename, "wb")
            f.write(anomizated_chunks)
            f.close()

window.close()
