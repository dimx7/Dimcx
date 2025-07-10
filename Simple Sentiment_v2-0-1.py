### Εισαγωγή Βιβλιοθηκών ###

import os # για το path του τρέχοντος αρχείου
import re # για να αφαιρέσουμε τα σημεία στίξης ,
import json # για να διαβάσουμε το αρχείο json
import unicodedata # για να αφαιρέσουμε τον τόνο
from datetime import datetime # για να πάρουμε την ημερομηνία
from collections import Counter # για να μετρήσουμε τις λέξεις
from difflib import SequenceMatcher # για να συγκρίνουμε τις λέξεις
import tkinter as tk # για το GUI
from tkinter import ttk, PhotoImage, messagebox, filedialog, scrolledtext # για το GUI , 
from ttkthemes import ThemedTk # για το GUI, 
import pandas as pd # για την επεξεργασία των δεδομένων
import matplotlib # για το διάγραμμα 
matplotlib.use("TkAgg") # για το διάγραμμα
from matplotlib.figure import Figure # για το διάγραμμα
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # για το διάγραμμα

# __version__ 2.0.1

# ...imports...

### === ΕΝΣΩΜΑΤΩΣΗ analyze_com ΚΑΙ ΚΛΑΣΕΩΝ === ###
DEBUG_MODE = True  # Άλλαξέ το σε True όταν θέλεις να δεις μηνύματα αποσφαλμάτωσης

def custom_print(message): # Εμφάνιση μηνυμάτων αποσφαλμάτωσης
    if DEBUG_MODE: # Αν είναι απενεργοποιημένη η αποσφαλμάτωση
        print(message) # Εμφάνιση του μηνύματος
# Ορισμοί paths
# Ορισμοί paths για τα αρχεία λέξεων
current_directory = os.path.dirname(os.path.abspath(__file__)) # Ορισμός του τρέχοντος directory
xrisimes_lekseis = os.path.join(current_directory, 'xrisimes_lekseis') # Ορισμός του directory για τα αρχεία λέξεων
if not os.path.exists(xrisimes_lekseis): # Αν δεν υπάρχει το directory
    os.makedirs(xrisimes_lekseis) # Δημιουργία του directory

thetikes_file = os.path.join(xrisimes_lekseis, "thetikes_lekseis.txt") # Ορισμός του αρχείου για τα θετικά αρχεία λέξεων
arnitikes_file = os.path.join(xrisimes_lekseis, "arnitikes_lekseis.txt") # Ορισμός του αρχείου για τα αρνητικά αρχεία λέξεων
stopwords_file = os.path.join(xrisimes_lekseis, "stopwords_lekseis.txt") # Ορισμός του αρχείου για τα stopwords
exact_phrases_file = os.path.join(xrisimes_lekseis, "exact_phrases.json") # Ορισμός του αρχείου για τα ακριβή αρχεία λέξεων

# Συνάρτηση για φόρτωση λέξεων από αρχεία
# Συνάρτηση για φόρτωση λέξεων από αρχεία
def load_words_from_file(file_path, default_words): # Φόρτωση λέξεων από αρχεία
    """Φορτώνει λέξεις από αρχείο, δημιουργεί το αρχείο αν δεν υπάρχει"""
    try:
        if os.path.exists(file_path): # αν υπάρχει το αρχείο 
            with open(file_path, 'r', encoding='utf-8') as file: # αν υπάρχει το αρχείο, ανάγνωση του αρχείου
                words = [line.strip() for line in file if line.strip()] # ανάγνωση των λέξεων από το αρχείο
                return words if words else default_words
        else:
            # Δημιουργία αρχείου με προεπιλεγμένες λέξεις 
            with open(file_path, 'w', encoding='utf-8') as file: # αν δεν υπάρχει το αρχείο, δημιουργία του αρχείου
                for word in default_words: # για κάθε λέξη στην προεπιλεγμένη λίστα
                    file.write(word + '\n') # γράφουμε την λέξη στο αρχείο
            return default_words # επιστροφή της προεπιλεγμένης λίστας
    except Exception as e: # αν υπάρχει σφάλμα, εμφάνιση του μηνύματος σφάλματος
        custom_print(f"Σφάλμα κατά τη φόρτωση του αρχείου {file_path}: {str(e)}") # εμφάνιση του μηνύματος σφάλματος
        return default_words

def load_words_to_text(text_widget, word_list, stats_label=None, selected_line_var=None): # συνάρτηση για την φόρτωση λέξεων σε text area
    text_widget.config(state=tk.NORMAL) # ενεργοποίηση του text widget
    text_widget.delete(1.0, tk.END) # καθαρισμός του πεδίου
    for word in word_list:
        text_widget.insert(tk.END, word + '\n') # εισαγωγή των λέξεων στο text widget
        
        # Καθαρισμός επιλογής
    if selected_line_var: # αν υπάρχει επιλογή 
        selected_line_var[0] = None # απενεργοποίηση της επιλογής , οι λίστες λέξεων
    text_widget.tag_remove("selected", "1.0", tk.END) # καθαρισμός της επιλογής
        
        # Καθαρισμός του φιλτραρίσματος
    text_widget.is_filtered = False # απενεργοποίηση του φιλτραρίσματος
    text_widget.original_word_list = word_list # αποθήκευση της πλήρους λίστας
        
    text_widget.config(state=tk.DISABLED) # απενεργοποίηση του text widget
    if stats_label:
        stats_label.config(text=f"Σύνολο λέξεων: {len(word_list)}") # ενημέρωση του στατιστικού με το πλήθος των λέξεων

   # Προσθέστε αυτή τη συνάρτηση στο μενού ή σε ένα κουμπί , οι λίστες λέξεων
def reload_all_lists(): 
       global thetikes_lekseis, arnitikes_lekseis, stopwords_lekseis, exact_phrases # Ορισμός των global μεταβλητών , οι λίστες λέξεων
       thetikes_lekseis = load_words_from_file(thetikes_file, default_thetikes) # Φόρτωση των θετικών λέξεων , οι λίστες λέξεων
       arnitikes_lekseis = load_words_from_file(arnitikes_file, default_arnitikes) # Φόρτωση των αρνητικών λέξεων , οι λίστες λέξεων
       stopwords_lekseis = load_words_from_file(stopwords_file, default_stopwords) # Φόρτωση των stopwords , οι λίστες λέξεων
       exact_phrases = load_exact_phrases() # Φόρτωση των ακριβών φράσεων , οι λίστες λέξεων
       messagebox.showinfo("Επαναφόρτωση", "Όλες οι λίστες λέξεων επαναφορτώθηκαν επιτυχώς!") # Εμφάνιση μηνύματος επιτυχίας

################### 


############ ΝΕΑ ΣΥΝΑΡΤΗΣΗ ΑΒΑΙΒΕΟΤΗΤΑΣ ΓΙΑ ΤΟΝ ΧΡΗΣΤΗ ############

def fix_word_files(): # Διόρθωση θετικών και αρνητικών λέξεων
       # Διόρθωση θετικών λέξεων
       try:
           with open(thetikes_file, 'r', encoding='utf-8') as file: # Αν υπάρχει το αρχείο
               content = file.read() # Ανάγνωση του αρχείου
               words = content.split() # Διαχωρισμός των λέξεων
           
           with open(thetikes_file, 'w', encoding='utf-8') as file: # Αν υπάρχει το αρχείο, γράφουμε τις λέξεις στο αρχείο
               for word in words:
                   file.write(word + '\n') # Γράφουμε την λέξη στο αρχείο
           
           # Διόρθωση αρνητικών λέξεων
           with open(arnitikes_file, 'r', encoding='utf-8') as file:
               content = file.read()
               words = content.split()
           
           with open(arnitikes_file, 'w', encoding='utf-8') as file: # Αν υπάρχει το αρχείο, γράφουμε τις λέξεις στο αρχείο, 
               for word in words:
                   file.write(word + '\n')
           
           # Επαναφόρτωση των λιστών
           global thetikes_lekseis, arnitikes_lekseis # Ορισμός των global μεταβλητών, 
           thetikes_lekseis = load_words_from_file(thetikes_file, default_thetikes) # Φόρτωση των θετικών λέξεων
           arnitikes_lekseis = load_words_from_file(arnitikes_file, default_arnitikes) # Φόρτωση των αρνητικών λέξεων
           
           messagebox.showinfo("Επιτυχία", "Τα αρχεία λέξεων διορθώθηκαν και επαναφορτώθηκαν.") # Εμφάνιση μηνύματος επιτυχίας
       except Exception as e:
           messagebox.showerror("Σφάλμα", f"Προέκυψε σφάλμα κατά τη διόρθωση των αρχείων: {str(e)}")


# Προεπιλεγμένες λέξεις
default_thetikes = [
    "καλός", "υπέροχος", "τέλειος", "όμορφος", "καταπληκτικός", "καλύτερος", "ευτυχισμένος",
    "χαρούμενος", "ικανοποιημένος", "ευχάριστος", "φοβερη", "απίστευτος", "καταπληκτικό", "φοβερός", "καταπληκτικά"
]

default_arnitikes = [
    "κακός", "χάλια", "άσχημος", "τραγικός", "απογοητευτικός", "χειρότερος", "λυπημένος",
    "θλιμμένος", "απογοητευμένος", "απαίσιος", "απογοητευτική"
]

default_stopwords = [
    "και", "το", "να", "σε", "με", "για", "από", "στο", "στη", "της", "του", "την", "τις", "τους"
]

# Προεπιλεγμένες ακριβείς φράσεις
default_exact_phrases = {
    "τέλειο": {"sentiment": "Θετικό", "score": 100},
    "καλούτσικο": {"sentiment": "Θετικό", "score": 60},
    "εξαιρετικό": {"sentiment": "Θετικό", "score": 90},
    "υπέροχο": {"sentiment": "Θετικό", "score": 95},
    "άψογο": {"sentiment": "Θετικό", "score": 100},
    "απαίσιο": {"sentiment": "Αρνητικό", "score": 100},
    "μέτριο": {"sentiment": "Αρνητικό", "score": 60},
    "χάλια": {"sentiment": "Αρνητικό", "score": 90},
    "πολύ κακό": {"sentiment": "Αρνητικό", "score": 80},
    "ουδέτερο": {"sentiment": "Ουδέτερο", "score": 100},
    "Θαυμάσιο": {"sentiment": "Θετικό", "score": 100},
    "θαυμάσιο": {"sentiment": "Θετικό", "score": 100},
    "Απιστευτο": {"sentiment": "Θετικό", "score": 100},
}

############ ΝΕΑ ΣΥΝΑΡΤΗΣΗ ΑΒΑΙΒΕΟΤΗΤΑΣ ΓΙΑ ΤΟΝ ΧΡΗΣΤΗ ############
###################################################################

# Προσθήκη στην αρχή του αρχείου, μετά τις άλλες λίστες λέξεων 
uncertainty_words = [
    'ίσως', 'ισως', 'μάλλον', 'μαλλον', 'πιθανώς', 'πιθανως', 
    'πιθανόν', 'πιθανον', 'ενδεχομένως', 'ενδεχομενως', 'κάπως', 'καπως',
    'λίγο', 'λιγο', 'κάπως', 'καπως', 'σχεδόν', 'σχεδον', 'περίπου', 'περιπου',
    'μπορεί', 'μπορει', 'φαίνεται', 'φαινεται', 'νομίζω', 'νομιζω',
    'πιστεύω', 'πιστευω', 'υποθέτω', 'υποθετω', 'φαντάζομαι', 'φανταζομαι'
    # ΝΕΕΣ ΠΡΟΣΘΗΚΕΣ: Λέξεις υποθετικότητας και αβεβαιότητας
    'θα', 'μπορούσε', 'μπορουσε', 'θα μπορούσε', 'θα μπορουσε',
    'ίσως να', 'ισως να', 'μάλλον να', 'μαλλον να',
    'πιθανώς να', 'πιθανως να', 'ενδεχομένως να', 'ενδεχομενως να',
    
    # Λέξεις που δηλώνουν υποθετικότητα
    'αν', 'εάν', 'εαν', 'όταν', 'οταν', 'εφόσον', 'εφοσον',
    'υπό προϋποθέσεις', 'υπο προυποθεσεις', 'με επιφύλαξη', 'με επιφυλαξη',
    
    # Λέξεις που μειώνουν τη βεβαιότητα
    'κάπως', 'καπως', 'λίγο', 'λιγο', 'αρκετά', 'αρκετα',
    'σχετικά', 'σχετικα', 'μάλλον', 'μαλλον', 'κάπως έτσι', 'καπως ετσι',
    
    # Φράσεις υποθετικότητας
    'θα ήταν', 'θα ηταν', 'θα είχε', 'θα ειχε', 'θα μπορούσε να',
    'θα μπορουσε να', 'ίσως να είναι', 'ισως να ειναι', 'μπορεί να είναι',
    'μπορει να ειναι', 'φαίνεται να', 'φαινεται να',
    
    # Λέξεις που εκφράζουν αμφιβολία
    'δεν είμαι σίγουρος', 'δεν ειμαι σιγουρος', 'δεν ξέρω', 'δεν ξερω',
    'δεν είμαι βέβαιος', 'δεν ειμαι βεβαιος', 'αμφιβάλλω', 'αμφιβαλλω',
    
    # Λέξεις που δηλώνουν προσωρινότητα ή μερικότητα
    'προσωρινά', 'προσωρινα', 'μερικώς', 'μερικως', 'εν μέρει', 'εν μερει',
    'κατά κάποιο τρόπο', 'κατα καποιο τροπο', 'με κάποιο τρόπο', 'με καποιο τροπο'
]

############## ΤΕΛΟΣ ΠΡΟΣΘΗΚΗΣ ΝΕΩΝ ΛΕΞΕΩΝ ΑΒΕΒΑΙΟΤΗΤΑΣ ####################

############ WELCOME SCREEN ############
########################################

def show_simple_welcome(callback_function): # Εμφάνιση welcome screen
    welcome_window = tk.Toplevel() # Δημιουργία νέου παράθυρου
    welcome_window.title("Καλώς ήρθατε") # Τίτλος παράθυρου
    welcome_window.configure(bg=colour1) # Χρώμα φόντου παράθυρου
    welcome_window.resizable(False, False) # Απαγορεύει την αλλαγή μεγέθους του παράθυρου

    # Προσθήκη εικονιδίου στο παράθυρο (αν υπάρχει)
    try:
        welcome_window.iconphoto(False, icon) 
        # edit_window.iconbitmap(default=app_icon1_path) # προσθήκη εικονιδίου στο παράθυρο
    except:
        pass  # Αγνοούμε αν δεν υπάρχει το εικονίδιο

    window_width = 440 # Πλάτος παράθυρου
    window_height = 340 # Ύψος παράθυρου
    screen_width = welcome_window.winfo_screenwidth() # Πλάτος οθόνης
    screen_height = welcome_window.winfo_screenheight() # Ύψος οθόνης
    x = (screen_width - window_width) // 2 # Κεντρική θέση παράθυρου
    y = (screen_height - window_height) // 2 # Κεντρική θέση παράθυρου
    welcome_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    label = tk.Label(
        welcome_window, 
        text="👋 Καλώς ήρθατε στην εφαρμογή\nΑνάλυσης Συναισθήματος!", # Κείμενο παράθυρου
        font=('Century Gothic', 17, 'bold'), # Γραμματοσειρά και μέγεθος κειμένου
        fg=colour3, # Χρώμα κειμένου
        bg=colour1, # Χρώμα φόντου παράθυρου
        justify='center' # Κεντρική τοποθέτηση κειμένου
    )
    label.pack(pady=(30, 10))

    info = (
        "🔍 Εδώ μπορείτε να:\n"
        "✨ Αναλύστε σχόλια για προϊόντα και υπηρεσίες (θετικό, αρνητικό, ουδέτερο)\n" # Περιγραφή των λειτουργιών της εφαρμογής
        "📊 Δείτε γραφικές αναπαραστάσεις\n" # Περιγραφή των λειτουργιών της εφαρμογής
        "📝 Διαχειριστείτε λίστες λέξεων\n" # Περιγραφή των λειτουργιών της εφαρμογής
        "💾 Αποθηκεύστε και εξάγετε δεδομένα\n\n" # Περιγραφή των λειτουργιών της εφαρμογής
        "💡 Ξεκινήστε πατώντας το κουμπί 'Έναρξη'!" # Περιγραφή των λειτουργιών της εφαρμογής
    )
    info_label = tk.Label(
        welcome_window,
        text=info,
        font=('Century Gothic', 11),
        fg=colour4,
        bg=colour1,
        justify='left',
        wraplength=400
    )
    info_label.pack(pady=(0, 20))

    start_btn = tk.Button(
        welcome_window,
        text="🚀 Έναρξη",
        font=('Century Gothic', 12, 'bold'), # Γραμματοσειρά και μέγεθος κειμένου
        bg='#FDCB60', # Χρώμα φόντου κουμπιού
        fg='#053A61', # Χρώμα κειμένου
        width=15, # Πλάτος κουμπιού
        command=lambda: [welcome_window.destroy(), callback_function()] # Κλήση της callback_function
    ) 
    start_btn.pack(pady=10) # Εμφάνιση του κουμπιού Έναρξη

    welcome_window.lift() # Εμφάνιση του παράθυρου
    welcome_window.focus_force() # Εστίαση του παράθυρου

############ ΤΕΛΟΣ WELCOME SCREEN ############

############## ΑΝΑΛΥΣΗ ΦΡΑΣΕΩΝ ΑΒΕΒΑΙΟΤΗΤΑΣ ##############

def check_uncertainty_in_comment(comment): # Έλεγχος αν το σχόλιο περιέχει λέξεις ή φράσεις αβεβαιότητας με βελτιωμένη ακρίβεια
    """Ελέγχει αν το σχόλιο περιέχει λέξεις ή φράσεις αβεβαιότητας με βελτιωμένη ακρίβεια"""
    comment_lower = comment.lower() # μετατροπή του σχολίου σε μικρά γράμματα
    cleaned_comment = clean_text_comment(comment_lower) # καθαρισμός του σχολίου
    
    found_uncertainty = []
    comment_no_accent = afairesi_tou_tonou(cleaned_comment) # αφαίρεση των τονισμών από το σχόλιο
    
    # Ταξινόμηση των λέξεων αβεβαιότητας - πρώτα οι μεγάλες φράσεις
    uncertainty_sorted = sorted(uncertainty_words, key=len, reverse=True) # ταξινόμηση των λέξεων αβεβαιότητας - πρώτα οι μεγάλες φράσεις
    
    for uncertainty_item in uncertainty_sorted:
        uncertainty_no_accent = afairesi_tou_tonou(uncertainty_item.lower()) # αφαίρεση των τονισμών από την λέξη ή φράση αβεβαιότητας                              
        
        # Ελέγχουμε αν η φράση/λέξη υπάρχει ως ολοκληρωμένη μονάδα
        if ' ' in uncertainty_item:  # Φράση
            # Για φράσεις ελέγχουμε πλήρη αντιστοίχιση
            if uncertainty_no_accent in comment_no_accent:
                # Επιπλέον έλεγχος: βεβαιώνουμε ότι δεν είναι μέρος μεγαλύτερης λέξης
                words_before_after = comment_no_accent.replace(uncertainty_no_accent, '|').split('|') # διαχωρισμός των λέξεων του σχολίου
                if len(words_before_after) >= 2:  # Βρέθηκε η φράση
                    found_uncertainty.append(uncertainty_item)
        else:  # Μονή λέξη
            # Για μονές λέξεις ελέγχουμε ότι είναι ξεχωριστή λέξη
            comment_words = comment_no_accent.split() # διαχωρισμός των λέξεων του σχολίου
            if uncertainty_no_accent in comment_words: # αν η λέξη αβεβαιότητας είναι στο σχόλιο
                found_uncertainty.append(uncertainty_item) # προσθήκη της λέξης αβεβαιότητας στη λίστα
    
    return found_uncertainty

def analyze_comment_with_uncertainty(comment_input): # Ανάλυση σχολίου με βελτιωμένη λογική αβεβαιότητας , βελτιωμένη λογική αβεβαιότητας
    """Αναλύει σχόλιο με βελτιωμένη λογική αβεβαιότητας""" 
    
    # 1. Έλεγχος για ακριβείς φράσεις πρώτα
    exact_sentiment, exact_score = check_exact_phrase(comment_input) # Έλεγχος για ακριβείς φράσεις , βελτιωμένη λογική αβεβαιότητας
    if exact_sentiment and exact_score:
        return exact_sentiment, exact_score, "exact_phrase" # επιστροφή της ακριβούς φράσης , βελτιωμένη λογική αβεβαιότητας
    
    # 2. Έλεγχος για αβεβαιότητα με βελτιωμένο αλγόριθμο
    uncertainty_words_found = check_uncertainty_in_comment(comment_input) # Έλεγχος για αβεβαιότητα με βελτιωμένο αλγόριθμο , 
    
    if uncertainty_words_found:
        # Υπολογισμός "βάρους" αβεβαιότητας
        uncertainty_weight = len(uncertainty_words_found) # υπολογισμός του βάρους της αβεβαιότητας , 
        for item in uncertainty_words_found:
            if len(item.split()) > 1:  # Φράσεις έχουν μεγαλύτερο βάρος
                uncertainty_weight += 1
        
        # Αν υπάρχει ισχυρή αβεβαιότητα, προτείνουμε διαχείριση
        if uncertainty_weight >= 2 or any(len(item.split()) > 2 for item in uncertainty_words_found): # αν υπάρχει ισχυρή αβεβαιότητα, προτείνουμε διαχείριση
            uncertainty_text = ", ".join(uncertainty_words_found) # συνένωση των λέξεων αβεβαιότητας
            
            result = messagebox.askyesnocancel(
                "Εντοπίστηκε Ισχυρή Αβεβαιότητα",  # Τίτλος του παραθύρου
                f"Το σχόλιο '{comment_input}' περιέχει σημαντικές λέξεις αβεβαιότητας:\n" # μήνυμα που εμφανίζεται στο παράθυρο
                f"'{uncertainty_text}'\n\n" # εμφάνιση των λέξεων αβεβαιότητας
                f"Αυτές επηρεάζουν σημαντικά το νόημα της φράσης.\n\n" # μήνυμα που εμφανίζεται στο παράθυρο
                f"• Πατήστε 'Ναι' για να προσθέσετε ως ακριβή φράση\n"
                f"• Πατήστε 'Όχι' για κανονική ανάλυση με μειωμένη βεβαιότητα\n"
                f"• Πατήστε 'Άκυρο' για ακύρωση"
            )
            
            if result is True:  # Προσθήκη ως ακριβής φράση
                return show_uncertainty_phrase_dialog(comment_input) # προσθήκη ως ακριβής φράση 
            elif result is False:  # Κανονική ανάλυση με μείωση
                return analyze_with_reduced_certainty(comment_input, uncertainty_weight) # κανονική ανάλυση με μείωση
            else:  # Άκυρο
                return None, None, "cancelled" # ακύρωση
    
    # 3. Κανονική ανάλυση αν δεν υπάρχει σημαντική αβεβαιότητα
    return perform_normal_analysis(comment_input) # κανονική ανάλυση

# Επίσης, βελτίωση της λίστας αβεβαιότητας
uncertainty_words = [
    # Φράσεις υψηλής αβεβαιότητας (ελέγχονται πρώτα) 
    'θα μπορούσε να ήταν', 'θα μπορουσε να ηταν', 
    'θα μπορούσε να είναι', 'θα μπορουσε να ειναι', 
    'θα μπορούσε να', 'θα μπορουσε να',
    'μπορεί να είναι', 'μπορει να ειναι',
    'ίσως να είναι', 'ισως να ειναι',
    'μάλλον να είναι', 'μαλλον να ειναι',
    'δεν είμαι σίγουρος', 'δεν ειμαι σιγουρος',
    'δεν ξέρω αν', 'δεν ξερω αν',
    'δεν είμαι βέβαιος', 'δεν ειμαι βεβαιος',
    
    # Φράσεις μέτριας αβεβαιότητας  
    'θα ήταν', 'θα ηταν', 'θα είχε', 'θα ειχε',
    'ίσως να', 'ισως να', 'μάλλον να', 'μαλλον να',
    'φαίνεται να', 'φαινεται να', 'φαντάζομαι ότι', 'φανταζομαι οτι',
    
    # Μονές λέξεις χαμηλής αβεβαιότητας
    'ίσως', 'ισως', 'μάλλον', 'μαλλον', 'πιθανώς', 'πιθανως',
    'πιθανόν', 'πιθανον', 'ενδεχομένως', 'ενδεχομενως',
    'μπορεί', 'μπορει', 'φαίνεται', 'φαινεται', 
    'νομίζω', 'νομιζω', 'πιστεύω', 'πιστευω', 'υποθέτω', 'υποθετω'
]

def show_uncertainty_phrase_dialog(phrase_text): # Εμφάνιση διαλόγου για προσθήκη φράσης με αβεβαιότητα, 
    """Εμφανίζει διάλογο για προσθήκη φράσης με αβεβαιότητα"""
    dialog = tk.Toplevel(root) # Δημιουργία νέου παραθύρου
    dialog.title("Προσθήκη Φράσης με Αβεβαιότητα") # Τίτλος του παραθύρου
    dialog.geometry("500x380")
    dialog.config(bg=colour1) # Χρώμα του παραθύρου
    dialog.transient(root) # Επιτρέπει την επικοινωνία μεταξύ των παραθύρων
    dialog.grab_set() # Καταστρέφει την επιλογή του χρήστη σε άλλα παράθυρα
    
    # Κεντράρισμα διαλόγου
    dialog.update_idletasks() # Ενημέρωση του παραθύρου
    x = (dialog.winfo_screenwidth() // 2) - (250) # Υπολογισμός της θέσης του παραθύρου
    y = (dialog.winfo_screenheight() // 2) - (190) # Υπολογισμός της θέσης του παραθύρου
    dialog.geometry(f"500x380+{x}+{y}") # Οργάνωση του παραθύρου
    
    result = {"action": "cancel"} # Αρχικοποίηση του αποτελέσματος
    
    # Τίτλος 
    title_label = tk.Label(dialog, text="Προσθήκη Φράσης με Αβεβαιότητα", 
                          bg=colour1, fg=colour4, font=('Century Gothic', 12, 'bold')) # Τίτλος του παραθύρου
    title_label.pack(pady=10) # Προσθήκη του τίτλου στο παράθυρο
    
    # Φράση
    phrase_frame = tk.Frame(dialog, bg=colour1) # Κεντράρισμα του παραθύρου
    phrase_frame.pack(pady=5, padx=20, fill="x") # Προσθήκη του παραθύρου στο παράθυρο
    
    tk.Label(phrase_frame, text="Φράση:", bg=colour1, fg=colour4, font=('Century Gothic', 10)).pack(anchor="w") # Προσθήκη του κειμένου στο παράθυρο
    phrase_entry = tk.Entry(phrase_frame, width=50, font=('Century Gothic', 10)) # Προσθήκη του πεδίου εισαγωγής στο παράθυρο
    phrase_entry.pack(fill="x", pady=2) # Προσθήκη του πεδίου εισαγωγής στο παράθυρο
    phrase_entry.insert(0, phrase_text) # Προσθήκη της φράσης στο πεδίο εισαγωγής
    
    # Συναίσθημα
    sentiment_frame = tk.Frame(dialog, bg=colour1) # Κεντράρισμα του παραθύρου
    sentiment_frame.pack(pady=5, padx=20, fill="x") # Προσθήκη του παραθύρου στο παράθυρο
    
    tk.Label(sentiment_frame, text="Συναίσθημα:", bg=colour1, fg=colour4, font=('Century Gothic', 10)).pack(anchor="w") # Προσθήκη του κειμένου στο παράθυρο
    sentiment_var = tk.StringVar(value="Ουδέτερο")  # Default για αβεβαιότητα
    sentiment_combo = ttk.Combobox(sentiment_frame, textvariable=sentiment_var, 
                                 values=["Θετικό", "Αρνητικό", "Ουδέτερο"], state="readonly",
                                 font=('Century Gothic', 10)) # Προσθήκη του πεδίου επιλογής στο παράθυρο   
    sentiment_combo.pack(fill="x", pady=2) # Προσθήκη του πεδίου επιλογής στο παράθυρο
    
    # Βαθμολογία με προτεινόμενη τιμή
    score_frame = tk.Frame(dialog, bg=colour1) # Κεντράρισμα του παραθύρου
    score_frame.pack(pady=5, padx=20, fill="x") # Προσθήκη του παραθύρου στο παράθυρο
    
    tk.Label(score_frame, text="Βαθμολογία (0-100):", bg=colour1, fg=colour4, font=('Century Gothic', 10)).pack(anchor="w") # Προσθήκη του κειμένου στο παράθυρο
    score_var = tk.StringVar(value="50")  # Μειωμένη βεβαιότητα
    score_entry = tk.Entry(score_frame, textvariable=score_var, width=10, font=('Century Gothic', 10))
    score_entry.pack(anchor="w", pady=2)
    
    # Επεξήγηση
    explanation_label = tk.Label( # Προσθήκη του κειμένου στο παράθυρο
        dialog,
        text="💡 Συμβουλή: Για φράσεις με αβεβαιότητα προτείνεται\nχαμηλότερη βαθμολογία (30-60) ή 'Ουδέτερο'", # Προσθήκη του κειμένου στο παράθυρο, 
        bg=colour1,
        fg="#666666",
        font=('Century Gothic', 9),
        justify=tk.CENTER
    )
    explanation_label.pack(pady=10)
    
    # Κουμπιά
    button_frame = tk.Frame(dialog, bg=colour1) # Κεντράρισμα του παραθύρου
    button_frame.pack(pady=20) # Προσθήκη του παραθύρου στο παράθυρο
    
    def add_and_analyze(): # Προσθήκη και ανάλυση της φράσης
        try:
            phrase = phrase_entry.get().strip() # Προσθήκη της φράσης στο πεδίο εισαγωγής
            sentiment = sentiment_var.get() # Προσθήκη του συναίσθηματος στο πεδίο επιλογής
            score = int(score_var.get()) # Προσθήκη της βαθμολογίας στο πεδίο εισαγωγής
            
            if not phrase:
                messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε μια φράση.") # μήνυμα σφάλματος
                return
            
            if not (0 <= score <= 100):
                messagebox.showerror("Σφάλμα", "Η βαθμολογία πρέπει να είναι μεταξύ 0 και 100.") # μήνυμα σφάλματος
                return
            
            # Προσθήκη στο λεξικό
            exact_phrases[phrase] = {"sentiment": sentiment, "score": score} # Προσθήκη της φράσης στο λεξικό
            
            # Αποθήκευση στο αρχείο
            with open(exact_phrases_file, 'w', encoding='utf-8') as file: # Αποθήκευση των ακριβών φράσεων στο αρχείο
                json.dump(exact_phrases, file, ensure_ascii=False, indent=4) # Αποθήκευση των ακριβών φράσεων στο αρχείο
            
            result["action"] = "added"
            result["phrase"] = phrase
            result["sentiment"] = sentiment
            result["score"] = score
            
            messagebox.showinfo("Επιτυχία", f"Η φράση '{phrase}' προστέθηκε επιτυχώς!")
            dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Σφάλμα", "Η βαθμολογία πρέπει να είναι αριθμός.")
     
    def continue_with_reduced(): # Συνέχεια με μειωμένη βεβαιότητα
        result["action"] = "reduced" # Αποθήκευση της ενέργειας στο αποτέλεσμα
        dialog.destroy() # Κλείσιμο του παραθύρου
    
    def cancel_analysis(): # Ακύρωση της ανάλυσης
        result["action"] = "cancel" # Αποθήκευση της ενέργειας στο αποτέλεσμα
        dialog.destroy() # Κλείσιμο του παραθύρου
    
    # ΔΙΟΡΘΩΣΗ: Προσθήκη του κουμπιού "Προσθήκη"
    add_btn = tk.Button( # Προσθήκη του κουμπιού "Προσθήκη"
        button_frame, 
        text="Προσθήκη", 
        bg=colour2, 
        fg=colour4, 
        font=('Century Gothic', 9, 'bold'),
        command=add_and_analyze, 
        width=12,
        height=1
    )
    add_btn.pack(side=tk.LEFT, padx=5)
    
    continue_btn = tk.Button(
        button_frame, 
        text="Συνέχεια με\nΜειωμένη Βεβαιότητα", 
        bg=colour3, 
        fg="white", 
        font=('Century Gothic', 9),
        command=continue_with_reduced, 
        width=18,
        height=2
    )
    continue_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(
        button_frame, 
        text="Άκυρο", 
        bg="#FF6B6B", 
        fg="white", 
        font=('Century Gothic', 9, 'bold'),
        command=cancel_analysis, 
        width=10,
        height=1
    )
    cancel_btn.pack(side=tk.LEFT, padx=5) # Προσθήκη του κουμπιού "Άκυρο" 
    
    dialog.wait_window()
    return result

def analyze_with_reduced_certainty(comment_input, uncertainty_count): # Ανάλυση με μειωμένη βεβαιότητα
    """Αναλύει σχόλιο με μειωμένη βεβαιότητα"""
    # Κανονική ανάλυση
    sentiment, score, analysis_type = perform_normal_analysis(comment_input) # Κανονική ανάλυση
    
    if sentiment and score:
        # Μείωση βεβαιότητας ανάλογα με τον αριθμό λέξεων αβεβαιότητας
        reduction_factor = min(uncertainty_count * 0.2, 0.4)  # Μέχρι 40% μείωση
        reduced_score = max(score * (1 - reduction_factor), 30)  # Ελάχιστο 30%
        
        return sentiment, int(reduced_score), "reduced_certainty"
    
    return sentiment, score, analysis_type

def perform_normal_analysis(comment_input): # Κανονική ανάλυση
    """Εκτελεί την κανονική ανάλυση συναισθήματος"""
    try:
        # Ανάλυση θετικών λέξεων
        comment_positive_words_to_remove_None = eisagogi_sxoliou(comment_input) # Ανάλυση θετικών λέξεων
        comment_negative_words_to_remove_None = eisagogi_sxoliou(comment_input, 'arnitikes') # Ανάλυση αρνητικών λέξεων
        
        comment_positive_words = [] # Αρχικοποίηση της λίστας θετικών λέξεων
        comment_negative_words = [] # Αρχικοποίηση της λίστας αρνητικών λέξεων
        
        # Καθαρισμός από None values
        if comment_positive_words_to_remove_None: # Αν υπάρχουν θετικές λέξεις
            for i in comment_positive_words_to_remove_None:
                if i is not None:
                    if isinstance(i, list):
                        comment_positive_words.extend(i) # Προσθήκη των λέξεων στη λίστα
                    else:
                        comment_positive_words.append(i) # Προσθήκη της λέξης στη λίστα
        
        if comment_negative_words_to_remove_None: # Αν υπάρχουν αρνητικές λέξεις
            for i in comment_negative_words_to_remove_None:
                if i is not None:
                    if isinstance(i, list):
                        comment_negative_words.extend(i)
                    else:
                        comment_negative_words.append(i)

        positive_count = len(comment_positive_words) # Υπολογισμός του πλήθους των θετικών λέξεων
        negative_count = len(comment_negative_words) # Υπολογισμός του πλήθους των αρνητικών λέξεων
        
        if positive_count > negative_count: # Αν το πλήθος των θετικών λέξεων είναι μεγαλύτερο από το πλήθος των αρνητικών λέξεων
            sentiment = 'Θετικό'
            score = (positive_count / (positive_count + negative_count)) * 100
        elif positive_count < negative_count: # Αν το πλήθος των θετικών λέξεων είναι μικρότερο από το πλήθος των αρνητικών λέξεων  
            sentiment = 'Αρνητικό'
            score = (negative_count / (positive_count + negative_count)) * 100
        else:
            sentiment = 'Ουδέτερο'
            score = 50
            
        return sentiment, int(score), "normal" # Επιστροφή του συναίσθηματος, της βαθμολογίας και του τύπου ανάλυσης
        
    except Exception as e:
        custom_print(f"ΣΦΑΛΜΑ στην ανάλυση: {e}") # Εμφάνιση του σφάλματος                          
        return None, None, "error" # Επιστροφή του συναίσθηματος, της βαθμολογίας και του τύπου ανάλυσης


################  ΔΙΟΡΘΩΣΗ: Καθαρισμός κειμένου  ###############################
################# ###############################


# Φόρτωση ακριβών φράσεων από αρχείο JSON 
def load_exact_phrases(): # Φόρτωση ακριβών φράσεων από αρχείο JSON
    if os.path.exists(exact_phrases_file) and os.path.getsize(exact_phrases_file) > 0: # Αν υπάρχει το αρχείο και είναι μεγέθους μεγαλύτερο από 0
        try:
            with open(exact_phrases_file, 'r', encoding='utf-8') as file: # Αν υπάρχει το αρχείο
                return json.load(file) # Επιστροφή των ακριβών φράσεων
        except:
            # Σε περίπτωση σφάλματος, χρησιμοποιούμε τις προεπιλογές
            with open(exact_phrases_file, 'w', encoding='utf-8') as file: # Αν δεν υπάρχει το αρχείο
                json.dump(default_exact_phrases, file, ensure_ascii=False, indent=4) # Δημιουργία του αρχείου με τις προεπιλεγμένες φράσεις
            return default_exact_phrases # Επιστροφή των προεπιλεγμένων φράσεων
    else:
        # Αν το αρχείο δεν υπάρχει ή είναι κενό, δημιουργούμε το με τις προεπιλεγμένες φράσεις
        with open(exact_phrases_file, 'w', encoding='utf-8') as file: # Δημιουργία του αρχείου με τις προεπιλεγμένες φράσεις
            json.dump(default_exact_phrases, file, ensure_ascii=False, indent=4) # Δημιουργία του αρχείου με τις προεπιλεγμένες φράσεις
        return default_exact_phrases

# Φόρτωση λέξεων από τα αρχεία
thetikes_lekseis = load_words_from_file(thetikes_file, default_thetikes) # Φόρτωση λέξεων από τα αρχεία
arnitikes_lekseis = load_words_from_file(arnitikes_file, default_arnitikes) # Φόρτωση λέξεων από τα αρχεία
stopwords_lekseis = load_words_from_file(stopwords_file, default_stopwords) # Φόρτωση λέξεων από τα αρχεία
exact_phrases = load_exact_phrases() # Φόρτωση ακριβών φράσεων από το αρχείο JSON

def clean_text_comment(lowered_text): # Καθαρισμός κειμένου
    clean_text = lowered_text.translate(str.maketrans("", "", ".,!")) # αφαίρεση σημείων στίξης
    return clean_text

def afairesi_tou_tonou(x): # Αφαίρεση τόνου
    text_xoris_tonos =''
    for word in x:
        for word_letter in unicodedata.normalize('NFD', word): ## κανονικοποίηση του κειμένου
            if unicodedata.category(word_letter) == 'Mn': ## έλεγχος αν το γράμμα είναι τόνος
                continue
            else:
                text_xoris_tonos = text_xoris_tonos+word_letter ## αφαίρεση τόνου

    return text_xoris_tonos

def afairesi_stopwords(comment_without_tono): # Αφαίρεση stopwords , 
    comment_without_tono_n_stopwords = [] # Ορισμός της λίστας με τις λέξεις που δεν είναι stopwords , 
    stopword_to_match = afairesi_tou_tonou(stopwords_lekseis) # Αφαίρεση τόνου από τις λέξεις της λίστας stopwords , 
    for word in comment_without_tono: # Για κάθε λέξη του σχολίου
        if word in stopword_to_match: # Αν η λέξη είναι stopword
            pass # Κάνει τίποτα
        else:
            comment_without_tono_n_stopwords.append(word) # Προσθήκη της λέξης στη λίστα
    return comment_without_tono_n_stopwords
            
def word_first_match(comment_without_tono, sent_expression=None): # Πρώτη σύγκριση λέξεων
    custom_print(f"Λέξεις προς αναγνώριση: {comment_without_tono}") # εμφάνιση της λίστας με τις λέξεις που θα αναγνωριστούν
    
    one_word_matches = [] # ορισμός της λίστας με τις λέξεις που ταιριάζουν
    if sent_expression is None: # αν δεν υπάρχει καμία λέξη
        thetikes_words = thetikes_lekseis # ορισμός της λίστας με τις θετικές λέξεις
        for com_word in comment_without_tono: # για κάθε λέξη του σχολίου
            custom_print(f"Ελέγχω τη λέξη: {com_word}") # εμφάνιση της λέξης
            matched_words = [] # ορισμός της λίστας με τις λέξεις που ταιριάζουν
            for thet_word in thetikes_words: # για κάθε λέξη της λίστας
                thet_word_to_match = afairesi_tou_tonou(thet_word.lower())
                similarity_score = SequenceMatcher(None, com_word, thet_word_to_match).ratio() ## σύγκριση λέξεων , αν η λέξη του σχολίου ταιριάζει με την λέξη της λίστας
                custom_print(f"  Σύγκριση με: {thet_word} -> {thet_word_to_match}, score: {similarity_score}") ## εμφάνιση της σύγκρισης , αν η λέξη του σχολίου ταιριάζει με την λέξη της λίστας
                if similarity_score == 1.0:
                    custom_print(f"  ΤΕΛΕΙΟ ΤΑΙΡΙΑΣΜΑ με {thet_word}") # εμφάνιση της λέξης
                    one_word_matches.append(thet_word_to_match) # προσθήκη της λέξης στη λίστα
                    break
                elif similarity_score >= 0.65 and similarity_score < 1.0: ## αν η λέξη είναι παρόμοια με την λέξη του σχολίου 
                    custom_print(f"  ΚΑΛΟ ΤΑΙΡΙΑΣΜΑ με {thet_word}: {similarity_score}") # εμφάνιση της λέξης
                    matched_words.append(thet_word_to_match) ## προσθήκη της λέξης στη λίστα
            
            if matched_words:
                custom_print(f"  Πιθανά ταιριάσματα για {com_word}: {matched_words}") # εμφάνιση της λέξης
            else:
                custom_print(f"  Δεν βρέθηκαν ταιριάσματα για {com_word}") ## εμφάνιση της λέξης , αν δεν υπάρχουν ταιριάσματα
                
            if len(matched_words) != 0: ## αν υπάρχουν λέξεις στη λίστα
                one_word_match = word_second_match(com_word, matched_words) ## σύγκριση λέξεων
                if one_word_match:
                    custom_print(f"  Τελικό ταίριασμα: {one_word_match}")
                    one_word_matches.append(one_word_match) ## προσθήκη της λέξης στη λίστα
    elif sent_expression == 'arnitikes': # αν υπάρχει λέξη
        arnitikes_words = arnitikes_lekseis ##  λίστα με τις αρνητικές λέξεις
        for com_word in comment_without_tono: ## για κάθε λέξη του σχολίου
            custom_print(f"Ελέγχω τη λέξη: {com_word} (αρνητικές)")
            matched_words = [] ## λίστα με τις λέξεις που ταιριάζουν
            for arn_word in arnitikes_words:
                arn_word_to_match = afairesi_tou_tonou(arn_word.lower()) ## αφαίρεση τόνου
                similarity_score = SequenceMatcher(None, com_word, arn_word_to_match).ratio() ## σύγκριση λέξεων
                custom_print(f"  Σύγκριση με: {arn_word} -> {arn_word_to_match}, score: {similarity_score}")
                if similarity_score == 1.0:
                    custom_print(f"  ΤΕΛΕΙΟ ΤΑΙΡΙΑΣΜΑ με {arn_word}") # εμφάνιση της λέξης
                    one_word_matches.append(arn_word_to_match) # προσθήκη της λέξης στη λίστα
                    break
                elif similarity_score >= 0.65 and similarity_score < 1.0: # αν η λέξη είναι παρόμοια με την λέξη του σχολίου 
                    custom_print(f"  ΚΑΛΟ ΤΑΙΡΙΑΣΜΑ με {arn_word}: {similarity_score}") # εμφάνιση της λέξης
                    matched_words.append(arn_word_to_match) # προσθήκη της λέξης στη λίστα
            
            if matched_words:
                custom_print(f"  Πιθανά ταιριάσματα για {com_word}: {matched_words}") # εμφάνιση της λέξης
            else:
                custom_print(f"  Δεν βρέθηκαν ταιριάσματα για {com_word}")  
                
            if len(matched_words) != 0:
                one_word_match = word_second_match(com_word, matched_words) # σύγκριση λέξεων
                if one_word_match:
                    custom_print(f"  Τελικό ταίριασμα: {one_word_match}") # εμφάνιση της λέξης
                    one_word_matches.append(one_word_match) # προσθήκη της λέξης στη λίστα
    
    custom_print(f"Συνολικά ταιριάσματα: {one_word_matches}") # εμφάνιση της λίστας με τα ταιριάσματα
    return one_word_matches

def word_second_match(com_word, matched_words):## Σύγκριση λέξεων
    text_letters = list(com_word) # λίστα με τα γράμματα της λέξης του σχολίου  
    ## print('WORD_SECOND_MATCH Η λέξη του σχολίου είναι ', com_word)
    best_match = [] ## λίστα με τις καλύτερες λέξεις
 
    for matched_word in matched_words: ## για κάθε λέξη που ταιριάζει
        matchword_letters = list(matched_word) ## λίστα με τις λέξεις που ταιριάζουν
        count = 0
       
        for text_letter, match_letter in zip(text_letters, matchword_letters): # για κάθε γράμμα της λέξης του σχολίου και της λέξης που ταιριάζει
            # print('WORD_SECOND_MATCH ', text_letter,match_letter)
            # print(count)
            if str(text_letter).strip() == str(match_letter).strip(): ## αν οι λέξεις ταιριάζουν
                count = count + 1
            elif str(text_letter) != str(match_letter): ## αν οι λέξεις δεν ταιριάζουν
                break
                ## print('##############################diaforetika############################')
            else:
                print('Auta ta grammata den tairiazoun')
        match_score = (count/(len(text_letters)))*100 ## ποσοστό ταιριάσματος
        # print(f'WORD_SECOND_MATCH Το σκόρ με το ταιριασμα της λέξης {com_word} και της ομοιας της {matched_word} ειναι: {match_score}')
        if match_score >= 65: ## αν το ποσοστό ταιριάσματος είναι μεγαλύτερο από 65
            best_match.append(matched_word) ## προσθήκη της λέξης στη λίστα
        matchword_letters = [] ## κενή λίστα για να μην κρατάει τις παλιές λέξεις
        # count = 0
    if len(best_match) != 0:
        return best_match
    else:
        
        return 


def eisagogi_sxoliou(comment_input, sent_expression=None): # Ανάλυση σχολίου , ανάλυση με error handling
    """Βελτιωμένη ανάλυση σχολίου με error handling"""
    try:
        custom_print(f"Ανάλυση σχολίου: {comment_input}") # εμφάνιση του σχολίου 
        
        # Έλεγχος εγκυρότητας εισόδου
        if not comment_input or not comment_input.strip():
            custom_print("Κενό σχόλιο - επιστροφή κενής λίστας") # εμφάνιση μήνυματος σφάλματος
            return []
        
        lowered_text = (comment_input.lower()) # μετατροπή του σχολίου σε πεζά
        custom_print(f"Κείμενο σε πεζά: {lowered_text}") # εμφάνιση του σχολίου σε πεζά
        
        cleaned_comment = clean_text_comment(lowered_text) # καθαρισμός του σχολίου
        custom_print(f"Καθαρισμένο κείμενο: {cleaned_comment}") # εμφάνιση του καθαρισμένου σχολίου
        
        comment_without_tono2 = afairesi_tou_tonou(cleaned_comment) # αφαίρεση τόνων
        comment_without_tono = comment_without_tono2.split() # διαχωρισμός του σχολίου σε λέξεις
        custom_print(f"Λέξεις χωρίς τόνους: {comment_without_tono}") # εμφάνιση του σχολίου χωρίς τόνους
        
        comment_without_tono_n_stopwords = afairesi_stopwords(comment_without_tono) # αφαίρεση stopwords
        custom_print(f"Λέξεις μετά την αφαίρεση stopwords: {comment_without_tono_n_stopwords}") # εμφάνιση του σχολίου χωρίς stopwords
        
        if sent_expression is None:
            custom_print(f"Λίστα θετικών λέξεων: {thetikes_lekseis}") # εμφάνιση της λίστας θετικών λέξεων
        else:
            custom_print(f"Λίστα αρνητικών λέξεων: {arnitikes_lekseis}") # εμφάνιση της λίστας αρνητικών λέξεων
        
        results = word_first_match(comment_without_tono_n_stopwords, sent_expression) # αναγνώριση λέξεων
        custom_print(f"Αποτελέσματα αναγνώρισης λέξεων: {results}") # εμφάνιση των αποτελεσμάτων της αναγνώρισης λέξεων
        
        return results if results else []
        
    except Exception as e:
        custom_print(f"ΣΦΑΛΜΑ στην ανάλυση σχολίου: {e}") # εμφάνιση μήνυματος σφάλματος
        return []

# Συνάρτηση που ελέγχει αν το σχόλιο περιέχει τις συγκεκριμένες λέξεις
def check_exact_phrase(comment): # Ελέγχει αν το σχόλιο περιέχει τις συγκεκριμένες λέξεις
    # Μετατροπή σε πεζά και καθαρισμός του σχολίου
    comment_lower = comment.lower()
    cleaned_comment = clean_text_comment(comment_lower) # καθαρισμός του σχολίου
    # Διαχωρισμός σε λέξεις
    comment_words = cleaned_comment.split() # διαχωρισμός του σχολίου σε λέξεις
    
    # Αφαίρεση τόνων από τις λέξεις του σχολίου
    comment_words_no_accent = [] # λίστα με τις λέξεις του σχολίου χωρίς τόνους
    for word in comment_words: # για κάθε λέξη του σχολίου
        word_no_accent = "" # λέξη χωρίς τόνους , κενή λίστα
        for letter in unicodedata.normalize('NFD', word): # για κάθε γράμμα της λέξης , αφαιρεί τους τόνους
            if unicodedata.category(letter) != 'Mn': # αν το γράμμα δεν είναι τόνος , προσθήκη του γράμματος στη λέξη
                word_no_accent += letter # προσθήκη του γράμματος στη λέξη , αφαιρεί τους τόνους
        comment_words_no_accent.append(word_no_accent) # προσθήκη της λέξης στη λίστα , αφαιρεί τους τόνους
    
    # Αναζήτηση για ακριβείς λέξεις/φράσεις
    best_match = None # καλύτερη αντιστοιχία
    best_score = -1 # καλύτερη βαθμολογία
    
    for phrase, info in exact_phrases.items(): # για κάθε φράση του σχολίου
        # Αφαίρεση τόνων από τη φράση-κλειδί και μετατροπή σε πεζά
        phrase_no_accent = "" # φράση χωρίς τόνους
        for letter in unicodedata.normalize('NFD', phrase.lower()): # για κάθε γράμμα της φράσης
            if unicodedata.category(letter) != 'Mn': # αν το γράμμα δεν είναι τόνος
                phrase_no_accent += letter # προσθήκη του γράμματος στη φράση
        
        # Αν η φράση-κλειδί έχει πολλές λέξεις, ελέγχουμε αν περιέχεται ως σύνολο
        if " " in phrase_no_accent: # αν η φράση έχει περιέχει κενά
            if phrase_no_accent in " ".join(comment_words_no_accent): # αν η φράση είναι στο σχολίο
                if info["score"] > best_score: # αν η βαθμολογία της φράσης είναι μεγαλύτερη από την καλύτερη βαθμολογία
                    best_match = phrase # προσθήκη της φράσης στη καλύτερη αντιστοιχία
                    best_score = info["score"] # προσθήκη της βαθμολογίας της φράσης στη καλύτερη βαθμολογία
        # Αλλιώς ελέγχουμε αν υπάρχει ως μεμονωμένη λέξη
        else:
            if phrase_no_accent in comment_words_no_accent: # αν η φράση είναι στο σχολίο   
                if info["score"] > best_score: # αν η βαθμολογία της φράσης είναι μεγαλύτερη από την καλύτερη βαθμολογία
                    best_match = phrase # προσθήκη της φράσης στη καλύτερη αντιστοιχία
                    best_score = info["score"] # προσθήκη της βαθμολογίας της φράσης στη καλύτερη βαθμολογία
    
    if best_match: # αν υπάρχει καλύτερη αντιστοιχία
        return exact_phrases[best_match]["sentiment"], exact_phrases[best_match]["score"] # επιστροφή της φράσης και της βαθμολογίας
    return None, None # επιστροφή None, None

### Δημιουργία κατεύθυνσης των αρχείων στο φάκελο που υπάρχει το τρέχον αρχείο .py ###
current_directory = os.path.dirname(os.path.abspath(__file__)) # οδηγία στον φάκελο που υπάρχει το τρέχον αρχείο .py
data_folder = os.path.join(current_directory, 'data') # οδηγία στον φάκελο που υπάρχει το φάκελο data
xrisimes_lekseis = os.path.join(current_directory, 'xrisimes_lekseis') # οδηγία στον φάκελο που υπάρχει το φάκελο xrisimes_lekseis
file_path_prod_comm = os.path.join(data_folder, "product_comments.csv") # οδηγία στον φάκελο που υπάρχει το αρχείο product_comments.csv
file_path_serv_comm = os.path.join(data_folder, "service_comments.csv") # οδηγία στον φάκελο που υπάρχει το αρχείο service_comments.csv


#####################################################################
###################### ΚΛΑΣΗ ΣΧΟΛΙΩΝ COMMENT ########################
###################### ΚΛΑΣΗ ΣΧΟΛΙΩΝ COMMENT ########################
class Comment():
    product_comments = [] # εδώ αποθηκευονται όλα τα σχόλια για τα προιόντα
    service_comments = [] # εδώ αποθηκεύονται όλα τα σχόλια για τις υπηρεσίες
    neutral_words = ['το'] # για μελλοντική χρήση

    def __init__(self, input_com, sent_score_perc= 0, sent_score_str = ''): # Χαρακτηριστικά σχολίου
        # Χαρακτηριστικά σχολίου
        self.input_com = input_com # Το ίδιο το σχόλιο
        self.sent_result_str_com = sent_score_str # Αποτέλεσμα συναισθήματος (ΘΕΤΙΚΟ, ΑΡΝΗΤΙΚΟ ,ΟΥΔΕΤΕΡΟ)
        self.positive_number = None # θετικές λέξεις σε αριθμό δημιουργείται απο analyze_com_this_code και χρησιμοποειται sentiment_result
        self.negative_number = None # αρνητικές λέξεις σε αριθμό δημιουργείται απο analyze_com_this_code και χρησιμοποειται sentiment_result
        self.sent_result_perc_com = sent_score_perc # Το ποσοστό συναισθήματος του σχολίου, βγαίνει απο sentiment_result και χρησιμοποιειται button_analusi_pressed
        # self.analyze_com()
        # self.sentiment_result()
        # self.all_comments()

    def analyze_com_this_code(self): # Βελτιωμένη ανάλυση σχολίου με καλύτερο error handling
        """Βελτιωμένη ανάλυση σχολίου με καλύτερο error handling"""
        try:
            # Έλεγχος για συγκεκριμένες λέξεις/φράσεις
            exact_sentiment, exact_score = check_exact_phrase(self.input_com) # Έλεγχος για συγκεκριμένες λέξεις/φράσεις

            if exact_sentiment and exact_score:
                # Αν βρέθηκε ακριβής φράση, χρησιμοποιούμε τα προκαθορισμένα αποτελέσματα
                Comment.sent_result_str_com = exact_sentiment
                Comment.sent_result_perc_com = exact_score
                
                # Ρυθμίζουμε τα positive_number και negative_number ανάλογα με το συναίσθημα
                if exact_sentiment == "Θετικό":
                    Comment.positive_number = 1
                    Comment.negative_number = 0
                elif exact_sentiment == "Αρνητικό":
                    Comment.positive_number = 0
                    Comment.negative_number = 1
                else:  # Ουδέτερο
                    Comment.positive_number = 1
                    Comment.negative_number = 1
                    
                custom_print(f"Βρέθηκε ακριβής φράση: {exact_sentiment} ({exact_score}%)") # εμφάνιση της φράσης και της βαθμολογίας  
                return
            
            # Αν δεν βρέθηκε ακριβής φράση, συνεχίζουμε με την κανονική ανάλυση
            comment_positive_words_to_remove_None = eisagogi_sxoliou(self.input_com) # κανονική ανάλυση
            comment_negative_words_to_remove_None = eisagogi_sxoliou(self.input_com, 'arnitikes') # κανονική ανάλυση
            
            comment_positive_words = []
            comment_negative_words = []
            
            # Καθαρισμός από None values
            if comment_positive_words_to_remove_None: 
                for i in comment_positive_words_to_remove_None: # αν υπάρχουν θετικές λέξεις
                    if i is not None:
                        if isinstance(i, list): # Αν το στοιχείο είναι λίστα
                            comment_positive_words.extend(i) # προσθήκη των λέξεων στη λίστα
                        else:
                            comment_positive_words.append(i) # προσθήκη της λέξης στη λίστα
            
            if comment_negative_words_to_remove_None:
                for i in comment_negative_words_to_remove_None: # αν υπάρχουν αρνητικές λέξεις
                    if i is not None:
                        if isinstance(i, list): # Αν το στοιχείο είναι λίστα
                            comment_negative_words.extend(i) # προσθήκη των λέξεων στη λίστα
                        else:
                            comment_negative_words.append(i) # προσθήκη της λέξης στη λίστα

            Comment.positive_number = len(comment_positive_words) # υπολογισμός του αριθμού των θετικών λέξεων
            Comment.negative_number = len(comment_negative_words) # υπολογισμός του αριθμού των αρνητικών λέξεων
            
            custom_print(f"Βρέθηκαν {Comment.positive_number} θετικές και {Comment.negative_number} αρνητικές λέξεις") # Εμφάνιση του αριθμού των θετικών και αρνητικών λέξεων
            
        except Exception as e:
            custom_print(f"ΣΦΑΛΜΑ στην ανάλυση: {e}") # Εμφάνιση του σφάλματος
            Comment.positive_number = 0
            Comment.negative_number = 0
       
          ####### ############  ######################
          ####### ############  ######################

    def sentiment_result(self): # υπολογισμός του συναισθήματος, με καλύτερο error handling
        # Το αποτέλεσμα του συναισθήματος
        positive = Comment.positive_number # αριθμός των θετικών λέξεων
        negative = Comment.negative_number # αριθμός των αρνητικών λέξεων
        
        if positive > negative:
            Comment.sent_result_str_com = 'Θετικό'
            Comment.sent_result_perc_com = (positive / (positive + negative)) * 100 # υπολογισμός του ποσοστού των θετικών λέξεων
        elif positive < negative:
            Comment.sent_result_str_com = 'Αρνητικό'
            Comment.sent_result_perc_com = (negative / (positive + negative)) * 100 # υπολογισμός του ποσοστού των αρνητικών λέξεων
        else:
            Comment.sent_result_str_com = 'Ουδέτερο'
            Comment.sent_result_perc_com = 50 # ποσοστό 50%

    def all_comments(self):
        if type(self).__name__ == 'Products':
            Comment.product_comments.append(self.input_com) # προσθήκη του σχολίου στη λίστα των σχολίων για τα προιόντα
        elif type(self).__name__ == 'Services':
            Comment.service_comments.append(self.input_com) # προσθήκη του σχολίου στη λίστα των σχολίων για τις υπηρεσίες
        ## print(Comment.product_comments)
        ## print(Comment.service_comments)

##################### YPOΚΛΑΣΗ ΣΧΟΛΙΩΝ PRODUCTS #####################

class Products(Comment): # Κλάση για τα προιόντα, που είναι γονική της Comment
    def __init__(self, input_com, sent_score_perc=0, sent_score_str=''):
        # Αλλαγή του τρόπου κλήσης του constructor της γονικής κλάσης
        super().__init__(input_com, sent_score_perc, sent_score_str)  # Χρήση του super()
        
        # Ή θέσε τις μεταβλητές απευθείας
        #self.input_com = input_com
        #self.sent_score_perc = sent_score_perc
        #self.sent_score_str = sent_score_str
      
        # self.save_comment()


    def save_comment(self): # αποθήκευση του σχολίου , με καλύτερο error handling
        # Προσθήκη ημερομηνίας και ώρας 
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Ημερομηνία και ώρα, σε μορφή ημερομηνίας και ώρας
        
        product_data = { # δεδομένα για το σχόλιο , σε μορφή λεξικού
            'Σχόλια': [self.input_com],  # σχόλιο
            'Συναίσθημα': [Comment.sent_result_str_com],  # συναισθηματικό αποτέλεσμα
            'Ποσοστό %': [Comment.sent_result_perc_com], # ποσοστό συναισθήματος
            'Ημερομηνία': [current_datetime]
        }
        product_df = pd.DataFrame(product_data) # δημιουργία πίνακα δεδομένων για το σχόλιο , σε μορφή πίνακα
        
        if os.path.exists(file_path_prod_comm): # αν υπάρχει το αρχείο προϊόντων , τότε φορτώνει τα δεδομένα από το αρχείο προϊόντων
            s = pd.read_csv(file_path_prod_comm) # ανάγνωση του αρχείου προϊόντων , μετατροπή σε λίστα dictionaries, Products
            s = pd.concat([s, product_df], ignore_index=True) # συνένωση του πίνακα δεδομένων με τον πίνακα δεδομένων του αρχείου , με ignore_index=True
        else:
            s = product_df # αν δεν υπάρχει το αρχείο προϊόντων , τότε δημιουργείται ένα νέο αρχείο
        s.to_csv(file_path_prod_comm, index=False) # αποθήκευση του σχολίου στο αρχείο
        ###############################################
        
    def save_sentiment(self): # αποθήκευση του συναισθήματος , με καλύτερο error handling
        pass 

    def all_comments(self): # προσθήκη του σχολίου στη λίστα των σχολίων για τα προιόντα , με καλύτερο error handling
        Products.products_comments_list.append(self.input_com) # προσθήκη του σχολίου στη λίστα των σχολίων για τα προιόντα 
        # print("ΛΙΣΑ PRODUCTS ", Products.products_comments_list)

    def all_sentiments(self): # προσθήκη του συναισθήματος στη λίστα των συναισθημάτων για τα προιόντα
        pass

##################### YPOΚΛΑΣΗ ΣΧΟΛΙΩΝ SERVICES #####################

class Services(Comment):
    def __init__(self, input_com, sent_score_perc=0, sent_score_str=''):
        # Αλλαγή του τρόπου κλήσης του constructor της γονικής κλάσης
        super().__init__(input_com, sent_score_perc, sent_score_str)  # Χρήση του super
        
        # Ή θέσε τις μεταβλητές απευθείας
        self.input_com = input_com # σχόλιο
        self.sent_score_perc = sent_score_perc # ποσοστό συναισθήματος
        self.sent_score_str = sent_score_str # συναισθηματικό αποτέλεσμα
        

    def save_comment(self): # αποθήκευση του σχολίου, με καλύτερο error handling
        # Προσθήκη ημερομηνίας και ώρας
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Ημερομηνία και ώρα, σε μορφή ημερομηνίας και ώρας
        
        product_data = { # δεδομένα για το σχόλιο
            'Σχόλια': [self.input_com],  # σχόλιο
            'Συναίσθημα': [Comment.sent_result_str_com],  # συναισθηματικό αποτέλεσμα
            'Ποσοστό %': [Comment.sent_result_perc_com], # ποσοστό συναισθήματος
            'Ημερομηνία': [current_datetime] # ημερομηνία και ώρα
        }
        product_df = pd.DataFrame(product_data) # δημιουργία πίνακα δεδομένων για το σχόλιο
        
        if os.path.exists(file_path_serv_comm): # αν υπάρχει το αρχείο , τότε φορτώνει τα δεδομένα από το αρχείο
            s = pd.read_csv(file_path_serv_comm) # ανάγνωση του αρχείου , μετατροπή σε λίστα dictionaries Services
            s = pd.concat([s, product_df], ignore_index=True) # συνένωση του πίνακα δεδομένων με τον πίνακα δεδομένων του αρχείου
        else:
            s = product_df # αν δεν υπάρχει το αρχείο, τότε δημιουργείται ένα νέο αρχείο
        s.to_csv(file_path_serv_comm, index=False) # αποθήκευση του σχολίου στο αρχείο
   
    def save_ser_sentiment(self): # αποθήκευση του συναισθήματος
        pass

    def all_comments(self): # προσθήκη του σχολίου στη λίστα των σχολίων για τις υπηρεσίες
        Services.services_comments_list.append(self.input_com) # προσθήκη του σχολίου στη λίστα των σχολίων για τις υπηρεσίες
        ## print("ΛΙΣΑ SERVICES ", Products.products_comments_list)

    def all_ser_sentiments(self): # προσθήκη του συναισθήματος στη λίστα των συναισθημάτων για τις υπηρεσίες
        pass
#####################################################################


                    ### ΓΡΑΦΙΚΗ ΔΙΕΠΑΦΗ ###
#####################################################################
##################### PATHS ΓΙΑ ΤΟ TKINTER ##########################
icons_folder = os.path.join(current_directory, 'icons') # οδηγία στον φάκελο που υπάρχει το φάκελο icons
app_icon1_path = os.path.join(icons_folder, "app_icon1.png") # οδηγία στον φάκελο που υπάρχει το αρχείο app_icon1.png
copy_btn_path = os.path.join(icons_folder, "icons8-copy-322.png") # οδηγία στον φάκελο που υπάρχει το αρχείο icons8-copy-322.png
paste_btn_path = os.path.join(icons_folder, "icons8-paste-322.png") # οδηγία στον φάκελο που υπάρχει το αρχείο icons8-paste-322.png
delete_btn_path = os.path.join(icons_folder, "icons8-delete-322.png") # οδηγία στον φάκελο που υπάρχει το αρχείο icons8-delete-322.png
######################################################################
# ΜΕΤΑΒΛΗΤΕΣ
global selected # μεταβλητή για την επιλογή του σχολίου
selected = False # αρχική τιμή της μεταβλητής selected

global focus_set_action # μεταβλητή για την επιλογή του σχολίου
global msg_diadikasia # μεταβλητή για την επιλογή του σχολίου , 

pie_chart_window = None # μεταβλητή για την επιλογή του σχολίου
pie_chart_canvas = None # μεταβλητή για την επιλογή του σχολίου
history = [] # μεταβλητή για την επιλογή του σχολίου
previous_valid_chart_option = "all"  # Κρατάει την προηγούμενη έγκυρη επιλογή διαγράμματος
chart_option = None
colour1 = '#99E2DB' # χρώμα 1   
colour2 = '#FDCB60' # χρώμα 2
colour3 = '#FDB211' # χρώμα 3
colour4 = '#053A61' # χρώμα 4

#####################################################################
####################### ΚΟΥΜΠΙΑ ΕΠΙΛΟΓΩΝ ############################
# κουμπί επιλογής ανάμεσα σε Προιόντα και Υπηρεσίες

def btn_choice(choice): # κουμπί επιλογής ανάμεσα σε Προιόντα και Υπηρεσίες
    global comment_type, main_selection
    comment_type.set(choice)
    
    # Συγχρονισμός radio buttons με την επιλογή
    main_selection.set(choice)
    
    # Ενημέρωση του μηνύματος
    if choice == "Products": 
        msg_diadikasia.set("Επιλέξατε καταχώρηση σχολίου για Προϊόντα") # εμφάνιση μηνύματος
    else:
        msg_diadikasia.set("Επιλέξατε καταχώρηση σχολίου για Υπηρεσίες") # εμφάνιση μηνύματος

# κουμπί Ανάλυσης συναισθήματος
# από εδώ ξεκινάνε η βασικές λειτουργίες της κλάσης Comment
# Στο button_analisi_pressed:
def button_analisi_pressed(x, y, z): # Ανάλυση και αποθήκευση σχολίου με έλεγχο αβεβαιότητας
    """Ανάλυση και αποθήκευση σχολίου με έλεγχο αβεβαιότητας"""
    comment_text_input = comment_text.get("1.0", tk.END).strip()
    
    # Έλεγχος εγκυρότητας εισαγωγής
    if not comment_text_input or comment_text_input == 'Γράψτε εδώ το σχόλιό σας!': # Έλεγχος εγκυρότητας εισαγωγής
        messagebox.showwarning("Προειδοποίηση", "Παρακαλώ εισάγετε ένα σχόλιο!") # εμφάνιση μηνύματος
        return
    
    # Μήνυμα επιβεβαίωσης
    confirm = messagebox.askyesno(
        "Επιβεβαίωση καταχώρησης", 
        "Είστε σίγουρος/η ότι θέλετε να καταχωρήσετε αυτό το σχόλιο;"
    )
    
    if not confirm:
        return
    
    try:
        # ΝΕΟΣ ΚΩΔΙΚΑΣ: Χρήση της συνάρτησης με έλεγχο αβεβαιότητας
        analysis_result = analyze_comment_with_uncertainty(comment_text_input) # Ανάλυση σχολίου με έλεγχο αβεβαιότητας
        
        # Έλεγχος αν η ανάλυση ακυρώθηκε
        if analysis_result is None or len(analysis_result) != 3:  
            custom_print("Η ανάλυση ακυρώθηκε από τον χρήστη") # εμφάνιση μηνύματος
            return
            
        sentiment_str, sentiment_score, analysis_type = analysis_result 
        
        # Έλεγχος αν η ανάλυση ακυρώθηκε
        if analysis_type == "cancelled":
            custom_print("Η ανάλυση ακυρώθηκε από τον χρήστη") # εμφάνιση μηνύματος
            return
        
        # Έλεγχος για σφάλματα
        if sentiment_str is None or sentiment_score is None:
            messagebox.showerror("Σφάλμα", "Δεν ήταν δυνατή η ανάλυση του σχολίου!")
            return
        
        # Εμφάνιση μηνύματος ανάλογα με τον τύπο ανάλυσης
        if analysis_type == "exact_phrase":
            custom_print(f"Βρέθηκε ακριβής φράση: {sentiment_str} ({sentiment_score}%)")
        elif analysis_type == "reduced_certainty":
            custom_print(f"Ανάλυση με μειωμένη βεβαιότητα: {sentiment_str} ({sentiment_score}%)")
        elif analysis_type == "normal":
            custom_print(f"Κανονική ανάλυση: {sentiment_str} ({sentiment_score}%)")
        
        # Ενημέρωση GUI
        y.set(f'{sentiment_score:.0f} %') # ενημέρωση της τιμής του πλαισίου
        z.set(sentiment_str) # ενημέρωση της τιμής του πλαισίου
        
        # Αποθήκευση σε CSV
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comment_data = {
            'Σχόλια': [comment_text_input], 
            'Συναίσθημα': [sentiment_str], 
            'Ποσοστό %': [sentiment_score],
            'Ημερομηνία': [current_datetime]
        }
        comment_df = pd.DataFrame(comment_data)
        
        # Επιλογή σωστού αρχείου
        if x.get() == 'Products':
            file_path = file_path_prod_comm
            msg_diadikasia.set('Το σχόλιο για το προιόν αναλύθηκε και αποθηκεύτηκε.')
        elif x.get() == 'Services':
            file_path = file_path_serv_comm
            msg_diadikasia.set('Το σχόλιο για την υπηρεσία αναλύθηκε και αποθηκεύτηκε.')
        else:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε τύπο σχολίου!")
            return
        
        # Αποθήκευση στο αρχείο
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path)
            updated_df = pd.concat([existing_df, comment_df], ignore_index=True)
        else:
            updated_df = comment_df
        
        updated_df.to_csv(file_path, index=False)
        
        # Καταγραφή στο history για το διάγραμμα
        history.append((
            comment_text_input,
            sentiment_str,
            sentiment_score,
            x.get()
        ))
        
        # Καθαρισμός πλαισίου και επιστροφή στην αρχική κατάσταση
        comment_text.delete(1.0, tk.END) # Καθαρισμός του πλαισίου , 
        comment_text.insert(tk.END, 'Γράψτε εδώ το σχόλιό σας!') # Εισαγωγή της προεπιλεγμένης λέξης , 
        comment_text.config(fg='grey', font=('Century Gothic', 12)) # Επιλογή του χρώματος και της γραμματοσειράς
        
        # Μήνυμα επιτυχίας με πληροφορίες για τον τύπο ανάλυσης
        if analysis_type == "reduced_certainty":
            custom_print(f"✅ Σχόλιο αποθηκεύτηκε με μειωμένη βεβαιότητα: {sentiment_str} ({sentiment_score:.0f}%)") # Μήνυμα επιτυχίας με πληροφορίες για τον τύπο ανάλυσης , 
        else:
            custom_print(f"✅ Σχόλιο αποθηκεύτηκε επιτυχώς: {sentiment_str} ({sentiment_score:.0f}%)")
        
    except Exception as e:
        custom_print(f"ΣΦΑΛΜΑ στην ανάλυση σχολίου: {e}") # Μήνυμα σφάλματος , 
        messagebox.showerror("Σφάλμα", f"Προέκυψε σφάλμα κατά την ανάλυση: {e}") # Μήνυμα σφάλματος , 

######## ΚΑΘΑΡΙΣΜΟΣ ΚΕΙΜΕΝΟΥ ######### 
def clean_text_comment(lowered_text): # Καθαρισμός κειμένου
    """Βελτιωμένος καθαρισμός κειμένου με περισσότερα σημεία στίξης"""
    try:
        if not lowered_text:
            return ""
        
        # Αφαίρεση περισσότερων σημείων στίξης και ειδικών χαρακτήρων
        clean_text = lowered_text.translate(str.maketrans("", "", ".,!?;:\"'()[]{}/*+-=~`@#$%^&_|\\<>")) # Αφαίρεση περισσότερων σημείων στίξης και ειδικών χαρακτήρων
        return clean_text.strip()
    except Exception as e:
        custom_print(f"ΣΦΑΛΜΑ στον καθαρισμό κειμένου: {e}")
        return lowered_text  # επιστροφή του αρχικού κειμένου σε περίπτωση σφάλματος

########## ΔΙΑΓΡΑΜΜΑ ΠΙΤΑΣ ##########

def show_pie_chart():
    global pie_chart_window, pie_chart_canvas, history, options_frame # μεταβλητές για το παράθυρο, το canvas, το history και το frame
    # if not history: # αν δεν υπάρχουν δεδομένα για διάγραμμα
    #     messagebox.showinfo("Πληροφορία", "Δεν υπάρχουν δεδομένα για διάγραμμα.") # εμφάνιση μηνύματος
    #     return

    # Αν το παράθυρο υπάρχει ήδη, απλά ενημέρωσέ το
    if pie_chart_window and tk.Toplevel.winfo_exists(pie_chart_window):
        update_pie_chart() # ενημέρωση του διαγράμματος
        pie_chart_window.lift() # ανύψωση του παραθύρου
        return

    # Δημιούργησε νέο παράθυρο και κράτα αναφορά
    pie_chart_window = tk.Toplevel(root) # δημιουργία νέου παραθύρου
    pie_chart_window.configure(bg=colour1)
    pie_chart_window.title("Γραφική απεικόνιση") # ορίζουμε το τίτλο του παραθύρου
    pie_chart_window.geometry("500x550") # ορίζουμε το μέγεθος του παραθύρου
    # Δημιουργία μεταβλητής για την επιλογή
    chart_option = tk.StringVar(value="all")  # Ορίζουμε την αρχική τιμή εδώ
    # Δημιουργία frame για τα radio buttons
    icon = PhotoImage(file=app_icon1_path) # εικονίδιο του παράθυρου,
    pie_chart_window.iconphoto(False, icon) # εικονίδιο του παράθυρου,
    app_width = 700 # πλάτος του παράθυρου
    app_heigth = 550 # ύψος του παράθυρου
    screen_width = pie_chart_window.winfo_screenwidth() # πλάτος του οθόνης
    screen_height = pie_chart_window.winfo_screenheight() # ύψος του οθόνης
    # print(screen_width, screen_height)
    xi = (screen_width / 2) - (app_width / 2) # θέση του παράθυρου στην οθόνη
    yi = (screen_height / 2) - (app_heigth / 2) # θέση του παράθυρου στην οθόνη
    pie_chart_window.geometry(f'{app_width}x{app_heigth}+{int(xi)}+{int(yi)}') # τοποθέτηση του παράθυρου στην οθόνη
    
    # Δημιουργία frame για τα radio buttons
    options_frame = tk.Frame(pie_chart_window, bg=colour1) # δημιουργία frame για τα radio buttons
    options_frame.pack(pady=10) # τοποθέτηση του frame
    
    # Δημιουργία μεταβλητής για την επιλογή
    chart_option = tk.StringVar() # δημιουργία μεταβλητής για την επιλογή
    chart_option.set("all")  # Προεπιλογή: όλα τα δεδομένα
    
    # Δημιουργία των radio buttons
    label_option = tk.Label( # δημιουργία ετικέτας για την επιλογή
        options_frame,
        text="Επιλέξτε τύπο δεδομένων:",
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 10, 'bold')
    )
    label_option.grid(row=0, column=0, columnspan=3, pady=5) # τοποθέτηση της ετικέτας

    ##### Ρύθμιση των radio buttons #####
    def handle_radio_selection(option): # συνάρτηση για την επιλογή του radio button
        if chart_option is not None: # αν υπάρχει επιλογή
            chart_option.set(option) # ορίζουμε την επιλογή
        update_pie_chart(option) # ενημέρωση του διαγράμματος

    ##### Δημιουργία των radio buttons #####

    rb_all = tk.Radiobutton( # δημιουργία radio button για την επιλογή
        options_frame, # frame για τα radio buttons
        text="Όλα", # κείμενο του radio button
        variable=chart_option, # μεταβλητή για την επιλογή
        value="all", # τιμή του radio button
        bg=colour1, # χρώμα του radio button
        fg=colour4, # χρώμα του κειμένου του radio button
        font=('Century Gothic', 10), # στυλ του κειμένου του radio button
        command=lambda: handle_radio_selection("all") # συνάρτηση που εκτελείται όταν επιλεγεί το radio button
    )
    rb_all.grid(row=1, column=0, padx=10) # τοποθέτηση του radio button
    
    rb_products = tk.Radiobutton( # δημιουργία radio button για την επιλογή
        options_frame, # frame για τα radio buttons
        text="Προϊόντα", # κείμενο του radio button
        variable=chart_option, # μεταβλητή για την επιλογή
        value="Products", # τιμή του radio button
        bg=colour1, # χρώμα του radio button
        fg=colour4, # χρώμα του κειμένου του radio button
        font=('Century Gothic', 10), # στυλ του κειμένου του radio button
        command=lambda: handle_radio_selection("Products") # συνάρτηση που εκτελείται όταν επιλεγεί το radio button
    )
    rb_products.grid(row=1, column=1, padx=10) # τοποθέτηση του radio button
    
    rb_services = tk.Radiobutton( # δημιουργία radio button για την επιλογή
        options_frame, # frame για τα radio buttons
        text="Υπηρεσίες", # κείμενο του radio button
        variable=chart_option, # μεταβλητή για την επιλογή
        value="Services", # τιμή του radio button
        bg=colour1, # χρώμα του radio button
        fg=colour4, # χρώμα του κειμένου του radio button
        font=('Century Gothic', 10), # στυλ του κειμένου του radio button
        command=lambda: handle_radio_selection("Services") # συνάρτηση που εκτελείται όταν επιλεγεί το radio button   
    )
    rb_services.grid(row=1, column=2, padx=10) # τοποθέτηση του radio button
    
    # ΠΡΟΣΘΗΚΗ: Ρύθμιση αρχικής κατάστασης radio buttons
    chart_option.set("all")  # Ορίζουμε την αρχική τιμή
    rb_all.select()         # Επιλέγουμε το "Όλα"
    rb_products.deselect()  # Αποεπιλέγουμε τα άλλα
    rb_services.deselect()
    
    # ΑΛΛΑΓΗ: Αντί για after, καλούμε απευθείας το update_pie_chart
    update_pie_chart("all") # ενημέρωση του διαγράμματος
    
###############################################################
###############################################################   


    # Ενημέρωση διαγράμματος
def update_pie_chart(option="all"):
    global pie_chart_window, pie_chart_canvas, options_frame, previous_valid_chart_option, chart_option # Ορισμός των global μεταβλητών , 
    
    # Έλεγχος ασφαλείας
    if not pie_chart_window or not hasattr(pie_chart_window, 'winfo_exists') or not pie_chart_window.winfo_exists(): # Έλεγχος αν υπάρχει το pie_chart_window , 
        return
    
    # Ορισμός της επιλογής στο chart_option
    if chart_option is not None:
        chart_option.set(option)

    # Έλεγχος δεδομένων πριν τη φόρτωση
    has_data = False
    try:
        if option == "all":
            prod_df = pd.read_csv(file_path_prod_comm) if os.path.exists(file_path_prod_comm) else pd.DataFrame() # ανάγνωση του αρχείου
            serv_df = pd.read_csv(file_path_serv_comm) if os.path.exists(file_path_serv_comm) else pd.DataFrame() # ανάγνωση του αρχείου
            has_data = not prod_df.empty or not serv_df.empty # αν υπάρχουν δεδομένα
        elif option == "Products":
            prod_df = pd.read_csv(file_path_prod_comm) if os.path.exists(file_path_prod_comm) else pd.DataFrame() # ανάγνωση του αρχείου
            has_data = not prod_df.empty # αν υπάρχουν δεδομένα
        elif option == "Services":
            serv_df = pd.read_csv(file_path_serv_comm) if os.path.exists(file_path_serv_comm) else pd.DataFrame() # ανάγνωση του αρχείου
            has_data = not serv_df.empty # αν υπάρχουν δεδομένα
    except pd.errors.EmptyDataError: # Ειδικός χειρισμός για κενά CSV
        has_data = False
    except Exception: # Γενικός χειρισμός για άλλα σφάλματα ανάγνωσης
        has_data = False
        messagebox.showerror("Σφάλμα Ανάγνωσης", f"Δεν ήταν δυνατή η ανάγνωση των δεδομένων για την επιλογή: {option}")
        # Επαναφορά στην προηγούμενη έγκυρη επιλογή αν αποτύχει η ανάγνωση
        if chart_option and previous_valid_chart_option != option: # Έλεγχος αν υπάρχει το chart_option
            chart_option.set(previous_valid_chart_option)
            # Δεν καλούμε ξανά update_pie_chart εδώ για να αποφύγουμε ατέρμονο βρόχο
        return

    ##### Αν δεν υπάρχουν δεδομένα #####
    if not has_data:
        messagebox.showinfo("Πληροφορία", f"Δεν υπάρχουν δεδομένα για: {option}") # εμφάνιση μηνύματος αν δεν υπάρχουν δεδομένα
        # Επαναφορά του radio button στην προηγούμενη έγκυρη επιλογή
        if chart_option is not None and previous_valid_chart_option != option:  # Άλλαξε τον έλεγχο εδώ
            chart_option.set(previous_valid_chart_option) # ορίζουμε την επιλογή
        return
    
    # Αν φτάσουμε εδώ, σημαίνει ότι υπάρχουν δεδομένα ή είναι η αρχική φόρτωση "all"
    previous_valid_chart_option = option # Ορίζουμε την τρέχουσα ως την τελευταία έγκυρη

    # Φόρτωση δεδομένων από CSV αρχεία αντί για history (Ο κώδικας από εδώ και κάτω παραμένει όπως ήταν)
    try:
        products_data = [] # λίστα για τα δεδομένα των προϊόντων
        services_data = [] # λίστα για τα δεδομένα των υπηρεσιών
        
        if os.path.exists(file_path_prod_comm): # αν υπάρχει το αρχείο
            try: # προσπάθεια ανάγνωσης του αρχείου
                prod_df = pd.read_csv(file_path_prod_comm)
                if not prod_df.empty: # Χρησιμοποιούμε .empty αντί για len() > 0
                    products_data = prod_df.iloc[:, 1].tolist()
            except pd.errors.EmptyDataError:
                pass # Το αρχείο είναι κενό, το products_data παραμένει κενό
            except Exception:
                pass # Άλλο σφάλμα ανάγνωσης
                
        if os.path.exists(file_path_serv_comm): # αν υπάρχει το αρχείο
            try: # προσπάθεια ανάγνωσης του αρχείου
                serv_df = pd.read_csv(file_path_serv_comm) 
                if not serv_df.empty: # αν το αρχείο δεν είναι κενό
                    services_data = serv_df.iloc[:, 1].tolist() # προσθήκη των δεδομένων του αρχείου στη λίστα
            except pd.errors.EmptyDataError:
                pass
            except Exception:
                pass
                
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη φόρτωση δεδομένων: {str(e)}") # εμφάνιση μηνύματος σφάλματος
        return
    
    # ... (Ο υπόλοιπος κώδικας της update_pie_chart παραμένει ο ίδιος) ...
    # ... μέχρι το τέλος της συνάρτησης ...

    # Στο τέλος της συνάρτησης, πριν το τέλος του try:
    fig = Figure(figsize=(4, 4)) # δημιουργία διαγράμματος
    ax = fig.add_subplot(111) # προσθήκη υποδιαγράμματος στο διάγραμμα
    color_map = {
        "Θετικό": "#4A9B3C",
        "Αρνητικό": "#FF6F61",
        "Ουδέτερο": "#AEAEAE"
    }
    
    current_counts = {} # Μετονομασία για σαφήνεια
    if option == "all": 
        sentiment_counts_calc = {"Θετικό": 0, "Αρνητικό": 0, "Ουδέτερο": 0} # οι λίστες λέξεων
        for sentiment in products_data:
            if sentiment in sentiment_counts_calc: # αν το συναισθημα υπάρχει στη λίστα
                sentiment_counts_calc[sentiment] += 1 # αύξηση του συναισθήματος
        for sentiment in services_data:
            if sentiment in sentiment_counts_calc: # αν το συναισθημα υπάρχει στη λίστα
                sentiment_counts_calc[sentiment] += 1
        current_counts = {k: v for k, v in sentiment_counts_calc.items() if v > 0}
    elif option == "Products":
        current_counts = Counter(products_data)
    elif option == "Services":
        current_counts = Counter(services_data)

    if not current_counts: # Αν μετά τον υπολογισμό δεν υπάρχουν counts (π.χ. κενά αρχεία)
        # Αυτή η περίπτωση καλύπτεται ήδη από τον έλεγχο has_data παραπάνω,
        # αλλά ένας επιπλέον έλεγχος εδώ είναι ασφαλής.
        # messagebox.showinfo("Πληροφορία", f"Δεν βρέθηκαν δεδομένα συναισθήματος για: {option}")
        # Δεν χρειάζεται να κάνουμε κάτι άλλο, το διάγραμμα δεν θα ενημερωθεί αν δεν υπάρχουν counts.
        # Αν θέλουμε να καθαρίσουμε το παλιό διάγραμμα:
        if pie_chart_canvas:
            pie_chart_canvas.get_tk_widget().destroy()
            pie_chart_canvas = None
        # Και ίσως να δείξουμε ένα κενό πλαίσιο ή μήνυμα στο παράθυρο του διαγράμματος
        return


    labels = list(current_counts.keys()) # λίστα με τα συναισθήματα
    colors = [color_map.get(label, "#cccccc") for label in labels] # χρώματα για τα συναισθήματα
    
    if option == "all":
        title = "Συνολική Κατανομή Συναισθημάτων (Αποθηκευμένα Δεδομένα)"
    elif option == "Products":
        title = "Κατανομή Συναισθημάτων (Προϊόντα - Αποθηκευμένα)"
    elif option == "Services":
        title = "Κατανομή Συναισθημάτων (Υπηρεσίες - Αποθηκευμένα)"
    
    values = list(current_counts.values()) # λίστα με τα αριθμοί των συναισθημάτων
    total = sum(values)
    
    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors) # δημιουργία διαγράμματος
    ax.set_title(title) # τίτλος του διαγράμματος

    if pie_chart_canvas:
        pie_chart_canvas.get_tk_widget().destroy()

    if not pie_chart_window or not pie_chart_window.winfo_exists(): # Επιπλέον έλεγχος
        return

    pie_chart_canvas = FigureCanvasTkAgg(fig, master=pie_chart_window) # δημιουργία canvas
    pie_chart_canvas.draw() # σχεδίαση του διαγράμματος
    pie_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True) # προσθήκη του canvas στο παράθυρο
    
    for widget in pie_chart_window.winfo_children(): # για κάθε widget στο παράθυρο
        if isinstance(widget, tk.Frame) and widget not in [options_frame, pie_chart_canvas.get_tk_widget().master]: # αν το widget είναι frame και δεν είναι το options_frame ή το master του canvas
            widget.destroy()
    
    stats_frame = tk.Frame(pie_chart_window, bg=colour1) # δημιουργία frame
    stats_frame.pack(pady=10) # προσθήκη του frame στο παράθυρο
    
    if option == "all": # αν η επιλογή είναι όλα
        prod_df_len = len(pd.read_csv(file_path_prod_comm)) if os.path.exists(file_path_prod_comm) else 0 # ανάγνωση του αρχείου
        serv_df_len = len(pd.read_csv(file_path_serv_comm)) if os.path.exists(file_path_serv_comm) else 0 # ανάγνωση του αρχείου
        total_label = tk.Label(
            stats_frame,
            text=f"Σύνολο αποθηκευμένων σχολίων: {total} (Προϊόντα: {prod_df_len}, Υπηρεσίες: {serv_df_len})", # εμφάνιση του συνόλου των σχολίων
            bg=colour1,
            fg=colour4,
            font=('Century Gothic', 10, 'bold')
        )
    else:
        current_df_len = 0 # αρχικοποίηση της μεταβλητής
        if option == "Products" and os.path.exists(file_path_prod_comm): # αν η επιλογή είναι προϊόντα και υπάρχει το αρχείο
            current_df_len = len(pd.read_csv(file_path_prod_comm)) # ανάγνωση του αρχείου
        elif option == "Services" and os.path.exists(file_path_serv_comm): # αν η επιλογή είναι υπηρεσίες και υπάρχει το αρχείο
            current_df_len = len(pd.read_csv(file_path_serv_comm)) # ανάγνωση του αρχείου
        total_label = tk.Label( # δημιουργία ετικέτας
            stats_frame,
            text=f"Σύνολο αποθηκευμένων σχολίων: {current_df_len}", # Εμφανίζουμε το σύνολο των γραμμών του CSV
            bg=colour1,
            fg=colour4, 
            font=('Century Gothic', 10, 'bold') 
        )
    total_label.pack() # προσθήκη της ετικέτας στο παράθυρο


#####################################################################
#################### ΕΜΦΑΝΙΣΗ ΔΕΔΟΜΕΝΩΝ #############################
#####################################################################

def show_in_treeview(): # εμφάνιση δεδομένων σε treeview
    popup_comments = tk.Toplevel() # δημιουργία νέου παράθυρου
    popup_comments.title('Simple Sentiment - Διαχείριση Σχολίων') # τίτλος
    popup_comments.config(background=colour1) # χρώμα του παράθυρου
    popup_comments.minsize(800, 500) # μέγεθος του παράθυρου
    popup_comments.iconphoto(False, icon) # εικονίδιο του παράθυρου
    
    app_width = 900 # πλάτος του παράθυρου
    app_heigth = 600 # ύψος του παράθυρου
    screen_width = popup_comments.winfo_screenwidth() # πλάτος του οθόνης
    screen_height = popup_comments.winfo_screenheight() # ύψος του οθόνης
    xi = (screen_width / 2) - (app_width / 2) # θέση του παράθυρου στην οθόνη
    yi = (screen_height / 2) - (app_heigth / 2) # θέση του παράθυρου στην οθόνη
    popup_comments.geometry(f'{app_width}x{app_heigth}+{int(xi)}+{int(yi)}') # τοποθέτηση του παράθυρου στην οθόνη

    # Μεταβλητές για την τρέχουσα επιλογή και δεδομένα
    current_data_type = tk.StringVar(value="Products") # αρχική επιλογή: Προϊόντα
    all_data = [] # όλα τα δεδομένα
    filtered_data = [] # φιλτραρισμένα δεδομένα
    
    # Συνάρτηση φόρτωσης δεδομένων
    def load_data(data_type): # φόρτωση δεδομένων, ορίζει το τύπο δεδομένων και φορτώνει τα δεδομένα από το αρχείο csv
        nonlocal all_data, filtered_data # μη τοπικές μεταβλητές , χρησιμοποιούνται για να αποφεύγεται η δημιουργία νέων τοπικών μεταβλητών
        try:
            if data_type == "Products":
                if os.path.exists(file_path_prod_comm): # αν υπάρχει το αρχείο προϊόντων , τότε φορτώνει τα δεδομένα από το αρχείο προϊόντων
                    df = pd.read_csv(file_path_prod_comm) # ανάγνωση του αρχείου προϊόντων , μετατροπή σε λίστα dictionaries
                    all_data = df.to_dict('records') # μετατροπή σε λίστα dictionaries , όλα τα δεδομένα από το αρχείο προϊόντων
                else:
                    all_data = [] # αν δεν υπάρχει το αρχείο προϊόντων , τότε δεν υπάρχουν δεδομένα
            elif data_type == "Services": # αν ο τύπος δεδομένων είναι υπηρεσίες
                if os.path.exists(file_path_serv_comm): # αν υπάρχει το αρχείο υπηρεσιών , τότε φορτώνει τα δεδομένα από το αρχείο υπηρεσιών
                    df = pd.read_csv(file_path_serv_comm) # ανάγνωση του αρχείου υπηρεσιών , μετατροπή σε λίστα dictionaries
                    all_data = df.to_dict('records') # μετατροπή σε λίστα dictionaries , όλα τα δεδομένα από το αρχείο υπηρεσιών
                else:
                    all_data = []
            
            filtered_data = all_data.copy() # αρχικά εμφανίζουμε όλα
            update_treeview() # ενημέρωση του treeview , εμφάνιση των δεδομένων στο treeview
            update_status_label() # ενημέρωση της ετικέτας κατάστασης , εμφάνιση της κατάστασης στην ετικέτα
            
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη φόρτωση δεδομένων: {e}") # εμφάνιση μηνύματος
            all_data = [] # αρχικοποίηση της μεταβλητής
            filtered_data = [] # αρχικοποίηση της μεταβλητής
            update_treeview() # ενημέρωση του treeview , εμφάνιση των δεδομένων στο treeview

    # Συνάρτηση ενημέρωσης του Treeview
    def update_treeview():
        # Καθαρισμός του treeview
        for item in show_tree.get_children(): # για κάθε στοιχείο του treeview
            show_tree.delete(item) # διαγραφή του στοιχείου
        
        # Προσθήκη δεδομένων
        for row in filtered_data:
            values = [row.get('Σχόλια', ''), row.get('Συναίσθημα', ''), row.get('Ποσοστό %', ''), row.get('Ημερομηνία', 'Άγνωστη')]
            show_tree.insert('', 'end', values=values)

    # ΠΡΟΣΘΗΚΗ: Συνάρτηση ενημέρωσης εμφάνισης κουμπιών
    def update_button_states():
        current_type = current_data_type.get()
        
        if current_type == "Products":
            # Ενεργό κουμπί Προϊόντα
            btn_products.config(
                bg=colour3,  # πιο έντονο χρώμα
                fg='white',  # λευκό κείμενο
                relief='sunken',  # φαίνεται πατημένο
                font=('Century Gothic', 10, 'bold')
            )
            # Ανενεργό κουμπί Υπηρεσίες
            btn_services.config(
                bg=colour2,  # κανονικό χρώμα
                fg=colour4,  # κανονικό κείμενο
                relief='raised',  # κανονικό relief
                font=('Century Gothic', 10, 'normal')
            )
        else:  # Services
            # Ανενεργό κουμπί Προϊόντα
            btn_products.config(
                bg=colour2,  # κανονικό χρώμα
                fg=colour4,  # κανονικό κείμενο
                relief='raised',  # κανονικό relief
                font=('Century Gothic', 10, 'normal')
            )
            # Ενεργό κουμπί Υπηρεσίες
            btn_services.config(
                bg=colour3,  # πιο έντονο χρώμα
                fg='white',  # λευκό κείμενο
                relief='sunken',  # φαίνεται πατημένο
                font=('Century Gothic', 10, 'bold')
            )

    # Συνάρτηση αλλαγής τύπου δεδομένων
    def change_data_type(data_type): # αλλαγή τύπου δεδομένων
        current_data_type.set(data_type)
        search_var.set("") # καθαρισμός αναζήτησης
        update_button_states()  # ΠΡΟΣΘΗΚΗ: ενημέρωση εμφάνισης κουμπιών
        load_data(data_type)

    # Συνάρτηση αναζήτησης
    def search_comments(): # αναζήτηση σχολίων
        nonlocal filtered_data
        search_term = search_var.get().strip().lower() # αφαίρεση κενών και μετατροπή σε πεζά
        
        if not search_term:
            filtered_data = all_data.copy() # αν δεν υπάρχει όρος αναζήτησης, εμφάνιση όλων
        else:
            filtered_data = [
                row for row in all_data 
                if search_term in str(row.get('Σχόλια', '')).lower() or 
                   search_term in str(row.get('Συναίσθημα', '')).lower()
            ]
        
        update_treeview()
        update_status_label()

    # Συνάρτηση καθαρισμού αναζήτησης
    def clear_search():
        search_var.set("")
        search_comments()

    # Συνάρτηση διαγραφής σχολίου
    def delete_selected_comment():
        selected_items = show_tree.selection()
        if not selected_items:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε ένα σχόλιο για διαγραφή!")
            return
        
        # Επιβεβαίωση διαγραφής
        confirm = messagebox.askyesno(
            "Επιβεβαίωση Διαγραφής", 
            "Είστε σίγουρος/η ότι θέλετε να διαγράψετε το επιλεγμένο σχόλιο;"
        )
        
        if not confirm:
            return
        
        try:
            # Παίρνουμε τα δεδομένα του επιλεγμένου στοιχείου
            selected_item = selected_items[0] # πρώτο στοιχείο της λίστας
            item_values = show_tree.item(selected_item, 'values') # τιμές του στοιχείου
            comment_to_delete = item_values[0] # το σχόλιο είναι στην πρώτη στήλη
            
            # Διαγραφή από το CSV αρχείο
            data_type = current_data_type.get() # τύπος δεδομένων
            if data_type == "Products": # αν ο τύπος δεδομένων είναι προϊόντα
                file_path = file_path_prod_comm # το αρχείο προϊόντων
            else:
                file_path = file_path_serv_comm # το αρχείο υπηρεσιών
            
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                # Αφαίρεση της γραμμής που περιέχει το συγκεκριμένο σχόλιο
                df = df[df.iloc[:, 0] != comment_to_delete]
                df.to_csv(file_path, index=False)
                
                # Επαναφόρτωση δεδομένων
                load_data(data_type)
                messagebox.showinfo("Επιτυχία", "Το σχόλιο διαγράφηκε επιτυχώς!")
            
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη διαγραφή: {e}")

    # Συνάρτηση ενημέρωσης ετικέτας κατάστασης
    def update_status_label(): # ενημέρωση της ετικέτας κατάστασης
        total_comments = len(all_data) # συνολικά σχόλια
        filtered_comments = len(filtered_data) # φιλτραρισμένα σχόλια
        data_type = current_data_type.get() # τύπος δεδομένων
        
        if total_comments == filtered_comments: # αν τα σχόλια είναι τα ίδια
            status_text = f"Εμφάνιση {total_comments} σχολίων ({data_type})" # εμφάνιση όλων
        else: # αν τα σχόλια δεν είναι τα ίδια
            status_text = f"Εμφάνιση {filtered_comments} από {total_comments} σχολίων ({data_type})" # εμφάνιση των φιλτραρισμένων
        
        status_label.config(text=status_text)

    # === INTERFACE ELEMENTS ===
    
    # Frame για επιλογή τύπου δεδομένων
    type_frame = tk.Frame(popup_comments, bg=colour1) # δημιουργία frame
    type_frame.pack(fill="x", padx=10, pady=5) # προσθήκη του frame στο παράθυρο
    
    tk.Label(type_frame, text="Τύπος Σχολίων:", bg=colour1, fg=colour4,  # ετικέτα τύπου σχολίων
             font=('Century Gothic', 10, 'bold')).pack(side=tk.LEFT, padx=5) # προσθήκη της ετικέτας στο frame
    
    # ΤΡΟΠΟΠΟΙΗΣΗ: Κουμπιά με δυναμική εμφάνιση
    btn_products = tk.Button( # κουμπί προϊόντων
        type_frame,
        text="Προϊόντα",
        bg=colour3,  # αρχικά ενεργό
        fg='white',   # αρχικά ενεργό
        font=('Century Gothic', 10, 'bold'),
        relief='sunken',  # αρχικά ενεργό
        width=12,
        cursor='hand2',
        command=lambda: change_data_type("Products")
    )
    btn_products.pack(side=tk.LEFT, padx=5)
    
    btn_services = tk.Button(
        type_frame,
        text="Υπηρεσίες",
        bg=colour2,  # αρχικά ανενεργό
        fg=colour4,  # αρχικά ανενεργό
        font=('Century Gothic', 10, 'normal'),
        relief='raised',  # αρχικά ανενεργό
        width=12,
        cursor='hand2',
        command=lambda: change_data_type("Services")
    )
    btn_services.pack(side=tk.LEFT, padx=5)

    # Frame για αναζήτηση
    search_frame = tk.Frame(popup_comments, bg=colour1)
    search_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(search_frame, text="Αναζήτηση:", bg=colour1, fg=colour4, 
             font=('Century Gothic', 10, 'bold')).pack(side=tk.LEFT, padx=5)
    
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30, font=('Century Gothic', 10))
    search_entry.pack(side=tk.LEFT, padx=5)
    
    search_button = tk.Button(
        search_frame,
        text="Αναζήτηση",
        bg=colour2,
        fg=colour4,
        font=('Century Gothic', 9, 'bold'),
        cursor='hand2',
        command=search_comments
    )
    search_button.pack(side=tk.LEFT, padx=2)
    
    clear_button = tk.Button( # κουμπί καθαρισμού
        search_frame,
        text="Καθαρισμός",
        bg=colour2,
        fg=colour4,
        font=('Century Gothic', 9, 'bold'),
        cursor='hand2',
        command=clear_search
    )
    clear_button.pack(side=tk.LEFT, padx=2)
    
    # Binding για αναζήτηση καθώς γράφεις
    search_var.trace('w', lambda *args: search_comments())

    # Frame για κουμπιά διαχείρισης
    manage_frame = tk.Frame(popup_comments, bg=colour1) # δημιουργία frame
    manage_frame.pack(fill="x", padx=10, pady=5) # προσθήκη του frame στο παράθυρο
    
    delete_button = tk.Button( # κουμπί διαγραφής
        manage_frame,
        text="Διαγραφή Επιλεγμένου",
        bg='#FF6B6B',  # κόκκινο χρώμα για διαγραφή
        fg='white',
        font=('Century Gothic', 10, 'bold'),
        width=18,
        cursor='hand2',
        command=delete_selected_comment
    )
    delete_button.pack(side=tk.LEFT, padx=5)

    # Frame για το Treeview
    tree_frame = tk.Frame(popup_comments, bg=colour1) # δημιουργία frame
    tree_frame.pack(fill="both", expand=True, padx=10, pady=5) # προσθήκη του frame στο παράθυρο
    
    # Δημιουργία του Treeview
    columns = ('Σχόλια', 'Συναίσθημα', 'Ποσοστό %', 'Ημερομηνία') # στήλες
    show_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Treeview', cursor='hand2') # δημιουργία του Treeview
    show_tree.heading('Ημερομηνία', text='Ημερομηνία') # κεφαλίδα της στήλης ημερομηνία
    show_tree.column('Ημερομηνία', width=150, minwidth=150)    
    # Ορισμός κεφαλίδων των στηλών
    show_tree.heading('Σχόλια', text='Σχόλια') # κεφαλίδα της στήλης σχόλια
    show_tree.heading('Συναίσθημα', text='Συναίσθημα') # κεφαλίδα της στήλης συναίσθημα
    show_tree.heading('Ποσοστό %', text='Ποσοστό %') # κεφαλίδα της στήλης ποσοστό %
    
    # Ορισμός πλάτους στηλών
    show_tree.column('Σχόλια', width=500, minwidth=300) # πλάτος της στήλης σχόλια
    show_tree.column('Συναίσθημα', width=120, minwidth=100) # πλάτος της στήλης συναίσθημα
    show_tree.column('Ποσοστό %', width=100, minwidth=80) # πλάτος της στήλης ποσοστό %
    
    # Scrollbar για το Treeview
    scrollbar_tree = tk.Scrollbar(tree_frame, orient="vertical", command=show_tree.yview) # δημιουργία του scrollbar
    show_tree.configure(yscrollcommand=scrollbar_tree.set) # συνδέσιμο του scrollbar με το Treeview
    
    # Pack του Treeview και Scrollbar
    show_tree.pack(side="left", fill="both", expand=True)
    scrollbar_tree.pack(side="right", fill="y")

    # Στυλ για το Treeview
    style = ttk.Style()
    style.theme_use('default')
    style.configure('Treeview',
                    background=colour1,
                    foreground=colour4,
                    fieldbackground=colour1,
                    rowheight=35,
                    font=('Century Gothic', 10))
    style.map('Treeview', background=[('selected', colour2)])
    style.configure('Treeview.Heading',
                    background=colour3,
                    foreground=colour4,
                    font=('Century Gothic', 11, 'bold'))

    # Ετικέτα κατάστασης
    status_label = tk.Label( 
        popup_comments,
        text="",
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 9, 'bold')
    )
    status_label.pack(side="bottom", fill="x", padx=10, pady=5)

    # Αρχική φόρτωση δεδομένων (Προϊόντα) και ενημέρωση κουμπιών
    load_data("Products") # φόρτωση των δεδομένων (προϊόντα)
    # update_button_states() # Δεν χρειάζεται γιατί τα κουμπιά έχουν ήδη τη σωστή αρχική εμφάνιση


    ###  ΤΕΛΟΣ TREEVIEW  ####
##################################################################### 

def show_data(): # συνάρτηση που εμφανίζει τα σχόλια
    def show_choice(comments_type): # συνάρτηση που εμφανίζει τα σχόλια
        count = 1
        
        try:
            data_area.config(state="normal") # επιτρέπει την επεξεργασία του πεδίου
            data_area.delete(1.0, tk.END) # καθαρισμός του πεδίου
            
            if comments_type == "Products":
                file_path = file_path_prod_comm
                btn_products.config(bg=colour3, relief="sunken") # αλλαγή χρώματος του κουμπιού προϊόντων
                btn_services.config(bg=colour2, relief="raised") # αλλαγή χρώματος του κουμπιού υπηρεσιών
            else:  # Services
                file_path = file_path_serv_comm
                btn_services.config(bg=colour3, relief="sunken")
                btn_products.config(bg=colour2, relief="raised")
            
            # ΔΙΟΡΘΩΣΗ: Έλεγχος πόσες στήλες υπάρχουν
            if os.path.exists(file_path): # αν υπάρχει το αρχείο
                df_temp = pd.read_csv(file_path) # ανάγνωση του αρχείου
                if len(df_temp.columns) >= 4: # αν υπάρχουν τουλάχιστον 4 στήλες
                    df = pd.read_csv(file_path, usecols=[0,1,2,3])  # Με ημερομηνία
                else:
                    df = pd.read_csv(file_path, usecols=[0,1,2])    # Χωρίς ημερομηνία
                    
                dimiourgia_sunolon(df) # υπολογισμός των συνολικών σχολίων και των ποσοστών τους
                
                for index, rows in df.iterrows(): # για κάθε γραμμή του πίνακα
                    # Εμφάνιση με ημερομηνία αν υπάρχει 4η στήλη
                    if len(rows) >= 4 and pd.notna(rows.iloc[3]): # αν υπάρχει 4η στήλη και δεν είναι κενή
                        data_area.insert("end", f'{count}. {rows.iloc[0]} \n' # εμφάνιση της ημερομηνίας
                                               f'   📅 {rows.iloc[3]} \n' # εμφάνιση της ημερομηνίας
                                               f'   ---{rows.iloc[1]}--- \t {rows.iloc[2]:.2f}% \n' # εμφάνιση του συναίσθημα και του ποσοστού
                                               f'   {"="*50} \n\n') # εμφάνιση της γραμμής διαχωρισμού
                    else:
                        data_area.insert("end", f'{count}. {rows.iloc[0]} \n' # εμφάνιση του σχολίου
                                               f'   ---{rows.iloc[1]}--- \t {rows.iloc[2]:.2f}% \n' # εμφάνιση του συναίσθημα και του ποσοστού
                                               f'   {"="*50} \n\n') # εμφάνιση της γραμμής διαχωρισμού
                    count += 1
            else:
                data_area.insert("end", f"❌ Το αρχείο {comments_type.lower()} δεν βρέθηκε.")
                
            data_area.config(state="disabled") # απενεργοποίηση του πεδίου, για να μην μπορεί να επεξεργαστεί
            
        except Exception as e:
            data_area.config(state="normal") # επιτρέπει την επεξεργασία του πεδίου
            data_area.delete(1.0, tk.END) # καθαρισμός του πεδίου
            data_area.insert("end", f"❌ Σφάλμα: {str(e)}") # εμφάνιση του σφάλματος
            data_area.config(state="disabled") # απενεργοποίηση του πεδίου, για να μην μπορεί να επεξεργαστεί
    
    def dimiourgia_sunolon(df): # συνάρτηση που υπολογίζει τα συνολικά σχόλια και τα ποσοστά τους
        total_comments = len(df) # υπολογισμός του συνολικού αριθμού των σχολίων
        pos_count = sum(df.iloc[:, 1] == 'Θετικό') # υπολογισμός του αριθμού των θετικών σχολίων
        neg_count = sum(df.iloc[:, 1] == 'Αρνητικό') # υπολογισμός του αριθμού των αρνητικών σχολίων
        neu_count = sum(df.iloc[:, 1] == 'Ουδέτερο') # υπολογισμός του αριθμού των ουδέτερων σχολίων

        pos_percent = (pos_count / total_comments) * 100 if total_comments > 0 else 0 # υπολογισμός του ποσοστού των θετικών σχολίων
        neg_percent = (neg_count / total_comments) * 100 if total_comments > 0 else 0 # υπολογισμός του ποσοστού των αρνητικών σχολίων
        neu_percent = (neu_count / total_comments) * 100 if total_comments > 0 else 0 # υπολογισμός του ποσοστού των ουδέτερων σχολίων

        total_positive_label.config(text=f"Θετικά: {pos_count} ({pos_percent:.2f}%)") # ενημέρωση του πεδίου total_positive_label   
        total_negative_label.config(text=f"Αρνητικά: {neg_count} ({neg_percent:.2f}%)") # ενημέρωση του πεδίου total_negative_label
        total_neutral_label.config(text=f"Ουδέτερα: {neu_count} ({neu_percent:.2f}%)") # ενημέρωση του πεδίου total_neutral_label

    popup_data = tk.Toplevel() # δημιουργία νέου παράθυρου
    popup_data.title('Simple Sentiment - Λίστα σχολίων') # τίτλος
    popup_data.config(background=colour1) # χρώμα του παράθυρου
    popup_data.rowconfigure(0, weight=0) # ρύθμιση του πλάτους του παράθυρου
    icon = PhotoImage(file=app_icon1_path) # εικονίδιο του παράθυρου
    popup_data.iconphoto(False, icon) # εικονίδιο του παράθυρου
    app_width = 700 # πλάτος του παράθυρου
    app_heigth = 600 # ύψος του παράθυρου
    screen_width = popup_data.winfo_screenwidth() # πλάτος του οθόνης
    screen_height = popup_data.winfo_screenheight() # ύψος του οθόνης
    # print(screen_width, screen_height)
    xi = (screen_width / 2) - (app_width / 2) # θέση του παράθυρου στην οθόνη
    yi = (screen_height / 2) - (app_heigth / 2) # θέση του παράθυρου στην οθόνη
    popup_data.geometry(f'{app_width}x{app_heigth}+{int(xi)}+{int(yi)}') # τοποθέτηση του παράθυρου στην οθόνη

    # Μήνυμα ενημέρωσης στο επάνω μέρος
    info_label = tk.Label( # ετικέτα για το μήνυμα ενημέρωσης
        popup_data, 
        text="📊 Προβολή Αποθηκευμένων Σχολίων - Επιλέξτε κατηγορία:", # μήνυμα ενημέρωσης
        bg=colour1, 
        fg=colour4, 
        font=('Century Gothic', 11, 'bold')
    )
    info_label.pack(pady=(10, 5))

    btn_fr = tk.Frame(popup_data, bg=colour1) # frame για τα κουμπιά
    btn_products = tk.Button(
        btn_fr, # frame για τα κουμπιά
        background=colour2, # χρώμα του κουμπιού
        foreground=colour4, # χρώμα του κουμπιού
        activebackground=colour3, # χρώμα του κουμπιού
        activeforeground=colour4, # χρώμα του κουμπιού
        highlightthickness=2, # πάχος του χρώματος του κουμπιού
        highlightbackground=colour2, # χρώμα του χρώματος του κουμπιού
        highlightcolor='WHITE',
        border=0,
        width=14,
        cursor='hand2',
        text= 'Προϊόντα',
        font=('Century Gothic', 10, 'bold'),
        state='normal',
        command=lambda:show_choice('Products')
        )
    btn_services = tk.Button( 
        btn_fr,
        background=colour2,
        foreground=colour4,
        activebackground=colour3,
        activeforeground=colour4,
        highlightthickness=2,
        highlightbackground=colour2,
        highlightcolor='WHITE',
        border=0,
        width=14,
        cursor='hand2',
        text= 'Υπηρεσίες',
        font=('Century Gothic', 10, 'bold'),
        command=lambda:show_choice('Services')
        )
    
    btn_fr.pack(pady=5)
    btn_products.grid(row= 0, column= 0, padx= 5,)
    btn_services.grid(row= 0, column= 1, padx= 5,)

    # === Σταθερό πλαίσιο με αυτόματη αλλαγή γραμμής και scrollbar ===
    text_frame = tk.Frame(popup_data, bg=colour1)
    text_frame.pack(fill="both", expand=1, padx=10, pady=5)

    data_area = tk.Text( # πεδίο για το κείμενο
        text_frame,
        wrap="word",         # Αυτόματη αλλαγή γραμμής σε λέξη
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 10),
        width=80,            # Σταθερό πλάτος (σε χαρακτήρες)
        height=20,           # Σταθερό ύψος (σε γραμμές)
        state="disabled",    # Μόνο για ανάγνωση
        cursor="arrow"       # Αλλαγή cursor για να δείχνει ότι δεν είναι επεξεργάσιμο
    )
    data_area.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(text_frame, command=data_area.yview) # scrollbar για την κύλιση του κειμένου , 
    scrollbar.pack(side="right", fill="y") # τοποθέτηση του scrollbar στη δεξιά πλευρά του πεδίου
    data_area.config(yscrollcommand=scrollbar.set) # ορίζει την κύλιση του πεδίου

    # Αυτόματη φόρτωση δεδομένων κατά την εκκίνηση
    data_area.config(state="normal") # επιτρέπει την επεξεργασία του πεδίου
    data_area.insert("1.0", "🔄 Φόρτωση δεδομένων... Επιλέξτε μια κατηγορία για προβολή.") # εμφάνιση του μηνύματος ενημέρωσης
    data_area.config(state="disabled") # απενεργοποίηση του πεδίου, για να μην μπορεί να επεξεργαστεί

    # Binding για copy μόνο
    data_area.bind("<Control-c>", lambda e: data_area.event_generate("<<Copy>>"))  # συνάρτηση για το Copy

    # Frame για τα στατιστικά
    sunola_fr = tk.Frame(popup_data, bg=colour1) # frame για τα πεδία των σχολίων
    sunola_fr.pack(fill="x", pady=10, padx=10)

    total_positive_label = tk.Label(sunola_fr, text="Θετικά: 0 (0%)", bg=colour1, fg=colour4, font=('Century Gothic', 10, 'bold')) # πεδίο για το ποσοστό των θετικών σχολίων
    total_negative_label = tk.Label(sunola_fr, text="Αρνητικά: 0 (0%)", bg=colour1, fg=colour4, font=('Century Gothic', 10, 'bold')) # πεδίο για το ποσοστό των αρνητικών σχολίων   
    total_neutral_label = tk.Label(sunola_fr, text="Ουδέτερα: 0 (0%)", bg=colour1, fg=colour4, font=('Century Gothic', 10, 'bold')) # πεδίο για το ποσοστό των ουδέτερων σχολίων

    total_positive_label.grid(row=0, column=0, padx=10) # τοποθέτηση του πεδίου total_positive_label
    total_negative_label.grid(row=0, column=1, padx=10) # τοποθέτηση του πεδίου total_negative_label
    total_neutral_label.grid(row=0, column=2, padx=10) # τοποθέτηση του πεδίου total_neutral_label

#####################################################################
##################################################################### 

    
#####################################################################
########################### EVENTS ##################################
#####################################################################
def on_focus_in(event): # συνάρτηση για το focus , οι λίστες λέξεων
    """Συνάρτηση για το focus - διορθωμένη"""
    current_text = comment_text.get(1.0, tk.END).strip() # ανάγνωση του πεδίου , 
    if current_text == 'Γράψτε εδώ το σχόλιό σας!' or current_text == '': # αν το πεδίο είναι κενό
        comment_text.delete(1.0, tk.END) # καθαρισμός του πεδίου
        comment_text.config(fg=colour4, font=('Century Gothic', 12))  # Επαναφορά κανονικού στυλ

def on_first_key(event): # συνάρτηση για το πρώτο πάτημα πλήκτρου
    """Καλείται στο πρώτο πάτημα πλήκτρου"""
    current_text = comment_text.get(1.0, tk.END).strip() # ανάγνωση του πεδίου , 
    if current_text == 'Γράψτε εδώ το σχόλιό σας!': # αν το πεδίο είναι κενό
        if event.keysym not in ['Return', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R']:
            comment_text.delete(1.0, tk.END)
            comment_text.config(fg=colour4, font=('Century Gothic', 12))


############### Εντολές Cut, Copy, Paste, Delete ####################
def cut_text(e): # συνάρτηση για το Cut 
    global selected # global variable για το selected
    if e: # αν το πάτημα πλήκτρου είναι true
        selected = root.clipboard_get() # ανάγνωση του πεδίου
    else: # αν το πάτημα πλήκτρου δεν είναι true
        if comment_text.selection_get():
            selected = comment_text.selection_get()
            comment_text.delete('sel.first', 'sel.last')
            root.clipboard_clear()
            root.clipboard_append(selected) # προσθήκη του selected στο πεδίο

def copy_text(e): # συνάρτηση για το Copy
    global selected # global variable για το selected
    if e:
        selected = root.clipboard_get()
    
    if comment_text.selection_get():
        selected = comment_text.selection_get()
        root.clipboard_clear()
        root.clipboard_append(selected)      

def paste_text(e): # συνάρτηση για το Paste
    global selected # global variable για το selected
    # if e:
    #     selected = root.clipboard_get()
    # else:
    try:
        clipboard_text  =root.clipboard_get()
        comment_text.insert(tk.END, clipboard_text)
    except tk.TclError:
        comment_text.delete(1.0, tk.END)
        comment_text.insert(tk.END, "")
    # if selected:
    #     position = comment_text.index('insert')
    #     comment_text.insert(position, selected)

def delete_text(): # συνάρτηση για το Delete
    global msg_diadikasia # global variable για το msg_diadikasia
    comment_text.delete(1.0, tk.END) # καθαρισμός του πεδίου
    comment_text.config(fg=colour4) # επαναφορά του χρώματος του πεδίου
    msg_diadikasia.set('') # καθαρισμός του πεδίου
#####################################################################
def exit_program():
    root.destroy()
#####################################################################


#####################################################################
######################### ΚΥΡΙΟ ΠΑΡΑΘΥΡΟ ############################
#####################################################################
root = tk.Tk()                                                      #
root.title('Simple Sentiment')                                      #
icon = PhotoImage(file=app_icon1_path)                              #
root.iconphoto(False, icon) 

# ΕΝΤΟΛΕΣ STRINGVAR() - ΠΡΕΠΕΙ ΝΑ ΕΙΝΑΙ ΜΕΤΑ ΤΟ root = tk.Tk()
comment_type = tk.StringVar()
comment_type.set('Products')
msg_diadikasia = tk.StringVar()
instant_score = tk.StringVar() 
instant_score_str = tk.StringVar()

###############################                                        
root.minsize(500,400)                                               #
root.configure(bg=colour1)                                          #
# root.grid_rowconfigure(0, weight=1)                               #
# root.grid_columnconfigure(1, weight=1)                            #
focus_set_action = root.focus_set()                                 #
                                                                    #
app_width = 500                                                     #
app_heigth = 400                                                    #
screen_width = root.winfo_screenwidth()                             #
screen_height = root.winfo_screenheight()                           #
xi = (screen_width / 2) - (app_width / 2)                           #
yi = (screen_height / 2) - (app_heigth / 2)                         #
root.geometry(f'{app_width}x{app_heigth}+{int(xi)}+{int(yi)}')      #
#####################################################################
#####################################################################

# ΕΝΤΟΛΕΣ STRINGVAR()
msg_diadikasia = tk.StringVar() # μεταβλητή για το πεδίο των σχολίων
instant_score = tk.StringVar() # μεταβλητή για το πεδίο του σκορ
instant_score_str = tk.StringVar() # μεταβλητή για το πεδίο του σκορ


####################################################################
####################################################################

def export_comments_to_csv(): # Εξαγωγή σχολίων σε CSV
    # Επιλογή τύπου σχολίων 
    export_type = tk.simpledialog.askstring("Εξαγωγή", "Εξαγωγή σχολίων για: Products ή Services;") # επιλογή τύπου σχολίων
    if not export_type or export_type.lower() not in ["products", "services"]: # αν δεν δόθηκε σωστή επιλογή
        messagebox.showinfo("Εξαγωγή", "Η εξαγωγή ακυρώθηκε ή δεν δόθηκε σωστή επιλογή.") # εμφάνιση μηνύματος
        return

    if export_type.lower() == "products": # Επιλογή προϊόντων
        file_path = file_path_prod_comm
        default_name = "product_comments_export.csv" # ονομασία του αρχείου
    else:
        file_path = file_path_serv_comm
        default_name = "service_comments_export.csv" # ονομασία του αρχείου

    if not os.path.exists(file_path): # Αρχείο δεν υπάρχει
        messagebox.showwarning("Εξαγωγή", "Δεν υπάρχουν σχόλια για εξαγωγή.") # εμφάνιση μηνύματος  
        return

    df = pd.read_csv(file_path) #   Διαβάζουμε το αρχείο CSV
    export_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile=default_name,
        filetypes=(("CSV files", "*.csv"), ("All Files", "*.*")) # τύποι αρχείων
    )
    if export_path: # Αν ο χρήστης επιλέξει διαδρομή
        df.to_csv(export_path, index=False, encoding='utf-8-sig')
        messagebox.showinfo("Εξαγωγή", f"Η εξαγωγή ολοκληρώθηκε:\n{export_path}") # εμφάνιση μηνύματος


#####################################################################
######################### ΕΙΚΟΝΙΔΙΑ MENU ############################
menu_fr = tk.Menu(root, bg=colour1) # menu frame
root.config(menu=menu_fr, background=colour1) # config του menu frame
file_menu = tk.Menu(menu_fr, tearoff=0) # menu file
edit_menu = tk.Menu(menu_fr, tearoff=0) # menu edit
show_menu = tk.Menu(menu_fr, tearoff=0) # menu show
exit_menu = tk.Menu(menu_fr, tearoff=0) # menu exit

menu_fr.add_cascade(menu=file_menu, label= 'Αρχείο') # add cascade menu file
#file_menu.add_command(label='Άνοιγμα', command=lambda: file_open_dialog()) # add command menu file
#file_menu.add_command(label='Αποθήκευση', command=lambda: file_save()) # add command menu file
#file_menu.add_command(label='Αποθήκευση ως...', command=lambda: file_save_as()) # add command menu file
#file_menu.add_separator() # add separator menu file
#file_menu.add_command(label='Εκτύπωση', command=lambda: file_print()) # add command menu file
#file_menu.add_separator() # add separator menu file
file_menu.add_command(label='Εξαγωγή σχολίων σε CSV', command=export_comments_to_csv) # add command menu file
file_menu.add_command(label='Κλείσιμο', command=exit_program) # add command menu file

menu_fr.add_cascade(menu=edit_menu, label= 'Επεξεργασία')
#edit_menu.add_command(label='Αποκοπή', command=lambda: cut_text(False)) 
#edit_menu.add_command(label='Αντιγραφή', command=lambda: copy_text(False))
#edit_menu.add_command(label='Επικόλληση', command=lambda: paste_text(False))
#edit_menu.add_command(label='Διαγραφή', command=lambda: delete_text(False))
edit_menu.add_command(label='Επεξεργασία λεξικού συναισθημάτων', command=lambda: edit_word_lists()) # προσθήκη εντολής για την επεξεργασία λιστών λέξεων

menu_fr.add_cascade(menu=show_menu, label= 'Προβολή')
show_menu.add_command(label='Προβολή σχολίων', command= show_in_treeview)

 
def show_help(): # συνάρτηση για την επικοινωνία
    messagebox.showinfo(
        "Επικοινωνία",
        "Για απορίες ή βοήθεια επικοινωνήστε με την ομάδα των:\n\n"
        "Χατζούλης Ιωάννης\n"
        "Θεοφυλάκτου Βασίλης\n"
        "Ξάφης Δημήτριος"
    )

def show_version(): # συνάρτηση για την έκδοση
    messagebox.showinfo(
        "Έκδοση λογισμικού",
        "Αυτή είναι η έκδοση 1.0 του λογισμικού Simple Sentiment.\n\n"
        "Δημιουργήθηκε από την ομάδα μας για ανάλυση συναισθήματος σχολίων."

    )

def clear_history(): # Διαγραφή ιστορικού
    ############# ΔΙΑΓΡΑΦΗ ΙΣΤΟΡΙΚΟΥ ΚΑΙ ΑΡΧΕΙΩΝ ΣΧΟΛΙΩΝ ################
    
    # Μήνυμα επιβεβαίωσης
    confirm = messagebox.askyesno(
        "Επιβεβαίωση Διαγραφής", 
        "Είστε σίγουρος/η ότι θέλετε να διαγράψετε όλο το ιστορικό και τα αποθηκευμένα σχόλια;\n\n"
        "Αυτή η ενέργεια δεν μπορεί να αναιρεθεί!",
        icon='warning'
    )
    
    # Αν ο χρήστης επιλέξει "Όχι", τερματίζουμε τη συνάρτηση
    if not confirm:
        messagebox.showinfo("Ακύρωση", "Η διαγραφή ιστορικού ακυρώθηκε.")
        return
    
    # Αν ο χρήστης επιλέξει "Ναι", συνεχίζουμε με τη διαγραφή
    try:
        global history, pie_chart_canvas, pie_chart_window
        
        # Καθαρισμός ιστορικού στη μνήμη
        history.clear()
        
        # Διαγραφή περιεχομένου αρχείων προϊόντων και υπηρεσιών
        open(file_path_prod_comm, 'w', encoding='utf-8').write('Σχόλια,Συναίσθημα,Ποσοστό %,Ημερομηνία\n')
        open(file_path_serv_comm, 'w', encoding='utf-8').write('Σχόλια,Συναίσθημα,Ποσοστό %,Ημερομηνία\n')
        
        # Καθαρισμός διαγραμμάτων αν υπάρχουν
        if pie_chart_canvas:
            pie_chart_canvas.get_tk_widget().destroy()
            pie_chart_canvas = None
        if pie_chart_window:
            pie_chart_window.destroy()
            pie_chart_window = None
        
        # Μήνυμα επιτυχούς διαγραφής
        messagebox.showinfo(
            "Επιτυχής Διαγραφή", 
            "Το ιστορικό και όλα τα αποθηκευμένα σχόλια διαγράφηκαν επιτυχώς!"
        )
        
    except Exception as e:
        messagebox.showerror(
            "Σφάλμα Διαγραφής", 
            f"Προέκυψε σφάλμα κατά τη διαγραφή του ιστορικού:\n{str(e)}"
        )


def edit_word_lists(): # Επεξεργασία λιστών λέξεων
    edit_window = tk.Toplevel(root) # δημιουργία νέου παραθύρου
    edit_window.title("Επεξεργασία Λεξικού Συναισθημάτων") # τίτλος παραθύρου
    edit_window.geometry("900x700") # μέγεθος παραθύρου
    edit_window.config(background=colour1) # χρώμα παραθύρου
    
    # Προσθήκη εικονιδίου στο παράθυρο (αν υπάρχει)
    try:
        edit_window.iconphoto(False, icon) 
        # edit_window.iconbitmap(default=app_icon1_path) # προσθήκη εικονιδίου στο παράθυρο
    except:
        pass  # Αγνοούμε αν δεν υπάρχει το εικονίδιο
    
    # Κεντράρισμα παραθύρου
    edit_window.update_idletasks() # ενημέρωση του παραθύρου
    width = edit_window.winfo_width() # πλάτος παραθύρου
    height = edit_window.winfo_height() # ύψος παραθύρου
    x = (edit_window.winfo_screenwidth() // 2) - (width // 2) # x συντεταγμένη παραθύρου
    y = (edit_window.winfo_screenheight() // 2) - (height // 2)
    edit_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Προσθήκη τίτλου
    title_frame = tk.Frame(edit_window, bg=colour1, height=60) # δημιουργία τίτλου
    title_frame.pack(fill="x") # προσθήκη τίτλου
    title_frame.pack_propagate(False) # απόκρυψη του προσαρμοσμένου μεγέθους
    
    title_label = tk.Label( # δημιουργία τίτλου , 
        title_frame,
        text="Διαχείριση Λεξικού Συναισθημάτων",
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 16, 'bold')
    )
    title_label.pack(expand=True)
    
    # Δημιουργία καρτελών με βελτιωμένο στυλ
    style = ttk.Style()
    style.theme_use('clam') # χρήση του στυλ clam
    style.configure('TNotebook', background=colour1, borderwidth=0) # χρώμα παραθύρου και απόσταση από τα όρια
    style.configure('TNotebook.Tab', 
                   background=colour2,
                   foreground=colour4,
                   font=('Century Gothic', 10))
    style.map('TNotebook.Tab',
              background=[('selected', colour3)],
              foreground=[('selected', 'white')])
    
    tab_control = ttk.Notebook(edit_window)
    
    # ΔΗΜΙΟΥΡΓΙΑ ΚΑΡΤΕΛΩΝ ΠΡΩΤΑ
    # Καρτέλα για θετικές λέξεις
    tab_positive = tk.Frame(tab_control, bg=colour1) # δημιουργία της καρτέλας για τις θετικές λέξεις , 
    tab_control.add(tab_positive, text="Θετικές Λέξεις") # προσθήκη της καρτέλας στο tab_control
    
    # Καρτέλα για αρνητικές λέξεις
    tab_negative = tk.Frame(tab_control, bg=colour1) # δημιουργία της καρτέλας για τις αρνητικές λέξεις , 
    tab_control.add(tab_negative, text="Αρνητικές Λέξεις") # προσθήκη της καρτέλας στο tab_control
    
    # Καρτέλα για stop words
    tab_stopwords = tk.Frame(tab_control, bg=colour1) # δημιουργία της καρτέλας για τις λέξεις διακοπής , 
    tab_control.add(tab_stopwords, text="Λέξεις Διακοπής") # προσθήκη της καρτέλας στο tab_control
    
    # Καρτέλα για ακριβείς φράσεις
    tab_phrases = tk.Frame(tab_control, bg=colour1) # δημιουργία της καρτέλας για τις ακριβείς φράσεις , 
    tab_control.add(tab_phrases, text="Εκφράσεις και Συμφραζόμενα") # προσθήκη της καρτέλας στο tab_control
    
    tab_control.pack(expand=1, fill="both") # προσθήκη της καρτέλας στο tab_control , 

    # Μεταβλητές για την επιλογή γραμμών
    selected_line_positive = [None] # μεταβλητές για την επιλογή γραμμών
    selected_line_negative = [None] 
    selected_line_stopwords = [None]
    selected_line_phrases = [None]

    # Συναρτήσεις εξαγωγής/εισαγωγής
    def export_words(text_widget, list_name): # συνάρτηση για την εξαγωγή λέξεων , 
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt", # επέκταση αρχείου
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")], # τύποι αρχείων
            title=f"Εξαγωγή {list_name}" # τίτλος παραθύρου
        )
        if filename:
            try:
                text_widget.config(state='normal') # ενεργοποίηση του text widget
                content = text_widget.get(1.0, tk.END) # ανάγνωση του πεδίου
                text_widget.config(state='disabled') # απενεργοποίηση του text widget
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Επιτυχία", f"Οι λέξεις εξήχθησαν στο {filename}") # εμφάνιση μηνύματος επιτυχίας
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Σφάλμα εξαγωγής: {str(e)}") # εμφάνιση μηνύματος σφάλματος
    
    def import_words(text_widget, stats_label=None): # συνάρτηση για την εισαγωγή λέξεων ,  
        filename = filedialog.askopenfilename( # ανάγνωση του αρχείου
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")], # τύποι αρχείων
            title="Εισαγωγή λέξεων" # τίτλος παραθύρου
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f: # ανάγνωση του αρχείου
                    content = f.read()
                
                # Επιβεβαίωση
                if messagebox.askyesno("Επιβεβαίωση", "Θέλετε να αντικαταστήσετε τις υπάρχουσες λέξεις;"): # επιβεβαίωση για την αντικατάσταση των λέξεων
                    text_widget.config(state='normal') # ενεργοποίηση του text widget
                    text_widget.delete(1.0, tk.END) # καθαρισμός του πεδίου
                    text_widget.insert(1.0, content)
                    text_widget.config(state='disabled')
                    
                    # Ενημέρωση στατιστικών αν υπάρχει stats_label
                    if stats_label:
                        new_count = len([line.strip() for line in content.split('\n') if line.strip()]) # υπολογισμός του αριθμού των λέξεων
                        stats_label.config(text=f"Σύνολο λέξεων: {new_count}") # ενημέρωση του στατιστικού
                    
                    messagebox.showinfo("Επιτυχία", "Οι λέξεις εισήχθησαν επιτυχώς") # εμφάνιση μηνύματος επιτυχίας
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Σφάλμα εισαγωγής: {str(e)}") # εμφάνιση μηνύματος σφάλματος

    # Λειτουργία για επιλογή γραμμής με visual feedback
    def select_line(text_widget, event, selected_line_var): # συνάρτηση για την επιλογή γραμμής με visual feedback
        # Ενεργοποιούμε προσωρινά το text widget
        text_widget.config(state=tk.NORMAL) # ενεργοποίηση του text widget
        
        # Καθαρίζουμε προηγούμενη επιλογή
        text_widget.tag_remove("selected", "1.0", tk.END)
        
        # Βρίσκουμε τη γραμμή που κλικάρισε ο χρήστης
        index = text_widget.index(f"@{event.x},{event.y}") # υπολογισμός της γραμμής που κλικάρισε ο χρήστης
        line_start = text_widget.index(f"{index} linestart") # υπολογισμός της αρχής της γραμμής
        line_end = text_widget.index(f"{index} lineend") # υπολογισμός της λήξης της γραμμής
        
        # Επιλέγουμε τη γραμμή με χρώμα
        text_widget.tag_add("selected", line_start, line_end) # προσθήκη του χρώματος στη γραμμή
        text_widget.tag_config("selected", background="#4A90E2", foreground="white") # χρώμα της γραμμής
        
        # Αποθηκεύουμε την επιλεγμένη γραμμή
        selected_line_var[0] = (line_start, line_end) # αποθήκευση της επιλεγμένης γραμμής
        
        # Τοποθετούμε τον cursor στη γραμμή
        text_widget.mark_set("insert", line_start) # τοποθέτηση του cursor στη γραμμή
        
        # Απενεργοποιούμε ξανά το text widget
        text_widget.config(state=tk.DISABLED) # απενεργοποίηση του text widget
    
    # Λειτουργία για αποθήκευση λέξεων από text area
    def save_words_from_text(text_widget, file_path, list_var, stats_label=None): # συνάρτηση για την αποθήκευση λέξεων από text area
        global thetikes_lekseis, arnitikes_lekseis, stopwords_lekseis
        text_widget.config(state=tk.NORMAL) # ενεργοποίηση του text widget
        words = [line.strip() for line in text_widget.get(1.0, tk.END).split('\n') if line.strip()]
        text_widget.config(state=tk.DISABLED) # απενεργοποίηση του text widget, έτσι ώστε να μην μπορεί να επεξεργαστεί ο χρήστης
        
        with open(file_path, 'w', encoding='utf-8') as file:
            for word in words:
                file.write(word + '\n')
                
        thetikes_lekseis = load_words_from_file(thetikes_file, default_thetikes) # φόρτωση των λέξεων από το αρχείο
        arnitikes_lekseis = load_words_from_file(arnitikes_file, default_arnitikes) # φόρτωση των λέξεων από το αρχείο
        stopwords_lekseis = load_words_from_file(stopwords_file, default_stopwords) # φόρτωση των λέξεων από το αρχείο

        # Ενημέρωση στατιστικών
        if stats_label:
            stats_label.config(text=f"Σύνολο λέξεων: {len(words)}") # ενημέρωση του στατιστικού
 
        messagebox.showinfo("Αποθήκευση", "Οι λέξεις αποθηκεύτηκαν επιτυχώς!") # εμφάνιση μηνύματος επιτυχίας
    
    # Λειτουργία αναζήτησης λέξεων με βελτιωμένη λειτουργικότητα
    def search_words(search_term, text_widget, word_list, stats_label=None, selected_line_var=None): # συνάρτηση για την αναζήτηση λέξεων με βελτιωμένη λειτουργικότητα
        if not search_term:
            load_words_to_text(text_widget, word_list, stats_label, selected_line_var)
            return
        
        search_term_no_accent = afairesi_tou_tonou(search_term.lower()) # αφαίρεση των τονών
        
        filtered_words = [] # λίστα για τις λέξεις που βρίσκονται στη λίστα των λέξεων
        for word in word_list:
            word_no_accent = afairesi_tou_tonou(word.lower()) # αφαίρεση των τονών
            if search_term_no_accent in word_no_accent: # αναζήτηση της λέξης στη λίστα των λέξεων
                filtered_words.append(word) # προσθήκη της λέξης στη λίστα των λέξεων
        
        text_widget.config(state=tk.NORMAL) # ενεργοποίηση του text widget
        text_widget.delete(1.0, tk.END) # καθαρισμός του πεδίου
        for word in filtered_words:
            text_widget.insert(tk.END, word + '\n') # εισαγωγή των λέξεων στο text widget
        
        # Καθαρισμός επιλογής
        if selected_line_var: 
            selected_line_var[0] = None # απενεργοποίηση της επιλογής
        text_widget.tag_remove("selected", "1.0", tk.END) # καθαρισμός της επιλογής
        
        text_widget.config(state=tk.DISABLED) # απενεργοποίηση του text widget, έτσι ώστε να μην μπορεί να επεξεργαστεί ο χρήστης
        
        if stats_label:
            stats_label.config(text=f"Βρέθηκαν: {len(filtered_words)} από {len(word_list)} λέξεις") # ενημέρωση του στατιστικού

    # Λειτουργία γρήγορης προσθήκης λέξης
    def add_word(entry_widget, text_widget, stats_label=None):
        word = entry_widget.get().strip() # αφαίρεση των κενών
        if word:
            text_widget.config(state=tk.NORMAL) # ενεργοποίηση του text widget
            current_text = text_widget.get(1.0, tk.END) # ανάγνωση του πεδίου
            if word + '\n' not in current_text: # αν η λέξη δεν υπάρχει στο πεδίο
                text_widget.insert(tk.END, word + '\n') # εισαγωγή της λέξης στο πεδίο
                # Ενημέρωση στατιστικών
                if stats_label:
                    current_count = len([line.strip() for line in current_text.split('\n') if line.strip()])
                    stats_label.config(text=f"Σύνολο λέξεων: {current_count + 1}") # ενημέρωση του στατιστικού
            text_widget.config(state=tk.DISABLED) # απενεργοποίηση του text widget, έτσι ώστε να μην μπορεί να επεξεργαστεί ο χρήστης
            entry_widget.delete(0, tk.END) # καθαρισμός του πεδίου
    
    # Βελτιωμένη λειτουργία για διαγραφή επιλεγμένης λέξης
    def delete_selected_word(text_widget, stats_label=None, selected_line_var=None): # συνάρτηση για την διαγραφή επιλεγμένης λέξης
        try:
            if selected_line_var and selected_line_var[0]: # αν η επιλογή είναι επιλεγμένη
                text_widget.config(state=tk.NORMAL) # ενεργοποίηση του text widget
                
                line_start, line_end = selected_line_var[0] # υπολογισμός της γραμμής που κλικάρισε ο χρήστης
                line_text = text_widget.get(line_start, line_end).strip() # ανάγνωση της γραμμής
                
                if line_text:
                    # Επιβεβαίωση διαγραφής
                    if messagebox.askyesno("Διαγραφή", f"Θέλετε να διαγράψετε τη λέξη '{line_text}';"): # επιβεβαίωση για την διαγραφή της λέξης
                        # Διαγραφή της γραμμής συμπεριλαμβανομένου του newline
                        next_line = text_widget.index(f"{line_end} + 1 char") # υπολογισμός της επόμενης γραμμής
                        text_widget.delete(line_start, next_line) # διαγραφή της γραμμής
                        
                        # Καθαρισμός επιλογής
                        text_widget.tag_remove("selected", "1.0", tk.END) # καθαρισμός της επιλογής
                        selected_line_var[0] = None # απενεργοποίηση της επιλογής
                        
                        # Ενημέρωση στατιστικών
                        if stats_label:
                            remaining_text = text_widget.get(1.0, tk.END) # ανάγνωση του πεδίου
                            remaining_count = len([line.strip() for line in remaining_text.split('\n') if line.strip()]) # υπολογισμός του αριθμού των λέξεων
                            stats_label.config(text=f"Σύνολο λέξεων: {remaining_count}") # ενημέρωση του στατιστικού
                        
                        messagebox.showinfo("Επιτυχία", f"Η λέξη '{line_text}' διαγράφηκε.") # εμφάνιση μηνύματος επιτυχίας
                else:
                    messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε μια λέξη για διαγραφή.") # εμφάνιση μηνύματος προειδοποίησης
            else:
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε μια λέξη κάνοντας κλικ πάνω της.") # εμφάνιση μηνύματος προειδοποίησης
                
            text_widget.config(state=tk.DISABLED) # απενεργοποίηση του text widget
        except Exception as e:
            text_widget.config(state=tk.DISABLED) # απενεργοποίηση του text widget
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη διαγραφή: {str(e)}")

    # Βελτιωμένη λειτουργία για διαγραφή επιλεγμένης φράσης
    def delete_selected_phrase(text_widget, selected_line_var=None): # συνάρτηση για την διαγραφή επιλεγμένης φράσης
        try:
            if selected_line_var and selected_line_var[0]:
                text_widget.config(state=tk.NORMAL) # ενεργοποίηση του text widget
                
                line_start, line_end = selected_line_var[0] # υπολογισμός της γραμμής που κλικάρισε ο χρήστης   
                line_text = text_widget.get(line_start, line_end).strip() # ανάγνωση της γραμμής
                
                if line_text and not line_text.startswith('#'): # αν η γραμμή δεν ξεκινά με '#'
                    # Επιβεβαίωση διαγραφής
                    if messagebox.askyesno("Διαγραφή", f"Θέλετε να διαγράψετε τη φράση '{line_text}';"): # επιβεβαίωση για την διαγραφή της φράσης
                        # Διαγραφή της γραμμής συμπεριλαμβανομένου του newline
                        next_line = text_widget.index(f"{line_end} + 1 char") # υπολογισμός της επόμενης γραμμής
                        text_widget.delete(line_start, next_line) # διαγραφή της γραμμής
                        
                        # Καθαρισμός επιλογής
                        text_widget.tag_remove("selected", "1.0", tk.END) # καθαρισμός της επιλογής
                        selected_line_var[0] = None # απενεργοποίηση της επιλογής
                        
                        # Αποθήκευση των αλλαγών
                        save_exact_phrases_user_friendly(text_widget) # αποθήκευση των αλλαγών
                        
                        messagebox.showinfo("Επιτυχία", f"Η φράση '{line_text}' διαγράφηκε.") # εμφάνιση μηνύματος επιτυχίας
                elif line_text.startswith('#'):
                    messagebox.showwarning("Προειδοποίηση", "Δεν μπορείτε να διαγράψετε γραμμές σχολίων.") # εμφάνιση μηνύματος προειδοποίησης
                else:
                    messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε μια φράση για διαγραφή.") # εμφάνιση μηνύματος προειδοποίησης
            else:
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε μια φράση κάνοντας κλικ πάνω της.") # εμφάνιση μηνύματος προειδοποίησης
                
            text_widget.config(state=tk.DISABLED)
        except Exception as e:
            text_widget.config(state=tk.DISABLED)
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη διαγραφή: {str(e)}")
    
    # Λειτουργία για αποθήκευση ακριβών φράσεων σε φιλική μορφή
    def save_exact_phrases_user_friendly(text_widget): 
        global exact_phrases
        try:
            new_phrases = {}  
            text_widget.config(state=tk.NORMAL)  
            lines = text_widget.get(1.0, tk.END).strip().split('\n') 
            text_widget.config(state=tk.DISABLED)
            
            for line in lines: 
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('=')
                if len(parts) != 2:
                    continue
                
                phrase = parts[0].strip()
                value_parts = parts[1].strip().split(',')
                if len(value_parts) != 2:
                    continue
                
                sentiment = value_parts[0].strip()
                try:
                    score = int(value_parts[1].strip())
                except ValueError:
                    continue
                
                new_phrases[phrase] = {"sentiment": sentiment, "score": score}
            
            with open(exact_phrases_file, 'w', encoding='utf-8') as file:
                json.dump(new_phrases, file, ensure_ascii=False, indent=4)
            
            exact_phrases = load_exact_phrases()
            exact_phrases = new_phrases

            messagebox.showinfo("Αποθήκευση", "Οι ακριβείς φράσεις αποθηκεύτηκαν επιτυχώς!")
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Προέκυψε σφάλμα: {str(e)}")

    # Λειτουργία για έξυπνη πρόταση φράσης
    def suggest_phrase_addition(comment_text): # συνάρτηση για την πρόταση φράσης, Συνάρτηση που προτείνει στον χρήστη να προσθέσει μια φράση στο λεξικό, Συνάρτηση μέσα σε μια συναρτήση
        """Προτείνει στον χρήστη να προσθέσει μια φράση στο λεξικό"""
        result = messagebox.askyesnocancel(
            "Άγνωστη Φράση", 
            f"Η φράση '{comment_text}' δεν αναγνωρίστηκε από το σύστημα.\n\n"
            f"Θέλετε να την προσθέσετε στο λεξικό ακριβών φράσεων;\n\n"
            f"• Πατήστε 'Ναι' για να την προσθέσετε τώρα\n"
            f"• Πατήστε 'Όχι' για να συνεχίσετε με την κανονική ανάλυση\n"
            f"• Πατήστε 'Άκυρο' για να ακυρώσετε την ανάλυση"
        )
        
        if result is True:  # Ναι - Προσθήκη φράσης
            return show_phrase_addition_dialog(comment_text)
        elif result is False:  # Όχι - Συνέχεια με κανονική ανάλυση
            return "continue"
        else:  # Άκυρο - Ακύρωση
            return "cancel"

    def show_phrase_addition_dialog(phrase_text): # συνάρτηση για την προσθήκη φράσης
        """Εμφανίζει διάλογο για προσθήκη φράσης"""
        dialog = tk.Toplevel(root) # δημιουργία του διαλόγου
        dialog.title("Προσθήκη Νέας Φράσης") # τίτλος του διαλόγου
        dialog.geometry("400x250") # μέγεθος του διαλόγου
        dialog.config(bg=colour1) # χρώμα του διαλόγου
        dialog.transient(root) # ο διαλόγος να είναι transient
        dialog.grab_set() # ο διαλόγος να είναι grab_set
        
        # Κεντράρισμα διαλόγου
        dialog.update_idletasks() # ενημέρωση του διαλόγου
        x = (dialog.winfo_screenwidth() // 2) - (200) # υπολογισμός της θέσης του διαλόγου
        y = (dialog.winfo_screenheight() // 2) - (125) # υπολογισμός της θέσης του διαλόγου
        dialog.geometry(f"400x250+{x}+{y}") # τοποθέτηση του διαλόγου
        
        result = {"action": "cancel"}
        
        # Τίτλος
        title_label = tk.Label(dialog, text="Προσθήκη Νέας Φράσης",  # τίτλος του διαλόγου
                              bg=colour1, fg=colour4, font=('Century Gothic', 12, 'bold')) # χρώμα του τίτλου, γραμματοσειρά και μέγεθος του τίτλου
        title_label.pack(pady=10) # τοποθέτηση του τίτλου
        
        # Φράση
        phrase_frame = tk.Frame(dialog, bg=colour1) # δημιουργία του πλαισίου της φράσης
        phrase_frame.pack(pady=5, padx=20, fill="x") # τοποθέτηση του πλαισίου της φράσης
        
        tk.Label(phrase_frame, text="Φράση:", bg=colour1, fg=colour4).pack(anchor="w")
        phrase_entry = tk.Entry(phrase_frame, width=50)
        phrase_entry.pack(fill="x", pady=2)
        phrase_entry.insert(0, phrase_text)
        
        # Συναίσθημα
        sentiment_frame = tk.Frame(dialog, bg=colour1) # δημιουργία του πλαισίου του συναίσθημα
        sentiment_frame.pack(pady=5, padx=20, fill="x") # τοποθέτηση του πλαισίου του συναίσθημα
        
        tk.Label(sentiment_frame, text="Συναίσθημα:", bg=colour1, fg=colour4).pack(anchor="w") # τίτλος του πλαισίου του συναίσθημα
        sentiment_var = tk.StringVar(value="Θετικό") # ορίζει την προεπιλεγμένη τιμή του συναίσθημα
        sentiment_combo = ttk.Combobox(sentiment_frame, textvariable=sentiment_var, 
                                     values=["Θετικό", "Αρνητικό", "Ουδέτερο"], state="readonly")
        sentiment_combo.pack(fill="x", pady=2)
        
        # Βαθμολογία
        score_frame = tk.Frame(dialog, bg=colour1) # δημιουργία του πλαισίου της βαθμολογίας
        score_frame.pack(pady=5, padx=20, fill="x") # τοποθέτηση του πλαισίου της βαθμολογίας
        
        tk.Label(score_frame, text="Βαθμολογία (0-100):", bg=colour1, fg=colour4).pack(anchor="w") # τίτλος του πλαισίου της βαθμολογίας
        score_var = tk.StringVar(value="75") # ορίζει την προεπιλεγμένη τιμή της βαθμολογίας
        score_entry = tk.Entry(score_frame, textvariable=score_var, width=10) # δημιουργία της εισόδου της βαθμολογίας
        score_entry.pack(anchor="w", pady=2) # τοποθέτηση της εισόδου της βαθμολογίας
        
        # Κουμπιά
        button_frame = tk.Frame(dialog, bg=colour1) # δημιουργία του πλαισίου των κουμπιών
        button_frame.pack(pady=20) # τοποθέτηση του πλαισίου των κουμπιών
        
        def add_and_continue(): # συνάρτηση για την προσθήκη και συνέχεια, Συνάρτηση που προσθέτει μια φράση στο λεξικό και συνεχίζει την ανάλυση
            try:
                phrase = phrase_entry.get().strip() # ανάγνωση της φράσης
                sentiment = sentiment_var.get() # ανάγνωση του συναίσθημα
                score = int(score_var.get()) # ανάγνωση της βαθμολογίας
                
                if not phrase:
                    messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε μια φράση.") # εμφάνιση μηνύματος σφάλματος
                    return
                
                if not (0 <= score <= 100): # αν η βαθμολογία δεν είναι μεταξύ 0 και 100
                    messagebox.showerror("Σφάλμα", "Η βαθμολογία πρέπει να είναι μεταξύ 0 και 100.") # εμφάνιση μηνύματος σφάλματος
                    return
                
                # Προσθήκη στο λεξικό 
                exact_phrases[phrase] = {"sentiment": sentiment, "score": score} # προσθήκη της φράσης στο λεξικό
                
                # Αποθήκευση στο αρχείο
                with open(exact_phrases_file, 'w', encoding='utf-8') as file: # αποθήκευση της φράσης στο αρχείο, χρησιμοποιώντας το json
                    json.dump(exact_phrases, file, ensure_ascii=False, indent=4) # αποθήκευση της φράσης στο αρχείο, χρησιμοποιώντας το json
                
                result["action"] = "added" # ορίζει την ενέργεια του κουμπιού
                result["phrase"] = phrase # ορίζει την φράση
                result["sentiment"] = sentiment # ορίζει το συναίσθημα
                result["score"] = score # ορίζει την βαθμολογία
                dialog.destroy() # καταστροφή του διαλόγου
                
            except ValueError:
                messagebox.showerror("Σφάλμα", "Η βαθμολογία πρέπει να είναι αριθμός.") # εμφάνιση μηνύματος σφάλματος
        
        def continue_without_adding(): # συνάρτηση για την συνέχεια χωρίς προσθήκη , Συνάρτηση που συνεχίζει την ανάλυση χωρίς προσθήκη φράσης
            result["action"] = "continue" # ορίζει την ενέργεια του κουμπιού
            dialog.destroy() # καταστροφή του διαλόγου
        
        def cancel_analysis(): # συνάρτηση για την ακύρωση της ανάλυσης
            result["action"] = "cancel" # ορίζει την ενέργεια του κουμπιού
            dialog.destroy() # καταστροφή του διαλόγου
        
        tk.Button(button_frame, text="Προσθήκη & Συνέχεια", bg=colour2, fg=colour4, # κουμπί προσθήκης και συνέχειας
                 command=add_and_continue, width=15).pack(side=tk.LEFT, padx=5) # τοποθέτηση του κουμπιού
        tk.Button(button_frame, text="Συνέχεια χωρίς Προσθήκη", bg=colour3, fg="white", # κουμπί συνέχειας χωρίς προσθήκη
                 command=continue_without_adding, width=18).pack(side=tk.LEFT, padx=5) # τοποθέτηση του κουμπιού
        tk.Button(button_frame, text="Άκυρο", bg="#FF6B6B", fg="white", # κουμπί ακύρωσης
                 command=cancel_analysis, width=10).pack(side=tk.LEFT, padx=5) # τοποθέτηση του κουμπιού
         
        dialog.wait_window() # περιμένει την καταστροφή του διαλόγου
        return result # επιστρέφει το αποτέλεσμα
    
    # ΘΕΤΙΚΕΣ ΛΕΞΕΙΣ
    # Δημιουργία toolbar για θετικές λέξεις
    toolbar_positive = tk.Frame(tab_positive, bg=colour1, height=50) # δημιουργία του toolbar για θετικές λέξεις
    toolbar_positive.pack(fill="x", padx=10, pady=(10, 5)) # τοποθέτηση του toolbar για θετικές λέξεις
    toolbar_positive.pack_propagate(False) # ο toolbar για θετικές λέξεις να μην μεταβάλλει το μέγεθος του
    
    # Στατιστικά για θετικές λέξεις
    stats_positive = tk.Label( 
        toolbar_positive,
        text=f"Σύνολο λέξεων: {len(thetikes_lekseis)}", # εμφάνιση του αριθμού των λέξεων
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 9) # γραμματοσειρά και μέγεθος του στατιστικού
    )
    stats_positive.pack(side=tk.LEFT, padx=10) # τοποθέτηση του στατιστικού
    
    # Κουμπιά εργαλείων για θετικές λέξεις
    tools_frame_positive = tk.Frame(toolbar_positive, bg=colour1) # δημιουργία του πλαισίου για τα εργαλεία
    tools_frame_positive.pack(side=tk.RIGHT, padx=10)
    
    # Αναζήτηση για θετικές λέξεις με αυτόματη ενημέρωση
    search_frame_positive = tk.Frame(tab_positive, bg=colour1) # δημιουργία του πλαισίου για την αναζήτηση
    search_frame_positive.pack(fill="x", padx=10, pady=5)
    
    search_label_positive = tk.Label(search_frame_positive, text="Αναζήτηση:", bg=colour1, fg=colour4) # τίτλος της αναζήτησης
    search_label_positive.pack(side=tk.LEFT, padx=5)
    
    search_var_positive = tk.StringVar() # ορίζει την τιμή της αναζήτησης
    search_entry_positive = tk.Entry(search_frame_positive, textvariable=search_var_positive, width=30) # δημιουργία της εισόδου της αναζήτησης
    search_entry_positive.pack(side=tk.LEFT, padx=5) # τοποθέτηση της εισόδου της αναζήτησης
     
    clear_button_positive = tk.Button( 
        search_frame_positive,
        text="Καθαρισμός",
        bg=colour2,
        fg=colour4,
        command=lambda: [search_var_positive.set(""), load_words_to_text(positive_text, thetikes_lekseis, stats_positive, selected_line_positive)] # καθαρισμός της αναζήτησης
    )
    clear_button_positive.pack(side=tk.LEFT, padx=5)
    
    # Γρήγορη προσθήκη για θετικές λέξεις
    add_frame_positive = tk.Frame(tab_positive, bg=colour1) # δημιουργία του πλαισίου για την προσθήκη λέξεων
    add_frame_positive.pack(fill="x", padx=10, pady=5) # τοποθέτηση του πλαισίου για την προσθήκη λέξεων
    
    add_label_positive = tk.Label(add_frame_positive, text="Προσθήκη λέξης:", bg=colour1, fg=colour4) # τίτλος της προσθήκης
    add_label_positive.pack(side=tk.LEFT, padx=5) # τοποθέτηση του τίτλου
    
    add_entry_positive = tk.Entry(add_frame_positive, width=30) # δημιουργία της εισόδου της προσθήκης
    add_entry_positive.pack(side=tk.LEFT, padx=5) # τοποθέτηση της εισόδου της προσθήκης
    
    add_button_positive = tk.Button(
        add_frame_positive,
        text="Προσθήκη",
        bg=colour2,
        fg=colour4,
        command=lambda: add_word(add_entry_positive, positive_text, stats_positive)
    )
    add_button_positive.pack(side=tk.LEFT, padx=5)
    
    # Προσθήκη κουμπιού διαγραφής για θετικές λέξεις
    delete_button_positive = tk.Button(
        add_frame_positive,
        text="Διαγραφή Επιλεγμένης",
        bg="#FF6B6B",
        fg="white",
        command=lambda: delete_selected_word(positive_text, stats_positive, selected_line_positive)
    )
    delete_button_positive.pack(side=tk.LEFT, padx=5)
    
    # Text widget για θετικές λέξεις με βελτιωμένη επιλογή
    positive_text = tk.Text(
        tab_positive, 
        height=18, 
        width=80, 
        wrap="word", 
        bg=colour1, 
        fg=colour4,
        cursor="hand2",
        selectbackground="#4A90E2",
        selectforeground="white"
    )
    positive_text.pack(pady=10, padx=10, fill="both", expand=True) # τοποθέτηση του text widget για θετικές λέξεις
    load_words_to_text(positive_text, thetikes_lekseis, stats_positive, selected_line_positive) # φόρτωση των λέξεων στο text widget , και επιλογή της γραμμής
    
    # Προσθήκη event για κλικ στο text widget
    positive_text.bind("<Button-1>", lambda e: select_line(positive_text, e, selected_line_positive)) # κλικ στο text widget, και επιλογή της γραμμής
    
    # ΤΩΡΑ προσθέτουμε τα κουμπιά εξαγωγής/εισαγωγής στο toolbar
    export_btn_positive = tk.Button(
        tools_frame_positive,
        text="📁 Εξαγωγή",
        bg=colour3,
        fg="white",
        cursor='hand2',
        font=('Century Gothic', 9),
        command=lambda: export_words(positive_text, "Θετικές Λέξεις")
    )
    export_btn_positive.pack(side=tk.LEFT, padx=2)
    
    import_btn_positive = tk.Button(
        tools_frame_positive,
        text="📂 Εισαγωγή",
        bg=colour3,
        fg="white",
        cursor='hand2',
        font=('Century Gothic', 9),
        command=lambda: import_words(positive_text, stats_positive)
    )
    import_btn_positive.pack(side=tk.LEFT, padx=2)
    
    # Προσθήκη αυτόματης αναζήτησης κατά την πληκτρολόγηση
    search_var_positive.trace('w', lambda *args: search_words(search_var_positive.get(), positive_text, thetikes_lekseis, stats_positive, selected_line_positive))
    
    btn_save_positive = tk.Button(
        tab_positive,
        background=colour2,
        foreground=colour4,
        activebackground=colour3,
        activeforeground=colour4,
        highlightthickness=2,
        highlightbackground=colour2,
        highlightcolor='WHITE',
        border=0,
        width=20,
        cursor='hand2',
        text='Αποθήκευση',
        font=('Century Gothic', 10, 'bold'),
        command=lambda: save_words_from_text(positive_text, thetikes_file, thetikes_lekseis, stats_positive)
    )
    btn_save_positive.pack(pady=10)

    # ΑΡΝΗΤΙΚΕΣ ΛΕΞΕΙΣ
    # Δημιουργία toolbar για αρνητικές λέξεις
    toolbar_negative = tk.Frame(tab_negative, bg=colour1, height=50) # δημιουργία του toolbar για αρνητικές λέξεις
    toolbar_negative.pack(fill="x", padx=10, pady=(10, 5)) # τοποθέτηση του toolbar για αρνητικές λέξεις
    toolbar_negative.pack_propagate(False) # ο toolbar για αρνητικές λέξεις να μην μεταβάλλει το μέγεθος του
    
    # Στατιστικά για αρνητικές λέξεις
    stats_negative = tk.Label(
        toolbar_negative,
        text=f"Σύνολο λέξεων: {len(arnitikes_lekseis)}", # εμφάνιση του αριθμού των λέξεων
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 9) # γραμματοσειρά και μέγεθος του στατιστικού
    )
    stats_negative.pack(side=tk.LEFT, padx=10) # τοποθέτηση του στατιστικού
    
    # Κουμπιά εργαλείων για αρνητικές λέξεις
    tools_frame_negative = tk.Frame(toolbar_negative, bg=colour1) # δημιουργία του πλαισίου για τα εργαλεία
    tools_frame_negative.pack(side=tk.RIGHT, padx=10) # τοποθέτηση του πλαισίου για τα εργαλεία
    
    # Αναζήτηση για αρνητικές λέξεις με αυτόματη ενημέρωση
    search_frame_negative = tk.Frame(tab_negative, bg=colour1) # δημιουργία του πλαισίου για την αναζήτηση
    search_frame_negative.pack(fill="x", padx=10, pady=5) # τοποθέτηση του πλαισίου για την αναζήτηση
     
    search_label_negative = tk.Label(search_frame_negative, text="Αναζήτηση:", bg=colour1, fg=colour4) # τίτλος της αναζήτησης
    search_label_negative.pack(side=tk.LEFT, padx=5) 
    
    search_var_negative = tk.StringVar() # ορίζει την τιμή της αναζήτησης
    search_entry_negative = tk.Entry(search_frame_negative, textvariable=search_var_negative, width=30) # δημιουργία της εισόδου της αναζήτησης
    search_entry_negative.pack(side=tk.LEFT, padx=5) # τοποθέτηση της εισόδου της αναζήτησης
    
    clear_button_negative = tk.Button(
        search_frame_negative,
        text="Καθαρισμός",
        bg=colour2,
        fg=colour4,
        command=lambda: [search_var_negative.set(""), load_words_to_text(negative_text, arnitikes_lekseis, stats_negative, selected_line_negative)] # καθαρισμός της αναζήτησης
    )
    clear_button_negative.pack(side=tk.LEFT, padx=5) # τοποθέτηση του κουμπιού
    
    # Γρήγορη προσθήκη για αρνητικές λέξεις
    add_frame_negative = tk.Frame(tab_negative, bg=colour1) # δημιουργία του πλαισίου για την προσθήκη λέξεων
    add_frame_negative.pack(fill="x", padx=10, pady=5) # τοποθέτηση του πλαισίου για την προσθήκη λέξεων
    
    add_label_negative = tk.Label(add_frame_negative, text="Προσθήκη λέξης:", bg=colour1, fg=colour4) # τίτλος της προσθήκης
    add_label_negative.pack(side=tk.LEFT, padx=5) # τοποθέτηση του τίτλου
    
    add_entry_negative = tk.Entry(add_frame_negative, width=30)
    add_entry_negative.pack(side=tk.LEFT, padx=5)
    
    add_button_negative = tk.Button(
        add_frame_negative,
        text="Προσθήκη",
        bg=colour2,
        fg=colour4,
        cursor='hand2',
        command=lambda: add_word(add_entry_negative, negative_text, stats_negative)
    )
    add_button_negative.pack(side=tk.LEFT, padx=5)
    
    # Προσθήκη κουμπιού διαγραφής για αρνητικές λέξεις
    delete_button_negative = tk.Button(
        add_frame_negative,
        text="Διαγραφή Επιλεγμένης",
        bg="#FF6B6B",
        fg="white",
        cursor='hand2',
        command=lambda: delete_selected_word(negative_text, stats_negative, selected_line_negative)
    )
    delete_button_negative.pack(side=tk.LEFT, padx=5)
    
    # Text widget για αρνητικές λέξεις με βελτιωμένη επιλογή
    negative_text = tk.Text(
        tab_negative, 
        height=18, 
        width=80, 
        wrap="word", 
        bg=colour1, 
        fg=colour4,
        cursor="hand2",
        selectbackground="#4A90E2",
        selectforeground="white"
    )
    negative_text.pack(pady=10, padx=10, fill="both", expand=True)
    load_words_to_text(negative_text, arnitikes_lekseis, stats_negative, selected_line_negative)
    
    # Προσθήκη event για κλικ
    negative_text.bind("<Button-1>", lambda e: select_line(negative_text, e, selected_line_negative))
    
    # Κουμπιά εξαγωγής/εισαγωγής για αρνητικές λέξεις
    export_btn_negative = tk.Button(
        tools_frame_negative,
        text="📁 Εξαγωγή",
        bg=colour3,
        fg="white",
        cursor='hand2',
        font=('Century Gothic', 9),
        command=lambda: export_words(negative_text, "Αρνητικές Λέξεις")
    )
    export_btn_negative.pack(side=tk.LEFT, padx=2)
    
    import_btn_negative = tk.Button(
        tools_frame_negative,
        text="📂 Εισαγωγή",
        bg=colour3,
        fg="white",
        cursor='hand2',
        font=('Century Gothic', 9),
        command=lambda: import_words(negative_text, stats_negative)
    )
    import_btn_negative.pack(side=tk.LEFT, padx=2)
    
    # Προσθήκη αυτόματης αναζήτησης κατά την πληκτρολόγηση
    search_var_negative.trace('w', lambda *args: search_words(search_var_negative.get(), negative_text, arnitikes_lekseis, stats_negative, selected_line_negative)) # αυτόματη αναζήτηση κατά την πληκτρολόγηση
    
    btn_save_negative = tk.Button( 
        tab_negative,
        background=colour2,
        foreground=colour4,
        activebackground=colour3,
        activeforeground=colour4,
        highlightthickness=2,
        highlightbackground=colour2,
        highlightcolor='WHITE',
        border=0,
        width=20,
        cursor='hand2',
        text='Αποθήκευση',
        font=('Century Gothic', 10, 'bold'),
        command=lambda: save_words_from_text(negative_text, arnitikes_file, arnitikes_lekseis, stats_negative)
    )
    btn_save_negative.pack(pady=10)

    # ΛΕΞΕΙΣ ΔΙΑΚΟΠΗΣ (STOPWORDS)
    # Δημιουργία toolbar για stopwords
    toolbar_stopwords = tk.Frame(tab_stopwords, bg=colour1, height=50)
    toolbar_stopwords.pack(fill="x", padx=10, pady=(10, 5))
    toolbar_stopwords.pack_propagate(False)
    
    # Στατιστικά για stopwords
    stats_stopwords = tk.Label(
        toolbar_stopwords,
        text=f"Σύνολο λέξεων: {len(stopwords_lekseis)}",
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 9)
    )
    stats_stopwords.pack(side=tk.LEFT, padx=10)
    
    # Κουμπιά εργαλείων για stopwords
    tools_frame_stopwords = tk.Frame(toolbar_stopwords, bg=colour1) # δημιουργία του πλαισίου για τα εργαλεία
    tools_frame_stopwords.pack(side=tk.RIGHT, padx=10) # τοποθέτηση του πλαισίου για τα εργαλεία
    
    # Αναζήτηση για stopwords με αυτόματη ενημέρωση
    search_frame_stopwords = tk.Frame(tab_stopwords, bg=colour1) # δημιουργία του πλαισίου για την αναζήτηση
    search_frame_stopwords.pack(fill="x", padx=10, pady=5) # τοποθέτηση του πλαισίου για την αναζήτηση
    
    search_label_stopwords = tk.Label(search_frame_stopwords, text="Αναζήτηση:", bg=colour1, fg=colour4) # τίτλος της αναζήτησης
    search_label_stopwords.pack(side=tk.LEFT, padx=5)
    
    search_var_stopwords = tk.StringVar() # ορίζει την τιμή της αναζήτησης
    search_entry_stopwords = tk.Entry(search_frame_stopwords, textvariable=search_var_stopwords, width=30) # δημιουργία της εισόδου της αναζήτησης
    search_entry_stopwords.pack(side=tk.LEFT, padx=5) # τοποθέτηση της εισόδου της αναζήτησης
    
    clear_button_stopwords = tk.Button(
        search_frame_stopwords,
        text="Καθαρισμός",
        bg=colour2,
        fg=colour4,
        cursor='hand2',
        command=lambda: [search_var_stopwords.set(""), load_words_to_text(stopwords_text, stopwords_lekseis, stats_stopwords, selected_line_stopwords)] # καθαρισμός της αναζήτησης
    )
    clear_button_stopwords.pack(side=tk.LEFT, padx=5) # τοποθέτηση του κουμπιού
    
    # Γρήγορη προσθήκη για stopwords
    add_frame_stopwords = tk.Frame(tab_stopwords, bg=colour1)
    add_frame_stopwords.pack(fill="x", padx=10, pady=5)
    
    add_label_stopwords = tk.Label(add_frame_stopwords, text="Προσθήκη λέξης:", bg=colour1, fg=colour4)
    add_label_stopwords.pack(side=tk.LEFT, padx=5)
    
    add_entry_stopwords = tk.Entry(add_frame_stopwords, width=30)
    add_entry_stopwords.pack(side=tk.LEFT, padx=5)
    
    add_button_stopwords = tk.Button(
        add_frame_stopwords,
        text="Προσθήκη",
        bg=colour2,
        fg=colour4,
        cursor='hand2',
        command=lambda: add_word(add_entry_stopwords, stopwords_text, stats_stopwords)
    )
    add_button_stopwords.pack(side=tk.LEFT, padx=5)
    
    # Προσθήκη κουμπιού διαγραφής για stopwords
    delete_button_stopwords = tk.Button(
        add_frame_stopwords,
        text="Διαγραφή Επιλεγμένης",
        bg="#FF6B6B",
        fg="white",
        command=lambda: delete_selected_word(stopwords_text, stats_stopwords, selected_line_stopwords)
    )
    delete_button_stopwords.pack(side=tk.LEFT, padx=5)
    
    # Text widget για stopwords με βελτιωμένη επιλογή
    stopwords_text = tk.Text(
        tab_stopwords, 
        height=18, 
        width=80, 
        wrap="word", 
        bg=colour1, 
        fg=colour4,
        cursor="hand2",
        selectbackground="#4A90E2",
        selectforeground="white"
    )
    stopwords_text.pack(pady=10, padx=10, fill="both", expand=True) # τοποθέτηση του text widget για stopwords
    load_words_to_text(stopwords_text, stopwords_lekseis, stats_stopwords, selected_line_stopwords) # φόρτωση των λέξεων στο text widget
    
    # Προσθήκη event για κλικ
    stopwords_text.bind("<Button-1>", lambda e: select_line(stopwords_text, e, selected_line_stopwords)) # επιλογή της γραμμής
    
    # Κουμπιά εξαγωγής/εισαγωγής για stopwords
    export_btn_stopwords = tk.Button( 
        tools_frame_stopwords,
        text="📁 Εξαγωγή", # προσθήκη πεδίου για την ανάλυση σχολίου
        bg=colour3, # προσθήκη πεδίου για την ανάλυση σχολίου
        fg="white",
        cursor='hand2',
        font=('Century Gothic', 9),
        command=lambda: export_words(stopwords_text, "Λέξεις Διακοπής") # εξαγωγή των λέξεων
    )
    export_btn_stopwords.pack(side=tk.LEFT, padx=2) # τοποθέτηση του κουμπιού
    
    import_btn_stopwords = tk.Button(  
        tools_frame_stopwords,
        text="📂 Εισαγωγή", # προσθήκη πεδίου για την ανάλυση σχολίου
        bg=colour3, # προσθήκη πεδίου για την ανάλυση σχολίου
        fg="white",
        cursor='hand2',
        font=('Century Gothic', 9),
        command=lambda: import_words(stopwords_text, stats_stopwords) # εισαγωγή των λέξεων
    )
    import_btn_stopwords.pack(side=tk.LEFT, padx=2) # τοποθέτηση του κουμπιού
    
    # Προσθήκη αυτόματης αναζήτησης κατά την πληκτρολόγηση
    search_var_stopwords.trace('w', lambda *args: search_words(search_var_stopwords.get(), stopwords_text, stopwords_lekseis, stats_stopwords, selected_line_stopwords)) # αυτόματη αναζήτηση κατά την πληκτρολόγηση
    
    btn_save_stopwords = tk.Button( 
        tab_stopwords,
        background=colour2,
        foreground=colour4,
        activebackground=colour3,
        activeforeground=colour4,
        highlightthickness=2,
        highlightbackground=colour2,
        highlightcolor='WHITE',
        border=0,
        width=20,
        cursor='hand2',
        text='Αποθήκευση',
        font=('Century Gothic', 10, 'bold'),
        command=lambda: save_words_from_text(stopwords_text, stopwords_file, stopwords_lekseis, stats_stopwords)
    )
    btn_save_stopwords.pack(pady=10)
    
    # ΑΚΡΙΒΕΙΣ ΦΡΑΣΕΙΣ
    # Text widget για ακριβείς φράσεις με βελτιωμένη επιλογή
    phrases_text = tk.Text(
        tab_phrases, 
        height=20, 
        width=80, 
        wrap="word", 
        bg=colour1, 
        fg=colour4,
        cursor="hand2",
        selectbackground="#4A90E2",
        selectforeground="white"
    )
    phrases_text.pack(pady=10, padx=10, fill="both", expand=True)
    
    # Προσθήκη event για κλικ στις φράσεις
    phrases_text.bind("<Button-1>", lambda e: select_line(phrases_text, e, selected_line_phrases))
    
    # Φόρτωση των ακριβών φράσεων στο text area σε φιλική μορφή
    phrases_text.config(state=tk.NORMAL) # προσθήκη πεδίου για την ανάλυση σχολίου
    phrases_text.insert(tk.END, "# Μορφή: λέξη/φράση = Συναίσθημα, Βαθμολογία\n") # προσθήκη πεδίου για την ανάλυση σχολίου
    phrases_text.insert(tk.END, "# Παραδείγματα:\n") # προσθήκη πεδίου για την ανάλυση σχολίου
    phrases_text.insert(tk.END, "# τέλειο = Θετικό, 100\n") # προσθήκη πεδίου για την ανάλυση σχολίου
    phrases_text.insert(tk.END, "# χάλια = Αρνητικό, 90\n")
    phrases_text.insert(tk.END, "# ουδέτερο = Ουδέτερο, 50\n\n")
    
    # Προσθήκη των υπαρχουσών φράσεων
    for phrase, info in exact_phrases.items():
        phrases_text.insert(tk.END, f"{phrase} = {info['sentiment']}, {info['score']}\n")
    phrases_text.config(state=tk.DISABLED)
    
    save_note = tk.Label(
        tab_phrases,
        text="ΣΗΜΕΙΩΣΗ: Οι ακριβείς φράσεις αποθηκεύονται αυτόματα μόλις προστεθούν.",
        bg=colour1,
        fg="red",
        font=('Century Gothic', 9, 'bold'),
        wraplength=600
    )
    save_note.pack(pady=5)

    # Γρήγορη προσθήκη για ακριβείς φράσεις
    add_frame_phrases = tk.Frame(tab_phrases, bg=colour1) # προσθήκη πεδίου για την ανάλυση σχολίου
    add_frame_phrases.pack(fill="x", padx=10, pady=5) # προσθήκη πεδίου για την ανάλυση σχολίου
    
    add_label_phrase = tk.Label(add_frame_phrases, text="Φράση:", bg=colour1, fg=colour4) # προσθήκη πεδίου για την ανάλυση σχολίου
    add_label_phrase.pack(side=tk.LEFT, padx=5) # προσθήκη πεδίου για την ανάλυση σχολίου
    
    add_entry_phrase = tk.Entry(add_frame_phrases, width=20)
    add_entry_phrase.pack(side=tk.LEFT, padx=5)
    
    add_label_sentiment = tk.Label(add_frame_phrases, text="Συναίσθημα:", bg=colour1, fg=colour4) # προσθήκη πεδίου για την ανάλυση σχολίου
    add_label_sentiment.pack(side=tk.LEFT, padx=5)

    sentiment_var = tk.StringVar()
    sentiment_var.set("Θετικό")
    sentiment_combo = ttk.Combobox(add_frame_phrases, textvariable=sentiment_var, values=["Θετικό", "Αρνητικό", "Ουδέτερο"], width=10)
    sentiment_combo.pack(side=tk.LEFT, padx=5)
    
    add_label_score = tk.Label(add_frame_phrases, text="Βαθμός (0-100):", bg=colour1, fg=colour4)
    add_label_score.pack(side=tk.LEFT, padx=5)
    
    score_var = tk.StringVar()
    score_var.set("100")
    score_entry = tk.Entry(add_frame_phrases, textvariable=score_var, width=5) # προσθήκη πεδίου για την ανάλυση σχολίου
    score_entry.pack(side=tk.LEFT, padx=5) # προσθήκη πεδίου για την ανάλυση σχολίου
    
    def add_phrase():
        phrase = add_entry_phrase.get().strip() # προσθήκη πεδίου για την ανάλυση σχολίου
        sentiment = sentiment_var.get() # προσθήκη πεδίου για την ανάλυση σχολίου
        try:
            score = int(score_var.get()) # προσθήκη πεδίου για την ανάλυση σχολίου
            if 0 <= score <= 100 and phrase:
                phrases_text.config(state=tk.NORMAL)
                phrases_text.insert(tk.END, f"{phrase} = {sentiment}, {score}\n") # προσθήκη πεδίου για την ανάλυση σχολίου
                phrases_text.config(state=tk.DISABLED)
                add_entry_phrase.delete(0, tk.END) # προσθήκη πεδίου για την ανάλυση σχολίου
                score_var.set("100") # προσθήκη πεδίου για την ανάλυση σχολίου
                save_exact_phrases_user_friendly(phrases_text) # προσθήκη πεδίου για την ανάλυση σχολίου
        except ValueError:
            messagebox.showerror("Σφάλμα", "Ο βαθμός πρέπει να είναι αριθμός μεταξύ 0 και 100.") # προσθήκη πεδίου για την ανάλυση σχολίου
    
    add_button_phrase = tk.Button( 
        add_frame_phrases,
        text="Προσθήκη",
        bg=colour2,
        fg=colour4,
        command=add_phrase
    )
    add_button_phrase.pack(side=tk.LEFT, padx=5)

    # Προσθήκη κουμπιού διαγραφής για ακριβείς φράσεις
    delete_button_phrases = tk.Button(
        add_frame_phrases,
        text="Διαγραφή Επιλεγμένης",
        bg="#FF6B6B",
        fg="white",
        command=lambda: delete_selected_phrase(phrases_text, selected_line_phrases)
    )
    delete_button_phrases.pack(side=tk.LEFT, padx=5)

    # Προσθήκη επεξήγησης στην καρτέλα θετικών λέξεων
    positive_explanation = tk.Label(
        tab_positive,
        text="Οι λέξεις αυτής της λίστας χαρακτηρίζονται ως 'Θετικές'. Χρησιμοποιούνται για ανάλυση συναισθήματος όταν δεν υπάρχει ακριβής φράση.",
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 8),
        wraplength=600
    )
    positive_explanation.pack(pady=5)

    # Προσθήκη επεξήγησης στην καρτέλα αρνητικών λέξεων
    negative_explanation = tk.Label(
        tab_negative,
        text="Οι λέξεις αυτής της λίστας χαρακτηρίζονται ως 'Αρνητικές'. Χρησιμοποιούνται για ανάλυση συναισθήματος όταν δεν υπάρχει ακριβής φράση.",
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 8),
        wraplength=600
    )
    negative_explanation.pack(pady=5)

    # Βελτιωμένη επεξήγηση στην καρτέλα ακριβών φράσεων
    explanation = tk.Label(
        tab_phrases,
        text="Οι ακριβείς φράσεις έχουν προτεραιότητα στην ανάλυση συναισθήματος. Αν βρεθεί μια φράση στο κείμενο, θα χρησιμοποιηθεί το ακριβές συναίσθημα και ποσοστό που έχετε ορίσει.",
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 8),
        wraplength=600
    )
    explanation.pack(pady=5)

    # Προσθήκη οδηγιών χρήσης
    help_frame = tk.Frame(edit_window, bg=colour1)
    help_frame.pack(fill="x", padx=20, pady=10)
    
    help_text = """💡 Οδηγίες Χρήσης:
• Χρησιμοποιήστε την αναζήτηση για να βρείτε λέξεις (λειτουργεί με ή χωρίς τόνους)
• Προσθέστε νέες λέξεις από το πεδίο "Προσθήκη λέξης"
• Κάντε κλικ σε μια λέξη για να την επιλέξετε (θα γίνει μπλε) και πατήστε "Διαγραφή Επιλεγμένης"
• Χρησιμοποιήστε τα κουμπιά εξαγωγής/εισαγωγής για backup των λιστών σας
• Μην ξεχάσετε να πατήσετε "Αποθήκευση" για να σώσετε τις αλλαγές σας"""
    
    help_label = tk.Label(
        help_frame,
        text=help_text,
        bg=colour1,
        fg=colour4,
        font=('Century Gothic', 8),
        justify=tk.LEFT
    )
    help_label.pack()


####################################################################### 
####### ΕΝΤΟΛΕΣ ΓΙΑ ΤΟ ΜΕΝΟΥ #######################################

help_menu = tk.Menu(menu_fr, tearoff=0) # menu για την βοήθεια
help_menu.add_command(label='Επικοινωνία', command=show_help) # προσθήκη εντολής για την επικοινωνία
help_menu.add_command(label='Έκδoση λογισμικού', command=show_version) # προσθήκη εντολής για την έκδοση λογισμικού

history_menu = tk.Menu(menu_fr, tearoff=0) # menu για το ιστορικό
menu_fr.add_cascade(menu=history_menu, label='Ιστορικό') # προσθήκη menu στο παράθυρο
history_menu.add_command(label='Διαγραφή Ιστορικού', command=clear_history) # προσθήκη εντολής για την διαγραφή ιστορικού

menu_fr.add_cascade(menu=help_menu, label='Βοήθεια') # προσθήκη menu στο παράθυρο

#####################################################################

### ΕΠΙΚΕΦΑΛΙΔΑ ΠΑΡΑΘΥΡΟΥ ###
label_title = tk.Label( 
    root,
    text='Ανάλυση συναισθήματος σχολίου',
    bg=colour1,
    fg=colour4,
    font=('Century Gothic', 12, 'bold')
    )
label_title.pack(pady=5)

label_ask = tk.Label( 
    root,
    text="Επιλέγξτε για ποιο είδος θελετε να γίνει ανάλυση:",
    bg=colour1,
    fg=colour4,
    font=('Century Gothic', 10, 'bold')
    )
label_ask.pack()

### ΣΤΡΟΓΓΥΛΑ ΚΟΥΜΠΙΑ ΠΡΟΙΟΝΤΑ - ΥΠΗΡΕΣΙΕΣ ###

# Frame για τα κουμπιά επιλογής



# Frame για τα κουμπιά επιλογής
selection_fr = tk.Frame(root, bg=colour1) # δημιουργία του πλαισίου για τα κουμπιά επιλογής
selection_fr.pack(pady=12) # τοποθέτηση του πλαισίου για τα κουμπιά επιλογής

# Μεταβλητή για την επιλογή
main_selection = tk.StringVar()
main_selection.set("Products")  # Προεπιλογή: Προϊόντα

# Αριστερό radio button (Προϊόντα) - ΑΛΛΑΓΗ: από Υπηρεσίες σε Προϊόντα
rb_products = tk.Radiobutton(
    selection_fr,
    text="Προϊόντα",  # ΑΛΛΑΓΗ
    variable=main_selection,
    value="Products",  # ΑΛΛΑΓΗ
    bg=colour1,
    fg=colour4,
    indicatoron=0,
    font=('Century Gothic', 11, 'bold'),
    command=lambda: btn_choice("Products")  # ΑΛΛΑΓΗ
)
rb_products.pack(side=tk.LEFT, padx=20)  # ΑΛΛΑΓΗ: από rb_services σε rb_products

# Δεξί radio button (Υπηρεσίες) - ΑΛΛΑΓΗ: από Προϊόντα σε Υπηρεσίες
rb_services = tk.Radiobutton(
    selection_fr,
    text="Υπηρεσίες",  # ΑΛΛΑΓΗ
    variable=main_selection,
    value="Services",  # ΑΛΛΑΓΗ
    bg=colour1,
    fg=colour4,
    indicatoron=0,
    font=('Century Gothic', 11, 'bold'),
    command=lambda: btn_choice("Services")  # ΑΛΛΑΓΗ
)
rb_services.pack(side=tk.LEFT, padx=20)  # ΑΛΛΑΓΗ: από rb_products σε rb_services

############ στυλ για τα radio buttons ############

# Στυλ για τα radio buttons
rb_products.config(  # ΑΛΛΑΓΗ: από rb_services σε rb_products
    selectcolor=colour2,
    activebackground=colour1,
    activeforeground=colour4,
    width=10,  # Σταθερό πλάτος
    anchor='center',  # Κεντράρισμα κειμένου
)

rb_services.config(  # ΑΛΛΑΓΗ: από rb_products σε rb_services
    selectcolor=colour2,
    activebackground=colour1,
    activeforeground=colour4,
    width=10,  # Σταθερό πλάτος
    anchor='center',  # Κεντράρισμα κειμένου
)

####### Εντολές για το πεδίο εγγραφής σχολίων #######

### FRAME ΓΙΑ ΠΕΔΙΟ ΕΓΓΡΑΦΗΣ ΣΧΟΛΙΩΝ ###
comment_fr = tk.Frame(root, bg=colour1)
comment_fr.pack()

### ΠΕΔΙΟ ΕΓΓΡΑΦΗΣ ΣΧΟΛΙΩΝ ###

# Δημιουργία Text με σύνδεση στο scrollbar

comment_text = tk.Text(
    comment_fr,
    width=35,
    height=4,
    bg=colour1,
    fg='grey',
    font=('Century Gothic', 12),
)
comment_text.pack(side="left", fill="both", expand=True)

###### Εντολή για να αλλάξει το χρώμα του κειμένου όταν το πεδίο κειμένου αποκτά εστίαση

def on_enter(event):
    button_analisi_pressed(comment_type, instant_score, instant_score_str) ## Ανάλυση σχολίου
    #comment_text.delete(1.0, tk.END) ## Διαγραφή περιεχομένου πεδίου κειμένου
    #comment_text.config(fg=colour4) ## Αλλαγή χρώματος κειμένου
    return "break"  # Αποτρέπει την αλλαγή γραμμής

def on_Shift_enter(event): #    
    comment_text.insert(tk.INSERT, "\n") # Εισάγει νέα γραμμή
    num_lines = int(comment_text.index('end-1c').split('.')[0]) # Αριθμός γραμμών στο πεδίο κειμένου
    if num_lines >= 4:
        comment_text.config(height=num_lines) # Αυξάνει το ύψος του πεδίου
    else:
        comment_text.config(height=4)  # Επαναφορά στο ελάχιστο ύψος
    return "break"

def adjust_height(event=None):
    num_lines = int(comment_text.index('end-1c').split('.')[0])
    comment_text.config(height=max(4, num_lines))  # 4 είναι το ελάχιστο ύψος

comment_text.bind("<Shift-Return>", on_Shift_enter) # προσθήκη πεδίου για την ανάλυση σχολίου
comment_text.bind("<KeyRelease>", adjust_height) # προσθήκη πεδίου για την ανάλυση σχολίου

comment_text.grid(row=0, column=0, padx=5, pady=5) # προσθήκη πεδίου για την ανάλυση σχολίου
comment_text.insert(tk.END, 'Γράψτε εδώ το σχόλιό σας!') # προσθήκη πεδίου για την ανάλυση σχολίου



comment_text.bind("<Control-c>", lambda e: comment_text.event_generate("<<Copy>>")) ### Εντολή copy
comment_text.bind("<Control-x>", lambda e: comment_text.event_generate("<<Cut>>")) ## Εντολή cut
comment_text.bind("<Control-v>", lambda e: comment_text.event_generate("<<Paste>>")) ## Εντολή paste
comment_text.bind("<Return>", on_enter) ## Εντολή για να γίνει ανάλυση σχολίου
comment_text.bind("<Shift-Return>", on_Shift_enter) ## Εντολή για να μπει νέα γραμμή
comment_text.bind('<KeyPress>', on_first_key) # Προσθήκη του binding: , για να μην γίνεται ανάλυση σχολίου με το πρώτο πάτημα πλήκτρου

### ΚΟΥΜΠΙΑ COPY, PASTE, DELETE ΠΕΡΙΕΧΟΜΕΝΟΥ ΠΕΔΙΟΥ ###
buttons_comm_fr = tk.Frame(comment_fr, bg=colour1)
buttons_comm_fr.grid(row=0, column=1, padx=5, sticky='n')

copy_btn = PhotoImage(file=copy_btn_path) # φορτώνει το σχετικό εικονίδιο
paste_btn = PhotoImage(file=paste_btn_path) # φορτώνει το σχετικό εικονίδιο
delete_btn = PhotoImage(file=delete_btn_path) # φορτώνει το σχετικό εικονίδιο
label_icon_copy_btn = tk.Label(buttons_comm_fr, image=copy_btn, bg=colour1) # φορτώνει το σχετικό εικονίδιο
label_icon_paste_btn = tk.Label(buttons_comm_fr, image=paste_btn, bg=colour1) # φορτώνει το σχετικό εικονίδιο
label_icon_delete_btn = tk.Label(buttons_comm_fr, image=delete_btn,  bg=colour1)

button_copy = tk.Button(
    buttons_comm_fr,
    image=copy_btn,
    background=colour2,
    foreground=colour4,
    activebackground=colour3,
    activeforeground=colour4,
    highlightthickness=2,
    highlightbackground=colour2,
    highlightcolor='WHITE',
    border=0,
    relief='flat',
    bd=0,
    cursor='hand2',
    borderwidth=0,
    width=20,
    height=20,
    command=lambda:copy_text(False))
button_copy.pack(pady=5)

button_paste = tk.Button(
    buttons_comm_fr,
    image=paste_btn,
    background=colour2,
    foreground=colour4,
    activebackground=colour3,
    activeforeground=colour4,
    highlightthickness=2,
    highlightbackground=colour2,
    highlightcolor='WHITE',
    border=0,
    relief='flat',
    bd=0,
    cursor='hand2',
    borderwidth=0,
    width=20,
    height=20,
    command=lambda:paste_text(False))
button_paste.pack(pady=5)

button_delete = tk.Button(
    buttons_comm_fr,
    image=delete_btn,
    background=colour2,
    foreground=colour4,
    activebackground=colour3,
    activeforeground=colour4,
    highlightthickness=2,
    highlightbackground=colour2,
    highlightcolor='WHITE',
    border=0,
    cursor='hand2',
    borderwidth=0,
    width=20,
    height=20,
    command=delete_text)
button_delete.pack(pady=5)

### ΒΑΣΙΚΟ ΚΟΥΜΠΙ ΑΝΑΛΥΣΗΣ ΣΧΟΛΙΩΝ (ΠΕΡΙΕΧΕΙ ΤΙΣ ΕΝΤΟΛΕΣ ΓΙΑ ΝΑ ΓΙΝΕΙ Η ΑΝΑΛΥΣΗ) ###
# ΣΥΝΔΕΕΤΑΙ ΜΕ ΣΥΝΑΡΤΗΣΗ button_analisi_pressed (απο εδώ ξεκινάει όλη η δουλειά) #

analisi_fr = tk.Frame(root, bg=colour1)
analisi_fr.pack(pady=10)

button_analisi = tk.Button(
    analisi_fr,
    background=colour2,
    foreground=colour4,
    activebackground=colour3,
    activeforeground=colour4,
    highlightthickness=2,
    highlightbackground=colour2,
    highlightcolor='WHITE',
    border=0,
    relief='flat',
    bd=0,
    width=15,
    cursor='hand2',
    text='Ανάλυση σχολίου',
    font=('Century Gothic', 10, 'bold'),
    command=lambda:button_analisi_pressed(comment_type, instant_score, instant_score_str) # κλήση της συνάρτησης button_analisi_pressed
    )
button_analisi.grid(row= 0, column=0, padx=5, pady=5) # προσθήκη πεδίου για την ανάλυση σχολίου

button_show = tk.Button(
    analisi_fr, 
    background=colour2,
    foreground=colour4,
    activebackground=colour3,
    activeforeground=colour4,
    highlightthickness=2,
    highlightbackground=colour2,
    highlightcolor='WHITE',
    border=0,
    relief='flat',
    bd=0,
    width=15,
    cursor='hand2',
    text='Εμφάνιση σχολίων',
    font=('Century Gothic', 10, 'bold'),
    command=show_data    
    )
button_show.grid(row=0, column=1, padx=5, pady=5)

button_analisi.grid(row=0, column=0, padx=5, pady=5)
button_show.grid(row=0, column=1, padx=5, pady=5)

button_pie_chart = tk.Button(
    analisi_fr,
    background=colour2,
    foreground=colour4,
    activebackground=colour3,
    activeforeground=colour4,
    highlightthickness=2,
    highlightbackground=colour2,
    highlightcolor='WHITE',
    border=0,
    relief='flat',
    bd=0,
    width=17,
    cursor='hand2',
    text='Γραφική απεικόνιση',
    font=('Century Gothic', 10, 'bold'),
    command=show_pie_chart
)
button_pie_chart.grid(row=0, column=2, padx=5, pady=5)

### ΓΡΑΦΙΚΗ ΑΠΕΙΚΟΝΙΣΗ ΠΟΣΟΣΤΟΥ ΣΥΝΑΙΣΘΗΜΑΤΟΣ ###
gauge_frame = tk.LabelFrame(root, text="Ποσοστό Συναισθήματος", bg=colour1, fg=colour4, font=('Arial', 12)) # πλάνο για το ποσοστό συναισθήματος
gauge_frame.pack(pady=10) # προσθήκη πεδίου για το ποσοστό συναισθήματος

gauge_label = tk.Label( 
    gauge_frame,
    textvariable= instant_score, # μεταβλητή για το ποσοστό συναισθήματος
    bg=colour1,
    fg=colour4,
    font=('Century Gothic', 12, 'bold') # γραμματοσειρά για το ποσοστό συναισθήματος
    )
gauge_label2 = tk.Label(
    gauge_frame,
    textvariable= instant_score_str, # μεταβλητή για το ποσοστό συναισθήματος
    bg=colour1,
    fg=colour4,
    font=('Century Gothic', 12, 'bold') # γραμματοσειρά για το ποσοστό συναισθήματος
    ) 
gauge_label.pack() # προσθήκη πεδίου για το ποσοστό συναισθήματος
gauge_label2.pack() # προσθήκη πεδίου για το ποσοστό συναισθήματος

msg_frame = tk.Frame(root, bg=colour1) # πλάνο για το μήνυμα
msg_frame.pack() # προσθήκη πεδίου για το μήνυμα

msg_label = tk.Label(msg_frame,
    textvariable= msg_diadikasia, # μεταβλητή για το μήνυμα
    bg= colour1, # χρώμα γραμματοσειράς για το μήνυμα
    fg=colour4, # χρώμα γραμματοσειράς για το μήνυμα
    font=('Century Gothic', 8, 'bold') # γραμματοσειρά για το μήνυμα
    )
msg_label.pack(pady=5)

### ΑΡΧΙΚΟΠΟΙΗΣΗ ΜΕΤΑΒΛΗΤΩΝ STRINGVAR ###
instant_score.set('0') # αρχικοποίηση της μεταβλητής instant_score
instant_score_str.set('') # αρχικοποίηση της μεταβλητής instant_score_str
msg_diadikasia.set('') # αρχικοποίηση της μεταβλητής msg_diadikasia

### ΣΥΝΔΕΣΗ EVENT ΜΕ ΠΛΗΚΤΡΟΛΟΓΙΟ ΠΡΟΑΙΡΕΤΙΚΑ ΣΕ ΣΧΟΛΙΑΣΜΟ, ΣΦΑΛΜΑ ΜΕ ΤΗΝ ΠΡΟΗΓΟΥΜΕΝΗ BIND ###
#root.bind("<Control-x>", cut_text) 
#root.bind("<Control-c>", copy_text)
#root.bind("<Control-v>", paste_text)

comment_text.bind('<FocusIn>', on_focus_in) ## Εντολή για να αλλάξει το χρώμα του κειμένου όταν το πεδίο κειμένου αποκτά εστίαση
# comment_text.bind('<FocusOut>', on_focus_out)
# root.bind("<Button-1>", remove_focus)
def file_open_dialog():
    filename = filedialog.askopenfilename(
        initialdir=".",
        title="Άνοιγμα αρχείου",
        filetypes=(('csv files', '*.csv'), ('All Files', '*.*')) # τύπος αρχείου
    )
    if filename:
        try:
            with open(filename, 'r', encoding='utf-8') as f: # ανοίγμα του αρχείου
                content = f.read() # ανάγνωση του περιεχομένου του αρχείου
            comment_text.delete(1.0, tk.END) # διαγραφή του περιεχομένου του comment_text
            comment_text.insert(tk.END, content) # εισαγωγή του περιεχομένου του αρχείου στο comment_text
            msg_diadikasia.set(f'Άνοιγμα αρχείου: {filename}') # οθόνη μηνύματος
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία ανοίγματος αρχείου:\n{e}") # οθόνη μηνύματος

def file_save():
    # Αποθήκευση στο ίδιο αρχείο (αν υπάρχει), αλλιώς "Αποθήκευση ως"
    # Για απλότητα, πάντα "Αποθήκευση ως"
    file_save_as()

def file_save_as():
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=(("Text files", "*.txt"), ("All Files", "*.*")) # τύπος αρχείου
    )
    if filename:
        try:
            with open(filename, 'w', encoding='utf-8') as f: # αποθήκευση στο αρχείο
                f.write(comment_text.get(1.0, tk.END)) # γράψε το περιεχόμενο του comment_text στο αρχείο
            msg_diadikasia.set(f'Αποθήκευση στο αρχείο: {filename}') # οθόνη μηνύματος
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία αποθήκευσης:\n{e}") # οθόνη μηνύματος

def file_print():
    try:
        # Απλή εκτύπωση του περιεχομένου του comment_text (π.χ. σε PDF printer)
        import tempfile, os
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') # δημιουργία ενός προσωρινού αρχείου
        temp.write(comment_text.get(1.0, tk.END)) # γράψε το περιεχόμενο του comment_text στο προσωρινό αρχείο
        temp.close() # κλείσιμο του προσωρινού αρχείου
        os.startfile(temp.name, "print") # εκτύπωση του προσωρινού αρχείου
        msg_diadikasia.set('Εκτύπωση...') # οθόνη μηνύματος
    except Exception as e:
        messagebox.showerror("Σφάλμα", f"Αποτυχία εκτύπωσης:\n{e}")


def show_pie_in_popup(df, parent_frame): # εμφάνιση του διαγράμματος σε popup
    # Καθάρισε προηγούμενο διάγραμμα αν υπάρχει
    for widget in parent_frame.winfo_children(): # καθάρισε το προηγούμενο διάγραμμα αν υπάρχει
        widget.destroy()
    sentiments = df.iloc[:, 1] # παίρνει τα συναισθήματα από το dataframe
    counts = Counter(sentiments) # υπολογίζει το πλήθος των συναισθημάτων
    fig = Figure(figsize=(3, 3)) # δημιουργία του διαγράμματος
    ax = fig.add_subplot(111) # προσθήκη του διαγράμματος στο παράθυρο
    ax.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%') # προσθήκη των συναισθημάτων και των ποσοστών
    ax.set_title("Διάγραμμα Συναισθημάτων") # τίτλος του διαγράμματος
    canvas = FigureCanvasTkAgg(fig, master=parent_frame) # δημιουργία του canvas
    canvas.draw() # σχεδίαση του διαγράμματος
    canvas.get_tk_widget().pack() # προσθήκη του canvas στο παράθυρο

### ΔΙΑΤΗΡΗΣΗ ΠΑΡΑΘΥΡΟΥ ΣΤΗΝ ΕΠΙΦΑΝΕΙΑ ###

# Σωστό κλείσιμο εφαρμογής 
def on_closing(): # Κλείσιμο εφαρμογής
    """Κλείσιμο εφαρμογής"""
    root.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing) # Κλείσιμο εφαρμογής

# Εμφάνιση welcome screen πριν το κύριο παράθυρο 
def start_application():
    """Εκκίνηση εφαρμογής με welcome screen"""   
    # Κρύβουμε το κύριο παράθυρο προσωρινά 
    root.withdraw()
    
    # Εμφάνιση welcome screen
    def show_main_after_welcome(): # Κλήση της συνάρτησης show_main_after_welcome
        root.deiconify()
        root.lift()
        root.focus_force()
    
    show_simple_welcome(show_main_after_welcome)  # Κλήση της συνάρτησης show_main_after_welcome

# Εκκίνηση εφαρμογής
if __name__ == "__main__":
    start_application()
    root.mainloop()

