import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import json
import os
from datetime import datetime

class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Game")
        self.root.geometry("600x850")  # Increased height for timer
        self.root.resizable(False, False)
        
        # Set theme colors
        self.bg_color = "#f0f0f0"
        self.cell_bg = "#ffffff"
        self.cell_fg = "#000000"
        self.button_bg = "#4a90e2"
        self.button_fg = "#ffffff"
        self.grid_color = "#000000"
        self.box_color = "#000000"
        self.original_bg = "#e8e8e8"  # Light gray background for original numbers
        self.original_fg = "#000000"  # Black color for original numbers
        self.user_fg = "#4a90e2"      # Blue color for user input
        
        # Timer variables
        self.start_time = None
        self.timer_running = False
        self.timer_id = None
        self.best_time = self.load_best_time()
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Initialize the board
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        self.original_board = [[0 for _ in range(9)] for _ in range(9)]
        
        # Create title
        self.create_title()
        
        # Create timer display
        self.create_timer_display()
        
        # Create the main frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(pady=10)
        
        # Create the Sudoku grid
        self.cells = {}
        self.create_grid()
        
        # Create number input buttons
        self.create_number_buttons()
        
        # Create control buttons
        self.create_control_buttons()
        
        # Create specific clear buttons
        self.create_specific_clear_buttons()
        
        # Generate a new puzzle
        self.generate_puzzle()

    def create_timer_display(self):
        timer_frame = tk.Frame(self.root, bg=self.bg_color)
        timer_frame.pack(pady=5)
        
        # Current time display
        self.time_label = tk.Label(
            timer_frame,
            text="Time: 00:00",
            font=('Arial', 14, 'bold'),
            bg=self.bg_color,
            fg=self.button_bg
        )
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # Best time display
        self.best_time_label = tk.Label(
            timer_frame,
            text=f"Best Time: {self.format_time(self.best_time)}",
            font=('Arial', 14, 'bold'),
            bg=self.bg_color,
            fg=self.button_bg
        )
        self.best_time_label.pack(side=tk.RIGHT, padx=10)

    def format_time(self, seconds):
        if seconds is None:
            return "N/A"
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_timer(self):
        if self.timer_running:
            current_time = time.time() - self.start_time
            self.time_label.config(text=f"Time: {self.format_time(current_time)}")
            self.timer_id = self.root.after(1000, self.update_timer)

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        return time.time() - self.start_time if self.start_time else 0

    def load_best_time(self):
        try:
            if os.path.exists('best_time.json'):
                with open('best_time.json', 'r') as f:
                    data = json.load(f)
                    return data.get('best_time')
        except:
            pass
        return None

    def save_best_time(self, time_seconds):
        if self.best_time is None or time_seconds < self.best_time:
            self.best_time = time_seconds
            try:
                with open('best_time.json', 'w') as f:
                    json.dump({'best_time': time_seconds}, f)
                self.best_time_label.config(text=f"Best Time: {self.format_time(self.best_time)}")
            except:
                pass

    def create_title(self):
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="SUDOKU",
            font=('Helvetica', 24, 'bold'),
            bg=self.bg_color,
            fg=self.button_bg
        )
        title_label.pack()

    def create_grid(self):
        # Create a frame for the grid with a border
        grid_frame = tk.Frame(
            self.main_frame,
            bg=self.grid_color,
            padx=2,
            pady=2
        )
        grid_frame.pack()
        
        for i in range(9):
            for j in range(9):
                cell = tk.Entry(
                    grid_frame,
                    width=2,
                    font=('Arial', 20, 'bold'),
                    justify='center',
                    bg=self.cell_bg,
                    fg=self.cell_fg,
                    bd=1,
                    readonlybackground=self.original_bg  # Background color for readonly cells
                )
                cell.grid(row=i, column=j, padx=1, pady=1)
                cell.bind('<KeyRelease>', lambda e, row=i, col=j: self.validate_input(e, row, col))
                self.cells[(i, j)] = cell
                
                # Add borders for 3x3 boxes
                if i % 3 == 0 and i != 0:
                    cell.grid(pady=(5, 1))
                if j % 3 == 0 and j != 0:
                    cell.grid(padx=(5, 1))

    def create_number_buttons(self):
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        for i in range(1, 10):
            btn = tk.Button(
                button_frame,
                text=str(i),
                width=3,
                height=2,
                font=('Arial', 12, 'bold'),
                bg=self.button_bg,
                fg=self.button_fg,
                activebackground="#357abd",
                activeforeground="#ffffff",
                relief=tk.RAISED,
                bd=3,
                command=lambda x=i: self.insert_number(x)
            )
            btn.grid(row=0, column=i-1, padx=2)

    def create_control_buttons(self):
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(pady=10)
        
        button_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': self.button_bg,
            'fg': self.button_fg,
            'activebackground': "#357abd",
            'activeforeground': "#ffffff",
            'relief': tk.RAISED,
            'bd': 3,
            'width': 12,
            'height': 2
        }
        
        tk.Button(
            control_frame,
            text="New Game",
            command=self.generate_puzzle,
            **button_style
        ).grid(row=0, column=0, padx=5)
        
        tk.Button(
            control_frame,
            text="Check Solution",
            command=self.check_solution,
            **button_style
        ).grid(row=0, column=1, padx=5)
        
        tk.Button(
            control_frame,
            text="Clear All",
            command=self.clear_board,
            **button_style
        ).grid(row=0, column=2, padx=5)

    def create_specific_clear_buttons(self):
        clear_frame = tk.Frame(self.root, bg=self.bg_color)
        clear_frame.pack(pady=10)
        
        # Style for section labels
        label_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': self.bg_color,
            'fg': self.button_bg
        }
        
        # Style for clear buttons
        clear_button_style = {
            'font': ('Arial', 9),
            'bg': "#e0e0e0",
            'fg': "#000000",
            'activebackground': "#d0d0d0",
            'relief': tk.RAISED,
            'bd': 2,
            'width': 2
        }
        
        # Row clear buttons
        row_frame = tk.Frame(clear_frame, bg=self.bg_color)
        row_frame.pack(pady=5)
        tk.Label(row_frame, text="Clear Row:", **label_style).pack(side=tk.LEFT)
        for i in range(9):
            btn = tk.Button(
                row_frame,
                text=str(i+1),
                command=lambda x=i: self.clear_row(x),
                **clear_button_style
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Column clear buttons
        col_frame = tk.Frame(clear_frame, bg=self.bg_color)
        col_frame.pack(pady=5)
        tk.Label(col_frame, text="Clear Column:", **label_style).pack(side=tk.LEFT)
        for i in range(9):
            btn = tk.Button(
                col_frame,
                text=str(i+1),
                command=lambda x=i: self.clear_column(x),
                **clear_button_style
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Box clear buttons
        box_frame = tk.Frame(clear_frame, bg=self.bg_color)
        box_frame.pack(pady=5)
        tk.Label(box_frame, text="Clear Box:", **label_style).pack(side=tk.LEFT)
        for i in range(9):
            btn = tk.Button(
                box_frame,
                text=str(i+1),
                command=lambda x=i: self.clear_box(x),
                **clear_button_style
            )
            btn.pack(side=tk.LEFT, padx=2)

    def clear_row(self, row):
        for col in range(9):
            if self.original_board[row][col] == 0:
                self.board[row][col] = 0
                self.cells[(row, col)].delete(0, tk.END)
                self.cells[(row, col)].config(state='normal', bg=self.cell_bg)

    def clear_column(self, col):
        for row in range(9):
            if self.original_board[row][col] == 0:
                self.board[row][col] = 0
                self.cells[(row, col)].delete(0, tk.END)
                self.cells[(row, col)].config(state='normal', bg=self.cell_bg)

    def clear_box(self, box_num):
        start_row = (box_num // 3) * 3
        start_col = (box_num % 3) * 3
        
        for i in range(3):
            for j in range(3):
                row = start_row + i
                col = start_col + j
                if self.original_board[row][col] == 0:
                    self.board[row][col] = 0
                    self.cells[(row, col)].delete(0, tk.END)
                    self.cells[(row, col)].config(state='normal', bg=self.cell_bg)

    def validate_input(self, event, row, col):
        value = event.widget.get()
        if value:
            try:
                num = int(value)
                if num < 1 or num > 9:
                    event.widget.delete(0, tk.END)
                else:
                    self.board[row][col] = num
                    event.widget.config(fg=self.user_fg)  # Set user input color
            except ValueError:
                event.widget.delete(0, tk.END)

    def insert_number(self, number):
        focused = self.root.focus_get()
        if isinstance(focused, tk.Entry):
            focused.delete(0, tk.END)
            focused.insert(0, str(number))
            focused.config(fg=self.user_fg)  # Set user input color
            for pos, cell in self.cells.items():
                if cell == focused:
                    self.board[pos[0]][pos[1]] = number
                    break

    def is_valid_move(self, row, col, num):
        # Check row
        for x in range(9):
            if self.board[row][x] == num:
                return False
        
        # Check column
        for x in range(9):
            if self.board[x][col] == num:
                return False
        
        # Check 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.board[i + start_row][j + start_col] == num:
                    return False
        
        return True

    def solve_sudoku(self, row=0, col=0):
        if col == 9:
            if row == 8:
                return True
            row += 1
            col = 0
        
        if self.board[row][col] > 0:
            return self.solve_sudoku(row, col + 1)
        
        for num in range(1, 10):
            if self.is_valid_move(row, col, num):
                self.board[row][col] = num
                if self.solve_sudoku(row, col + 1):
                    return True
                self.board[row][col] = 0
        
        return False

    def generate_puzzle(self):
        # Stop the current timer if running
        if self.timer_running:
            self.stop_timer()
        
        self.clear_board()
        
        # Fill diagonal boxes
        for i in range(0, 9, 3):
            self.fill_box(i, i)
        
        # Solve the rest of the puzzle
        self.solve_sudoku()
        
        # Save the solution
        self.solution = [row[:] for row in self.board]
        
        # Remove numbers to create the puzzle
        for i in range(9):
            for j in range(9):
                if random.random() < 0.6:
                    self.board[i][j] = 0
        
        # Save the original board
        self.original_board = [row[:] for row in self.board]
        
        # Update the display
        self.update_display()
        
        # Start the timer
        self.start_timer()

    def fill_box(self, row, col):
        nums = list(range(1, 10))
        random.shuffle(nums)
        index = 0
        for i in range(3):
            for j in range(3):
                self.board[row + i][col + j] = nums[index]
                index += 1

    def update_display(self):
        for i in range(9):
            for j in range(9):
                value = self.board[i][j]
                cell = self.cells[(i, j)]
                cell.delete(0, tk.END)
                if value != 0:
                    cell.insert(0, str(value))
                    if self.original_board[i][j] != 0:
                        # Original numbers
                        cell.config(
                            state='readonly',
                            fg=self.original_fg,
                            bg=self.original_bg
                        )
                    else:
                        # User input numbers
                        cell.config(
                            state='normal',
                            fg=self.user_fg,
                            bg=self.cell_bg
                        )

    def clear_board(self):
        self.board = [row[:] for row in self.original_board]
        self.update_display()

    def check_solution(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != self.solution[i][j]:
                    messagebox.showinfo("Result", "Not quite right! Keep trying!")
                    return
        
        # Stop the timer and get the completion time
        completion_time = self.stop_timer()
        
        # Save the best time if it's better
        self.save_best_time(completion_time)
        
        # Show completion message with time
        messagebox.showinfo(
            "Congratulations!",
            f"You solved the puzzle!\nTime: {self.format_time(completion_time)}\nBest Time: {self.format_time(self.best_time)}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop() 