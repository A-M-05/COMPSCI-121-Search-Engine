import tkinter as tk
from tkinter import messagebox
from src.search.searcher import Searcher
import webbrowser
import time


class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UCI ZotSearch Engine")
        self.root.geometry("800x600")

        self.searcher = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Loading status
        self.status_loading = tk.Label(
            root,
            text="Loading index, please wait...",
            fg="blue",
            font=("Arial", 11)
        )
        self.status_loading.pack(pady=10)
        self.root.update()

        try:
            self.searcher = Searcher()
            self.status_loading.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load index:\n{e}")
            self.root.destroy()
            return

        # --- UI LAYOUT ---
        header = tk.Label(
            root,
            text="ZotSearch",
            font=("Arial", 28, "bold"),
            fg="#0064a4"  # UCI Blue
        )
        header.pack(pady=15)

        # Search Bar Area
        search_frame = tk.Frame(root)
        search_frame.pack(pady=10, fill=tk.X, padx=40)

        self.query_var = tk.StringVar()

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.query_var,
            font=("Arial", 14)
        )
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5)
        self.search_entry.bind("<Return>", lambda event: self.perform_search())
        self.search_entry.focus_set()

        search_btn = tk.Button(
            search_frame,
            text="Search",
            command=self.perform_search,
            bg="#ffd200",  # UCI Gold
            font=("Arial", 10, "bold")
        )
        search_btn.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)

        clear_btn = tk.Button(
            search_frame,
            text="Clear",
            command=self.clear_search
        )
        clear_btn.pack(side=tk.LEFT, ipady=5)

        # Results Info Label
        self.info_label = tk.Label(
            root,
            text="",
            font=("Arial", 10, "italic"),
            anchor="w",
            justify="left"
        )
        self.info_label.pack(anchor=tk.W, padx=40)

        # Results Listbox with Scrollbar
        list_frame = tk.Frame(root)
        list_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_list = tk.Listbox(
            list_frame,
            font=("Arial", 12),
            yscrollcommand=scrollbar.set
        )
        self.result_list.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar.config(command=self.result_list.yview)

        # Double-click to open in browser
        self.result_list.bind("<Double-1>", self.open_url)

        # Footer
        footer = tk.Label(
            root,
            text="Double-click a URL to open in browser",
            font=("Arial", 8),
            fg="gray"
        )
        footer.pack(side=tk.BOTTOM, pady=5)

    def perform_search(self):
        query = self.query_var.get().strip()
        if not query or self.searcher is None:
            return

        self.result_list.delete(0, tk.END)
        self.info_label.config(text="Searching...")
        self.root.update_idletasks()

        try:
            start_time = time.time()
            results = self.searcher.search(query, top_k=20)
            end_time = time.time()
        except Exception as e:
            self.info_label.config(text="")
            messagebox.showerror("Search Error", f"Could not complete search:\n{e}")
            return

        duration = round((end_time - start_time) * 1000, 2)

        if not results:
            self.info_label.config(text=f"No results found for '{query}' ({duration} ms)")
            self.result_list.insert(tk.END, "Try a different search term.")
        else:
            self.info_label.config(text=f"Found {len(results)} results in {duration} ms")
            for url in results:
                self.result_list.insert(tk.END, url)

    def clear_search(self):
        self.query_var.set("")
        self.result_list.delete(0, tk.END)
        self.info_label.config(text="")
        self.search_entry.focus_set()

    def open_url(self, event):
        selection = self.result_list.curselection()
        if not selection:
            return

        url = self.result_list.get(selection[0])
        if isinstance(url, str) and url.startswith("http"):
            webbrowser.open(url)

    def on_close(self):
        try:
            if self.searcher is not None:
                self.searcher.close()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApp(root)
    root.mainloop()
    