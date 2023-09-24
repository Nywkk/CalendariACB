import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from bs4 import BeautifulSoup
import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
import months, estadistica_partido

def generate_calendar():
    # Get the team selected by the user from the dropdown list
    team_name = team_combo.get()
    # Show initial progress message
    progress_label.config(text="Generating calendar...")

    # Sample HTML content with multiple matches
    url = "https://www.acb.com/calendario/"
    result = requests.get(url)
    # Parse the HTML content
    soup = BeautifulSoup(result.text, 'html.parser')
    # Obtener todos los partidos, incluidos los jugados y no jugados
    match_sections = soup.find_all('article', class_='partido')

    # Filtrar los partidos jugados
    match_sections_played = [match for match in match_sections if 'previa' not in match['class']]

    # Filtrar los partidos no jugados
    match_sections_not_played = [match for match in match_sections if 'previa' in match['class']]

    num_played_matches = len(match_sections_played)
    num_not_played_matches = len(match_sections_not_played)
    resultado_local_find = None
    date_played = None
    # Initialize an iCalendar object
    cal = Calendar()

    unique_teams = set()
    # Iterate through each match section
    # Iterate through both sets of match sections (played and not played)
    for match_sections in [match_sections_played, match_sections_not_played]:
        # Determine whether the matches are played or not played based on the list being processed
        is_played = match_sections is match_sections_played

        # Iterate through each match section
        for match in match_sections:
            # Find the parent "cabecera_jornada" div element
            header_div = match.find_previous('div', class_='cabecera_jornada')

            # Find the date within the "cabecera_jornada" div
            month_element = header_div.find('div', class_='float-right fechas mayusculas')

            # Extract and print the date
            if month_element:
                month_text = month_element.text.strip()

            # Find local team name
            local_name_element = match.find('div', class_='equipo local roboto_condensed_bold ellipsis texto-derecha')
            local_name = local_name_element.find('span', class_='nombre_largo').text if local_name_element else "N/A"
            if local_name == "N/A":
                local_name_element = match.find('div', class_='equipo local roboto_condensed_bold ellipsis texto-derecha ganador')
                local_name = local_name_element.find('span', class_='nombre_largo').text if local_name_element else "N/A"
            print(local_name)
            # Find visiting team name
            visiting_name_element = match.find('div', class_='equipo visitante roboto_condensed_bold ellipsis texto-izquierda')
            visiting_name = visiting_name_element.find('span', class_='nombre_largo').text if visiting_name_element else "N/A"
            if visiting_name == "N/A":
                visiting_name_element = match.find('div', class_='equipo visitante roboto_condensed_bold ellipsis texto-izquierda perdedor')
                visiting_name = visiting_name_element.find('span', class_='nombre_largo').text if visiting_name_element else "N/A"
            print(visiting_name)

            # Check if the user selected "Todos los equipos" or if the team name matches
            if team_name == "All teams" or team_name in local_name or team_name in visiting_name:
                
                if is_played:
                    print("Entra a partido jugado")

                    # Find the game id if the game has already been played
                    resultado_local_find = match.find('div', class_='resultado local ganador')
                    resultado_visitante_find = match.find('div', class_='resultado visitante perdedor')
                    print(resultado_local_find)
                    if resultado_local_find is None:
                        resultado_local_find = match.find('div', class_='resultado local perdedor')  
                        resultado_visitante_find = match.find('div', class_='resultado visitante ganador')

                    # Find the element <a> within the selected div
                    a_element_local = resultado_local_find.find('a') if resultado_local_find else None
                    a_element_visitante = resultado_visitante_find.find('a') if resultado_visitante_find else None
                    if a_element_local:
                        href = a_element_local.get('href')
                    else:
                        href = "N/A"  # Handle the case where the <a> element is not found
                    print("Href: "+href)
                    # Call the function extract_time to get the time the game was played
                    date_played = estadistica_partido.extract_time(href)

                    # Convert date_played to a datetime object
                    date_played = datetime.strptime(date_played, "%Y-%m-%dT%H:%M:%S")

                    if a_element_local:
                        res_local = a_element_local.text
                    else:
                        res_local = "N/A"  # Handle the case where the <a> element is not found
                    
                    if a_element_visitante:
                        res_visitante = a_element_visitante.text
                    else:
                        res_visitante = "N/A"  # Handle the case where the <a> element is not found

                else:
                    # Find date
                    date_element = match.find('span', class_='fecha')
                    date = date_element.text if date_element else "N/A"
                    # Extract the day from the date (assuming the format is consistent)
                    day = date.split()[1]

                    # Extract and print the "Month" value from wherever you have it
                    # Replace with the actual month value
                    month_replaced = month_text.replace('-', ' ')

                    # List of allowed months
                    allowed_months = ["Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May"]

                    # Split the 'month_replaced' variable into parts using spaces as separators
                    parts = month_replaced.split()

                    # Initialize a flag to control the loop
                    found = False

                    # Variables to store the current month and year
                    month = None
                    year = None

                    # Iterate through the parts of 'month'
                    for part in parts:
                        # Check if the current part is a number and if it matches 'day'
                        if part.isdigit() and part == day:
                            found = True  # Day found
                        elif found:
                            if part in allowed_months:
                                month = part
                            if len(part) == 4:
                                year = part
                            if year is not None and month is not None:
                                break

                    # Find time
                    time_element = match.find('span', class_='hora')
                    time = time_element.text if time_element else "N/A"

                    # Combine day and month to create a timedelta date string
                    timedelta_date = f"{day} {months.convertMonthNameToNumber(month)} {year} {time}" if time else f"{day} {months.convertMonthNameToNumber(month)} {year} 00:00"

                    # Check if the time is not empty before trying to create a datetime object
                    timedelta_date = datetime.strptime(timedelta_date, "%d %m %Y %H:%M")

                #Create an iCalendar event
                if is_played:
                    print(f"{local_name} {res_local} - {res_visitante} {visiting_name}")
                    event = Event()
                    event.name = f"{local_name} {res_local} - {res_visitante} {visiting_name}"
                    event.begin = date_played
                    event.end = date_played + timedelta(hours=2)
                    print("Acaba l'if de is_played")
                else:
                    event = Event()
                    event.name = f"{local_name} vs {visiting_name}"
                    event.begin = timedelta_date + timedelta(hours=-2)
                    event.end = timedelta_date
                
                cal.events.add(event)
                
    # Show completion message
    progress_label.config(text="Calendar generated successfully!")

    # Get the file location where the calendar will be saved
    file_path = filedialog.asksaveasfilename(defaultextension=".ics", filetypes=[("iCalendar files", "*.ics")])

    if file_path:
        # Save the iCalendar object to the selected file
        with open(file_path, 'wb') as f:
            # Serialize the Calendar object to a string
            ics_content = cal.serialize()

            # Add DTSTAMP property to each event
            ics_content = ics_content.replace("BEGIN:VEVENT", "DTSTAMP:" + datetime.now().strftime('%Y%m%dT%H%M%S') + "\r\nBEGIN:VEVENT")

            # Write the modified content to the file
            f.write(ics_content.encode('utf-8').replace(b'\n', b'\r\n'))

        # Show confirmation message
        messagebox.showinfo("Calendar Generated", f"The calendar has been generated successfully and saved to '{file_path}'.")

# Create the main application window
root = tk.Tk()
root.title("ACB Calendar Generator")
# Set the window size
root.geometry("400x300")

# Create a label
label = tk.Label(root, text="Selecciona un equipo:")
label.pack()

# Create a dropdown list with teams
teams = ['All teams', 'UCAM Murcia', 'Joventut Badalona', 'Barça', 'Bàsquet Girona', 'Valencia Basket', 'Casademont Zaragoza', 'BAXI Manresa', 'Coviran Granada', 'Unicaja', 'Monbus Obradoiro', 'Zunder Palencia', 'Baskonia', 'Lenovo Tenerife', 'Dreamland Gran Canaria', 'MoraBanc Andorra', 'Real Madrid', 'Río Breogán', 'Surne Bilbao Basket']
# Sort teams alphabetically without affecting the first option
sorted_teams = sorted(teams[1:])  # Exclude the first optionca
sorted_teams.insert(0, teams[0])  # Add the first option at the beginning
team_combo = ttk.Combobox(root, values=sorted_teams)
team_combo.pack()

# Add a blank space to separate the dropdown from the message
space_label = tk.Label(root, text="")
space_label.pack()

# Etiqueta para mostrar el progreso
aviso_label = tk.Label(root, text="Ésta operación puede tardar un tiempo.\nHay diferentes factores que pueden afectar al tiempo de creación \ndel calendario como la velocidad de conexión a internet, \nla carga de los servidores de www.acb.com, etc")
aviso_label.pack()

# Agregar un espacio en blanco para separar el desplegable del botón
space_label = tk.Label(root, text="")
space_label.pack()

# Label to display progress
progress_label = tk.Label(root, text="")
progress_label.pack()

# Create a button to generate the calendar
generate_button = tk.Button(root, text="Generate Calendar", command=generate_calendar)
generate_button.pack()

# Start the main application loop
root.mainloop()
