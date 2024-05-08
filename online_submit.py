import os
import pyperclip
import re
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from tkinter import *
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

def create_submit_window(final_file, lyric_file):
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

    '''
    # Username & Password input
    username_label = Label(main_frame, text='Username:', padx=5, pady=5)
    username_label.grid(row=1, column=0)
    username_entry = Entry(main_frame, width=45, borderwidth=2)
    username_entry.grid(row=1, column=1, columnspan=2)

    password_label = Label(main_frame, text='Password:', padx=5, pady=5)
    password_label.grid(row=2, column=0)
    password_entry = Entry(main_frame, width=45, borderwidth=2, show='💩')
    password_entry.grid(row=2, column=1, columnspan=2)
    '''

    lang_list = ['en', 'sp', 'fr', 'de']
    lang_label = Label(main_frame, text='Lyrics Language', padx=5, pady=5)
    lang_label.grid(row=1, column=0, sticky='e')

    lang_combo_box = ttk.Combobox(main_frame, values=lang_list, state='readonly')
    lang_combo_box.grid(row=1, column=1)

    submit_button = Button(main_frame, text='Submit', command=lambda: online_submit(
        final_file, lyric_file, link_entry, lang_combo_box, submit_window
        ))
    submit_button.grid(row=2, column=1)

    submit_window.mainloop()


def online_submit(final_file, lyric_file, link_entry, lang_combo_box, submit_window):
    # Pull user input from gui
    song_link = link_entry.get()
    #username = username_entry.get()
    #password = password_entry.get()
    lang = lang_combo_box.get()

    # Initialize Selenium WebDriver (assuming Chrome)
    driver = webdriver.Chrome()

    # Load the submission page
    driver.get(song_link)

    '''
    # Deal with login credentials
    # Need help from Senyo with this
    username_field = driver.find_element('id', "username")
    username_field.send_keys(username)

    password_field = driver.find_element('id', 'password')
    password_field.send_keys(password)
    '''

    # Wait for user to login
    revealed = driver.find_element('class_name', 'chartbuilder-input')

    wait = WebDriverWait(driver, timeout=15)
    wait.until(lambda d : revealed.is_displayed())

    # Read and parse the text file to extract sections
    with open(final_file, "r") as file:
        sections = file.read().split("\n\n")

    # Fill out each input field with the corresponding section
    for i, section in enumerate(sections[1:]):
        lines = section.split('\n')
        section_id = re.search(r'#(\d+)', lines[0]).group(1)

        section = ''.join(line for line in lines[2:])
        input_field = driver.find_element("id", f"coda_{section_id}")
        pyperclip.copy(section)
        input_field.send_keys(pyperclip.paste())

    # Read and parse lyric file
    with open(lyric_file, 'r') as l_file:
        l_sections = l_file.read().split('\n\n')

    for lyric in l_sections:
        lines = lyric.split('\n')
        lyric_id = re.search(r'#(\d+)', lines[0]).group(1)

        lyric = ''.join(line for line in lines[1:])
        l_input_field = driver.find_element('id', f'{lang}_chordPro_{lyric_id}') 
        pyperclip.copy(lyric)
        l_input_field.send_keys(pyperclip.paste())


    # Submit the form
    #submit_button = driver.find_element("id", "btnSubmit") # Not sure if that's right. We'll probably use <command> + 's'
    #submit_button.click()

    # Close the browser
    driver.quit()

    submit_window.destroy()


if __name__ == '__main__':
    project_path = filedialog.askdirectory(
    title='Select project location',
    message="Please choose the project's parent folder"
    )
    title = os.path.basename(project_path)
    final_file = os.path.join(project_path, 'Final', f'converted_{title}.txt')
    lyric_file = os.path.join(project_path, 'Final', f'{title} LYRICS.txt')
    print(final_file)
    print(lyric_file)
    create_submit_window(final_file, lyric_file)
