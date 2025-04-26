import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import random


class QuestionSet:
    """Represents a set of quiz questions"""
    def __init__(self, name="New Question Set", questions=None):
        self.name = name
        self.questions = questions or []
        
    def add_question(self, question, answer, points):
        """Add a new question to the set"""
        self.questions.append({
            "question": question,
            "answer": answer,
            "points": points
        })
        
    def remove_question(self, index):
        """Remove a question by index"""
        if 0 <= index < len(self.questions):
            del self.questions[index]
            
    def update_question(self, index, question, answer, points):
        """Update an existing question"""
        if 0 <= index < len(self.questions):
            self.questions[index] = {
                "question": question,
                "answer": answer,
                "points": points
            }
    
    def to_dict(self):
        """Convert to a dictionary for serialization"""
        return {
            "name": self.name,
            "questions": self.questions
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a QuestionSet from a dictionary"""
        return cls(
            name=data.get("name", "Unknown Set"),
            questions=data.get("questions", [])
        )


class QuestionSetManager:
    """Manages creation, editing, saving and loading of question sets"""
    def __init__(self, root, callback=None):
        self.root = root
        self.callback = callback
        self.question_sets = []
        self.current_set = None
        
        # Try to load default question sets directory
        self.sets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "question_sets")
        os.makedirs(self.sets_dir, exist_ok=True)
        
        # Add default set if none exist
        self.load_default_set()
        
    def load_default_set(self):
        """Load the default question set or create if none exists"""
        # Check if any question set files exist in the sets directory
        set_files = [f for f in os.listdir(self.sets_dir) if f.endswith('.json')]
        
        if not set_files:
            # Create a default animal set
            animal_set = QuestionSet("Animals")
            animal_set.add_question("I live on a farm. I make milk.", "Cow", 15)
            animal_set.add_question("I have a long neck and I eat leaves.", "Giraffe", 20)
            animal_set.add_question("I can fly and I chirp.", "Bird", 10)
            animal_set.add_question("I am man's best friend.", "Dog", 10)
            animal_set.add_question("I say 'meow'.", "Cat", 10)
            animal_set.add_question("I have stripes and run fast.", "Zebra", 15)
            animal_set.add_question("I swim and have fins.", "Fish", 10)
            animal_set.add_question("I jump and live in ponds.", "Frog", 10)
            animal_set.add_question("I have a trunk and big ears.", "Elephant", 25)
            
            # Save and add to memory
            self.question_sets.append(animal_set)
            self.current_set = animal_set
            self.save_question_set(animal_set)
            
            # Create another example set for variety
            math_set = QuestionSet("Basic Math")
            math_set.add_question("What is 5 + 7?", "12", 10)
            math_set.add_question("What is 8 × 9?", "72", 15)
            math_set.add_question("What is 64 ÷ 8?", "8", 10)
            math_set.add_question("What is 15 - 6?", "9", 10)
            math_set.add_question("What is 3² (3 squared)?", "9", 15)
            math_set.add_question("What is half of 42?", "21", 10)
            math_set.add_question("What is 7 × 7?", "49", 10)
            math_set.add_question("What is 13 + 28?", "41", 20)
            math_set.add_question("What is 100 - 35?", "65", 15)
            
            # Save and add to memory
            self.question_sets.append(math_set)
            self.save_question_set(math_set)
        else:
            # Load all existing question sets
            for filename in set_files:
                filepath = os.path.join(self.sets_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        question_set = QuestionSet.from_dict(data)
                        self.question_sets.append(question_set)
                except Exception as e:
                    print(f"Error loading question set {filename}: {e}")
            
            # Set the first one as current
            if self.question_sets:
                self.current_set = self.question_sets[0]
    
    def create_new_set(self):
        """Create a new empty question set"""
        name = simpledialog.askstring("New Question Set", "Enter name for the new question set:")
        if name:
            new_set = QuestionSet(name)
            self.question_sets.append(new_set)
            self.current_set = new_set
            return new_set
        return None
    
    def save_question_set(self, question_set):
        """Save a question set to a file"""
        if not question_set:
            return False
            
        # Create a valid filename
        filename = "".join(c for c in question_set.name if c.isalnum() or c in " _-").strip()
        filename = filename.replace(" ", "_").lower() + ".json"
        filepath = os.path.join(self.sets_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(question_set.to_dict(), f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving question set: {e}")
            return False
    
    def load_question_set(self, filepath=None):
        """Load a question set from a file"""
        if not filepath:
            filepath = filedialog.askopenfilename(
                title="Load Question Set",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                initialdir=self.sets_dir
            )
            
        if not filepath:
            return None
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                question_set = QuestionSet.from_dict(data)
                
                # Check if we already have this set loaded
                for i, qs in enumerate(self.question_sets):
                    if qs.name == question_set.name:
                        # Replace the existing set
                        self.question_sets[i] = question_set
                        return question_set
                
                # It's a new set, add it
                self.question_sets.append(question_set)
                return question_set
                
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading question set: {e}")
            return None
    
    def delete_question_set(self, question_set):
        """Delete a question set"""
        if question_set in self.question_sets:
            # Ask for confirmation
            if messagebox.askyesno("Confirm Delete", 
                                  f"Are you sure you want to delete the question set '{question_set.name}'?"):
                # Remove from memory
                self.question_sets.remove(question_set)
                
                # Remove file if it exists
                filename = "".join(c for c in question_set.name if c.isalnum() or c in " _-").strip()
                filename = filename.replace(" ", "_").lower() + ".json"
                filepath = os.path.join(self.sets_dir, filename)
                
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        messagebox.showwarning("Delete Warning", 
                                              f"Could not delete file: {e}")
                
                # Update current set
                if self.question_sets:
                    self.current_set = self.question_sets[0]
                else:
                    self.current_set = None
                    
                return True
        return False
    
    def show_manager(self):
        """Show the question set manager UI"""
        # Create a new top-level window
        manager_window = tk.Toplevel(self.root)
        manager_window.title("Question Set Manager")
        manager_window.minsize(800, 600)
        
        # Set background color
        bg_color = "#333333"  # Dark gray background
        button_color = "#666666"  # Medium gray for buttons
        manager_window.configure(bg=bg_color)
        
        # Configure grid
        manager_window.columnconfigure(0, weight=1)
        manager_window.rowconfigure(0, weight=0)  # Header
        manager_window.rowconfigure(1, weight=1)  # Main content
        manager_window.rowconfigure(2, weight=0)  # Footer
        
        # Header frame
        header_frame = tk.Frame(manager_window, bg=bg_color, pady=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20)
        
        tk.Label(
            header_frame,
            text="Question Set Manager",
            font=("Arial", 20, "bold"),
            bg=bg_color,
            fg="#FFD700"  # Gold
        ).pack(side=tk.LEFT, pady=10)
        
        # Button frame for header actions
        header_btn_frame = tk.Frame(header_frame, bg=bg_color)
        header_btn_frame.pack(side=tk.RIGHT, pady=10)
        
        # New Set button
        new_btn = tk.Frame(header_btn_frame, bg="#4CAF50", width=100, height=35)  # Green
        new_btn.pack(side=tk.LEFT, padx=5)
        new_btn.pack_propagate(False)
        
        new_label = tk.Label(
            new_btn,
            text="New Set",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white"
        )
        new_label.pack(expand=True, fill=tk.BOTH)
        
        # Load Set button
        load_btn = tk.Frame(header_btn_frame, bg="#2196F3", width=100, height=35)  # Blue
        load_btn.pack(side=tk.LEFT, padx=5)
        load_btn.pack_propagate(False)
        
        load_label = tk.Label(
            load_btn,
            text="Load Set",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white"
        )
        load_label.pack(expand=True, fill=tk.BOTH)
        
        # Main content frame
        content_frame = tk.Frame(manager_window, bg=bg_color)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Configure content grid
        content_frame.columnconfigure(0, weight=2)  # Set list
        content_frame.columnconfigure(1, weight=5)  # Question editor
        content_frame.rowconfigure(0, weight=1)
        
        # Left side - Set list
        set_list_frame = tk.Frame(content_frame, bg=bg_color, highlightbackground="#666666", highlightthickness=1)
        set_list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Set list header
        tk.Label(
            set_list_frame,
            text="Question Sets",
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg="white"
        ).pack(pady=10)
        
        # Create a listbox with a scrollbar for sets
        sets_container = tk.Frame(set_list_frame, bg=bg_color)
        sets_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(sets_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Use custom colors for the listbox
        set_listbox = tk.Listbox(
            sets_container,
            bg="#444444",
            fg="white",
            font=("Arial", 12),
            selectbackground="#2196F3",
            highlightbackground="#666666",
            highlightthickness=1,
            exportselection=0,
            yscrollcommand=scrollbar.set
        )
        set_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=set_listbox.yview)
        
        # Populate the listbox
        for q_set in self.question_sets:
            set_listbox.insert(tk.END, q_set.name)
            
        # Select the current set
        if self.current_set:
            for i, q_set in enumerate(self.question_sets):
                if q_set == self.current_set:
                    set_listbox.selection_set(i)
                    set_listbox.see(i)
                    break
        
        # Set actions buttons below the list
        set_actions_frame = tk.Frame(set_list_frame, bg=bg_color)
        set_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Rename button
        rename_btn = tk.Frame(set_actions_frame, bg=button_color, width=80, height=30)
        rename_btn.pack(side=tk.LEFT, padx=2)
        rename_btn.pack_propagate(False)
        
        rename_label = tk.Label(
            rename_btn,
            text="Rename",
            font=("Arial", 11),
            bg=button_color,
            fg="white"
        )
        rename_label.pack(expand=True, fill=tk.BOTH)
        
        # Delete button
        delete_btn = tk.Frame(set_actions_frame, bg="#F44336", width=80, height=30)  # Red
        delete_btn.pack(side=tk.RIGHT, padx=2)
        delete_btn.pack_propagate(False)
        
        delete_label = tk.Label(
            delete_btn,
            text="Delete",
            font=("Arial", 11),
            bg="#F44336",
            fg="white"
        )
        delete_label.pack(expand=True, fill=tk.BOTH)
        
        # Right side - Question editor
        question_editor_frame = tk.Frame(content_frame, bg=bg_color, highlightbackground="#666666", highlightthickness=1)
        question_editor_frame.grid(row=0, column=1, sticky="nsew")
        
        # Question editor header
        editor_header = tk.Frame(question_editor_frame, bg=bg_color)
        editor_header.pack(fill=tk.X, pady=10)
        
        set_name_var = tk.StringVar(value="No Set Selected")
        set_name_label = tk.Label(
            editor_header,
            textvariable=set_name_var,
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg="white"
        )
        set_name_label.pack(side=tk.LEFT, padx=10)
        
        # Add question button
        add_q_btn = tk.Frame(editor_header, bg="#4CAF50", width=120, height=30)  # Green
        add_q_btn.pack(side=tk.RIGHT, padx=10)
        add_q_btn.pack_propagate(False)
        
        add_q_label = tk.Label(
            add_q_btn,
            text="Add Question",
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white"
        )
        add_q_label.pack(expand=True, fill=tk.BOTH)
        
        # Create a frame for the questions table
        questions_frame = tk.Frame(question_editor_frame, bg=bg_color)
        questions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create the treeview for questions
        columns = ("question", "answer", "points")
        questions_tree = ttk.Treeview(questions_frame, columns=columns, show="headings")
        
        # Define column headings
        questions_tree.heading("question", text="Question")
        questions_tree.heading("answer", text="Answer")
        questions_tree.heading("points", text="Points")
        
        # Define column widths
        questions_tree.column("question", width=300, stretch=True)
        questions_tree.column("answer", width=150, stretch=True)
        questions_tree.column("points", width=50, stretch=False)
        
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(questions_frame, orient=tk.VERTICAL, command=questions_tree.yview)
        questions_tree.configure(yscroll=y_scrollbar.set)
        
        # Pack the treeview and scrollbars
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        questions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Footer frame
        footer_frame = tk.Frame(manager_window, bg=bg_color, pady=10)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20)
        
        # Save button
        save_btn = tk.Frame(footer_frame, bg="#4CAF50", width=100, height=35)  # Green
        save_btn.pack(side=tk.LEFT, padx=5)
        save_btn.pack_propagate(False)
        
        save_label = tk.Label(
            save_btn,
            text="Save",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white"
        )
        save_label.pack(expand=True, fill=tk.BOTH)
        
        # Use button - will close the window and set selected set as current
        use_btn = tk.Frame(footer_frame, bg="#2196F3", width=150, height=35)  # Blue
        use_btn.pack(side=tk.RIGHT, padx=5)
        use_btn.pack_propagate(False)
        
        use_label = tk.Label(
            use_btn,
            text="Use This Set",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white"
        )
        use_label.pack(expand=True, fill=tk.BOTH)
        
        # Cancel button
        cancel_btn = tk.Frame(footer_frame, bg="#F44336", width=100, height=35)  # Red
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        cancel_btn.pack_propagate(False)
        
        cancel_label = tk.Label(
            cancel_btn,
            text="Cancel",
            font=("Arial", 12),
            bg="#F44336",
            fg="white"
        )
        cancel_label.pack(expand=True, fill=tk.BOTH)
        
        # Function to update the questions treeview
        def update_questions_view(q_set=None):
            # Clear existing items
            for item in questions_tree.get_children():
                questions_tree.delete(item)
                
            if not q_set:
                return
                
            # Update the set name label
            set_name_var.set(q_set.name)
                
            # Add questions to the treeview
            for i, q in enumerate(q_set.questions):
                questions_tree.insert("", tk.END, values=(
                    q.get("question", ""),
                    q.get("answer", ""),
                    q.get("points", 10)
                ))
        
        # Function to get the selected question set
        def get_selected_set():
            try:
                index = set_listbox.curselection()[0]
                return self.question_sets[index]
            except (IndexError, TypeError):
                return None
        
        # Function to handle set selection
        def on_set_select(event):
            q_set = get_selected_set()
            if q_set:
                update_questions_view(q_set)
        
        # Dialog to edit a question
        def edit_question_dialog(title, question="", answer="", points=10):
            dialog = tk.Toplevel(manager_window)
            dialog.title(title)
            dialog.geometry("500x300")
            dialog.configure(bg=bg_color)
            dialog.transient(manager_window)
            dialog.grab_set()
            
            # Make dialog modal
            dialog.focus_set()
            
            # Center the dialog on the parent window
            center_window_on_parent(dialog, manager_window)
            
            # Configure grid
            dialog.columnconfigure(0, weight=0)
            dialog.columnconfigure(1, weight=1)
            dialog.rowconfigure(0, weight=0)
            dialog.rowconfigure(1, weight=0)
            dialog.rowconfigure(2, weight=0)
            dialog.rowconfigure(3, weight=1)
            
            # Question label and entry
            tk.Label(
                dialog, 
                text="Question:", 
                font=("Arial", 12),
                bg=bg_color,
                fg="white",
                anchor="e"
            ).grid(row=0, column=0, sticky="e", padx=10, pady=10)
            
            # Use a Text widget for multi-line question entry
            question_frame = tk.Frame(
                dialog,
                bg="white",
                highlightbackground="#999999",
                highlightthickness=1
            )
            question_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
            
            question_text = tk.Text(
                question_frame,
                height=4,
                font=("Arial", 12),
                bg="white",
                fg="black",
                relief="flat",
                wrap=tk.WORD
            )
            question_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            question_text.insert("1.0", question)
            
            # Answer label and entry
            tk.Label(
                dialog, 
                text="Answer:", 
                font=("Arial", 12),
                bg=bg_color,
                fg="white",
                anchor="e"
            ).grid(row=1, column=0, sticky="e", padx=10, pady=10)
            
            answer_var = tk.StringVar(value=answer)
            answer_frame = tk.Frame(
                dialog,
                bg="white",
                highlightbackground="#999999",
                highlightthickness=1,
                height=40
            )
            answer_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
            
            answer_entry = tk.Entry(
                answer_frame,
                textvariable=answer_var,
                font=("Arial", 12),
                bg="white",
                fg="black",
                relief="flat"
            )
            answer_entry.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Points label and entry
            tk.Label(
                dialog, 
                text="Points:", 
                font=("Arial", 12),
                bg=bg_color,
                fg="white",
                anchor="e"
            ).grid(row=2, column=0, sticky="e", padx=10, pady=10)
            
            # Create a frame for points with spinbox
            points_frame = tk.Frame(dialog, bg=bg_color)
            points_frame.grid(row=2, column=1, sticky="w", padx=10, pady=10)
            
            # Define valid point values
            point_values = [5, 10, 15, 20, 25, 30, 50, 100]
            
            # Use ttk Combobox for points
            points_var = tk.StringVar(value=str(points))
            points_combo = ttk.Combobox(
                points_frame,
                textvariable=points_var,
                values=[str(val) for val in point_values],
                width=5,
                font=("Arial", 12),
                state="readonly"
            )
            points_combo.pack()
            
            # Button frame
            button_frame = tk.Frame(dialog, bg=bg_color)
            button_frame.grid(row=3, column=0, columnspan=2, sticky="s", pady=20)
            
            # Dialog result variable
            result = {"value": None}
            
            # OK button
            def on_ok():
                # Validate
                q = question_text.get("1.0", tk.END).strip()
                a = answer_var.get().strip()
                try:
                    p = int(points_var.get())
                except ValueError:
                    p = 10
                
                if not q:
                    messagebox.showwarning("Validation Error", "Question cannot be empty.")
                    return
                    
                if not a:
                    messagebox.showwarning("Validation Error", "Answer cannot be empty.")
                    return
                
                result["value"] = {
                    "question": q,
                    "answer": a,
                    "points": p
                }
                dialog.destroy()
            
            # Cancel button
            def on_cancel():
                dialog.destroy()
            
            # OK button
            ok_btn = tk.Frame(button_frame, bg="#4CAF50", width=100, height=35)  # Green
            ok_btn.pack(side=tk.LEFT, padx=10)
            ok_btn.pack_propagate(False)
            
            ok_label = tk.Label(
                ok_btn,
                text="OK",
                font=("Arial", 12),
                bg="#4CAF50",
                fg="white"
            )
            ok_label.pack(expand=True, fill=tk.BOTH)
            
            # Bind click events
            ok_btn.bind("<Button-1>", lambda event: on_ok())
            ok_label.bind("<Button-1>", lambda event: on_ok())
            
            # Cancel button
            cancel_btn = tk.Frame(button_frame, bg="#F44336", width=100, height=35)  # Red
            cancel_btn.pack(side=tk.LEFT, padx=10)
            cancel_btn.pack_propagate(False)
            
            cancel_label = tk.Label(
                cancel_btn,
                text="Cancel",
                font=("Arial", 12),
                bg="#F44336",
                fg="white"
            )
            cancel_label.pack(expand=True, fill=tk.BOTH)
            
            # Bind click events
            cancel_btn.bind("<Button-1>", lambda event: on_cancel())
            cancel_label.bind("<Button-1>", lambda event: on_cancel())
            
            # Wait for the dialog to close
            dialog.wait_window()
            
            return result["value"]
        
        # Function to add a new question
        def add_question():
            q_set = get_selected_set()
            if not q_set:
                messagebox.showwarning("No Set Selected", "Please select a question set first.")
                return
                
            result = edit_question_dialog("Add New Question")
            if result:
                q_set.add_question(
                    result["question"],
                    result["answer"],
                    result["points"]
                )
                update_questions_view(q_set)
        
        # Function to edit a question
        def edit_question(event=None):
            q_set = get_selected_set()
            if not q_set:
                return
                
            # Get selected item
            selected_items = questions_tree.selection()
            if not selected_items:
                return
                
            # Get the index of the selected item
            item_id = selected_items[0]
            item_index = questions_tree.index(item_id)
            
            # Get current values
            current_q = q_set.questions[item_index]
            
            # Show edit dialog
            result = edit_question_dialog(
                "Edit Question",
                current_q["question"],
                current_q["answer"],
                current_q["points"]
            )
            
            if result:
                # Update the question
                q_set.update_question(
                    item_index,
                    result["question"],
                    result["answer"],
                    result["points"]
                )
                update_questions_view(q_set)
        
        # Function to delete a question
        def delete_question():
            q_set = get_selected_set()
            if not q_set:
                return
                
            # Get selected item
            selected_items = questions_tree.selection()
            if not selected_items:
                return
                
            # Confirm deletion
            if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this question?"):
                return
                
            # Get the index of the selected item
            item_id = selected_items[0]
            item_index = questions_tree.index(item_id)
            
            # Delete the question
            q_set.remove_question(item_index)
            update_questions_view(q_set)
        
        # Function to rename a set
        def rename_set():
            q_set = get_selected_set()
            if not q_set:
                messagebox.showwarning("No Set Selected", "Please select a question set first.")
                return
                
            new_name = simpledialog.askstring(
                "Rename Set", 
                "Enter new name:",
                initialvalue=q_set.name,
                parent=manager_window
            )
            
            if new_name and new_name.strip():
                # Check for duplicate names
                if any(s.name == new_name for s in self.question_sets if s != q_set):
                    messagebox.showwarning("Duplicate Name", "A set with this name already exists.")
                    return
                    
                q_set.name = new_name
                
                # Update the listbox
                index = set_listbox.curselection()[0]
                set_listbox.delete(index)
                set_listbox.insert(index, new_name)
                set_listbox.selection_set(index)
                
                # Update the editor header
                set_name_var.set(new_name)
        
        # Function to create a new question set
        def new_set():
            new_set = self.create_new_set()
            if new_set:
                # Add to listbox
                set_listbox.insert(tk.END, new_set.name)
                # Select it
                set_listbox.selection_clear(0, tk.END)
                set_listbox.selection_set(tk.END)
                set_listbox.see(tk.END)
                # Update the questions view
                update_questions_view(new_set)
        
        # Function to load a question set
        def load_set():
            q_set = self.load_question_set()
            if q_set:
                # Check if it already exists in our list
                found = False
                for i, existing_set in enumerate(self.question_sets):
                    if existing_set.name == q_set.name:
                        # Update the listbox
                        set_listbox.delete(i)
                        set_listbox.insert(i, q_set.name)
                        set_listbox.selection_set(i)
                        set_listbox.see(i)
                        found = True
                        break
                
                if not found:
                    # Add to listbox
                    set_listbox.insert(tk.END, q_set.name)
                    # Select it
                    set_listbox.selection_clear(0, tk.END)
                    set_listbox.selection_set(tk.END)
                    set_listbox.see(tk.END)
                
                # Update the questions view
                update_questions_view(q_set)
        
        # Function to delete a set
        def delete_set():
            q_set = get_selected_set()
            if not q_set:
                messagebox.showwarning("No Set Selected", "Please select a question set first.")
                return
                
            # Delete the set
            if self.delete_question_set(q_set):
                # Update the listbox
                index = set_listbox.curselection()[0]
                set_listbox.delete(index)
                
                # Select another set if available
                if set_listbox.size() > 0:
                    next_index = min(index, set_listbox.size() - 1)
                    set_listbox.selection_set(next_index)
                    set_listbox.see(next_index)
                    update_questions_view(self.question_sets[next_index])
                else:
                    # No sets left
                    update_questions_view(None)
        
        # Function to handle window closing and saving
        def on_close():
            # Ask about unsaved changes
            if messagebox.askyesno("Confirm Exit", "Save changes before closing?"):
                save_all()
            
            manager_window.destroy()
        
        # Function to save all sets
        def save_all():
            for q_set in self.question_sets:
                self.save_question_set(q_set)
            
            messagebox.showinfo("Save Complete", "All question sets have been saved.")
        
        # Function to use the selected set
        def use_selected_set():
            q_set = get_selected_set()
            if not q_set:
                messagebox.showwarning("No Set Selected", "Please select a question set first.")
                return
                
            # Set as current
            self.current_set = q_set
            
            # Save all changes
            save_all()
            
            # Call the callback if provided
            if self.callback:
                self.callback(q_set.questions)
            
            # Close the window
            manager_window.destroy()
        
        # Function to center a window on its parent
        def center_window_on_parent(window, parent):
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            
            width = window.winfo_width()
            height = window.winfo_height()
            
            # If the window hasn't been drawn yet, update idle tasks to get dimensions
            if width == 1:
                window.update_idletasks()
                width = window.winfo_width()
                height = window.winfo_height()
            
            x = parent_x + (parent_width - width) // 2
            y = parent_y + (parent_height - height) // 2
            
            window.geometry(f"+{x}+{y}")
        
        # Bind actions to buttons
        # Set selection
        set_listbox.bind("<<ListboxSelect>>", on_set_select)
        
        # Double-click on question to edit
        questions_tree.bind("<Double-1>", edit_question)
        
        # Right-click on question for context menu
        def question_context_menu(event):
            q_set = get_selected_set()
            if not q_set:
                return
                
            # Only show menu if clicking on a question
            if not questions_tree.identify_row(event.y):
                return
                
            # Create a menu
            menu = tk.Menu(questions_tree, tearoff=0, bg="#444444", fg="white",
                          activebackground="#2196F3", activeforeground="white")
            menu.add_command(label="Edit Question", command=edit_question)
            menu.add_command(label="Delete Question", command=delete_question)
            
            # Show the menu
            menu.post(event.x_root, event.y_root)
        
        questions_tree.bind("<Button-3>", question_context_menu)
        
        # Add Question button
        add_q_btn.bind("<Button-1>", lambda event: add_question())
        add_q_label.bind("<Button-1>", lambda event: add_question())
        
        # New Set button
        new_btn.bind("<Button-1>", lambda event: new_set())
        new_label.bind("<Button-1>", lambda event: new_set())
        
        # Load Set button
        load_btn.bind("<Button-1>", lambda event: load_set())
        load_label.bind("<Button-1>", lambda event: load_set())
        
        # Rename button
        rename_btn.bind("<Button-1>", lambda event: rename_set())
        rename_label.bind("<Button-1>", lambda event: rename_set())
        
        # Delete button
        delete_btn.bind("<Button-1>", lambda event: delete_set())
        delete_label.bind("<Button-1>", lambda event: delete_set())
        
        # Save button
        save_btn.bind("<Button-1>", lambda event: save_all())
        save_label.bind("<Button-1>", lambda event: save_all())
        
        # Use this Set button
        use_btn.bind("<Button-1>", lambda event: use_selected_set())
        use_label.bind("<Button-1>", lambda event: use_selected_set())
        
        # Cancel button
        cancel_btn.bind("<Button-1>", lambda event: manager_window.destroy())
        cancel_label.bind("<Button-1>", lambda event: manager_window.destroy())
        
        # Handle closing the window
        manager_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Initialize with the currently selected set
        if self.current_set:
            for i, q_set in enumerate(self.question_sets):
                if q_set == self.current_set:
                    set_listbox.selection_set(i)
                    update_questions_view(q_set)
                    break
        
        # Center the window on the parent
        manager_window.update_idletasks()
        center_window_on_parent(manager_window, self.root)
        
        # Make the window a modal dialog
        manager_window.transient(self.root)
        manager_window.grab_set()
        manager_window.focus_set()
        
        # Wait for the window to close
        self.root.wait_window(manager_window)
        return self.current_set