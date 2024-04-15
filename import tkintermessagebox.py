import tkinter as tk
from tkinter import font, messagebox, PhotoImage

def sign_in():
    username = entry_username.get()
    password = entry_password.get()
    messagebox.showinfo("Sign In", f"Sign in requested for user: {username}")

def forgot_password():
    messagebox.showinfo("Forgot Password", "Redirect to password recovery form.")

def sign_up(event):
    messagebox.showinfo("Sign Up", "Redirect to sign up form.")

def toggle_password():
    if entry_password.cget('show') == '':
        entry_password.config(show='*')
        button_eye.config(text='👁️')
    else:
        entry_password.config(show='')
        button_eye.config(text='👁️‍🗨️')

app = tk.Tk()
app.title("Login Form")
app.configure(bg='#4285F4')  
app.geometry('400x400')  

default_font = font.nametofont("TkDefaultFont")
default_font.configure(size=14)
link_font = font.Font(family="Helvetica", size=10, underline=True)

tk.Label(app, text="Username:", bg='#4285F4', fg='white', font=default_font).grid(row=0, column=0, sticky="e", padx=10)
tk.Label(app, text="Password:", bg='#4285F4', fg='white', font=default_font).grid(row=1, column=0, sticky="e", padx=10)

entry_username = tk.Entry(app, font=default_font)
entry_password = tk.Entry(app, font=default_font, show="*")
entry_username.grid(row=0, column=1, padx=10)
entry_password.grid(row=1, column=1, padx=10)

button_eye = tk.Button(app, text="👁️", command=toggle_password, font=default_font, bg='white', borderwidth=0)
button_eye.grid(row=1, column=2)

sign_in_button = tk.Button(app, text="Sign In", command=sign_in, font=default_font, bg='white', fg='#4285F4')
sign_in_button.grid(row=2, column=0, columnspan=3, padx=20, pady=10)

forgot_button = tk.Label(app, text="Forgot your password?", font=link_font, fg="yellow", bg='#4285F4', cursor="hand2")
forgot_button.grid(row=3, column=0, columnspan=3, pady=(5, 20))
forgot_button.bind("<Button-1>", lambda e: forgot_password())

sign_up_button = tk.Label(app, text="Don't have an account? Sign up here.", font=link_font, fg="yellow", bg='#4285F4', cursor="hand2")
sign_up_button.grid(row=4, column=0, columnspan=3)
sign_up_button.bind("<Button-1>", sign_up)

app.mainloop()





