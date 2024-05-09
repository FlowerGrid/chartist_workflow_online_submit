import os
import pyperclip
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tkinter import *
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

def create_submit_window(final_file, lyric_file):
    # Initialize webdriver so it stays open until tkinter window closed
    driver = webdriver.Chrome()


    win_width = 500
    win_height = 150

    submit_window = Tk()
    submit_window.geometry(f"{win_width}x{win_height}")
    submit_window.title("Submit to Back Office")
    submit_window.grid_columnconfigure(0, weight=1)


    screen_width = submit_window.winfo_screenwidth()
    screen_height = submit_window.winfo_screenheight()
    x = (screen_width/2) - (win_width/2)
    y = (screen_height/4) - (win_height/4)
    submit_window.geometry('%dx%d+%d+%d' % (win_width, win_height, x, y))

    # Frame
    main_frame = Frame(submit_window, padx=5, pady=5)
    main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    main_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform='columns')

    # Song link
    link_label = Label(main_frame, text='Song Link', padx=5, pady=5)
    link_label.grid(row=0, column=0, sticky='e')
    link_entry = Entry(main_frame, width=30, borderwidth=2)
    link_entry.grid(row=0, column=1, columnspan=2, sticky='w')

    lang_list = ['en', 'sp', 'fr', 'de']
    lang_label = Label(main_frame, text='Lyrics Language', padx=5, pady=5)
    lang_label.grid(row=1, column=0, sticky='e')

    lang_combo_box = ttk.Combobox(main_frame, values=lang_list, width=4, state='readonly')
    lang_combo_box.current(0)
    lang_combo_box.grid(row=1, column=1, sticky='w')

    lyric_checkbox_bool = IntVar()
    lyric_checkbox = Checkbutton(main_frame, text="Copy Lyrics", variable=lyric_checkbox_bool)
    lyric_checkbox.grid(row=1, column =2, sticky='w')

    submit_button = Button(main_frame, text='Submit', command=lambda: online_submit(
        driver, final_file, lyric_file, link_entry.get(), lang_combo_box.get(), lyric_checkbox_bool.get(), submit_window
        ))
    
    submit_button.grid(row=2, column=1)

    submit_window.mainloop()


def online_submit(driver, final_file, lyric_file, song_link, lang, lyric_checkbox_bool, submit_window):
    # Initialize Selenium WebDriver (assuming Chrome)
    #driver = webdriver.Chrome()

    # Load the submission page
    driver.get(song_link)

    # Wait for user to login
    try:
        wait = WebDriverWait(driver, 60)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "chartbuilder-input")))

        # Read and parse the text file to extract sections
        with open(final_file, "r") as file:
            sections = file.read().split("\n\n")

        # Fill out each input field with the corresponding section
        for i, section in enumerate(sections[2:]):
            lines = section.split('\n')
            section_id = re.search(r'#(\d+)', lines[0]).group(1)

            section = '\n'.join(line for line in lines[1:])
            input_field = driver.find_element("id", f"coda_{section_id}")
            pyperclip.copy(section)
            input_field.send_keys(pyperclip.paste())


        if lyric_checkbox_bool == 1:
            lyrics(lyric_file, driver, lang)

    except TimeoutException:
        print('Timeout')
        driver.quit()


    # Submit the form
    driver.find_element("id", "btnSave").click()

    # Close the browser
    #driver.quit()

    #submit_window.destroy()


def lyrics(lyric_file, driver, lang):
    # Read and parse lyric file
    with open(lyric_file, 'r') as l_file:
        l_sections = l_file.read().split('\n\n')

    for lyric in l_sections:
        lines = lyric.split('\n')
        lyric_id = re.search(r'#(\d+)', lines[0]).group(1)

        lyric = '\n'.join(line for line in lines[1:])
        l_input_field = driver.find_element('id', f'{lang}_chordPro_{lyric_id}') 
        pyperclip.copy(lyric)
        l_input_field.send_keys(pyperclip.paste())


if __name__ == '__main__':
    project_path = filedialog.askdirectory(
    title='Select project location',
    message="Please choose the project's parent folder"
    )
    title = os.path.basename(project_path)
    final_file = os.path.join(project_path, 'Final', f'converted_{title}.txt')
    lyric_file = os.path.join(project_path, 'Final', f'{title} LYRICS.txt')

    create_submit_window(final_file, lyric_file)
