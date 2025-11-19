#!/usr/bin/env python3
"""
Auto-Discovery GUI
Giao diện quản lý ESP với auto-discovery và dynamic port allocation
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import threading
import time
from datetime import datetime, timedelta
from auto_discovery_manager import AutoDiscoveryManager

class AutoDiscoveryGUI:
    """GUI cho Auto-Discovery ESP Management"""
    
    def __init__(self, root, config=None):
        self.root = root
        self.config = config
        self.manager = AutoDiscoveryManager(config)
        
        # GUI state
        self.selected_esp_ip = None
        self.auto_update_running = False
        self.discovery_running = False
        
        # Setup callbacks
        self.manager.on_esp_discovered = self.on_esp_discovered
        self.manager.on_esp_connected = self.on_esp_connected
        self.manager.on_esp_disconnected = self.on_esp_disconnected
        self.manager.on_data_received = self.on_data_received
        
        self.setup_window()
        self.create_widgets()
        self.start_auto_update()
    
    def setup_window(self):
        """Thiết lập cửa sổ"""
        self.root.title("🔍 Auto-Discovery ESP Manager")
        self.root.geometry("1600x1000")
        self.root.configure(bg="#f0f0f0")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_widgets(self):
        """Tạo giao diện"""
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure main frame
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Header with discovery controls
        self.create_header(main_frame)
        
        # Left: Discovery panel
        self.create_discovery_panel(main_frame)
        
        # Center: ESP Control panel
        self.create_control_panel(main_frame)
        
        # Right: System monitor
        self.create_monitor_panel(main_frame)
        
        # Bottom: Logs
        self.create_log_panel(main_frame)
    
    def create_header(self, parent):
        """Tạo header với discovery controls"""
        header_frame = tk.Frame(parent, bg="#2c3e50", height=100)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title and discovery status
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        tk.Label(title_frame, text="🔍", font=("Arial", 28), 
                bg="#2c3e50", fg="#3498db").pack(side=tk.LEFT, padx=(0, 15))
        
        title_label = tk.Label(title_frame, text="Auto-Discovery ESP Manager", 
                              font=("Arial", 20, "bold"), 
                              bg="#2c3e50", fg="white")
        title_label.pack(side=tk.LEFT)
        
        # Discovery status indicator
        status_frame = tk.Frame(header_frame, bg="#2c3e50")
        status_frame.grid(row=0, column=1, padx=20, pady=15)
        
        self.discovery_status_label = tk.Label(status_frame, 
                                              text="🔴 Discovery: Stopped", 
                                              font=("Arial", 14, "bold"), 
                                              bg="#2c3e50", fg="#e74c3c")
        self.discovery_status_label.pack()
        
        self.port_info_label = tk.Label(status_frame, 
                                       text="Discovery Port: 7000", 
                                       font=("Arial", 11), 
                                       bg="#2c3e50", fg="#bdc3c7")
        self.port_info_label.pack()
        
        # Control buttons
        control_frame = tk.Frame(header_frame, bg="#2c3e50")
        control_frame.grid(row=0, column=2, sticky="e", padx=20, pady=15)
        
        self.start_btn = tk.Button(control_frame, text="🚀 Start Discovery", 
                                  command=self.start_discovery,
                                  bg="#27ae60", fg="white", 
                                  font=("Arial", 12, "bold"), width=15)
        self.start_btn.pack(side=tk.TOP, pady=5)
        
        self.stop_btn = tk.Button(control_frame, text="🛑 Stop Discovery", 
                                 command=self.stop_discovery,
                                 bg="#e74c3c", fg="white", 
                                 font=("Arial", 12, "bold"), width=15,
                                 state=tk.DISABLED)
        self.stop_btn.pack(side=tk.TOP, pady=5)
    
    def create_discovery_panel(self, parent):
        """Tạo panel discovery"""
        discovery_frame = tk.LabelFrame(parent, text="🔍 ESP Discovery", 
                                       font=("Arial", 14, "bold"),
                                       bg="white", fg="#2c3e50", bd=2)
        discovery_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # Discovery info
        info_frame = tk.Frame(discovery_frame, bg="white")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = """Auto-Discovery Process:
1. ESPs send heartbeat to port 7000 every 5s
2. System auto-detects ESP IP addresses  
3. Dynamic port allocation (70XX format)
4. ESP receives port assignment
5. Data communication on assigned port"""
        
        tk.Label(info_frame, text=info_text, bg="white", 
                justify=tk.LEFT, font=("Arial", 9)).pack()
        
        # Discovered ESPs TreeView
        tree_frame = tk.Frame(discovery_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
        
        # TreeView columns
        columns = ("Name", "IP", "Port", "Status", "Last Seen", "Packets")
        self.esp_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {
            "Name": 100, "IP": 110, "Port": 60, 
            "Status": 80, "Last Seen": 80, "Packets": 60
        }
        
        for col in columns:
            self.esp_tree.heading(col, text=col)
            self.esp_tree.column(col, width=column_widths.get(col, 80), minwidth=50)
        
        # Scrollbar
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.esp_tree.yview)
        self.esp_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.esp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.esp_tree.bind("<<TreeviewSelect>>", self.on_esp_select)
        
        # Context menu
        self.create_esp_context_menu()
        
        # Control buttons
        btn_frame = tk.Frame(discovery_frame, bg="white")
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_esp_list,
                 bg="#3498db", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="📊 Details", command=self.show_esp_details,
                 bg="#9b59b6", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🗑️ Remove", command=self.remove_esp,
                 bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    def create_esp_context_menu(self):
        """Tạo context menu cho ESP tree"""
        self.esp_context_menu = tk.Menu(self.root, tearoff=0)
        self.esp_context_menu.add_command(label="📊 View Details", command=self.show_esp_details)
        self.esp_context_menu.add_command(label="🔄 Force Refresh", command=self.force_refresh_esp)
        self.esp_context_menu.add_separator()
        self.esp_context_menu.add_command(label="💡 Test LED", command=self.test_esp_led)
        self.esp_context_menu.add_command(label="📡 Send Ping", command=self.ping_esp)
        self.esp_context_menu.add_separator()
        self.esp_context_menu.add_command(label="🗑️ Remove", command=self.remove_esp)
        
        self.esp_tree.bind("<Button-3>", self.show_esp_context_menu)
    
    def create_control_panel(self, parent):
        """Tạo panel điều khiển ESP"""
        control_frame = tk.LabelFrame(parent, text="🎛️ ESP Control Panel", 
                                     font=("Arial", 14, "bold"),
                                     bg="white", fg="#2c3e50", bd=2)
        control_frame.grid(row=1, column=1, sticky="nsew", padx=5)
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Selected ESP info
        info_frame = tk.Frame(control_frame, bg="#ecf0f1", relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.selected_esp_label = tk.Label(info_frame, 
                                          text="🔘 No ESP selected", 
                                          font=("Arial", 13, "bold"),
                                          bg="#ecf0f1", fg="#2c3e50")
        self.selected_esp_label.pack(pady=15)
        
        # Quick actions
        quick_frame = tk.LabelFrame(control_frame, text="⚡ Quick Actions", bg="white")
        quick_frame.pack(fill=tk.X, padx=10, pady=10)
        
        quick_btn_frame = tk.Frame(quick_frame, bg="white")
        quick_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        quick_actions = [
            ("💡 Test LED", self.test_esp_led, "#f39c12"),
            ("🌈 Rainbow", self.send_rainbow, "#e91e63"),
            ("📡 Ping ESP", self.ping_esp, "#3498db"),
            ("🔄 Refresh", self.force_refresh_esp, "#95a5a6")
        ]
        
        for i, (text, command, color) in enumerate(quick_actions):
            btn = tk.Button(quick_btn_frame, text=text, command=command,
                           bg=color, fg="white", font=("Arial", 10))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        
        quick_btn_frame.grid_columnconfigure(0, weight=1)
        quick_btn_frame.grid_columnconfigure(1, weight=1)
        
        # Control tabs
        self.control_notebook = ttk.Notebook(control_frame)
        self.control_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # LED Control
        led_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(led_frame, text="💡 LED Control")
        self.create_led_controls(led_frame)
        
        # Touch Sensor  
        touch_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(touch_frame, text="👆 Touch Sensor")
        self.create_touch_controls(touch_frame)
        
        # Configuration
        config_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(config_frame, text="⚙️ Configuration")
        self.create_config_controls(config_frame)
        
        # Real-time data
        self.create_realtime_display(control_frame)
    
    def create_led_controls(self, parent):
        """Tạo điều khiển LED"""
        # Color control
        color_section = tk.LabelFrame(parent, text="🎨 Color Control", bg="white")
        color_section.pack(fill=tk.X, padx=10, pady=10)
        
        color_frame = tk.Frame(color_section, bg="white")
        color_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(color_frame, text="Color:", bg="white").pack(side=tk.LEFT)
        
        self.color_preview = tk.Label(color_frame, text="   ", bg="#ff0000", 
                                     relief=tk.RAISED, bd=2, cursor="hand2")
        self.color_preview.pack(side=tk.LEFT, padx=(10, 5))
        self.color_preview.bind("<Button-1>", lambda e: self.choose_color())
        
        tk.Button(color_frame, text="🎨 Choose Color", 
                 command=self.choose_color,
                 bg="#9b59b6", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Brightness
        brightness_section = tk.LabelFrame(parent, text="💡 Brightness", bg="white")
        brightness_section.pack(fill=tk.X, padx=10, pady=10)
        
        brightness_frame = tk.Frame(brightness_section, bg="white")
        brightness_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.brightness_var = tk.IntVar(value=128)
        
        tk.Label(brightness_frame, text="Brightness:", bg="white").pack(side=tk.LEFT)
        
        self.brightness_scale = tk.Scale(brightness_frame, from_=1, to=255, 
                                        orient=tk.HORIZONTAL, variable=self.brightness_var,
                                        command=self.on_brightness_change, bg="white")
        self.brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.brightness_label = tk.Label(brightness_frame, text="128", 
                                        bg="white", font=("Arial", 10, "bold"))
        self.brightness_label.pack(side=tk.LEFT)
        
        # LED Effects
        effects_section = tk.LabelFrame(parent, text="✨ Effects", bg="white")
        effects_section.pack(fill=tk.X, padx=10, pady=10)
        
        effects_frame = tk.Frame(effects_section, bg="white")
        effects_frame.pack(fill=tk.X, padx=10, pady=10)
        
        effects = [
            ("🌈 Rainbow", self.send_rainbow, "#e91e63"),
            ("⚡ Flash", self.flash_led, "#3f51b5"),
            ("🔴 Turn Off", self.turn_off_led, "#f44336"),
            ("💡 Full On", self.full_on_led, "#4caf50")
        ]
        
        for i, (text, command, color) in enumerate(effects):
            btn = tk.Button(effects_frame, text=text, command=command,
                           bg=color, fg="white", font=("Arial", 10))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        
        effects_frame.grid_columnconfigure(0, weight=1)
        effects_frame.grid_columnconfigure(1, weight=1)
    
    def create_touch_controls(self, parent):
        """Tạo điều khiển cảm biến chạm"""
        # Threshold setting
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
    
    def create_config_controls(self, parent):
        """Tạo điều khiển cấu hình"""
        # Resolume IP
        resolume_section = tk.LabelFrame(parent, text="🎬 Resolume Configuration", bg="white")
        resolume_section.pack(fill=tk.X, padx=10, pady=10)
        
        resolume_frame = tk.Frame(resolume_section, bg="white")
        resolume_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(resolume_frame, text="Resolume IP:", bg="white").pack()
        
        self.resolume_ip_var = tk.StringVar(value="192.168.0.241")
        resolume_entry = tk.Entry(resolume_frame, textvariable=self.resolume_ip_var,
                                 font=("Arial", 12), justify=tk.CENTER)
        resolume_entry.pack(pady=5)
        
        tk.Button(resolume_frame, text="🔄 Update IP",
                 command=self.update_resolume_ip,
                 bg="#2196F3", fg="white").pack(pady=5)
    
    def create_realtime_display(self, parent):
        """Tạo hiển thị dữ liệu realtime"""
        data_frame = tk.LabelFrame(parent, text="📊 Real-time Data", 
                                  font=("Arial", 12, "bold"), bg="white")
        data_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.data_display = tk.Text(data_frame, height=6, bg="#1e1e1e", fg="#00ff41",
                                   font=("Consolas", 9), wrap=tk.WORD)
        
        data_scrollbar = tk.Scrollbar(data_frame, orient=tk.VERTICAL, 
                                     command=self.data_display.yview)
        self.data_display.configure(yscrollcommand=data_scrollbar.set)
        
        self.data_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        data_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def create_monitor_panel(self, parent):
        """Tạo panel monitor"""
        monitor_frame = tk.LabelFrame(parent, text="📈 System Monitor", 
                                     font=("Arial", 14, "bold"),
                                     bg="white", fg="#2c3e50", bd=2)
        monitor_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0))
        
        # Statistics
        stats_section = tk.LabelFrame(monitor_frame, text="📊 Statistics", bg="white")
        stats_section.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_labels = {}
        stats_items = [
            ("Total ESPs", "total_esps"),
            ("Connected", "connected_esps"),
            ("Offline", "offline_esps"),
            ("Active Ports", "active_ports"),
            ("Total Heartbeats", "total_heartbeats"),
            ("Total Data Packets", "total_data_packets")
        ]
        
        for label, key in stats_items:
            row_frame = tk.Frame(stats_section, bg="white")
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(row_frame, text=f"{label}:", bg="white", 
                    font=("Arial", 9)).pack(side=tk.LEFT)
            
            value_label = tk.Label(row_frame, text="0", bg="white", 
                                  font=("Arial", 9, "bold"), fg="#2c3e50")
            value_label.pack(side=tk.RIGHT)
            
            self.stats_labels[key] = value_label
        
        # Port assignments
        port_section = tk.LabelFrame(monitor_frame, text="🌐 Port Assignments", bg="white")
        port_section.pack(fill=tk.X, padx=10, pady=10)
        
        self.port_listbox = tk.Listbox(port_section, height=8, font=("Consolas", 9))
        port_scrollbar = tk.Scrollbar(port_section, orient=tk.VERTICAL)
        
        self.port_listbox.config(yscrollcommand=port_scrollbar.set)
        port_scrollbar.config(command=self.port_listbox.yview)
        
        self.port_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        port_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Discovery timeline
        timeline_section = tk.LabelFrame(monitor_frame, text="⏱️ Discovery Timeline", bg="white")
        timeline_section.pack(fill=tk.X, padx=10, pady=10)
        
        self.timeline_text = tk.Text(timeline_section, height=6, bg="white", 
                                    font=("Arial", 8), wrap=tk.WORD)
        timeline_scrollbar = tk.Scrollbar(timeline_section, orient=tk.VERTICAL,
                                         command=self.timeline_text.yview)
        self.timeline_text.configure(yscrollcommand=timeline_scrollbar.set)
        
        self.timeline_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        timeline_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def create_log_panel(self, parent):
        """Tạo panel logs"""
        log_frame = tk.LabelFrame(parent, text="📜 System Logs", 
                                 font=("Arial", 12, "bold"),
                                 bg="white", fg="#2c3e50", bd=2)
        log_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        parent.grid_rowconfigure(2, weight=0, minsize=180)
        
        # Log controls
        log_controls = tk.Frame(log_frame, bg="white")
        log_controls.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(log_controls, text="🧹 Clear", command=self.clear_logs,
                 bg="#95a5a6", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_controls, text="💾 Export", command=self.export_logs,
                 bg="#34495e", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        tk.Checkbutton(log_controls, text="Auto-scroll", variable=self.auto_scroll_var,
                      bg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=10)
        
        # Log text
        log_text_frame = tk.Frame(log_frame, bg="white")
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(log_text_frame, height=8, bg="#1e1e1e", fg="#00ff41",
                               font=("Consolas", 9), wrap=tk.WORD)
        
        log_scrollbar = tk.Scrollbar(log_text_frame, orient=tk.VERTICAL,
                                    command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Event handlers
    def start_discovery(self):
        """Bắt đầu discovery"""
        if self.manager.start_discovery():
            self.discovery_running = True
            self.discovery_status_label.config(text="🟢 Discovery: Running", fg="#27ae60")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.add_timeline_entry("🚀 Discovery service started")
            messagebox.showinfo("Success", "Auto-Discovery started!\\nESPs will be detected automatically when they send heartbeats.")
        else:
            messagebox.showerror("Error", "Failed to start discovery service")
    
    def stop_discovery(self):
        """Dừng discovery"""
        self.manager.stop_discovery()
        self.discovery_running = False
        self.discovery_status_label.config(text="🔴 Discovery: Stopped", fg="#e74c3c")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.add_timeline_entry("🛑 Discovery service stopped")
        messagebox.showinfo("Info", "Auto-Discovery stopped")
    
    def on_esp_select(self, event):
        """Xử lý chọn ESP"""
        selection = self.esp_tree.selection()
        if selection:
            item = self.esp_tree.item(selection[0])
            values = item['values']
            
            esp_name = values[0]
            esp_ip = values[1]
            esp_port = values[2]
            status = values[3]
            
            self.selected_esp_ip = esp_ip
            self.selected_esp_label.config(
                text=f"🎯 {esp_name} ({esp_ip}:{esp_port}) [{status}]")
    
    def refresh_esp_list(self):
        """Refresh danh sách ESP"""
        # Clear current items
        for item in self.esp_tree.get_children():
            self.esp_tree.delete(item)
        
        # Get discovered ESPs
        esps = self.manager.get_discovered_esps()
        
        for esp in esps:
            # Calculate time since last seen
            if esp['last_heartbeat'] > 0:
                time_diff = time.time() - esp['last_heartbeat']
                if time_diff < 60:
                    last_seen = f"{int(time_diff)}s ago"
                else:
                    last_seen = f"{int(time_diff/60)}m ago"
            else:
                last_seen = "Never"
            
            # Status with emoji
            status_map = {
                "Discovered": "🔍 Discovered",
                "Assigned": "📡 Assigned", 
                "Connected": "🟢 Connected",
                "Offline": "🔴 Offline"
            }
            status_text = status_map.get(esp['status'], esp['status'])
            
            # Packets info
            packets_info = f"H:{esp['heartbeat_count']} D:{esp['data_packets_received']}"
            
            self.esp_tree.insert("", tk.END, values=(
                esp['name'],
                esp['ip'],
                esp['assigned_port'],
                status_text,
                last_seen,
                packets_info
            ))
    
    def start_auto_update(self):
        """Bắt đầu auto-update"""
        if self.auto_update_running:
            return
        
        self.auto_update_running = True
        
        def update_loop():
            while self.auto_update_running:
                try:
                    # Update statistics
                    stats = self.manager.get_statistics()
                    
                    for key, label in self.stats_labels.items():
                        if key in stats:
                            label.config(text=str(stats[key]))
                    
                    # Update port assignments
                    self.port_listbox.delete(0, tk.END)
                    for port, esp_ip in stats.get('port_assignments', {}).items():
                        esp_name = next((esp['name'] for esp in self.manager.get_discovered_esps() 
                                       if esp['ip'] == esp_ip), esp_ip)
                        self.port_listbox.insert(tk.END, f"Port {port}: {esp_name} ({esp_ip})")
                    
                    # Update ESP list
                    self.refresh_esp_list()
                    
                    # Update logs
                    self.update_log_display()
                    
                except Exception as e:
                    print(f"Auto-update error: {e}")
                
                time.sleep(2)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def update_log_display(self):
        """Cập nhật hiển thị logs"""
        logs = self.manager.get_logs(15)
        
        self.log_text.delete(1.0, tk.END)
        for log in logs:
            self.log_text.insert(tk.END, log + "\\n")
        
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
    
    def add_timeline_entry(self, message):
        """Thêm entry vào timeline"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}\\n"
        
        self.timeline_text.insert(tk.END, entry)
        self.timeline_text.see(tk.END)
    
    # ESP event callbacks
    def on_esp_discovered(self, esp_info):
        """Callback khi phát hiện ESP mới"""
        self.add_timeline_entry(f"🔍 ESP discovered: {esp_info['name']} ({esp_info['ip']})")
        self.refresh_esp_list()
    
    def on_esp_connected(self, esp_info):
        """Callback khi ESP kết nối"""
        self.add_timeline_entry(f"✅ ESP connected: {esp_info['name']} on port {esp_info['assigned_port']}")
        self.refresh_esp_list()
    
    def on_esp_disconnected(self, esp_info):
        """Callback khi ESP ngắt kết nối"""
        self.add_timeline_entry(f"⚠️ ESP disconnected: {esp_info['name']} ({esp_info['ip']})")
        self.refresh_esp_list()
    
    def on_data_received(self, data):
        """Callback khi nhận dữ liệu"""
        if self.selected_esp_ip == data.get('esp_ip'):
            # Update real-time display for selected ESP
            timestamp = datetime.now().strftime("%H:%M:%S")
            data_str = f"[{timestamp}] {data.get('esp_name', 'Unknown')}: "
            
            # Format data nicely
            for key, value in data.items():
                if key not in ['esp_name', 'esp_ip', 'esp_port', 'sender_ip', 'timestamp']:
                    data_str += f"{key}={value} "
            
            self.data_display.insert(tk.END, data_str + "\\n")
            self.data_display.see(tk.END)
            
            # Limit display length
            lines = self.data_display.get(1.0, tk.END).split('\\n')
            if len(lines) > 20:
                self.data_display.delete(1.0, f"{len(lines)-20}.0")
    
    # Control methods
    def choose_color(self):
        """Chọn màu LED"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP first")
            return
        
        color = colorchooser.askcolor(title="Choose LED Color")
        if color and color[0]:
            r, g, b = map(int, color[0])
            self.color_preview.config(bg=color[1])
            
            command = f"LEDCTRL:ALL,{r},{g},{b}"
            self.manager.send_command_to_esp(self.selected_esp_ip, command)
    
    def on_brightness_change(self, value):
        """Thay đổi độ sáng"""
        brightness = int(float(value))
        self.brightness_label.config(text=str(brightness))
    
    def test_esp_led(self):
        """Test LED ESP"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP first")
            return
        
        self.manager.send_command_to_esp(self.selected_esp_ip, "LED_TEST")
    
    def send_rainbow(self):
        """Gửi hiệu ứng rainbow"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP first")
            return
        
        self.manager.send_command_to_esp(self.selected_esp_ip, "RAINBOW:START")
    
    def flash_led(self):
        """Flash LED"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "LED_FLASH")
    
    def turn_off_led(self):
        """Tắt LED"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "LED:0")
    
    def full_on_led(self):
        """Bật sáng LED"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "LED:1")
    
    def send_threshold(self):
        """Gửi threshold"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP first")
            return
        
        try:
            threshold = int(self.threshold_var.get())
            command = f"THRESHOLD:{threshold}"
            
            if self.manager.send_command_to_esp(self.selected_esp_ip, command):
                messagebox.showinfo("Success", f"Threshold {threshold} sent successfully")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def update_resolume_ip(self):
        """Cập nhật IP Resolume"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP first")
            return
        
        new_ip = self.resolume_ip_var.get().strip()
        command = f"RESOLUME_IP:{new_ip}"
        
        if self.manager.send_command_to_esp(self.selected_esp_ip, command):
            messagebox.showinfo("Success", f"Resolume IP updated to {new_ip}")
    
    def ping_esp(self):
        """Ping ESP"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "PING")
    
    def force_refresh_esp(self):
        """Force refresh ESP"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "STATUS_REQUEST")
    
    def show_esp_details(self):
        """Hiển thị chi tiết ESP"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP first")
            return
        
        esps = self.manager.get_discovered_esps()
        esp_data = next((esp for esp in esps if esp['ip'] == self.selected_esp_ip), None)
        
        if esp_data:
            # Calculate uptime
            uptime = time.time() - esp_data['discovery_time']
            uptime_str = f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s"
            
            details = f"""ESP Detailed Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {esp_data['name']}
IP Address: {esp_data['ip']}
Assigned Port: {esp_data['assigned_port']}
Status: {esp_data['status']}

Discovery Time: {datetime.fromtimestamp(esp_data['discovery_time']).strftime('%Y-%m-%d %H:%M:%S')}
Last Heartbeat: {datetime.fromtimestamp(esp_data['last_heartbeat']).strftime('%Y-%m-%d %H:%M:%S') if esp_data['last_heartbeat'] > 0 else 'Never'}
Uptime: {uptime_str}

Statistics:
• Heartbeat Count: {esp_data['heartbeat_count']}
• Data Packets Received: {esp_data['data_packets_received']}

Port Convention:
• Port = 7000 + {esp_data['ip'].split('.')[-1]} = {esp_data['assigned_port']}"""
            
            messagebox.showinfo(f"ESP Details - {esp_data['name']}", details)
    
    def remove_esp(self):
        """Xóa ESP"""
        if not self.selected_esp_ip:
            messagebox.showwarning("Warning", "Please select an ESP first")
            return
        
        esp_name = next((esp['name'] for esp in self.manager.get_discovered_esps() 
                        if esp['ip'] == self.selected_esp_ip), self.selected_esp_ip)
        
        if messagebox.askyesno("Confirm", f"Remove ESP {esp_name} ({self.selected_esp_ip})?"):
            if self.manager.remove_esp(self.selected_esp_ip):
                self.selected_esp_ip = None
                self.selected_esp_label.config(text="🔘 No ESP selected")
                self.refresh_esp_list()
                messagebox.showinfo("Success", "ESP removed successfully")
    
    def show_esp_context_menu(self, event):
        """Hiển thị context menu"""
        item = self.esp_tree.selection()
        if item:
            self.esp_context_menu.post(event.x_root, event.y_root)
    
    def clear_logs(self):
        """Clear logs"""
        self.manager.log_messages.clear()
        self.log_text.delete(1.0, tk.END)
    
    def export_logs(self):
        """Export logs"""
        try:
            filename = f"auto_discovery_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                for log in self.manager.log_messages:
                    f.write(log + "\\n")
            messagebox.showinfo("Success", f"Logs exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {e}")

# Main application
if __name__ == "__main__":
    class DemoConfig:
        pass
    
    root = tk.Tk()
    config = DemoConfig()
    app = AutoDiscoveryGUI(root, config)
    
    try:
        root.mainloop()
    finally:
        app.auto_update_running = False
        app.manager.stop_discovery()