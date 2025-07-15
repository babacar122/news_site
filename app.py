import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from datetime import datetime

class NewsHubAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NewsHub Admin Client")
        self.root.geometry("1000x700")
        
        self.base_url = "http://localhost:8000"
        self.api_url = f"{self.base_url}/api/"
        self.auth_token = None
        self.current_user = None
        
        self.setup_ui()
        
    def setup_ui(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_login_panel()
        
        self.admin_panel = ttk.Frame(self.main_frame)
        self.setup_admin_panel()
        
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X)
        self.update_status("Prêt - Non connecté")
    
    def setup_login_panel(self):
        self.login_panel = ttk.LabelFrame(
            self.main_frame, 
            text=" Connexion ", 
            padding=(15, 10))
        self.login_panel.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.login_panel, text="Nom d'utilisateur:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(self.login_panel, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_panel, text="Mot de passe:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(self.login_panel, show="*", width=30)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(self.login_panel)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.login_btn = ttk.Button(
            btn_frame, 
            text="Se connecter", 
            command=self.login,
            width=15
        )
        self.login_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Quitter", 
            command=self.root.quit,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        self.username_entry.focus_set()
        
    def setup_admin_panel(self):
        self.notebook = ttk.Notebook(self.admin_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.user_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.user_tab, text="Gestion Utilisateurs")
        self.setup_user_tab()
        
        self.article_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.article_tab, text="Gestion Articles")
        self.setup_article_tab()
        
        self.category_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.category_tab, text="Gestion Catégories")
        self.setup_category_tab()
    
    def setup_user_tab(self):
        columns = ("id", "username", "email", "first_name", "last_name", "role")
        self.user_tree = ttk.Treeview(
            self.user_tab, 
            columns=columns, 
            show="headings",
            selectmode="browse"
        )
        
        self.user_tree.heading("id", text="ID", anchor=tk.W)
        self.user_tree.heading("username", text="Nom d'utilisateur", anchor=tk.W)
        self.user_tree.heading("email", text="Email", anchor=tk.W)
        self.user_tree.heading("first_name", text="Prénom", anchor=tk.W)
        self.user_tree.heading("last_name", text="Nom", anchor=tk.W)
        self.user_tree.heading("role", text="Rôle", anchor=tk.W)
        
        self.user_tree.column("id", width=50, stretch=tk.NO)
        self.user_tree.column("username", width=120)
        self.user_tree.column("email", width=180)
        self.user_tree.column("first_name", width=100)
        self.user_tree.column("last_name", width=100)
        self.user_tree.column("role", width=80)
        
        yscroll = ttk.Scrollbar(
            self.user_tab, 
            orient=tk.VERTICAL, 
            command=self.user_tree.yview
        )
        self.user_tree.configure(yscroll=yscroll.set)
        
        self.user_tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        
        tool_frame = ttk.Frame(self.user_tab)
        tool_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        
        ttk.Button(
            tool_frame, 
            text="Actualiser", 
            command=self.load_users
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            tool_frame, 
            text="Ajouter", 
            command=self.show_add_user_dialog
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            tool_frame, 
            text="Modifier", 
            command=self.show_edit_user_dialog
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            tool_frame, 
            text="Supprimer", 
            command=self.delete_user
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            tool_frame, 
            text="Générer Token", 
            command=self.generate_token
        ).pack(side=tk.LEFT, padx=2)
        
        self.user_tab.rowconfigure(0, weight=1)
        self.user_tab.columnconfigure(0, weight=1)
    
    def setup_article_tab(self):
        columns = ("id", "title", "author", "category", "pub_date")
        self.article_tree = ttk.Treeview(
            self.article_tab, 
            columns=columns, 
            show="headings",
            selectmode="browse"
        )
        
        self.article_tree.heading("id", text="ID", anchor=tk.W)
        self.article_tree.heading("title", text="Titre", anchor=tk.W)
        self.article_tree.heading("author", text="Auteur", anchor=tk.W)
        self.article_tree.heading("category", text="Catégorie", anchor=tk.W)
        self.article_tree.heading("pub_date", text="Date", anchor=tk.W)
        
        self.article_tree.column("id", width=50, stretch=tk.NO)
        self.article_tree.column("title", width=250)
        self.article_tree.column("author", width=120)
        self.article_tree.column("category", width=120)
        self.article_tree.column("pub_date", width=100)
        
        yscroll = ttk.Scrollbar(
            self.article_tab, 
            orient=tk.VERTICAL, 
            command=self.article_tree.yview
        )
        self.article_tree.configure(yscroll=yscroll.set)
        
        self.article_tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        
        tool_frame = ttk.Frame(self.article_tab)
        tool_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        
        ttk.Button(
            tool_frame, 
            text="Actualiser", 
            command=self.load_articles
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            tool_frame, 
            text="Nouvel Article", 
            command=self.show_add_article_dialog
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            tool_frame, 
            text="Voir Détails", 
            command=self.show_article_details
        ).pack(side=tk.LEFT, padx=2)
        
        self.format_var = tk.StringVar(value="json")
        format_frame = ttk.Frame(tool_frame)
        format_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT)
        ttk.Radiobutton(
            format_frame, 
            text="JSON", 
            variable=self.format_var, 
            value="json"
        ).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(
            format_frame, 
            text="XML", 
            variable=self.format_var, 
            value="xml"
        ).pack(side=tk.LEFT, padx=2)
        
        self.article_tab.rowconfigure(0, weight=1)
        self.article_tab.columnconfigure(0, weight=1)
    
    def setup_category_tab(self):
        ttk.Label(
            self.category_tab, 
            text="Gestion des catégories (à implémenter)"
        ).pack(pady=50)
    
    def update_status(self, message):
        self.status_var.set(message)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Champs manquants", "Veuillez saisir un nom d'utilisateur et un mot de passe")
            return
        
        try:
            response = requests.post(
                f"{self.api_url}auth/",
                json={'username': username, 'password': password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.current_user = username
                self.update_status(f"Connecté en tant que {username}")
                
                self.login_panel.pack_forget()
                self.admin_panel.pack(fill=tk.BOTH, expand=True)
                
                self.load_users()
                self.load_articles()
                
            else:
                error_msg = response.json().get('error', 'Échec de la connexion')
                messagebox.showerror("Erreur", error_msg)
                self.update_status("Échec de la connexion")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Impossible de se connecter au serveur: {str(e)}")
            self.update_status("Erreur de connexion")
    
    def load_users(self):
        if not self.auth_token:
            return
        
        try:
            headers = {'Authorization': f'Token {self.auth_token}'}
            response = requests.get(f"{self.api_url}users/", headers=headers)
            
            if response.status_code == 200:
                for item in self.user_tree.get_children():
                    self.user_tree.delete(item)
                
                data = response.json()
                for user in data.get('users', []):
                    self.user_tree.insert("", tk.END, values=(
                        user.get('id'),
                        user.get('username'),
                        user.get('email'),
                        user.get('first_name'),
                        user.get('last_name'),
                        user.get('role')
                    ))
                
                self.update_status(f"{len(data.get('users', []))} utilisateurs chargés")
            else:
                error_msg = response.json().get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_msg)
                self.update_status("Erreur lors du chargement des utilisateurs")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur réseau: {str(e)}")
            self.update_status("Erreur réseau")
    
    def load_articles(self):
        try:
            params = {'format': self.format_var.get()}
            response = requests.get(f"{self.api_url}articles/", params=params)
            
            if response.status_code == 200:
                for item in self.article_tree.get_children():
                    self.article_tree.delete(item)
                
                data = response.json()
                for article in data:
                    pub_date = datetime.strptime(
                        article.get('pub_date'),
                        '%Y-%m-%dT%H:%M:%S.%fZ'
                    ).strftime('%d/%m/%Y %H:%M')
                    
                    self.article_tree.insert("", tk.END, values=(
                        article.get('id'),
                        article.get('title'),
                        article.get('author'),
                        article.get('category'),
                        pub_date
                    ))
                
                self.update_status(f"{len(data)} articles chargés")
            else:
                error_msg = response.json().get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_msg)
                self.update_status("Erreur lors du chargement des articles")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur réseau: {str(e)}")
            self.update_status("Erreur réseau")
    
    def show_add_user_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un utilisateur")
        dialog.transient(self.root)
        dialog.grab_set()
        
        username_var = tk.StringVar()
        email_var = tk.StringVar()
        first_name_var = tk.StringVar()
        last_name_var = tk.StringVar()
        password_var = tk.StringVar()
        confirm_var = tk.StringVar()
        role_var = tk.StringVar(value="VISITOR")
        
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Nom d'utilisateur:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=username_var).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Email:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=email_var).grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Prénom:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=first_name_var).grid(
            row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Nom:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=last_name_var).grid(
            row=3, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Mot de passe:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=password_var, show="*").grid(
            row=4, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Confirmation:").grid(
            row=5, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=confirm_var, show="*").grid(
            row=5, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Rôle:").grid(
            row=6, column=0, padx=5, pady=5, sticky="e")
        ttk.Combobox(
            form_frame, 
            textvariable=role_var, 
            values=["VISITOR", "EDITOR", "ADMIN"],
            state="readonly"
        ).grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Annuler", 
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Enregistrer", 
            command=lambda: self.save_new_user(
                dialog,
                username_var.get(),
                email_var.get(),
                first_name_var.get(),
                last_name_var.get(),
                password_var.get(),
                confirm_var.get(),
                role_var.get()
            )
        ).pack(side=tk.LEFT, padx=5)
        
        form_frame.columnconfigure(1, weight=1)
        dialog.resizable(False, False)
    
    def save_new_user(self, dialog, username, email, first_name, last_name, password, confirm, role):
        if not username or not password:
            messagebox.showwarning("Champs manquants", "Le nom d'utilisateur et le mot de passe sont obligatoires")
            return
        
        if password != confirm:
            messagebox.showwarning("Erreur", "Les mots de passe ne correspondent pas")
            return
        
        user_data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'role': role
        }
        
        try:
            headers = {'Authorization': f'Token {self.auth_token}'}
            response = requests.post(
                f"{self.api_url}users/",
                json=user_data,
                headers=headers
            )
            
            if response.status_code == 201:
                messagebox.showinfo("Succès", "Utilisateur créé avec succès")
                self.load_users()
                dialog.destroy()
            else:
                error_msg = response.json().get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_msg)
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur réseau: {str(e)}")
    
    def show_edit_user_dialog(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un utilisateur à modifier")
            return
        
        user_id = self.user_tree.item(selected[0])['values'][0]
        
        try:
            headers = {'Authorization': f'Token {self.auth_token}'}
            response = requests.get(f"{self.api_url}users/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user = next((u for u in data.get('users', []) if u.get('id') == user_id), None)
                
                if user:
                    self._show_edit_user_dialog(user)
                else:
                    messagebox.showerror("Erreur", "Utilisateur non trouvé")
            else:
                error_msg = response.json().get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_msg)
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur réseau: {str(e)}")
    
    def _show_edit_user_dialog(self, user):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Modifier {user.get('username')}")
        dialog.transient(self.root)
        dialog.grab_set()
        
        username_var = tk.StringVar(value=user.get('username'))
        email_var = tk.StringVar(value=user.get('email'))
        first_name_var = tk.StringVar(value=user.get('first_name'))
        last_name_var = tk.StringVar(value=user.get('last_name'))
        role_var = tk.StringVar(value=user.get('role'))
        
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Nom d'utilisateur:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=username_var, state='readonly').grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Email:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=email_var).grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Prénom:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=first_name_var).grid(
            row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Nom:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(form_frame, textvariable=last_name_var).grid(
            row=3, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Rôle:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e")
        ttk.Combobox(
            form_frame, 
            textvariable=role_var, 
            values=["VISITOR", "EDITOR", "ADMIN"],
            state="readonly"
        ).grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Annuler", 
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Enregistrer", 
            command=lambda: self.save_user_changes(
                dialog,
                user.get('id'),
                email_var.get(),
                first_name_var.get(),
                last_name_var.get(),
                role_var.get()
            )
        ).pack(side=tk.LEFT, padx=5)
        
        form_frame.columnconfigure(1, weight=1)
        dialog.resizable(False, False)
    
    def save_user_changes(self, dialog, user_id, email, first_name, last_name, role):
        user_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': role
        }
        
        try:
            headers = {'Authorization': f'Token {self.auth_token}'}
            response = requests.put(
                f"{self.api_url}users/{user_id}/",
                json=user_data,
                headers=headers
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Succès", "Utilisateur mis à jour avec succès")
                self.load_users()
                dialog.destroy()
            else:
                error_msg = response.json().get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_msg)
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur réseau: {str(e)}")
    
    def delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un utilisateur à supprimer")
            return
        
        user_id = self.user_tree.item(selected[0])['values'][0]
        username = self.user_tree.item(selected[0])['values'][1]
        
        if not messagebox.askyesno(
            "Confirmation", 
            f"Êtes-vous sûr de vouloir supprimer l'utilisateur {username} ?"
        ):
            return
        
        try:
            headers = {'Authorization': f'Token {self.auth_token}'}
            response = requests.delete(
                f"{self.api_url}users/{user_id}/",
                headers=headers
            )
            
            if response.status_code == 204:
                messagebox.showinfo("Succès", "Utilisateur supprimé avec succès")
                self.load_users()
            else:
                error_msg = response.json().get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_msg)
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur réseau: {str(e)}")
    
    def generate_token(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un utilisateur")
            return
        
        user_id = self.user_tree.item(selected[0])['values'][0]
        username = self.user_tree.item(selected[0])['values'][1]
        
        try:
            headers = {'Authorization': f'Token {self.auth_token}'}
            response = requests.post(
                f"{self.api_url}users/{user_id}/generate_token/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                
                token_dialog = tk.Toplevel(self.root)
                token_dialog.title(f"Token pour {username}")
                
                tk.Label(
                    token_dialog, 
                    text=f"Token généré pour {username}:",
                    font=('Helvetica', 10, 'bold')
                ).pack(pady=10)
                
                token_text = scrolledtext.ScrolledText(
                    token_dialog, 
                    width=50, 
                    height=4,
                    wrap=tk.WORD,
                    font=('Courier', 10)
                )
                token_text.pack(padx=10, pady=5)
                token_text.insert(tk.END, token)
                token_text.config(state='disabled')
                
                tk.Button(
                    token_dialog, 
                    text="Fermer", 
                    command=token_dialog.destroy
                ).pack(pady=10)
                
            else:
                error_msg = response.json().get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_msg)
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur réseau: {str(e)}")
    
    def show_add_article_dialog(self):
        messagebox.showinfo("Information", "Fonctionnalité à implémenter")
    
    def show_article_details(self):
        selected = self.article_tree.selection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un article")
            return
        
        article_id = self.article_tree.item(selected[0])['values'][0]
        
        try:
            response = requests.get(f"{self.api_url}articles/{article_id}/")
            
            if response.status_code == 200:
                article = response.json()
                self._show_article_details(article)
            else:
                error_msg = response.json().get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_msg)
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur", f"Erreur réseau: {str(e)}")
    
    def _show_article_details(self, article):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Détails de l'article: {article.get('title')}")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        info_frame = ttk.LabelFrame(main_frame, text="Informations", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Titre: {article.get('title')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Auteur: {article.get('author')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Catégorie: {article.get('category')}").pack(anchor=tk.W)
        pub_date = datetime.strptime(
            article.get('pub_date'),
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ).strftime('%d/%m/%Y à %H:%M')
        ttk.Label(info_frame, text=f"Publié le: {pub_date}").pack(anchor=tk.W)
        
        content_frame = ttk.LabelFrame(main_frame, text="Contenu", padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        content_text = scrolledtext.ScrolledText(
            content_frame, 
            wrap=tk.WORD,
            width=80,
            height=20
        )
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert(tk.END, article.get('content'))
        content_text.config(state='disabled')
        
        ttk.Button(
            main_frame, 
            text="Fermer", 
            command=dialog.destroy
        ).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = NewsHubAdminApp(root)
    root.mainloop()