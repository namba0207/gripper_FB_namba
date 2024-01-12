import PySimpleGUI as sg

layout = [[sg.Text('確信度', font=('Arial',32), pad=((450,0),(100,0)))],
          [sg.Text('0                                                  100'
                   , font=('Arial',20), pad=((270,0),(0,0)))],
        [sg.Slider((0,100),key='-Slider1-', pad=((270,0),(0,0))
                   , orientation='h', size=(50, 30),
         enable_events=True, disable_number_display=True)]
        ]

window = sg.Window('スライダー', layout,size=(1000, 400))

while True: # Event Loop

    event, values = window.read()
    print(values['-Slider1-'])
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()