"""
Questo modulo contiene tutte le funzioni relative all'interfaccia grafica dell'applicazione.
Include la creazione della finestra principale, gestione degli eventi e visualizzazione dei risultati.
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import pandas as pd
import random
import math
import config  # Importa il modulo di configurazione

def ask_order_of_generation(root, items, selected_cab_plc, status_var, excel_file_path):
    """
    Crea una finestra per selezionare l'ordine di generazione dei file.
    
    Args:
        root: Finestra principale
        items: Lista degli elementi da ordinare
        selected_cab_plc: CAB_PLC selezionato
        status_var: Variabile per lo stato dell'operazione
        excel_file_path: Percorso del file Excel selezionato
    """
    # Import process_excel here to avoid circular import
    from elaborazione_principale import process_excel
    
    order_window = tk.Toplevel(root)
    order_window.title("Ordine di Generazione")
    order_window.geometry("600x600")
    order_window.configure(bg="#2C3E50")
    order_window.transient(root)  # Rende la finestra modale rispetto alla principale
    order_window.grab_set()  # Impedisce l'interazione con la finestra principale
    
    # Applica lo stile moderno
    style = ttk.Style()
    style.configure("Order.TFrame", background="#2C3E50")
    style.configure("Order.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                   font=("Segoe UI", 12))
    style.configure("OrderTitle.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                   font=("Segoe UI", 16, "bold"))
    style.configure("Order.TButton", font=("Segoe UI", 10), padding=10)
    
    # Crea un canvas con scrollbar
    canvas = tk.Canvas(order_window, bg="#2C3E50", highlightthickness=0)
    scrollbar = ttk.Scrollbar(order_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, style="Order.TFrame")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=580)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Titolo
    title_frame = ttk.Frame(scrollable_frame, style="Order.TFrame")
    title_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
    
    title_label = ttk.Label(title_frame, text="Ordine di Generazione", 
                           style="OrderTitle.TLabel", anchor="center")
    title_label.pack(fill=tk.X)
    
    subtitle_label = ttk.Label(title_frame, text="Seleziona l'ordine di generazione dei file", 
                             style="Order.TLabel", anchor="center")
    subtitle_label.pack(fill=tk.X, pady=(5, 0))

    # Crea i frame per il layout
    frame = ttk.Frame(scrollable_frame, style="Order.TFrame")
    frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    # Frame per gli elementi disponibili
    available_frame = ttk.Frame(frame, style="Order.TFrame")
    available_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    available_label = ttk.Label(available_frame, text="Linee Disponibili:", 
                              style="Order.TLabel")
    available_label.pack(pady=5)

    available_listbox = tk.Listbox(available_frame, selectmode=tk.SINGLE, 
                                 height=15, font=("Segoe UI", 12), width=15,
                                 bg="#34495E", fg="#ECF0F1", selectbackground="#3498DB",
                                 selectforeground="#ECF0F1", relief=tk.FLAT)
    unique_items = list(dict.fromkeys(item[:4] for item in items))
    for item in unique_items:
        available_listbox.insert(tk.END, item)
    available_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

    # Frame per i pulsanti di spostamento
    move_button_frame = ttk.Frame(frame, style="Order.TFrame")
    move_button_frame.pack(side=tk.LEFT, padx=10)

    move_to_order_button = ttk.Button(move_button_frame, text=">>", 
                                    command=lambda: move_item(available_listbox, ordered_listbox),
                                    style="Order.TButton", width=5)
    move_to_order_button.pack(pady=5)

    move_to_available_button = ttk.Button(move_button_frame, text="<<", 
                                        command=lambda: move_item(ordered_listbox, available_listbox),
                                        style="Order.TButton", width=5)
    move_to_available_button.pack(pady=5)
    
    def on_confirm():
        selected_order = ordered_listbox.get(0, tk.END)
        if selected_order:
            process_excel(selected_cab_plc, status_var, root, selected_order, excel_file_path)
            order_window.destroy()
        else:
            messagebox.showwarning("Avviso", "Seleziona almeno un elemento per procedere.")

    confirm_button = ttk.Button(move_button_frame, text="Conferma", 
                              command=on_confirm, style="Order.TButton", width=10)
    confirm_button.pack(pady=20)

    # Frame per gli elementi ordinati
    ordered_frame = ttk.Frame(frame, style="Order.TFrame")
    ordered_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

    ordered_label = ttk.Label(ordered_frame, text="Linee Ordinate:", 
                            style="Order.TLabel")
    ordered_label.pack(pady=5)

    ordered_listbox = tk.Listbox(ordered_frame, selectmode=tk.SINGLE, 
                               height=15, font=("Segoe UI", 12), width=15,
                               bg="#34495E", fg="#ECF0F1", selectbackground="#3498DB",
                               selectforeground="#ECF0F1", relief=tk.FLAT)
    ordered_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

    def move_item(source_listbox, target_listbox):
        selected_index = source_listbox.curselection()
        if selected_index:
            selected_item = source_listbox.get(selected_index)
            if target_listbox == ordered_listbox:
                target_listbox.insert(tk.END, f"{target_listbox.size() + 1}. {selected_item}")
            else:
                target_listbox.insert(tk.END, f"{selected_item[3:]}")
            source_listbox.delete(selected_index)

    available_listbox.bind("<Double-Button-1>", 
                         lambda e: move_item(available_listbox, ordered_listbox))
    ordered_listbox.bind("<Double-Button-1>", 
                        lambda e: move_item(ordered_listbox, available_listbox))
    
    # Aggiungi istruzioni
    instructions_frame = ttk.Frame(scrollable_frame, style="Order.TFrame")
    instructions_frame.pack(fill=tk.X, pady=(10, 20), padx=20)
    
    instructions_label = ttk.Label(instructions_frame, 
                                 text="Doppio click su un elemento per spostarlo o usa i pulsanti >> e <<",
                                 style="Order.TLabel", anchor="center")
    instructions_label.pack(fill=tk.X)
    
    # Aggiungi il canvas e la scrollbar alla finestra
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Configura il binding per la rotella del mouse
    def _on_mousewheel(event):
        try:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except tk.TclError:
            pass  # Ignora l'errore se il canvas non esiste più
    
    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    canvas.bind("<Enter>", _bind_mousewheel)
    canvas.bind("<Leave>", _unbind_mousewheel)
    
    # Imposta il focus sulla finestra
    order_window.focus_set()
    
    # Centra la finestra rispetto alla finestra principale
    order_window.update_idletasks()
    width = order_window.winfo_width()
    height = order_window.winfo_height()
    x = (order_window.winfo_screenwidth() // 2) - (width // 2)
    y = (order_window.winfo_screenheight() // 2) - (height // 2)
    order_window.geometry(f'{width}x{height}+{x}+{y}')

def create_gui():
    """
    Crea l'interfaccia grafica principale dell'applicazione.
    """
    root = tk.Tk()
    root.title("Configuratore Nastri Trasportatori")
    root.geometry("700x600")
    root.configure(bg="#2C3E50")
    root.minsize(600, 500)  # Imposta una dimensione minima

    try:
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configura lo stile moderno
        style.configure("TFrame", background="#2C3E50")
        style.configure("TLabel", background="#2C3E50", foreground="#ECF0F1", 
                       font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                       font=("Segoe UI", 24, "bold"))
        style.configure("Subtitle.TLabel", background="#2C3E50", foreground="#BDC3C7", 
                       font=("Segoe UI", 14))
        style.configure("Status.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                       font=("Segoe UI", 10))
        
        style.configure("TButton", font=("Segoe UI", 10), padding=10)
        style.configure("Action.TButton", font=("Segoe UI", 12, "bold"), padding=15)
        
        style.configure("Custom.TCombobox",
                       padding=15,
                       relief="flat",
                       background="#3498DB",
                       fieldbackground="#3498DB",
                       foreground="#ECF0F1",
                       arrowcolor="#ECF0F1",
                       font=("Segoe UI", 12))
        
        style.map("Custom.TCombobox",
                 fieldbackground=[("readonly", "#3498DB"), ("active", "#2980B9")],
                 selectbackground=[("readonly", "#2980B9")],
                 selectforeground=[("readonly", "#ECF0F1")],
                 background=[("active", "#2980B9"), ("pressed", "#2980B9")])
        
    except Exception as e:
        print(f"Errore nel setting dello stile: {e}")
    
    # Frame principale
    main_frame = ttk.Frame(root, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Titolo
    title_label = ttk.Label(main_frame, text="Configuratore Nastri Trasportatori", 
                           style="Title.TLabel", anchor="center")
    title_label.pack(pady=(0, 20), fill=tk.X)
    
    # Sottotitolo
    subtitle_label = ttk.Label(main_frame,
                             text="Seleziona il file Excel e il controller PLC per generare le configurazioni",
                             style="Subtitle.TLabel",
                             wraplength=500,
                             anchor="center")
    subtitle_label.pack(pady=(0, 30), fill=tk.X)
    
    # Frame per la selezione del file Excel
    excel_frame = ttk.Frame(main_frame)
    excel_frame.pack(fill=tk.X, pady=10)
    
    excel_label = ttk.Label(excel_frame, text="File Excel:", 
                           font=("Segoe UI", 12), background="#2C3E50", foreground="#ECF0F1")
    excel_label.pack(side=tk.LEFT, padx=(0, 10))
    
    excel_path_var = tk.StringVar()
    
    # Carica le opzioni CAB_PLC
    cab_plc_options = ["Seleziona un file Excel..."]
    
    def load_cab_plc_options(file_path):
        nonlocal cab_plc_options
        try:
            # Verifica se il file è stato effettivamente selezionato
            if file_path == "Nessun file selezionato":
                cab_plc_options = ["Seleziona un file Excel..."]
                cab_plc_var.set(cab_plc_options[0])
                cab_plc_dropdown['values'] = cab_plc_options
                return
                
            if os.path.exists(file_path):
                if 'pd' in globals():
                    df = pd.read_excel(file_path)
                    if 'CAB_PLC' in df.columns:
                        cab_plc_options = sorted(df['CAB_PLC'].unique(), 
                                              key=lambda x: x[-3:])
                        cab_plc_var.set(cab_plc_options[0] if cab_plc_options else "")
                    else:
                        messagebox.showwarning("Avviso", 
                                             "La colonna CAB_PLC non è presente nel file Excel.")
                        cab_plc_options = ["Errore: colonna mancante"]
                else:
                    messagebox.showwarning("Avviso", 
                                         "Pandas non è stato caricato correttamente.")
                    cab_plc_options = ["Errore di caricamento"]
            else:
                messagebox.showwarning("Avviso", f"Il file {file_path} non esiste.")
                cab_plc_options = ["File non trovato"]
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento del file Excel: {e}")
            cab_plc_options = ["Errore di caricamento"]
        
        # Aggiorna il dropdown
        cab_plc_dropdown['values'] = cab_plc_options
    
    # Carica l'ultimo percorso del file Excel se disponibile
    last_excel_path = config.get_last_excel_path()
    if last_excel_path:
        excel_path_var.set(last_excel_path)
    else:
        excel_path_var.set("Nessun file selezionato")  # Messaggio iniziale
    
    excel_path_label = ttk.Label(excel_frame, textvariable=excel_path_var,
                                font=("Segoe UI", 10), background="#2C3E50", foreground="#ECF0F1",
                                width=30, anchor="w")
    excel_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def select_excel_file():
        file_path = filedialog.askopenfilename(
            title="Seleziona il file Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            excel_path_var.set(file_path)
            # Salva il percorso del file Excel
            config.save_last_excel_path(file_path)
            # Ricarica le opzioni CAB_PLC
            load_cab_plc_options(file_path)
    
    excel_button = ttk.Button(excel_frame, text="Sfoglia...", command=select_excel_file, style="TButton")
    excel_button.pack(side=tk.RIGHT, padx=(10, 0))
    
    # Frame di selezione CAB_PLC
    selection_frame = tk.Frame(main_frame, bg="#3498DB")
    selection_frame.pack(fill=tk.X, pady=20, padx=20)
    
    shadow_frame = tk.Frame(selection_frame, bg="#2980B9")
    shadow_frame.place(relx=0, rely=0, relwidth=1, height=2)
    
    # Label per CAB_PLC
    cab_plc_label = ttk.Label(selection_frame, text="CAB_PLC:", 
                             font=("Segoe UI", 12), background="#3498DB", foreground="#ECF0F1")
    cab_plc_label.pack(side=tk.LEFT, padx=(10, 10))
    
    # Dropdown CAB_PLC
    cab_plc_var = tk.StringVar()
    if cab_plc_options and len(cab_plc_options) > 0:
        cab_plc_var.set(cab_plc_options[0])
    
    cab_plc_dropdown = ttk.Combobox(selection_frame, 
                                   textvariable=cab_plc_var,
                                   values=cab_plc_options,
                                   width=30,
                                   state="readonly",
                                   style="Custom.TCombobox",
                                   justify="center",
                                   font=("Segoe UI", 12))
    cab_plc_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    cab_plc_dropdown.option_add('*TCombobox*Listbox.font', ('Segoe UI', 12))
    cab_plc_dropdown.option_add('*TCombobox*Listbox.justify', 'center')
    
    # Ricarica le opzioni CAB_PLC con il percorso salvato se disponibile
    if last_excel_path:
        load_cab_plc_options(last_excel_path)
    
    def on_enter(e):
        selection_frame.config(bg="#2980B9")
        shadow_frame.config(bg="#2471A3")
    
    def on_leave(e):
        selection_frame.config(bg="#3498DB")
        shadow_frame.config(bg="#2980B9")
    
    selection_frame.bind("<Enter>", on_enter)
    selection_frame.bind("<Leave>", on_leave)
    
    # Frame per i pulsanti
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=20)
    
    def on_process():
        selected_cab_plc = cab_plc_var.get()
        excel_file_path = excel_path_var.get()
        
        if selected_cab_plc == "Seleziona un file Excel..." or selected_cab_plc == "Errore: colonna mancante" or selected_cab_plc == "Errore di caricamento" or selected_cab_plc == "File non trovato":
            messagebox.showwarning("Avviso", "Seleziona un CAB_PLC valido prima di procedere.")
            return
        
        if excel_file_path == "Nessun file selezionato":
            messagebox.showwarning("Avviso", "Seleziona un file Excel prima di procedere.")
            return
        
        try:
            # Carica il file Excel
            df = pd.read_excel(excel_file_path)
            
            # Verifica le colonne richieste
            required_columns = ['ITEM_ID_CUSTOM', 'CAB_PLC', 'ITEM_TRUNK', 'ITEM_SPEED_TRANSPORT', 
                              'ITEM_SPEED_LAUNCH', 'ITEM_SPEED_MAX', 'ITEM_ACCELERATION', 'ITEM_L']
            if not all(col in df.columns for col in required_columns):
                messagebox.showerror("Errore", "Alcune colonne richieste sono mancanti nel file Excel.")
                return
            
            # Filtra le righe escludendo ITEM_ID_CUSTOM contenenti "OG", "SD", "RS", "CX", "CN", "CH", "XR", "SO", "LC", "IN"
            df = df[~df['ITEM_ID_CUSTOM'].str.contains('OG|SD|RS|CX|CN|CH|XR|SO|LC|IN', case=False, na=False)]
            
            # Filtra il DataFrame per il CAB_PLC selezionato
            cab_plc_data = df[df['CAB_PLC'] == selected_cab_plc]
            
            # Verifica se ci sono dati per il CAB_PLC selezionato
            if cab_plc_data.empty:
                messagebox.showerror("Errore", f"Nessun dato trovato per il CAB_PLC {selected_cab_plc} nel file Excel.")
                return
            
            # Estrai i prefissi unici da ITEM_ID_CUSTOM
            unique_items = sorted(set(item[:4].lower() for item in cab_plc_data['ITEM_ID_CUSTOM']))
            
            # Se c'è solo una linea, salta la selezione dell'ordine e procedi direttamente
            if len(unique_items) == 1:
                # Import process_excel here to avoid circular import
                from elaborazione_principale import process_excel
                
                # Crea un ordine con l'unica linea disponibile
                single_order = [f"1. {unique_items[0]}"]
                
                # Procedi direttamente con l'elaborazione
                status_var.set("Elaborazione in corso...")
                process_excel(selected_cab_plc, status_var, root, single_order, excel_file_path)
            else:
                # Mostra la finestra per selezionare l'ordine di generazione
                ask_order_of_generation(root, cab_plc_data['ITEM_ID_CUSTOM'].tolist(), 
                                      selected_cab_plc, status_var, excel_file_path)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'elaborazione del file Excel: {e}")
    
    process_button = ttk.Button(button_frame, text="Genera Configurazioni", 
                              command=on_process, style="Action.TButton")
    process_button.pack(pady=10)
    
    # Frame per lo stato
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=(20, 0))
    
    status_var = tk.StringVar()
    status_var.set("Pronto")
    
    status_label = ttk.Label(status_frame, textvariable=status_var, 
                            style="Status.TLabel", anchor="w")
    status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    copyright_label = ttk.Label(status_frame, 
                              text="© Baggage Handling System",
                              relief=tk.SUNKEN,
                              padding=(10, 5))
    copyright_label.pack(side=tk.RIGHT)
    
    # Imposta il valore iniziale del dropdown CAB_PLC
    cab_plc_var.set("Seleziona un file Excel...")
    
    return root 

def show_feedback_window(root, selected_cab_plc, selected_order, excel_file_path):
    """
    Mostra una finestra di feedback con i dettagli della selezione.
    
    Args:
        root: Finestra principale
        selected_cab_plc: CAB_PLC selezionato
        selected_order: Ordine di generazione selezionato
        excel_file_path: Percorso del file Excel selezionato
    """
    feedback_window = tk.Toplevel(root)
    feedback_window.title("Dettagli Selezione")
    feedback_window.geometry("800x600")
    feedback_window.configure(bg="#2C3E50")
    feedback_window.transient(root)
    feedback_window.grab_set()
    
    # Applica lo stile moderno
    style = ttk.Style()
    style.configure("Feedback.TFrame", background="#2C3E50")
    style.configure("Feedback.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                   font=("Segoe UI", 12))
    style.configure("FeedbackTitle.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                   font=("Segoe UI", 16, "bold"))
    
    # Frame principale
    main_frame = ttk.Frame(feedback_window, style="Feedback.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Titolo
    title_label = ttk.Label(main_frame, text="Dettagli della Selezione", 
                           style="FeedbackTitle.TLabel", anchor="center")
    title_label.pack(fill=tk.X, pady=(0, 20))
    
    # Informazioni CAB_PLC
    cab_plc_label = ttk.Label(main_frame, text=f"CAB_PLC selezionato: {selected_cab_plc}", 
                             style="Feedback.TLabel")
    cab_plc_label.pack(anchor="w", pady=(0, 10))
    
    # Label per l'ordine di generazione
    order_label = ttk.Label(main_frame, text="Ordine di generazione:", 
                           style="Feedback.TLabel")
    order_label.pack(anchor="w", pady=(0, 10))
    
    # Frame per le colonne
    columns_frame = ttk.Frame(main_frame, style="Feedback.TFrame")
    columns_frame.pack(fill=tk.BOTH, expand=True)
    
    # Calcola il numero di elementi per colonna
    total_items = len(selected_order)
    items_per_column = (total_items + 2) // 3  # Arrotonda per eccesso
    
    # Crea tre colonne
    for col in range(3):
        column_frame = ttk.Frame(columns_frame, style="Feedback.TFrame")
        column_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Calcola gli indici di inizio e fine per questa colonna
        start_idx = col * items_per_column
        end_idx = min((col + 1) * items_per_column, total_items)
        
        # Aggiungi gli elementi alla colonna
        for i in range(start_idx, end_idx):
            item_label = ttk.Label(column_frame, text=selected_order[i], 
                                 style="Feedback.TLabel", anchor="w")
            item_label.pack(fill=tk.X, pady=2)
    
    # Pulsante di chiusura
    close_button = ttk.Button(main_frame, text="Chiudi", 
                             command=feedback_window.destroy)
    close_button.pack(padx=20, pady=20)
    
    # Imposta il focus sulla finestra
    feedback_window.focus_set()
    
    # Centra la finestra rispetto alla finestra principale
    feedback_window.update_idletasks()
    width = feedback_window.winfo_width()
    height = feedback_window.winfo_height()
    x = (feedback_window.winfo_screenwidth() // 2) - (width // 2)
    y = (feedback_window.winfo_screenheight() // 2) - (height // 2)
    feedback_window.geometry(f'{width}x{height}+{x}+{y}') 

def show_completion_message(root, selected_cab_plc):
    """
    Mostra una finestra con il messaggio di completamento e i dettagli dei file creati.
    
    Args:
        root: Finestra principale
        selected_cab_plc: CAB_PLC selezionato
    """
    try:
        # Ottieni la lista delle sottocartelle e dei loro file
        all_subfolders = os.listdir(os.path.join('Configurazioni', selected_cab_plc))
        subfolder_files = {
            subfolder: os.listdir(os.path.join('Configurazioni', selected_cab_plc, subfolder))
            for subfolder in all_subfolders
            if os.path.isdir(os.path.join('Configurazioni', selected_cab_plc, subfolder))
        }
        
        # Calcola la dimensione della finestra in base al contenuto
        max_files = max(len(files) for files in subfolder_files.values())
        window_height = 200 + max_files * 20
        window_width = 600  # Adjusted for four columns
        
        completion_window = tk.Toplevel(root)
        completion_window.title("Operazione Completata")
        completion_window.geometry(f"{window_width}x{window_height}")
        completion_window.configure(bg="#2C3E50")
        completion_window.transient(root)
        completion_window.grab_set()
        
        # Crea un unico canvas che copre l'intera finestra
        canvas = tk.Canvas(completion_window, width=window_width, height=window_height, 
                          bg='#2C3E50', highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Applica lo stile moderno
        style = ttk.Style()
        style.configure("Completion.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                       font=("Segoe UI", 12))
        style.configure("CompletionTitle.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                       font=("Segoe UI", 16, "bold"))
        style.configure("CompletionSubtitle.TLabel", background="#2C3E50", foreground="#ECF0F1", 
                       font=("Segoe UI", 14))
        
        # Titolo
        canvas.create_text(window_width / 2, 40, text="Elaborazione completata con successo!", 
                           fill="#ECF0F1", font=("Segoe UI", 16, "bold"))
        
        # Sottotitolo
        canvas.create_text(window_width / 2, 80, text=f"File generati per {selected_cab_plc}:", 
                           fill="#ECF0F1", font=("Segoe UI", 14))
        
        # Calcola il numero di sottocartelle per colonna
        total_subfolders = len(subfolder_files)
        subfolders_per_column = (total_subfolders + 3) // 4  # Adjusted for four columns
        
        # Crea quattro colonne centrate
        column_positions = [window_width / 7, 2 * window_width / 5, 3 * window_width / 5, 4 * window_width / 5]
        
        # Tieni traccia dell'altezza massima raggiunta per posizionare il pulsante di chiusura
        max_y_position = 120
        
        for col in range(4):
            start_idx = col * subfolders_per_column
            end_idx = min((col + 1) * subfolders_per_column, total_subfolders)
            subfolders_list = list(subfolder_files.keys())[start_idx:end_idx]
            y_position = 120
            
            for subfolder in subfolders_list:
                canvas.create_text(column_positions[col], y_position, text=subfolder, 
                                   fill="#ECF0F1", font=("Segoe UI", 12, "bold"), anchor="w")
                y_position += 20  # Adjusted spacing
                
                # Aggiungi i file della sottocartella
                for file in sorted(subfolder_files[subfolder]):
                    canvas.create_text(column_positions[col], y_position, text=f"• {file}", 
                                       fill="#ECF0F1", font=("Segoe UI", 12), anchor="w")
                    y_position += 20  # Adjusted spacing
                
                # Aggiorna l'altezza massima
                max_y_position = max(max_y_position, y_position)
            
            # Aggiungi spazio extra tra le colonne
            max_y_position = max(max_y_position, y_position + 20)
        
        # Aggiungi spazio extra per il pulsante di chiusura
        max_y_position += 40
        
        # Pulsante di chiusura
        close_button = ttk.Button(completion_window, text="Chiudi", 
                                 command=completion_window.destroy)
        close_button.place(x=window_width / 2 - 50, y=max_y_position)
        
        # Lista per memorizzare i coriandoli
        confetti_pieces = []
        
        # Colori dei coriandoli
        colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F1C40F", "#9B59B6", "#1ABC9C"]
        
        # Crea i coriandoli
        for _ in range(100):
            x = random.randint(0, window_width)
            y = random.randint(-600, 0)
            color = random.choice(colors)
            size = random.randint(5, 15)
            shape = random.choice(["circle", "rectangle", "triangle"])
            
            try:
                if shape == "circle":
                    piece = canvas.create_oval(x, y, x+size, y+size, fill=color, outline="")
                elif shape == "rectangle":
                    piece = canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline="")
                else:  # triangle
                    points = [x, y+size, x+size, y, x+size, y+size]
                    piece = canvas.create_polygon(points, fill=color, outline="")
                
                # Aggiungi velocità casuale
                dx = random.uniform(-2, 2)
                dy = random.uniform(1, 3)
                rotation = random.uniform(-5, 5)
                
                confetti_pieces.append({
                    "id": piece,
                    "dx": dx,
                    "dy": dy,
                    "rotation": rotation,
                    "shape": shape,
                    "size": size
                })
            except tk.TclError:
                continue
        
        # Funzione per animare i coriandoli
        def animate_confetti():
            if not completion_window.winfo_exists():
                return
                
            for piece in confetti_pieces[:]:
                try:
                    # Ottieni le coordinate attuali
                    coords = canvas.coords(piece["id"])
                    if not coords:  # Se l'oggetto non esiste più
                        confetti_pieces.remove(piece)
                        continue
                    
                    # Aggiorna le coordinate
                    new_coords = []
                    for i in range(0, len(coords), 2):
                        new_coords.append(coords[i] + piece["dx"])
                        new_coords.append(coords[i+1] + piece["dy"])
                    
                    # Applica la rotazione se è un triangolo
                    if piece["shape"] == "triangle":
                        # Calcola il centro
                        center_x = sum(new_coords[::2]) / 3
                        center_y = sum(new_coords[1::2]) / 3
                        
                        # Ruota i punti
                        rotated_coords = []
                        for i in range(0, len(new_coords), 2):
                            x = new_coords[i] - center_x
                            y = new_coords[i+1] - center_y
                            
                            # Applica la rotazione
                            angle = math.radians(piece["rotation"])
                            rotated_x = x * math.cos(angle) - y * math.sin(angle)
                            rotated_y = x * math.sin(angle) + y * math.cos(angle)
                            
                            rotated_coords.append(rotated_x + center_x)
                            rotated_coords.append(rotated_y + center_y)
                        
                        canvas.coords(piece["id"], *rotated_coords)
                    else:
                        canvas.coords(piece["id"], *new_coords)
                    
                    # Aggiungi gravità
                    piece["dy"] += 0.1
                    
                    # Rimuovi i coriandoli che escono dallo schermo
                    if coords[1] > window_height:
                        canvas.delete(piece["id"])
                        confetti_pieces.remove(piece)
                except tk.TclError:
                    # Se c'è un errore con il canvas (es. finestra chiusa), rimuovi il pezzo
                    if piece in confetti_pieces:
                        confetti_pieces.remove(piece)
            
            # Continua l'animazione se ci sono ancora coriandoli e la finestra esiste
            if confetti_pieces and completion_window.winfo_exists():
                completion_window.after(20, animate_confetti)
        
        # Imposta il focus sulla finestra
        completion_window.focus_set()
        
        # Centra la finestra rispetto alla finestra principale
        completion_window.update_idletasks()
        width = completion_window.winfo_width()
        height = completion_window.winfo_height()
        x = (completion_window.winfo_screenwidth() // 2) - (width // 2)
        y = (completion_window.winfo_screenheight() // 2) - (height // 2)
        completion_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Avvia l'animazione
        completion_window.after(100, animate_confetti)
        
    except Exception as e:
        print(f"Errore nella creazione della finestra di completamento: {e}")
        # Mostra un messaggio di errore semplice se la finestra animata fallisce
        messagebox.showinfo("Operazione Completata", 
                          f"Elaborazione completata con successo per {selected_cab_plc}!") 