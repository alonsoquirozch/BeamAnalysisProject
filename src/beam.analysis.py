"""
Beam Analysis Tool
A graphical application to calculate reactions and moments for a simply supported beam with a point load.
Supports MKS, Imperial, and Americano unit systems with visualization of shear and moment diagrams.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class BeamAnalysisApp:
    """Main application class for beam analysis with a Tkinter-based GUI."""

    def __init__(self, root):
        """Initialize the application with a Tkinter root window."""
        self.root = root
        self.root.title("Análisis Estructural de Viga - Carga Puntual")
        self.root.configure(bg="#000000")
        
        # Configure styles inspired by Grok with rounded edges
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 12), foreground="#FFFFFF", background="#000000")
        style.configure("TEntry", font=("Arial", 12), fieldbackground="#333333", foreground="#000000", padding=5)
        style.configure("TButton", font=("Arial", 12, "bold"), background="#1A1A1A", foreground="#FFFFFF", padding=8)
        style.configure("TCombobox", font=("Arial", 12), fieldbackground="#333333", foreground="#FFFFFF", padding=5)
        style.configure("TFrame", background="#000000")
        
        # Apply rounded edge styles
        style.configure("Rounded.TButton", borderwidth=0, relief="flat", borderradius=10)
        style.configure("Rounded.TCombobox", borderwidth=0, relief="flat", borderradius=10)
        style.configure("Rounded.TEntry", borderwidth=0, relief="flat", borderradius=10)
        
        # Style for Combobox dropdown
        style.map("TCombobox", fieldbackground=[("readonly", "#333333")])
        style.configure("TCombobox.Listbox", background="#333333", foreground="#FFFFFF", borderwidth=0)
        
        # Unit system variable
        self.unit_system = tk.StringVar(value="MKS")
        self.unit_system.trace("w", self.update_unit_labels)
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input variables
        self.a = tk.DoubleVar()
        self.w = tk.DoubleVar()
        self.l = tk.DoubleVar()
        
        # Create input fields
        self.title_label = ttk.Label(self.main_frame, text="Análisis de Viga Simplemente Apoyada", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.label_a = ttk.Label(self.main_frame, text="Distancia de la carga (a) [m]:")
        self.label_a.grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.a, width=15, style="Rounded.TEntry").grid(row=1, column=1, pady=5)
        
        self.label_w = ttk.Label(self.main_frame, text="Carga puntual (w) [kN]:")
        self.label_w.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.w, width=15, style="Rounded.TEntry").grid(row=2, column=1, pady=5)
        
        self.label_l = ttk.Label(self.main_frame, text="Longitud de la viga (L) [m]:")
        self.label_l.grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.main_frame, textvariable=self.l, width=15, style="Rounded.TEntry").grid(row=3, column=1, pady=5)
        
        # Unit selector
        ttk.Label(self.main_frame, text="Sistema de unidades:").grid(row=4, column=0, sticky=tk.W, pady=5)
        unit_options = ["MKS", "Imperial", "Americano"]
        self.unit_selector = ttk.Combobox(self.main_frame, textvariable=self.unit_system, values=unit_options, state="readonly", width=15, style="Rounded.TCombobox")
        self.unit_selector.grid(row=4, column=1, pady=5)
        
        # Buttons
        ttk.Button(self.main_frame, text="Calcular", command=self.calculate, style="Rounded.TButton").grid(row=5, column=0, pady=10)
        ttk.Button(self.main_frame, text="Exportar Resultados", command=self.export_results, style="Rounded.TButton").grid(row=5, column=1, pady=10)
        
        # Frames for results and plots
        self.result_frame = ttk.Frame(self.main_frame)
        self.result_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.plot_frame = ttk.Frame(self.main_frame)
        self.plot_frame.grid(row=7, column=0, columnspan=2, pady=10)

    def update_unit_labels(self, *args):
        """Update unit labels based on the selected unit system."""
        unit_system = self.unit_system.get()
        if unit_system == "MKS":
            self.label_a.configure(text="Distancia de la carga (a) [m]:")
            self.label_w.configure(text="Carga puntual (w) [kN]:")
            self.label_l.configure(text="Longitud de la viga (L) [m]:")
        elif unit_system == "Imperial":
            self.label_a.configure(text="Distancia de la carga (a) [ft]:")
            self.label_w.configure(text="Carga puntual (w) [kips]:")
            self.label_l.configure(text="Longitud de la viga (L) [ft]:")
        else:  # Americano
            self.label_a.configure(text="Distancia de la carga (a) [ft]:")
            self.label_w.configure(text="Carga puntual (w) [lb]:")
            self.label_l.configure(text="Longitud de la viga (L) [ft]:")
        if self.a.get() > 0 and self.w.get() > 0 and self.l.get() > 0:
            self.calculate()

    def calculate(self):
        """Perform beam analysis calculations and display results."""
        try:
            a = self.a.get()
            w = self.w.get()
            L = self.l.get()
            
            # Convert to MKS if not already
            if self.unit_system.get() == "Imperial":
                a /= 3.28084  # ft to m
                w /= 0.224809  # kips to kN
                L /= 3.28084  # ft to m
            elif self.unit_system.get() == "Americano":
                a /= 3.28084  # ft to m
                w /= 224.809  # lb to kN
                L /= 3.28084  # ft to m
            
            # Validate inputs
            if a < 0 or w < 0 or L <= 0 or a > L:
                raise ValueError("Invalid values: a ≤ L and all values must be positive.")
            
            # Perform calculations in MKS
            Rb = w * a / L
            Ra = w - Rb
            Ma = 0
            Mb = -w * a * (L - a) / L
            
            # Convert back to original unit system
            if self.unit_system.get() == "Imperial":
                a *= 3.28084  # m to ft
                w *= 0.224809  # kN to kips
                L *= 3.28084  # m to ft
                Ra *= 0.224809  # kN to kips
                Rb *= 0.224809  # kN to kips
                Mb *= 0.737562  # kN-m to kip-ft
            elif self.unit_system.get() == "Americano":
                a *= 3.28084  # m to ft
                w *= 224.809  # kN to lb
                L *= 3.28084  # m to ft
                Ra *= 224.809  # kN to lb
                Rb *= 224.809  # kN to lb
                Mb *= 737.562  # kN-m to lb-ft
            
            # Clear previous results
            for widget in self.result_frame.winfo_children():
                widget.destroy()
            
            # Display results
            unit_length = "m" if self.unit_system.get() == "MKS" else "ft"
            unit_force = "kN" if self.unit_system.get() == "MKS" else "kips" if self.unit_system.get() == "Imperial" else "lb"
            unit_moment = "kN-m" if self.unit_system.get() == "MKS" else "kip-ft" if self.unit_system.get() == "Imperial" else "lb-ft"
            ttk.Label(self.result_frame, text=f"Reacción en A (Ra): {Ra:.2f} {unit_force}", font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, pady=2)
            ttk.Label(self.result_frame, text=f"Reacción en B (Rb): {Rb:.2f} {unit_force}", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=2)
            ttk.Label(self.result_frame, text=f"Momento en A (Ma): {Ma:.2f} {unit_moment}", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=2)
            ttk.Label(self.result_frame, text=f"Momento en B (Mb): {Mb:.2f} {unit_moment}", font=("Arial", 11)).grid(row=3, column=0, sticky=tk.W, pady=2)
            
            # Generate diagrams
            self.plot_diagrams(a, w, L, Ra, Rb)
            
        except ValueError as e:
            for widget in self.result_frame.winfo_children():
                widget.destroy()
            ttk.Label(self.result_frame, text=f"Error: {str(e)}", foreground="#FF5555").grid(row=0, column=0)

    def plot_diagrams(self, a, w, L, Ra, Rb):
        """Generate and display shear and moment diagrams."""
        # Clear previous plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
        # Create figure with black background
        fig = plt.Figure(figsize=(8, 6), facecolor="#000000")
        
        # Set units based on system
        unit_length = "m" if self.unit_system.get() == "MKS" else "ft"
        unit_force = "kN" if self.unit_system.get() == "MKS" else "kips" if self.unit_system.get() == "Imperial" else "lb"
        unit_moment = "kN-m" if self.unit_system.get() == "MKS" else "kip-ft" if self.unit_system.get() == "Imperial" else "lb-ft"
        
        # Shear diagram
        ax1 = fig.add_subplot(211, facecolor="#1A1A1A")
        x = np.array([0, a, a, L])
        V = np.array([Ra, Ra, Ra - w, Rb])
        ax1.plot(x, V, 'b-', linewidth=2, label="Cortante")
        ax1.fill_between(x, V, alpha=0.1, color="blue")
        ax1.set_title("Diagrama de Cortante", fontsize=12, pad=10, color="#FFFFFF")
        ax1.set_xlabel(f"Longitud ({unit_length})", fontsize=10, color="#FFFFFF")
        ax1.set_ylabel(f"Cortante ({unit_force})", fontsize=10, color="#FFFFFF")
        ax1.grid(True, linestyle='--', alpha=0.3, color="#D3D3D3")
        ax1.set_xlim(0, L)
        ax1.legend(facecolor="#333333", edgecolor="#FFFFFF", labelcolor="#FFFFFF")
        ax1.tick_params(colors="#FFFFFF")
        
        # Moment diagram
        ax2 = fig.add_subplot(212, facecolor="#1A1A1A")
        x_m = np.linspace(0, L, 100)
        M = np.zeros_like(x_m)
        for i, x_val in enumerate(x_m):
            if x_val <= a:
                M[i] = Ra * x_val
            else:
                M[i] = Ra * x_val - w * (x_val - a)
        ax2.plot(x_m, M, 'r-', linewidth=2, label="Momento")
        ax2.fill_between(x_m, M, alpha=0.1, color="red")
        ax2.set_title("Diagrama de Momento Flector", fontsize=12, pad=10, color="#FFFFFF")
        ax2.set_xlabel(f"Longitud ({unit_length})", fontsize=10, color="#FFFFFF")
        ax2.set_ylabel(f"Momento ({unit_moment})", fontsize=10, color="#FFFFFF")
        ax2.grid(True, linestyle='--', alpha=0.3, color="#D3D3D3")
        ax2.set_xlim(0, L)
        ax2.legend(facecolor="#333333", edgecolor="#FFFFFF", labelcolor="#FFFFFF")
        ax2.tick_params(colors="#FFFFFF")
        
        # Adjust layout
        fig.tight_layout()
        
        # Integrate figure into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
        # Adjust window size
        self.root.geometry("")
        self.root.update()

    def export_results(self):
        """Export calculation results to a text file."""
        try:
            a = self.a.get()
            w = self.w.get()
            L = self.l.get()
            
            # Convert to MKS for calculations
            if self.unit_system.get() == "Imperial":
                a /= 3.28084
                w /= 0.224809
                L /= 3.28084
            elif self.unit_system.get() == "Americano":
                a /= 3.28084
                w /= 224.809
                L /= 3.28084
            
            Rb = w * a / L
            Ra = w - Rb
            Ma = 0
            Mb = -w * a * (L - a) / L
            
            # Convert back to original unit system
            if self.unit_system.get() == "Imperial":
                a *= 3.28084
                w *= 0.224809
                L *= 3.28084
                Ra *= 0.224809
                Rb *= 0.224809
                Mb *= 0.737562
            elif self.unit_system.get() == "Americano":
                a *= 3.28084
                w *= 224.809
                L *= 3.28084
                Ra *= 224.809
                Rb *= 224.809
                Mb *= 737.562
            
            unit_length = "m" if self.unit_system.get() == "MKS" else "ft"
            unit_force = "kN" if self.unit_system.get() == "MKS" else "kips" if self.unit_system.get() == "Imperial" else "lb"
            unit_moment = "kN-m" if self.unit_system.get() == "MKS" else "kip-ft" if self.unit_system.get() == "Imperial" else "lb-ft"
            
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, 'w') as f:
                    f.write("Análisis de Viga Simplemente Apoyada\n")
                    f.write(f"Sistema de unidades: {self.unit_system.get()}\n")
                    f.write(f"Distancia de la carga (a): {a:.2f} {unit_length}\n")
                    f.write(f"Carga puntual (w): {w:.2f} {unit_force}\n")
                    f.write(f"Longitud de la viga (L): {L:.2f} {unit_length}\n")
                    f.write(f"Reacción en A (Ra): {Ra:.2f} {unit_force}\n")
                    f.write(f"Reacción en B (Rb): {Rb:.2f} {unit_force}\n")
                    f.write(f"Momento en A (Ma): {Ma:.2f} {unit_moment}\n")
                    f.write(f"Momento en B (Mb): {Mb:.2f} {unit_moment}\n")
                ttk.Label(self.result_frame, text="Resultados exportados con éxito", foreground="#55FF55").grid(row=4, column=0)
        except Exception:
            ttk.Label(self.result_frame, text="Error al exportar resultados", foreground="#FF5555").grid(row=4, column=0)

if __name__ == "__main__":
    root = tk.Tk()
    app = BeamAnalysisApp(root)
    root.mainloop()