#!/usr/bin/env python3
"""
Port-Per-ESP Management GUI
Giao diện quản lý nhiều ESP với port riêng biệt
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import threading
import time
from datetime import datetime
from port_per_esp_manager import PortPerESPManager

class PortPerESPGUI:
    """GUI quản lý ESP với port riêng biệt"""
    
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.manager = PortPerESPManager(config)
        
        # GUI state
        self.selected_esp_ip = None
        self.auto_update_running = False
        
        # Setup callbacks
        self.manager.on_data_received = self.on_data_received
        self.manager.on_esp_status_change = self.on_esp_status_change
        
        self.setup_window()
        self.create_widgets()
        self.start_auto_update()
        
        # Load default ESPs
        self.load_default_esps()
    
    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        self.root.title("🌐 Port-Per-ESP Manager")
        self.root.geometry("1500x900")
        self.root.configure(bg="#f5f5f5")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_widgets(self):
        """Tạo giao diện"""
        # Main container
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure main frame grid
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Left panel - ESP Management
        self.create_esp_management_panel(main_frame)
        
        # Center panel - Selected ESP Control
        self.create_esp_control_panel(main_frame)
        
        # Right panel - System Monitor
        self.create_system_monitor_panel(main_frame)
        
        # Bottom panel - Logs
        self.create_log_panel(main_frame)
    
    def create_header(self, parent):
        """Tạo header với thông tin tổng quan"""
        header_frame = tk.Frame(parent, bg="#2c3e50", height=80)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        tk.Label(title_frame, text="🌐", font=("Arial", 24), 
                bg="#2c3e50", fg="#3498db").pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(title_frame, text="Port-Per-ESP Manager", 
                font=("Arial", 18, "bold"), 
                bg="#2c3e50", fg="white").pack(side=tk.LEFT)
        
        # Status indicators
        status_frame = tk.Frame(header_frame, bg="#2c3e50")
        status_frame.grid(row=0, column=1, padx=20, pady=20)
        
        self.header_labels = {}
        
        # Total ESPs
        esp_frame = tk.Frame(status_frame, bg="#2c3e50")
        esp_frame.pack(side=tk.LEFT, padx=15)
        
        tk.Label(esp_frame, text="Total ESPs", font=("Arial", 10), 
                bg="#2c3e50", fg="#bdc3c7").pack()
        
        self.header_labels['total_esps'] = tk.Label(esp_frame, text="0", 
                                                   font=("Arial", 16, "bold"), 
                                                   bg="#2c3e50", fg="#3498db")
        self.header_labels['total_esps'].pack()
        
        # Online ESPs
        online_frame = tk.Frame(status_frame, bg="#2c3e50")
        online_frame.pack(side=tk.LEFT, padx=15)
        
        tk.Label(online_frame, text="Online", font=("Arial", 10), 
                bg="#2c3e50", fg="#bdc3c7").pack()
        
        self.header_labels['online_esps'] = tk.Label(online_frame, text="0", 
                                                    font=("Arial", 16, "bold"), 
                                                    bg="#2c3e50", fg="#27ae60")
        self.header_labels['online_esps'].pack()
        
        # Active Ports
        ports_frame = tk.Frame(status_frame, bg="#2c3e50")
        ports_frame.pack(side=tk.LEFT, padx=15)
        
        tk.Label(ports_frame, text="Active Ports", font=("Arial", 10), 
                bg="#2c3e50", fg="#bdc3c7").pack()
        
        self.header_labels['active_ports'] = tk.Label(ports_frame, text="0", 
                                                     font=("Arial", 16, "bold"), 
                                                     bg="#2c3e50", fg="#f39c12")
        self.header_labels['active_ports'].pack()
        
        # Control buttons
        control_frame = tk.Frame(header_frame, bg="#2c3e50")
        control_frame.grid(row=0, column=2, sticky="e", padx=20, pady=20)
        
        tk.Button(control_frame, text="🚀 Start All", 
                 command=self.start_communication,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="🛑 Stop All", 
                 command=self.stop_communication,
                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
    
    def create_esp_management_panel(self, parent):
        """Tạo panel quản lý ESP"""
        esp_frame = tk.LabelFrame(parent, text="📱 ESP32 Devices", 
                                 font=("Arial", 12, "bold"),
                                 bg="white", fg="#2c3e50", bd=2)
        esp_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # Add ESP controls
        add_frame = tk.Frame(esp_frame, bg="white")
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(add_frame, text="➕ Add ESP", 
                 command=self.add_esp_dialog,
                 bg="#3498db", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(add_frame, text="🗑️ Remove", 
                 command=self.remove_esp,
                 bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(add_frame, text="🔄 Refresh", 
                 command=self.refresh_esp_list,
                 bg="#95a5a6", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # ESP TreeView with detailed columns
        columns = ("Name", "IP", "Port", "Status", "Packets")
        self.esp_tree = ttk.Treeview(esp_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        column_widths = {"Name": 100, "IP": 120, "Port": 60, "Status": 80, "Packets": 80}
        for col in columns:
            self.esp_tree.heading(col, text=col)
            self.esp_tree.column(col, width=column_widths.get(col, 80), minwidth=60)
        
        # Scrollbar
        esp_scrollbar = ttk.Scrollbar(esp_frame, orient=tk.VERTICAL, command=self.esp_tree.yview)
        self.esp_tree.configure(yscrollcommand=esp_scrollbar.set)
        
        # Pack tree and scrollbar
        tree_frame = tk.Frame(esp_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.esp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        esp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.esp_tree.bind("<<TreeviewSelect>>", self.on_esp_select)
        
        # Context menu for ESP tree
        self.create_esp_context_menu()
    
    def create_esp_context_menu(self):
        """Tạo context menu cho ESP tree"""
        self.esp_context_menu = tk.Menu(self.root, tearoff=0)
        self.esp_context_menu.add_command(label="📊 View Details", command=self.view_esp_details)
        self.esp_context_menu.add_command(label="🔌 Connect", command=self.connect_esp)
        self.esp_context_menu.add_command(label="🔌 Disconnect", command=self.disconnect_esp)
        self.esp_context_menu.add_separator()
        self.esp_context_menu.add_command(label="🗑️ Remove", command=self.remove_esp)
        
        # Bind right click
        self.esp_tree.bind("<Button-3>", self.show_esp_context_menu)
    
    def create_esp_control_panel(self, parent):
        """Tạo panel điều khiển ESP được chọn"""
        control_frame = tk.LabelFrame(parent, text="🎛️ ESP Control Panel", 
                                     font=("Arial", 12, "bold"),
                                     bg="white", fg="#2c3e50", bd=2)
        control_frame.grid(row=1, column=1, sticky="nsew", padx=5)
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Selected ESP info
        info_frame = tk.Frame(control_frame, bg="#ecf0f1", relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.selected_esp_label = tk.Label(info_frame, 
                                          text="🔘 No ESP selected", 
                                          font=("Arial", 12, "bold"),
                                          bg="#ecf0f1", fg="#2c3e50")
        self.selected_esp_label.pack(pady=10)
        
        # Control tabs
        self.control_notebook = ttk.Notebook(control_frame)
        self.control_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # LED Control tab
        led_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(led_frame, text="💡 LED Control")
        self.create_led_controls(led_frame)
        
        # Touch Sensor tab
        touch_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(touch_frame, text="👆 Touch Sensor")
        self.create_touch_controls(touch_frame)
        
        # Configuration tab
        config_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(config_frame, text="⚙️ Configuration")
        self.create_config_controls(config_frame)
        
        # Port Management tab
        port_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(port_frame, text="🌐 Port Management")
        self.create_port_management(port_frame)
        
        # Real-time data display
        self.create_realtime_display(control_frame)
    
    def create_led_controls(self, parent):
        """Tạo điều khiển LED"""
        # Color picker section
        color_section = tk.LabelFrame(parent, text="🎨 Color Control", bg="white")
        color_section.pack(fill=tk.X, padx=10, pady=10)
        
        color_frame = tk.Frame(color_section, bg="white")
        color_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(color_frame, text="Color:", bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.color_preview = tk.Label(color_frame, text="   ", bg="#ff0000", 
                                     relief=tk.RAISED, bd=2, cursor="hand2")
        self.color_preview.pack(side=tk.LEFT, padx=(10, 5))
        self.color_preview.bind("<Button-1>", lambda e: self.choose_color())
        
        tk.Button(color_frame, text="🎨 Pick Color", 
                 command=self.choose_color,
                 bg="#9b59b6", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Brightness control
        brightness_section = tk.LabelFrame(parent, text="💡 Brightness", bg="white")
        brightness_section.pack(fill=tk.X, padx=10, pady=10)
        
        brightness_frame = tk.Frame(brightness_section, bg="white")
        brightness_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(brightness_frame, text="Brightness:", bg="white").pack(side=tk.LEFT)
        
        self.brightness_var = tk.IntVar(value=128)
        self.brightness_scale = tk.Scale(brightness_frame, from_=1, to=255, 
                                        orient=tk.HORIZONTAL, variable=self.brightness_var,
                                        command=self.on_brightness_change,
                                        bg="white", highlightthickness=0)
        self.brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.brightness_label = tk.Label(brightness_frame, text="128", 
                                        bg="white", font=("Arial", 10, "bold"))
        self.brightness_label.pack(side=tk.LEFT)
        
        # LED effect buttons
        effects_section = tk.LabelFrame(parent, text="✨ Effects", bg="white")
        effects_section.pack(fill=tk.X, padx=10, pady=10)
        
        effects_frame = tk.Frame(effects_section, bg="white")
        effects_frame.pack(fill=tk.X, padx=10, pady=10)
        
        effects = [
            ("🌈 Rainbow", self.send_rainbow, "#e91e63"),
            ("💡 Test LED", self.test_led, "#ff9800"),
            ("⚡ Flash", self.flash_led, "#3f51b5"),
            ("🔴 Turn Off", self.turn_off_led, "#f44336")
        ]
        
        for i, (text, command, color) in enumerate(effects):
            btn = tk.Button(effects_frame, text=text, command=command,
                           bg=color, fg="white", font=("Arial", 9))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        
        effects_frame.grid_columnconfigure(0, weight=1)
        effects_frame.grid_columnconfigure(1, weight=1)
    
    def create_touch_controls(self, parent):
        """Tạo điều khiển cảm biến chạm"""
        # Threshold configuration
        threshold_section = tk.LabelFrame(parent, text="🎯 Touch Threshold", bg="white")
        threshold_section.pack(fill=tk.X, padx=10, pady=10)
        
        threshold_frame = tk.Frame(threshold_section, bg="white")
        threshold_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(threshold_frame, text="Threshold Value:", bg="white").pack()
        
        self.threshold_var = tk.StringVar(value="2932")
        threshold_entry = tk.Entry(threshold_frame, textvariable=self.threshold_var,
                                  font=("Arial", 14), justify=tk.CENTER, width=10)
        threshold_entry.pack(pady=10)
        
        tk.Button(threshold_frame, text="📤 Send Threshold",
                 command=self.send_threshold,
                 bg="#4CAF50", fg="white", font=("Arial", 11)).pack(pady=5)
        
        # Touch status display
        status_section = tk.LabelFrame(parent, text="📊 Touch Status", bg="white")
        status_section.pack(fill=tk.X, padx=10, pady=10)
        
        self.touch_status_frame = tk.Frame(status_section, bg="white")
        self.touch_status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Will be populated with real-time data
        self.touch_labels = {}
    
    def create_config_controls(self, parent):
        """Tạo điều khiển cấu hình"""
        # Resolume IP configuration
        resolume_section = tk.LabelFrame(parent, text="🎬 Resolume Configuration", bg="white")
        resolume_section.pack(fill=tk.X, padx=10, pady=10)
        
        resolume_frame = tk.Frame(resolume_section, bg="white")
        resolume_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(resolume_frame, text="Resolume IP Address:", bg="white").pack()
        
        self.resolume_ip_var = tk.StringVar(value="192.168.0.241")
        resolume_entry = tk.Entry(resolume_frame, textvariable=self.resolume_ip_var,
                                 font=("Arial", 12), justify=tk.CENTER)
        resolume_entry.pack(pady=5)
        
        tk.Button(resolume_frame, text="🔄 Update Resolume IP",
                 command=self.update_resolume_ip,
                 bg="#2196F3", fg="white", font=("Arial", 10)).pack(pady=5)
        
        # Other configuration options
        other_section = tk.LabelFrame(parent, text="⚙️ Other Settings", bg="white")
        other_section.pack(fill=tk.X, padx=10, pady=10)
        
        other_frame = tk.Frame(other_section, bg="white")
        other_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Config mode toggle
        tk.Button(other_frame, text="🔧 Toggle Config Mode",
                 command=self.toggle_config_mode,
                 bg="#9c27b0", fg="white").pack(pady=5)
    
    def create_port_management(self, parent):
        """Tạo quản lý port"""
        # Port information
        info_section = tk.LabelFrame(parent, text="📡 Port Information", bg="white")
        info_section.pack(fill=tk.X, padx=10, pady=10)
        
        self.port_info_frame = tk.Frame(info_section, bg="white")
        self.port_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Port calculation explanation
        explain_section = tk.LabelFrame(parent, text="💡 Port Convention", bg="white")
        explain_section.pack(fill=tk.X, padx=10, pady=10)
        
        explain_text = """Port Convention Rules:
• Each ESP gets a dedicated port
• Port = 7000 + last IP octet
• Example: 192.168.0.43 → Port 7043
• Example: 192.168.0.44 → Port 7044
• Valid range: 7001-7255"""
        
        tk.Label(explain_section, text=explain_text, 
                bg="white", justify=tk.LEFT, font=("Arial", 9)).pack(padx=10, pady=10)
    
    def create_realtime_display(self, parent):
        """Tạo hiển thị dữ liệu realtime"""
        data_frame = tk.LabelFrame(parent, text="📊 Real-time Data", 
                                  font=("Arial", 11, "bold"), bg="white")
        data_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Data grid
        self.data_grid = tk.Frame(data_frame, bg="white")
        self.data_grid.pack(fill=tk.X, padx=10, pady=10)
        
        self.realtime_labels = {}
        
        # Initialize with empty data
        self.update_realtime_display({})
    
    def create_system_monitor_panel(self, parent):
        """Tạo panel monitor hệ thống"""
        monitor_frame = tk.LabelFrame(parent, text="📈 System Monitor", 
                                     font=("Arial", 12, "bold"),
                                     bg="white", fg="#2c3e50", bd=2)
        monitor_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0))
        
        # Performance metrics
        perf_section = tk.LabelFrame(monitor_frame, text="⚡ Performance", bg="white")
        perf_section.pack(fill=tk.X, padx=10, pady=10)
        
        self.perf_labels = {}
        perf_metrics = [
            ("Total Packets Received", "total_received"),
            ("Total Packets Sent", "total_sent"),
            ("Active Connections", "active_connections"),
            ("Packets/Second", "packets_per_second")
        ]
        
        for label, key in perf_metrics:
            row_frame = tk.Frame(perf_section, bg="white")
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(row_frame, text=f"{label}:", bg="white", 
                    font=("Arial", 9)).pack(side=tk.LEFT)
            
            value_label = tk.Label(row_frame, text="0", bg="white", 
                                  font=("Arial", 9, "bold"), fg="#2c3e50")
            value_label.pack(side=tk.RIGHT)
            
            self.perf_labels[key] = value_label
        
        # Port status
        port_section = tk.LabelFrame(monitor_frame, text="🌐 Port Status", bg="white")
        port_section.pack(fill=tk.X, padx=10, pady=10)
        
        self.port_listbox = tk.Listbox(port_section, height=8, font=("Consolas", 9))
        port_scrollbar = tk.Scrollbar(port_section, orient=tk.VERTICAL)
        self.port_listbox.config(yscrollcommand=port_scrollbar.set)
        port_scrollbar.config(command=self.port_listbox.yview)
        
        self.port_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        port_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def create_log_panel(self, parent):
        """Tạo panel logs"""
        log_frame = tk.LabelFrame(parent, text="📜 System Logs", 
                                 font=("Arial", 11, "bold"),
                                 bg="white", fg="#2c3e50", bd=2)
        log_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        parent.grid_rowconfigure(2, weight=0, minsize=150)
        
        # Log controls
        log_controls = tk.Frame(log_frame, bg="white")
        log_controls.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(log_controls, text="🧹 Clear Logs",
                 command=self.clear_logs,
                 bg="#95a5a6", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_controls, text="💾 Export Logs",
                 command=self.export_logs,
                 bg="#34495e", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        tk.Checkbutton(log_controls, text="Auto-scroll", variable=self.auto_scroll_var,
                      bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=10)
        
        # Log text widget
        log_text_frame = tk.Frame(log_frame, bg="white")
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(log_text_frame, height=6, bg="#1e1e1e", fg="#00ff41",
                               font=("Consolas", 9), wrap=tk.WORD)
        
        log_text_scrollbar = tk.Scrollbar(log_text_frame, orient=tk.VERTICAL,
                                         command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_text_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Event handlers and methods
    def load_default_esps(self):
        """Load default ESP configurations"""
        default_esps = [
            ("ESP_043", "192.168.0.43"),
            ("ESP_044", "192.168.0.44"),
        ]
        
        for name, ip in default_esps:
            self.manager.register_esp(ip, name)
        
        self.refresh_esp_list()
    
    def add_esp_dialog(self):
        """Dialog thêm ESP mới"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New ESP32")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # ESP IP
        tk.Label(dialog, text="ESP32 IP Address:", bg="white", 
                font=("Arial", 11)).pack(pady=10)
        
        ip_var = tk.StringVar()
        ip_entry = tk.Entry(dialog, textvariable=ip_var, font=("Arial", 12), width=20)
        ip_entry.pack(pady=5)
        ip_entry.focus()
        
        # ESP Name
        tk.Label(dialog, text="Device Name (optional):", bg="white", 
                font=("Arial", 11)).pack(pady=(10, 0))
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, font=("Arial", 12), width=20)
        name_entry.pack(pady=5)
        
        # Port preview
        port_label = tk.Label(dialog, text="", bg="white", font=("Arial", 10), fg="#666")
        port_label.pack(pady=5)
        
        def update_port_preview():
            ip = ip_var.get().strip()
            if ip:
                try:
                    port = self.manager.calculate_port(ip)
                    port_label.config(text=f"Will use port: {port}")
                except:
                    port_label.config(text="Invalid IP format")
            else:
                port_label.config(text="")
        
        ip_var.trace('w', lambda *args: update_port_preview())
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg="white")
        btn_frame.pack(pady=20)
        
        def add_esp():
            ip = ip_var.get().strip()
            name = name_var.get().strip() or None
            
            if not ip:
                messagebox.showerror("Error", "Please enter an IP address")
                return
            
            if self.manager.register_esp(ip, name):
                self.refresh_esp_list()
                dialog.destroy()
                messagebox.showinfo("Success", f"ESP {ip} added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add ESP32")
        
        tk.Button(btn_frame, text="Add ESP", command=add_esp,
                 bg="#27ae60", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                 bg="#95a5a6", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        dialog.bind('<Return>', lambda e: add_esp())
    
    def refresh_esp_list(self):
        """Refresh ESP list"""
        # Clear current items
        for item in self.esp_tree.get_children():
            self.esp_tree.delete(item)
        
        # Add ESP devices
        esp_list = self.manager.get_esp_list()
        for esp in esp_list:
            status_color = "#27ae60" if esp['status'] == "Online" else "#e74c3c"
            
            item_id = self.esp_tree.insert("", tk.END, values=(
                esp['name'],
                esp['ip'], 
                esp['port'],
                esp['status'],
                f"R:{esp['packets_received']} S:{esp['packets_sent']}"
            ))
            
            # Color code by status
            if esp['status'] == "Online":
                self.esp_tree.set(item_id, "Status", "🟢 Online")
            else:
                self.esp_tree.set(item_id, "Status", "🔴 Offline")
    
    def on_esp_select(self, event):
        """Xử lý khi chọn ESP"""
        selection = self.esp_tree.selection()
        if selection:
            item = self.esp_tree.item(selection[0])
            values = item['values']
            
            esp_name = values[0]
            esp_ip = values[1]
            esp_port = values[2]
            
            self.selected_esp_ip = esp_ip
            self.selected_esp_label.config(
                text=f"🎯 {esp_name} ({esp_ip}:{esp_port})")
            
            # Update port management display
            self.update_port_info_display(esp_ip, esp_port)
    
    def update_port_info_display(self, esp_ip, port):
        """Cập nhật hiển thị thông tin port"""
        # Clear existing widgets
        for widget in self.port_info_frame.winfo_children():
            widget.destroy()
        
        # Create new display
        info_text = f"""Selected ESP: {esp_ip}
Listening Port: {port}
Port Calculation: 7000 + {esp_ip.split('.')[-1]} = {port}
ESP Send Port: 4210"""
        
        tk.Label(self.port_info_frame, text=info_text,
                bg="white", justify=tk.LEFT, font=("Consolas", 9)).pack()
    
    def start_auto_update(self):
        """Bắt đầu cập nhật tự động"""
        if self.auto_update_running:
            return
        
        self.auto_update_running = True
        
        def update_loop():
            while self.auto_update_running:
                try:
                    # Update header stats
                    stats = self.manager.get_performance_stats()
                    
                    self.header_labels['total_esps'].config(text=str(stats['total_esp_count']))
                    self.header_labels['online_esps'].config(text=str(stats['online_esp_count']))
                    self.header_labels['active_ports'].config(text=str(len(stats['ports_in_use'])))
                    
                    # Update performance labels
                    self.perf_labels['total_received'].config(text=str(stats['total_packets_received']))
                    self.perf_labels['total_sent'].config(text=str(stats['total_packets_sent']))
                    self.perf_labels['active_connections'].config(text=str(len(stats['active_connections'])))
                    
                    # Update port status
                    self.port_listbox.delete(0, tk.END)
                    for ip, port in stats['active_connections']:
                        self.port_listbox.insert(tk.END, f"🟢 {ip}:{port}")
                    
                    for port in stats['ports_in_use']:
                        if not any(p == port for _, p in stats['active_connections']):
                            self.port_listbox.insert(tk.END, f"🔴 Port {port} (Inactive)")
                    
                    # Update ESP list
                    self.refresh_esp_list()
                    
                    # Update logs
                    self.update_log_display()
                    
                except Exception as e:
                    print(f"Auto-update error: {e}")
                
                time.sleep(2)  # Update every 2 seconds
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def update_log_display(self):
        """Cập nhật hiển thị logs"""
        logs = self.manager.get_logs(20)  # Get last 20 logs
        
        # Clear and update
        self.log_text.delete(1.0, tk.END)
        for log in logs:
            self.log_text.insert(tk.END, log + "\\n")
        
        # Auto-scroll to bottom if enabled
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
    
    def start_communication(self):
        """Bắt đầu giao tiếp với tất cả ESP"""
        if self.manager.start_communication():
            messagebox.showinfo("Success", "Communication started for all registered ESPs")
        else:
            messagebox.showerror("Error", "Failed to start communication")
    
    def stop_communication(self):
        """Dừng giao tiếp"""
        self.manager.stop_communication()
        messagebox.showinfo("Info", "All communication stopped")
    
    def on_data_received(self, data):
        """Xử lý khi nhận dữ liệu từ ESP"""
        # Update real-time display if this is the selected ESP
        if self.selected_esp_ip == data.get('esp_ip'):
            self.update_realtime_display(data)
    
    def update_realtime_display(self, data):
        """Cập nhật hiển thị realtime"""
        # Clear existing widgets
        for widget in self.data_grid.winfo_children():
            widget.destroy()
        
        if not data:
            tk.Label(self.data_grid, text="No data available", 
                    bg="white", font=("Arial", 10), fg="#666").pack()
            return
        
        # Display data fields
        row = 0
        for key, value in data.items():
            if key in ['esp_name', 'esp_ip', 'esp_port', 'sender_ip', 'timestamp']:
                continue  # Skip metadata
            
            frame = tk.Frame(self.data_grid, bg="white")
            frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
            
            tk.Label(frame, text=f"{key.replace('_', ' ').title()}:", 
                    bg="white", font=("Arial", 9)).pack(side=tk.LEFT)
            
            tk.Label(frame, text=str(value), 
                    bg="white", font=("Arial", 9, "bold"), fg="#2c3e50").pack(side=tk.RIGHT)
            
            row += 1
        
        self.data_grid.grid_columnconfigure(0, weight=1)
    
    # Command methods
    def choose_color(self):
        """Chọn màu LED"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP32 first")
            return
        
        color = colorchooser.askcolor(title="Choose LED Color")
        if color and color[0]:
            r, g, b = map(int, color[0])
            self.color_preview.config(bg=color[1])
            
            # Send color command
            command = f"LEDCTRL:ALL,{r},{g},{b}"
            self.manager.send_command_to_esp(self.selected_esp_ip, command)
    
    def on_brightness_change(self, value):
        """Thay đổi độ sáng"""
        brightness = int(float(value))
        self.brightness_label.config(text=str(brightness))
        
        if self.selected_esp_ip:
            # Send brightness command (if supported)
            pass
    
    def send_rainbow(self):
        """Gửi hiệu ứng rainbow"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "RAINBOW:START")
    
    def test_led(self):
        """Test LED"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "LED_TEST")
    
    def flash_led(self):
        """Flash LED"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "LED_FLASH")
    
    def turn_off_led(self):
        """Tắt LED"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "LED:0")
    
    def send_threshold(self):
        """Gửi ngưỡng cảm biến"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP32 first")
            return
        
        try:
            threshold = int(self.threshold_var.get())
            command = f"THRESHOLD:{threshold}"
            
            if self.manager.send_command_to_esp(self.selected_esp_ip, command):
                messagebox.showinfo("Success", f"Threshold {threshold} sent successfully")
            else:
                messagebox.showerror("Error", "Failed to send threshold")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def update_resolume_ip(self):
        """Cập nhật IP Resolume"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP32 first")
            return
        
        new_ip = self.resolume_ip_var.get().strip()
        
        if not new_ip:
            messagebox.showerror("Error", "Please enter a valid IP address")
            return
        
        command = f"RESOLUME_IP:{new_ip}"
        
        if self.manager.send_command_to_esp(self.selected_esp_ip, command):
            messagebox.showinfo("Success", f"Resolume IP updated to {new_ip}")
        else:
            messagebox.showerror("Error", "Failed to update Resolume IP")
    
    def toggle_config_mode(self):
        """Toggle config mode"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP32 first")
            return
        
        # Toggle between CONFIG:1 and CONFIG:0
        # You might want to track state here
        self.manager.send_command_to_esp(self.selected_esp_ip, "CONFIG:1")
    
    def clear_logs(self):
        """Clear logs"""
        self.manager.log_messages.clear()
        self.log_text.delete(1.0, tk.END)
    
    def export_logs(self):
        """Export logs to file"""
        try:
            filename = f"esp_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                for log in self.manager.log_messages:
                    f.write(log + "\\n")
            messagebox.showinfo("Success", f"Logs exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {e}")
    
    def on_esp_status_change(self, esp_ip, status):
        """Xử lý khi trạng thái ESP thay đổi"""
        self.refresh_esp_list()
    
    def show_esp_context_menu(self, event):
        """Hiển thị context menu"""
        item = self.esp_tree.selection()
        if item:
            self.esp_context_menu.post(event.x_root, event.y_root)
    
    def view_esp_details(self):
        """Xem chi tiết ESP"""
        if not self.selected_esp_ip:
            return
        
        esp_list = self.manager.get_esp_list()
        esp_data = next((esp for esp in esp_list if esp['ip'] == self.selected_esp_ip), None)
        
        if esp_data:
            details = f"""ESP Details:
Name: {esp_data['name']}
IP Address: {esp_data['ip']}
Listen Port: {esp_data['port']}
Status: {esp_data['status']}
Packets Received: {esp_data['packets_received']}
Packets Sent: {esp_data['packets_sent']}
Queue Size: {esp_data['queue_size']}"""
            
            messagebox.showinfo("ESP Details", details)
    
    def connect_esp(self):
        """Connect to ESP"""
        # Implementation depends on your connection logic
        pass
    
    def disconnect_esp(self):
        """Disconnect from ESP"""
        # Implementation depends on your connection logic
        pass
    
    def remove_esp(self):
        """Remove ESP"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP32 first")
            return
        
        if messagebox.askyesno("Confirm", f"Remove ESP {self.selected_esp_ip}?"):
            if self.manager.unregister_esp(self.selected_esp_ip):
                self.selected_esp_ip = None
                self.selected_esp_label.config(text="🔘 No ESP selected")
                self.refresh_esp_list()
                messagebox.showinfo("Success", "ESP removed successfully")


# Example usage
if __name__ == "__main__":
    class DemoConfig:
        pass
    
    root = tk.Tk()
    config = DemoConfig()
    app = PortPerESPGUI(root, config)
    
    try:
        root.mainloop()
    finally:
        app.auto_update_running = False
        app.manager.stop_communication()