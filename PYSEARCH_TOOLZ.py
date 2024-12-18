import os
import re
import shutil
import time
import tkinter as tk
from tkinter import filedialog, messagebox, Spinbox, Toplevel, Listbox
from tkinter.scrolledtext import ScrolledText


class PyGrepSim:
    def __init__(self, root):
        self.root = root
        self.root.title("PyGrepSim - Multi-Keyword Search")
        
        # Initialize options
        self.var_recursive = tk.BooleanVar()
        self.var_case_insensitive = tk.BooleanVar()
        self.path = os.path.expanduser("~")
        self.matched_files = []
        self.ignored_extensions = set()  # Set of extensions to ignore
        
        # List of all available extensions (populate dynamically if needed)
        self.all_extensions = ['.exe', '.jpg', '.png', '.pdf', '.docx', '.xlsx', '.zip', '.rar', '.mp3', '.mp4']
        
        # GUI setup
        self.setup_gui()
        
    def setup_gui(self):
        self.create_options_frame()
        self.create_file_frame()
        self.create_lines_control_frame()
        self.create_text_area()
        
    def create_options_frame(self):
        frame_options = tk.Frame(self.root)
        frame_options.pack(pady=5, padx=5, fill='x')
        
        tk.Label(frame_options, text="Search Pattern(s):").grid(row=0, column=0, padx=5)
        self.entry_pattern = tk.Entry(frame_options, width=50)
        self.entry_pattern.grid(row=0, column=1, padx=5)
        
        tk.Checkbutton(frame_options, text="Recursive", variable=self.var_recursive).grid(row=0, column=2, padx=5)
        tk.Checkbutton(frame_options, text="Case Insensitive", variable=self.var_case_insensitive).grid(row=0, column=3, padx=5)
        
        tk.Button(frame_options, text="Browse Directory", command=self.open_directory).grid(row=0, column=4, padx=5)
        tk.Button(frame_options, text="Set Ignored Extensions", command=self.open_extension_selector).grid(row=0, column=5, padx=5)
        
    def open_extension_selector(self):
        # Create a new window for selecting extensions
        ext_window = Toplevel(self.root)
        ext_window.title("Select Extensions to Ignore")
        
        tk.Label(ext_window, text="Select file extensions to ignore:").pack(pady=5)
        
        # Create a list of checkboxes for extensions
        self.extension_vars = {ext: tk.BooleanVar(value=(ext in self.ignored_extensions)) for ext in self.all_extensions}
        for ext, var in self.extension_vars.items():
            tk.Checkbutton(ext_window, text=ext, variable=var).pack(anchor='w')
        
        tk.Button(ext_window, text="Save", command=lambda: self.save_ignored_extensions(ext_window)).pack(pady=5)
        
    def save_ignored_extensions(self, window):
        # Update the set of ignored extensions
        self.ignored_extensions = {ext for ext, var in self.extension_vars.items() if var.get()}
        window.destroy()  # Close the extension selector window
        messagebox.showinfo("Extensions Updated", f"Ignored extensions: {', '.join(self.ignored_extensions)}")
        
    def search_for_pattern(self):
        self.clear_all()
        pattern_input = self.entry_pattern.get()
        if not pattern_input:
            messagebox.showwarning("No Pattern", "Please enter at least one search pattern.")
            return

        # Split patterns by commas and strip whitespace
        patterns = [p.strip() for p in pattern_input.split(',') if p.strip()]
        if not patterns:
            messagebox.showwarning("Invalid Pattern", "Please enter valid search patterns separated by commas.")
            return

        lines_before = int(self.spinbox_before.get())
        lines_after = int(self.spinbox_after.get())
        flags = re.IGNORECASE if self.var_case_insensitive.get() else 0

        # Perform search
        for root, _, files in os.walk(self.path) if self.var_recursive.get() else [(self.path, [], os.listdir(self.path))]:
            for file in files:
                file_path = os.path.join(root, file)
                if not any(file_path.endswith(ext) for ext in self.ignored_extensions):  # Exclude ignored extensions
                    if file_path.endswith(('.txt', '.log', '.py')):  # Process text-based files
                        self.process_file(file_path, patterns, flags, lines_before, lines_after)

        if not self.matched_files:
            messagebox.showinfo("No Matches", "No matches found.")
    
    def process_file(self, file_path, patterns, flags, lines_before, lines_after):
        try:
            with open(file_path, 'r', errors='ignore') as f:
                lines = f.readlines()
                
            matched = False
            for i, line in enumerate(lines):
                if any(re.search(pattern, line, flags) for pattern in patterns):
                    if not matched:
                        self.matched_files.append(file_path)
                        self.listbox_files.insert(tk.END, file_path)
                        matched = True
                    
                    # Display surrounding lines
                    start = max(i - lines_before, 0)
                    end = min(i + lines_after + 1, len(lines))
                    self.text_area.insert(tk.END, f"\n--- {file_path} ---\n")
                    self.text_area.insert(tk.END, ''.join(lines[start:end]))
                    self.text_area.insert(tk.END, '-'*50 + '\n')
                    
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    def create_file_frame(self):
        frame_file = tk.Frame(self.root)
        frame_file.pack(pady=5, padx=5, fill='x')
        
        tk.Label(frame_file, text="Matched Files:").pack(side='left')
        self.listbox_files = Listbox(frame_file, width=50, height=10)
        self.listbox_files.pack(side='left', fill='both', expand=True)
        
        tk.Button(frame_file, text="Group & Copy Files", command=self.group_and_copy_files).pack(side='left', padx=5)
        
    def create_lines_control_frame(self):
        frame_lines = tk.Frame(self.root)
        frame_lines.pack(pady=5, padx=5, fill='x')
        
        tk.Label(frame_lines, text="Lines Before:").pack(side='left')
        self.spinbox_before = Spinbox(frame_lines, from_=0, to=10, width=5)
        self.spinbox_before.pack(side='left')
        self.spinbox_before.insert(0, 1)
        
        tk.Label(frame_lines, text="Lines After:").pack(side='left')
        self.spinbox_after = Spinbox(frame_lines, from_=0, to=10, width=5)
        self.spinbox_after.pack(side='left')
        self.spinbox_after.insert(0, 3)
        
        tk.Button(frame_lines, text="Search", command=self.search_for_pattern).pack(side='left', padx=10)
        tk.Button(frame_lines, text="Clear", command=self.clear_all).pack(side='left', padx=5)
        
    def create_text_area(self):
        self.text_area = ScrolledText(self.root, width=100, height=25)
        self.text_area.pack(pady=5, padx=5)
        
    def open_directory(self):
        self.path = filedialog.askdirectory()
        if self.path:
            messagebox.showinfo("Directory Selected", f"Searching in: {self.path}")
        
    def group_and_copy_files(self):
        if not self.matched_files:
            messagebox.showinfo("No Files", "No matched files to group and copy.")
            return
        
        target_dir = filedialog.askdirectory(title="Select Destination Directory")
        if not target_dir:
            return
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        dest_dir = os.path.join(target_dir, f"matched_files_{timestamp}")
        os.makedirs(dest_dir, exist_ok=True)
        
        for file in self.matched_files:
            shutil.copy(file, dest_dir)
        
        messagebox.showinfo("Files Copied", f"Files copied to: {dest_dir}")
        
    def clear_all(self):
        self.text_area.delete('1.0', tk.END)
        self.listbox_files.delete(0, tk.END)
        self.matched_files.clear()


if __name__ == "__main__":
    root = tk.Tk()
    app = PyGrepSim(root)
    root.mainloop()
