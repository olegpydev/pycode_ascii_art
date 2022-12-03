import os
import PySimpleGUI as sg
import clipboard
from PIL import Image, ImageDraw, ImageFont

from pycode_ascii_art import PyCodeAsciiArt


def save_as_image(filename: str, text: str, background_color: str = 'white', text_color: str = 'black') -> None:
    """
    Save ASCII art as png image file

    :param filename: str
    :param text: str
    :param background_color: str
    :param text_color: str
    :return: None
    """
    lines = text.split('\n')
    width = len(max(lines, key=len))
    height = len(lines)
    width_coef = 9.65
    height_coef = 15.65
    image = Image.new("RGB", (int(width * width_coef), int(height * height_coef)), color=background_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("Courier", size=16)
    for i, line in enumerate(lines):
        draw.text((0, int(i * height_coef)), line, font=font, fill=text_color)
    image.save(filename)


def preview_window(text: str) -> None:
    height = text.count('\n') + 1
    width = max(len(i) for i in text.split('\n')) + 1
    layout = [[sg.In(default_text='white', visible=False, enable_events=True, key='-BACKGROUND_COLOR-'),
               sg.ColorChooserButton('Background Color', target='-BACKGROUND_COLOR-'),
               sg.In(default_text='black', visible=False, enable_events=True, key='-TEXT_COLOR-'),
               sg.ColorChooserButton('Text Color', target='-TEXT_COLOR-'),
               sg.Text('Font size:'),
               sg.Combo([*range(2, 16)], default_value=6, key='-FONTSIZE-', enable_events=True),
               sg.Push(),
               sg.InputText(visible=False, enable_events=True, key='-SAVE_IMAGE-'),
               sg.FileSaveAs('Save as Image', target='-SAVE_IMAGE-', default_extension='png')
               ],
              [sg.Multiline(default_text=text, key='-ML_TEXT-', size=(width, height), font=('Courier', 6),
                            no_scrollbar=True, p=(10, 10), border_width=0, background_color='white',
                            text_color='black', expand_x=True, expand_y=True)
               ]]
    window = sg.Window("Result Art Preview", layout, modal=True, font=('Arial', 14), element_justification='center',
                       resizable=True)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == '-FONTSIZE-':
            window['-ML_TEXT-'].update(font=('Courier', values['-FONTSIZE-']))

        elif event == '-BACKGROUND_COLOR-' and values['-BACKGROUND_COLOR-'] != 'None':
            window['-ML_TEXT-'].update(background_color=values['-BACKGROUND_COLOR-'])

        elif event == '-TEXT_COLOR-' and values['-TEXT_COLOR-'] != 'None':
            window['-ML_TEXT-'].update(text_color=values['-TEXT_COLOR-'])

        elif event == '-SAVE_IMAGE-' and values['-ML_TEXT-'] != '':
            save_as_image(values['-SAVE_IMAGE-'], values['-ML_TEXT-'],
                          values['-BACKGROUND_COLOR-'], values['-TEXT_COLOR-'])
    window.close()


def main():
    ascii_art = PyCodeAsciiArt(img=Image.open('python_logo.png'))

    sg.theme('DarkGrey5')
    original_art_column = [[sg.Text('Original Art (Editable)', justification="center", expand_x=True)],
                           [sg.Multiline(default_text=ascii_art.create_preview(), key='-ML_ORIGINAL-', size=(90, 50),
                                         font=('Courier', 6), enable_events=True,
                                         expand_x=True, expand_y=True, horizontal_scroll=True)],
                           [sg.Input(key='-FILEBROWSE-', enable_events=True, visible=False),
                            sg.FileBrowse('Select Image', target='-FILEBROWSE-'),
                            sg.Push(),
                            sg.Text('Width:'), sg.Input(tooltip='Width image in chars', key='-WIDTH-', size=(3, 1),
                                                        default_text='70', enable_events=True),
                            sg.Push(),
                            sg.Checkbox('Invert', key='-INVERT-', enable_events=True),
                            sg.Push(),
                            sg.Checkbox('4 bit color', key='-4BIT-', enable_events=True)]
                           ]

    result_art_column = [[sg.Push(),
                          sg.Text('Result Art', justification="center", expand_x=True),
                          sg.Push()],
                         [sg.Multiline(key='-ML_RESULT-', size=(90, 50), font=('Courier', 6), expand_x=True,
                                       expand_y=True, horizontal_scroll=True)],
                         [sg.Checkbox('Add "exec"',
                                      tooltip='Adds exec and base64 decode\ncommands to run the script',
                                      key='-EXEC-', default=True, enable_events=True),
                          sg.Checkbox('Fill', key='-FILL-', tooltip='Fills in missing characters', enable_events=True),
                          sg.Push(),
                          sg.Button('Preview', tooltip='Full size Preview in new window', key='-WINDOW-'),
                          sg.Push(),
                          sg.Button('Copy to clipboard', key='-CLIPBOARD-', enable_events=True)]
                         ]

    source_text_pan = [[sg.Text('Python code or text', justification="center", expand_x=True)],
                       [sg.Multiline(key='-ML_TEXT-', size=(100, 18), font=('Courier', 12), enable_events=True,
                                     expand_x=True, expand_y=True, horizontal_scroll=True)
                        ]]

    layout = [source_text_pan,
              [sg.Column(original_art_column, expand_x=True, expand_y=True),
               sg.VSeparator(),
               sg.Column(result_art_column, expand_x=True, expand_y=True)
               ]]
    window = sg.Window("Python Code to ASCII Art", layout, font=('Arial', 14))

    while True:
        event, values = window.read()

        if event == 'Exit' or event == sg.WIN_CLOSED:
            break

        if event == '-FILEBROWSE-':
            filename = values['-FILEBROWSE-']
            if os.path.exists(filename):
                try:
                    ascii_art.img = Image.open(filename)
                    ascii_art.width = int(values['-WIDTH-'])
                    ascii_art.invert = values['-INVERT-']
                    window['-ML_ORIGINAL-'].update(ascii_art.create_preview())
                except ValueError:
                    sg.Popup('Unable to open image file', font=('Arial', 14))

        elif event in ('-INVERT-', '-WIDTH-', '-4BIT-'):
            if values['-WIDTH-'].isdigit():
                ascii_art.width = int(values['-WIDTH-'])
            ascii_art.invert = values['-INVERT-']
            ascii_art.color_4bit = values['-4BIT-']
            window['-ML_ORIGINAL-'].update(ascii_art.create_preview())

        elif event == '-ML_TEXT-':
            ascii_art.source_text = values['-ML_TEXT-']

        elif event == '-CLIPBOARD-':
            clipboard.copy(values['-ML_RESULT-'])

        elif event == '-ML_ORIGINAL-':
            ascii_art.ascii_image = values['-ML_ORIGINAL-']

        elif event == '-EXEC-':
            ascii_art.add_exec = values['-EXEC-']

        elif event == '-FILL-':
            ascii_art.need_fill = values['-FILL-']

        elif event == '-WINDOW-' and values['-ML_RESULT-'] != '':
            preview_window(values['-ML_RESULT-'])

        window['-ML_RESULT-'].update(ascii_art.create_art())

    window.close()


if __name__ == '__main__':
    main()
