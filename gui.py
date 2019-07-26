import tkinter as gui
from tkinter import Label, Button, Entry, messagebox
import Connection


def get_repositories():
    """Controls "Look for licenses" button; checks for valid credentials, and creates second window
       that matches licenses with repos. If no license is found for a repository, a button to add a license
       will display.
    """
    
    username = userEntry.get()
    organization = orgEntry.get()
    password = passEntry.get()

    if username == "":
        messagebox.showinfo("Missing Username", "Please enter your GitHub account username in the field provided.")
        return
    if organization == "":
        messagebox.showinfo("Missing Organization", "Please enter a GitHub organization in  the field provided")
        return
    if password == "":
        messagebox.showinfo("Missing Password", "Please enter your GitHub account password.")
        return

    connection = Connection.Connection(username, password)
    repo_licenses = connection.get_repos(organization)

    if repo_licenses is None:
        messagebox.showerror("Invalid credentials.", "Please enter valid credentials.")
    else:
        repo_win = gui.Tk()
        repo_win.title("Repositories")
        row = 0
        for key in repo_licenses:
            Label(repo_win, text=key, justify=gui.LEFT).grid(padx=10, pady=7, row=row, column=0)
            if repo_licenses[key] == "No License":
                add_button = Button(repo_win, text="Add license",
                                    command=lambda: get_licenses(connection, organization, key, add_button),
                                    bg="#b3b8ba")
                add_button.grid(padx=10, pady=7, row=row, column=1)
            else:
                Label(repo_win, text=repo_licenses[key], justify=gui.LEFT).grid(padx=10, pady=7, row=row, column=1)
            row = row + 1


def get_licenses(connection, organization, repo_name, add_button):
    """Controls "add license" button. Attempts to add license, and shows message explaining result of 
    attempt.
    Parameters
    -----------
        connections : Connection
            Connection object that contains authorization for current user
        organization : str
            Name of organization that was searched
        repo_name : str
            Name of repo to which license is being added
        add_button : Button
            Button object that was used to request license
    """
    
    if connection.get_license(organization, repo_name):
        messagebox.showinfo("Success", "A new branch with an MIT license was created, and a pull request was sent.")
        add_button["state"] = "disabled"
    else:
        messagebox.showinfo("Oops", "Request not completed. Have you already sent a pull request?")


main = gui.Tk()
main.title("GitHub License Adder")

Label(main, text="Username").pack(padx=40, pady=2)
userEntry = Entry(main)
userEntry.pack(padx=40, pady=5)

Label(main, text="Organization").pack(padx=40, pady=2)
orgEntry = Entry(main)
orgEntry.pack(padx=40, pady=5)

Label(main, text="Password").pack(padx=40, pady=2)
passEntry = Entry(main, show="*")
passEntry.pack(padx=40, pady=2)

Button(main, text="Look for licenses", bg="#b3b8ba", command=get_repositories).pack(padx=40, pady=10)
main.mainloop()

