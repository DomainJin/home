#!/usr/bin/env python3
"""
GUI module for Cube Touch Monitor
Giao diện người dùng được tối ưu hóa
"""

import tkinter as tk
from tkinter import colorchooser, ttk, messagebox, scrolledtext
from led import LEDController
from touch import TouchController
import threading
from auto_discovery_manager import AutoDiscoveryManager
from auto_discovery_gui import AutoDiscoveryGUI

class CubeTouchGUI:
    """Giao diện chính của ứng dụng"""
    
    def __init__(self, root, comm_handler, config):
        self.root = root
        self.comm_handler = comm_handler
        self.config = config
        
        # Controllers
        self.led_controller = LEDController(comm_handler)
        self.touch_controller = TouchController(comm_handler)
        
        # GUI components
        self.admin_window = None
        
        # Setup callback
        self.comm_handler.on_data_update = self.update_realtime_data
        
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        self.root.title(self.config.window_title)
        self.root.geometry("1100x750")
        self.root.configure(bg="#f8f9fa")
        self.root.minsize(900, 600)
        
        # Center window on screen
        self.center_window()
        
        # Enable responsive scaling
        self.root.resizable(True, True)
        
        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Add window icon and styling
        try:
            self.root.iconbitmap(default="")
        except:
            pass
    
    def create_widgets(self):
        """Tạo các widget"""
        # Main scrollable frame
        self.create_scrollable_frame()
        
        # Create sections
        self.create_header()
        self.create_led_control_section()
        self.create_config_section()
        self.create_touch_section()
        self.create_realtime_section()
        self.create_status_section()
    
    def create_scrollable_frame(self):
        """Tạo frame có thể cuộn với responsive design"""
        # Create main container
        main_container = tk.Frame(self.root, bg="#f8f9fa")
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(main_container, bg="#f8f9fa", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8f9fa")
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Grid canvas and scrollbar
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Configure responsive grid - 3 columns with equal weight
        for i in range(3):
            self.scrollable_frame.grid_columnconfigure(i, weight=1, minsize=300)
        
        # Configure rows
        self.scrollable_frame.grid_rowconfigure(1, weight=1)  # Main content row
        
        # Add padding to main frame
        self.scrollable_frame.configure(bg="#f8f9fa")
        
        # Mouse wheel scrolling
        self._bind_mousewheel()
    
    def center_window(self):
        """Căn giữa cửa sổ trên màn hình"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def on_window_resize(self, event):
        """Xử lý khi resize cửa sổ"""
        if event.widget == self.root:
            # Update canvas scroll region
            self.root.after_idle(self.update_scroll_region)
    
    def update_scroll_region(self):
        """Cập nhật scroll region"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _bind_mousewheel(self):
        """Bind mouse wheel to canvas"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.root.bind("<MouseWheel>", _on_mousewheel)
    
    def on_canvas_configure(self, event):
        """Xử lý khi canvas resize"""
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Make scrollable_frame fill canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def create_header(self):
        """Tạo header hiện đại với responsive design"""
        # Main header container with gradient effect
        header_main = tk.Frame(self.scrollable_frame, bg="#2c3e50", height=80)
        header_main.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        header_main.grid_propagate(False)
        header_main.grid_columnconfigure(1, weight=1)
        
        # Left side - Logo and title
        left_frame = tk.Frame(header_main, bg="#2c3e50")
        left_frame.grid(row=0, column=0, sticky="w", padx=30, pady=15)
        
        title_label = tk.Label(left_frame, text="🎨 CUBE TOUCH", 
                              font=("Segoe UI", 24, "bold"), 
                              bg="#2c3e50", fg="#ecf0f1")
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = tk.Label(left_frame, text="Professional LED Control System", 
                                 font=("Segoe UI", 11), 
                                 bg="#2c3e50", fg="#bdc3c7")
        subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Right side - Navigation
        nav_frame = tk.Frame(header_main, bg="#2c3e50")
        nav_frame.grid(row=0, column=2, sticky="e", padx=30, pady=20)
        
        # Status indicator
        self.status_indicator = tk.Label(nav_frame, text="●", font=("Segoe UI", 16), 
                                        bg="#2c3e50", fg="#27ae60")
        self.status_indicator.grid(row=0, column=0, padx=(0, 10))
        
        status_text = tk.Label(nav_frame, text="ONLINE", font=("Segoe UI", 10, "bold"), 
                              bg="#2c3e50", fg="#27ae60")
        status_text.grid(row=0, column=1, padx=(0, 20))
        
        # Admin button with modern style
        admin_btn = tk.Button(nav_frame, text="⚙️ ADMIN PANEL", command=self.open_admin_window,
                             bg="#e74c3c", fg="white", font=("Segoe UI", 11, "bold"),
                             relief=tk.FLAT, cursor="hand2", padx=25, pady=8,
                             activebackground="#c0392b")
        admin_btn.grid(row=0, column=2)
    
    def create_led_control_section(self):
        """Tạo section điều khiển LED với thiết kế card"""
        # LED Control Card
        led_card = tk.Frame(self.scrollable_frame, bg="white", relief="solid", bd=1)
        led_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add shadow effect
        shadow_frame = tk.Frame(self.scrollable_frame, bg="#e0e0e0", height=2)
        shadow_frame.grid(row=1, column=0, sticky="ew", padx=17, pady=17, ipady=1)
        
        # Card header
        header = tk.Frame(led_card, bg="#3498db", height=50)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        
        header_label = tk.Label(header, text="🎯 LED CONTROL", 
                               font=("Segoe UI", 14, "bold"), 
                               bg="#3498db", fg="white")
        header_label.grid(row=0, column=0, pady=15)
        
        # Card content
        led_frame = tk.Frame(led_card, bg="white", padx=25, pady=25)
        led_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure grid
        led_frame.grid_columnconfigure(0, weight=1)
        
        # LED Toggle
        self.btn_led_toggle = tk.Button(led_frame, text="🟢 LED: Bật", 
                                       command=self.toggle_led,
                                       font=("Segoe UI", 12, "bold"), 
                                       bg=self.config.colors['success'], fg="white",
                                       relief=tk.FLAT, cursor="hand2", pady=10)
        self.btn_led_toggle.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        
        # Color chooser
        btn_color = tk.Button(led_frame, text="🎨 Chọn màu", command=self.choose_color,
                             font=("Segoe UI", 12), bg=self.config.colors['primary'], 
                             fg="white", relief=tk.FLAT, cursor="hand2", pady=8)
        btn_color.grid(row=1, column=0, pady=(0, 15), sticky="ew")
        
        # Color preview
        self.color_preview = tk.Label(led_frame, text="Preview", height=3,
                                     font=("Segoe UI", 11), bg="white", 
                                     relief=tk.RAISED, bd=2)
        self.color_preview.grid(row=2, column=0, pady=(0, 15), sticky="ew")
        
        # Brightness control
        brightness_label = tk.Label(led_frame, text="💡 Độ sáng", 
                                   font=("Segoe UI", 12, "bold"),
                                   bg=self.config.colors['background'], 
                                   fg=self.config.colors['secondary'])
        brightness_label.grid(row=3, column=0, sticky="ew")
        
        self.brightness_var = tk.IntVar(value=self.config.default_brightness)
        self.brightness_scale = tk.Scale(led_frame, from_=1, to=255, orient="horizontal",
                                        variable=self.brightness_var, 
                                        bg=self.config.colors['background'],
                                        command=self.on_brightness_change,
                                        font=("Segoe UI", 10),
                                        troughcolor=self.config.colors['light'],
                                        activebackground=self.config.colors['primary'])
        self.brightness_scale.grid(row=4, column=0, pady=(5, 15), sticky="ew")
        
        # RGB info
        self.rgb_label = tk.Label(led_frame, text="Chưa có màu được chọn",
                                 font=("Segoe UI", 10), 
                                 bg=self.config.colors['background'],
                                 fg=self.config.colors['dark'])
        self.rgb_label.grid(row=5, column=0, sticky="ew")
        
        # Direction controls
        direction_frame = tk.LabelFrame(led_frame, text="🔄 Chiều di chuyển",
                                       font=("Segoe UI", 11, "bold"),
                                       bg=self.config.colors['background'],
                                       fg=self.config.colors['secondary'])
        direction_frame.grid(row=6, column=0, pady=(15, 0), sticky="ew")
        direction_frame.grid_columnconfigure(0, weight=1)
        direction_frame.grid_columnconfigure(1, weight=1)
        
        btn_up = tk.Button(direction_frame, text="⬆️ Up", command=lambda: self.set_direction(1),
                          font=("Segoe UI", 10), bg=self.config.colors['success'], 
                          fg="white", relief=tk.FLAT, cursor="hand2", pady=5)
        btn_up.grid(row=0, column=0, padx=(0, 5), pady=10, sticky="ew")
        
        btn_down = tk.Button(direction_frame, text="⬇️ Down", command=lambda: self.set_direction(0),
                            font=("Segoe UI", 10), bg=self.config.colors['danger'], 
                            fg="white", relief=tk.FLAT, cursor="hand2", pady=5)
        btn_down.grid(row=0, column=1, padx=(5, 0), pady=10, sticky="ew")
        
        self.direction_label = tk.Label(direction_frame, text="Chưa chọn chiều",
                                       font=("Segoe UI", 9),
                                       bg=self.config.colors['background'],
                                       fg=self.config.colors['dark'])
        self.direction_label.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="ew")
    
    def create_config_section(self):
        """Tạo section config mode với card design"""
        # Config Card
        config_card = tk.Frame(self.scrollable_frame, bg="white", relief="solid", bd=1)
        config_card.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        # Card header
        header = tk.Frame(config_card, bg="#e74c3c", height=50)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        
        header_label = tk.Label(header, text="🔧 CONFIG MODE", 
                               font=("Segoe UI", 14, "bold"), 
                               bg="#e74c3c", fg="white")
        header_label.grid(row=0, column=0, pady=15)
        
        # Card content
        config_frame = tk.Frame(config_card, bg="white", padx=25, pady=25)
        config_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure grid
        config_frame.grid_columnconfigure(0, weight=1)
        
        # Config mode toggle
        self.btn_config_toggle = tk.Button(config_frame, text="🔵 Config: Tắt",
                                          command=self.toggle_config_mode,
                                          font=("Segoe UI", 12, "bold"),
                                          bg=self.config.colors['primary'], fg="white",
                                          relief=tk.FLAT, cursor="hand2", pady=10)
        self.btn_config_toggle.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        
        # Config status
        self.config_status_label = tk.Label(config_frame, text="🔵 Config Mode: Tắt",
                                           font=("Segoe UI", 11),
                                           bg=self.config.colors['background'],
                                           fg=self.config.colors['primary'])
        self.config_status_label.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        
        # Effects buttons
        effects_frame = tk.LabelFrame(config_frame, text="✨ Hiệu ứng",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=self.config.colors['background'],
                                     fg=self.config.colors['secondary'])
        effects_frame.grid(row=2, column=0, sticky="ew")
        effects_frame.grid_columnconfigure(0, weight=1)
        
        btn_rainbow = tk.Button(effects_frame, text="🌈 Rainbow",
                               command=self.send_rainbow_effect,
                               font=("Segoe UI", 11), bg="#e91e63", fg="white",
                               relief=tk.FLAT, cursor="hand2", pady=8)
        btn_rainbow.grid(row=0, column=0, pady=10, sticky="ew")
        
        btn_test = tk.Button(effects_frame, text="💡 Test LED",
                            command=self.test_led,
                            font=("Segoe UI", 11), bg=self.config.colors['warning'], 
                            fg="white", relief=tk.FLAT, cursor="hand2", pady=8)
        btn_test.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        
        # IP Configuration frame
        ip_config_frame = tk.LabelFrame(config_frame, text="🌐 Cấu hình IP Resolume",
                                       font=("Segoe UI", 11, "bold"),
                                       bg=self.config.colors['background'],
                                       fg=self.config.colors['secondary'])
        ip_config_frame.grid(row=3, column=0, sticky="ew", pady=(15, 0))
        ip_config_frame.grid_columnconfigure(0, weight=1)
        
        # Current IP display
        current_ip_frame = tk.Frame(ip_config_frame, bg=self.config.colors['background'])
        current_ip_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        current_ip_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(current_ip_frame, text="IP hiện tại:", 
                font=("Segoe UI", 10), 
                bg=self.config.colors['background']).grid(row=0, column=0, sticky="w")
        
        self.current_ip_label = tk.Label(current_ip_frame, 
                                        text=self.config.resolume_ip,
                                        font=("Segoe UI", 10, "bold"),
                                        bg=self.config.colors['background'],
                                        fg=self.config.colors['success'])
        self.current_ip_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # New IP entry
        new_ip_frame = tk.Frame(ip_config_frame, bg=self.config.colors['background'])
        new_ip_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        new_ip_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(new_ip_frame, text="IP mới:", 
                font=("Segoe UI", 10), 
                bg=self.config.colors['background']).grid(row=0, column=0, sticky="w")
        
        self.new_ip_entry = tk.Entry(new_ip_frame, font=("Segoe UI", 10))
        self.new_ip_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        self.new_ip_entry.insert(0, self.config.resolume_ip)
        
        # Update button
        btn_update_ip = tk.Button(ip_config_frame, text="🔄 Cập nhật IP Resolume",
                                 command=self.update_resolume_ip,
                                 font=("Segoe UI", 10), 
                                 bg=self.config.colors['info'], 
                                 fg="white", relief=tk.FLAT, cursor="hand2", pady=8)
        btn_update_ip.grid(row=2, column=0, pady=(5, 10), sticky="ew", padx=10)
    
    def create_touch_section(self):
        """Tạo section hiển thị thông tin touch sensor"""
        # Touch Info Full-width Card
        touch_card = tk.Frame(self.scrollable_frame, bg="white", relief="solid", bd=1)
        touch_card.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        
        # Card header
        header = tk.Frame(touch_card, bg="#16a085", height=50)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        
        header_label = tk.Label(header, text="📊 TOUCH SENSOR STATUS", 
                               font=("Segoe UI", 14, "bold"), 
                               bg="#16a085", fg="white")
        header_label.grid(row=0, column=0, pady=15)
        
        # Card content with sensor info
        touch_frame = tk.Frame(touch_card, bg="white", padx=30, pady=25)
        touch_frame.grid(row=1, column=0, sticky="nsew")
        touch_frame.grid_columnconfigure(0, weight=1)
        touch_frame.grid_columnconfigure(1, weight=1)
        touch_frame.grid_columnconfigure(2, weight=1)
        
        # Sensor status info
        status_info = [
            ("🔌", "CONNECTION", "ESP32 ↔ PIC16F887", "#27ae60"),
            ("⚡", "SAMPLING RATE", "Real-time OSC Data", "#3498db"),
            ("🎛️", "CALIBRATION", "Auto-calibrated", "#f39c12")
        ]
        
        for i, (icon, title, desc, color) in enumerate(status_info):
            info_card = tk.Frame(touch_frame, bg=color, relief="flat")
            info_card.grid(row=0, column=i, sticky="nsew", padx=10, pady=10)
            info_card.grid_columnconfigure(0, weight=1)
            
            # Icon
            icon_label = tk.Label(info_card, text=icon, font=("Segoe UI", 20),
                                 bg=color, fg="white")
            icon_label.grid(row=0, column=0, pady=(15, 5))
            
            # Title
            title_label = tk.Label(info_card, text=title, font=("Segoe UI", 10, "bold"),
                                  bg=color, fg="white")
            title_label.grid(row=1, column=0, pady=(0, 5))
            
            # Description
            desc_label = tk.Label(info_card, text=desc, font=("Segoe UI", 9),
                                 bg=color, fg="white", wraplength=150)
            desc_label.grid(row=2, column=0, pady=(0, 15))
    
    def create_realtime_section(self):
        """Tạo section monitoring với dashboard design"""
        # Realtime Card - Third column
        realtime_card = tk.Frame(self.scrollable_frame, bg="white", relief="solid", bd=1)
        realtime_card.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
        
        # Card header
        header = tk.Frame(realtime_card, bg="#27ae60", height=50)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        
        header_label = tk.Label(header, text="📊 LIVE MONITORING", 
                               font=("Segoe UI", 14, "bold"), 
                               bg="#27ae60", fg="white")
        header_label.grid(row=0, column=0, pady=15)
        
        # Dashboard content
        realtime_frame = tk.Frame(realtime_card, bg="white", padx=25, pady=25)
        realtime_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure grid
        realtime_frame.grid_columnconfigure(0, weight=1)
        
        # Metric cards container
        metrics_container = tk.Frame(realtime_frame, bg="white")
        metrics_container.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        
        # Metric cards
        metrics_data = [
            ("raw_touch", "📱", "RAW TOUCH", "#3498db", "N/A"),
            ("value", "📈", "VALUE", "#e74c3c", "N/A"),
            ("threshold", "🎯", "THRESHOLD", "#f39c12", "N/A")
        ]
        
        self.metric_labels = {}
        
        for i, (key, icon, title, color, default_value) in enumerate(metrics_data):
            # Metric card
            metric_card = tk.Frame(metrics_container, bg=color, relief="flat")
            metric_card.grid(row=i, column=0, sticky="ew", pady=5)
            metric_card.grid_columnconfigure(1, weight=1)
            
            # Icon
            icon_label = tk.Label(metric_card, text=icon, font=("Segoe UI", 16),
                                 bg=color, fg="white", width=3)
            icon_label.grid(row=0, column=0, rowspan=2, padx=15, pady=15)
            
            # Title
            title_label = tk.Label(metric_card, text=title, font=("Segoe UI", 10, "bold"),
                                  bg=color, fg="white", anchor="w")
            title_label.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=(15, 0))
            
            # Value
            self.metric_labels[key] = tk.Label(metric_card, text=default_value, 
                                              font=("Segoe UI", 14, "bold"),
                                              bg=color, fg="white", anchor="w")
            self.metric_labels[key].grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=(0, 15))
        
        # Threshold Control Section
        threshold_control = tk.Frame(realtime_frame, bg="#f8f9fa", relief="solid", bd=1)
        threshold_control.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        threshold_control.grid_columnconfigure(1, weight=1)
        
        # Threshold control header
        control_header = tk.Frame(threshold_control, bg="#9b59b6", height=35)
        control_header.grid(row=0, column=0, columnspan=3, sticky="ew")
        control_header.grid_propagate(False)
        control_header.grid_columnconfigure(0, weight=1)
        
        tk.Label(control_header, text="⚙️ THRESHOLD CONTROL", 
                font=("Segoe UI", 11, "bold"), bg="#9b59b6", fg="white").grid(row=0, column=0, pady=8)
        
        # Threshold input section
        input_frame = tk.Frame(threshold_control, bg="#f8f9fa", padx=20, pady=15)
        input_frame.grid(row=1, column=0, columnspan=3, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(input_frame, text="Ngưỡng:", font=("Segoe UI", 11, "bold"),
                bg="#f8f9fa", fg="#2c3e50").grid(row=0, column=0, padx=(0, 15), sticky="w")
        
        self.threshold_entry = tk.Entry(input_frame, font=("Segoe UI", 11),
                                       relief=tk.FLAT, bd=5, justify=tk.CENTER,
                                       bg="white", fg="#2c3e50")
        self.threshold_entry.grid(row=0, column=1, padx=(0, 15), sticky="ew", ipady=5)
        self.threshold_entry.insert(0, self.config.default_threshold)
        
        btn_send_threshold = tk.Button(input_frame, text="📤 Gửi",
                                      command=self.send_threshold,
                                      font=("Segoe UI", 11, "bold"), 
                                      bg="#9b59b6", fg="white",
                                      relief=tk.FLAT, cursor="hand2", padx=20, pady=8,
                                      activebackground="#8e44ad")
        btn_send_threshold.grid(row=0, column=2, sticky="e")
        
        # Status label
        self.threshold_status_label = tk.Label(input_frame, text="Chưa gửi ngưỡng",
                                              font=("Segoe UI", 10),
                                              bg="#f8f9fa", fg="#7f8c8d")
        self.threshold_status_label.grid(row=1, column=0, columnspan=3, pady=(10, 0), sticky="ew")
    
    def create_status_section(self):
        """Tạo footer status với modern design"""
        # Footer status bar
        footer = tk.Frame(self.scrollable_frame, bg="#34495e", height=50)
        footer.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(20, 0))
        footer.grid_propagate(False)
        footer.grid_columnconfigure(1, weight=1)
        
        # Connection status
        conn_frame = tk.Frame(footer, bg="#34495e")
        conn_frame.grid(row=0, column=0, sticky="w", padx=30, pady=15)
        
        status_icon = tk.Label(conn_frame, text="🌐", font=("Segoe UI", 12), 
                              bg="#34495e", fg="#3498db")
        status_icon.grid(row=0, column=0, padx=(0, 10))
        
        self.status_label = tk.Label(conn_frame, text="OSC Server: Active on port 7000",
                                    font=("Segoe UI", 11, "bold"), 
                                    bg="#34495e", fg="#ecf0f1")
        self.status_label.grid(row=0, column=1)
        
        # System info
        info_frame = tk.Frame(footer, bg="#34495e")
        info_frame.grid(row=0, column=2, sticky="e", padx=30, pady=15)
        
        # Resolume IP info
        resolume_info = tk.Label(info_frame, 
                                text=f"Resolume: {self.config.resolume_ip}:{self.config.resolume_port}",
                                font=("Segoe UI", 9), 
                                bg="#34495e", fg="#3498db")
        resolume_info.grid(row=0, column=0, sticky="e")
        
        # ESP32 IP info
        esp_info = tk.Label(info_frame, 
                           text=f"ESP32: {self.config.esp_ip}:{self.config.esp_port}",
                           font=("Segoe UI", 9), 
                           bg="#34495e", fg="#95a5a6")
        esp_info.grid(row=1, column=0, sticky="e")
        
        # Store reference để cập nhật sau
        self.resolume_info_label = resolume_info
    
    # Event handlers
    def choose_color(self):
        """Chọn màu"""
        color = colorchooser.askcolor(title="Chọn màu LED")
        if color and color[0]:
            r, g, b = map(int, color[0])
            self.led_controller.set_color(r, g, b)
            self.color_preview.config(bg=color[1])
            
            brightness = self.brightness_var.get()
            self.rgb_label.config(text=f"RGB: ({r}, {g}, {b}) | Độ sáng: {brightness}")
    
    def on_brightness_change(self, val):
        """Thay đổi độ sáng"""
        brightness = int(float(val))
        self.led_controller.set_brightness(brightness)
        
        state = self.led_controller.get_state()
        self.rgb_label.config(text=f"RGB: ({state['r']}, {state['g']}, {state['b']}) | Độ sáng: {brightness}")
    
    def toggle_led(self):
        """Bật/tắt LED"""
        enabled = self.led_controller.toggle_led()
        
        self.btn_led_toggle.config(
            text=f"{'🟢 LED: Bật' if enabled else '🔴 LED: Tắt'}",
            bg=self.config.colors['success'] if enabled else self.config.colors['danger']
        )
    
    def set_direction(self, direction: int):
        """Thiết lập chiều"""
        success = self.led_controller.set_direction(direction)
        
        if not success:
            self.direction_label.config(
                text="⚠️ Vui lòng bật LED trước khi chọn chiều",
                fg=self.config.colors['danger']
            )
        else:
            direction_text = "Move Up" if direction == 1 else "Move Down"
            self.direction_label.config(
                text=f"✅ Chiều: {direction_text}",
                fg=self.config.colors['success']
            )
    
    def toggle_config_mode(self):
        """Bật/tắt config mode"""
        enabled = self.led_controller.toggle_config_mode()
        
        self.btn_config_toggle.config(
            text=f"{'🟡 Config: Bật' if enabled else '🔵 Config: Tắt'}",
            bg=self.config.colors['warning'] if enabled else self.config.colors['primary']
        )
        
        self.config_status_label.config(
            text=f"{'🟡 Config Mode: ESP32 nhận lệnh LED' if enabled else '🔵 Config Mode: Tắt'}",
            fg=self.config.colors['warning'] if enabled else self.config.colors['primary']
        )
    
    def send_rainbow_effect(self):
        """Gửi hiệu ứng rainbow"""
        success = self.led_controller.send_rainbow_effect()
        if not success:
            messagebox.showwarning("Config Mode", "Vui lòng bật Config Mode trước!")
    
    def test_led(self):
        """Test LED"""
        success = self.led_controller.send_led_test()
        if not success:
            messagebox.showwarning("Config Mode", "Vui lòng bật Config Mode trước!")
    
    def update_resolume_ip(self):
        """Cập nhật IP Resolume"""
        try:
            new_ip = self.new_ip_entry.get().strip()
            
            if not new_ip:
                messagebox.showerror("Lỗi", "Vui lòng nhập IP hợp lệ!")
                return
            
            # Xác nhận thay đổi
            old_ip = self.config.resolume_ip
            confirm = messagebox.askyesno(
                "Xác nhận", 
                f"Bạn có chắc muốn thay đổi IP Resolume?\n\n"
                f"Từ: {old_ip}\n"
                f"Thành: {new_ip}"
            )
            
            if not confirm:
                return
            
            # Thực hiện cập nhật
            success = self.comm_handler.update_resolume_ip(new_ip)
            
            if success:
                # Cập nhật hiển thị
                self.current_ip_label.config(text=new_ip)
                # Cập nhật footer info nếu tồn tại
                if hasattr(self, 'resolume_info_label'):
                    self.resolume_info_label.config(
                        text=f"Resolume: {new_ip}:{self.config.resolume_port}")
                messagebox.showinfo("Thành công", 
                                   f"Đã cập nhật IP Resolume thành: {new_ip}")
            else:
                messagebox.showerror("Lỗi", 
                                   "Không thể cập nhật IP. Vui lòng kiểm tra:\n"
                                   "- Format IP hợp lệ (vd: 192.168.1.100)\n"
                                   "- Kết nối với ESP32")
                # Reset lại giá trị cũ
                self.new_ip_entry.delete(0, tk.END)
                self.new_ip_entry.insert(0, old_ip)
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            # Reset lại giá trị cũ
            self.new_ip_entry.delete(0, tk.END)
            self.new_ip_entry.insert(0, self.config.resolume_ip)
    
    def send_threshold(self):
        """Gửi ngưỡng"""
        try:
            threshold_value = int(self.threshold_entry.get())
            success = self.touch_controller.set_threshold(threshold_value)
            
            if success:
                self.threshold_status_label.config(
                    text=f"✅ Đã gửi ngưỡng: {threshold_value}",
                    fg=self.config.colors['success']
                )
            else:
                self.threshold_status_label.config(
                    text="❌ Ngưỡng không hợp lệ (100-10000)",
                    fg=self.config.colors['danger']
                )
        except ValueError:
            self.threshold_status_label.config(
                text="❌ Vui lòng nhập số nguyên hợp lệ",
                fg=self.config.colors['danger']
            )
        except Exception as e:
            self.threshold_status_label.config(
                text=f"❌ Lỗi: {str(e)}",
                fg=self.config.colors['danger']
            )
    
    def update_realtime_data(self, data):
        """Cập nhật dữ liệu realtime"""
        def update():
            self.metric_labels['raw_touch'].config(text=str(data['raw_touch']))
            self.metric_labels['value'].config(text=str(data['value']))
            self.metric_labels['threshold'].config(text=str(data['threshold']))
            
            # Update admin window if open
            if self.admin_window and hasattr(self.admin_window, 'update_stats'):
                self.admin_window.update_stats()
        
        self.root.after(0, update)
    
    def open_admin_window(self):
        """Mở cửa sổ admin"""
        if self.admin_window is not None:
            try:
                if self.admin_window.winfo_exists():
                    self.admin_window.lift()
                    self.admin_window.focus_force()
                    return
            except tk.TclError:
                pass
        
        self.admin_window = AdminWindow(self.root, self.comm_handler, self.config)

class AdminWindow:
    """Cửa sổ quản trị"""
    
    def __init__(self, parent, comm_handler, config):
        self.comm_handler = comm_handler
        self.config = config
        
        self.window = tk.Toplevel(parent)
        self.window.title("🔧 Administrator Panel")
        self.window.geometry("900x650")
        self.window.configure(bg=self.config.colors['secondary'])
        self.window.resizable(True, True)
        self.window.minsize(700, 500)
        
        # Center admin window
        self.center_admin_window()
        
        self.create_widgets()
        self.update_stats()
    
    def center_admin_window(self):
        """Căn giữa admin window"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Tạo widgets cho admin window"""
        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = tk.Frame(self.window, bg=self.config.colors['dark'], padx=20, pady=15)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        tk.Label(header_frame, text="🔧 Administrator Control Panel",
                font=("Segoe UI", 16, "bold"), bg=self.config.colors['dark'], fg="white").pack()
        
        # Main content
        content_frame = tk.Frame(self.window, bg=self.config.colors['secondary'], padx=20, pady=15)
        content_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure content grid  
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Statistics frame
        stats_frame = tk.LabelFrame(content_frame, text="📊 System Statistics",
                                   font=("Segoe UI", 12, "bold"), bg=self.config.colors['dark'],
                                   fg="white", padx=15, pady=15)
        stats_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))
        
        # Stats labels
        self.stats_labels = {}
        stats_data = [
            ('packets_sent', "Packets Sent: 0"),
            ('packets_received', "Packets Received: 0"),
            ('connection_status', "Status: Disconnected"),
            ('raw_touch', "Raw Touch: N/A"),
            ('value', "Value: N/A"),
            ('threshold', "Threshold: N/A")
        ]
        
        for i, (key, text) in enumerate(stats_data):
            self.stats_labels[key] = tk.Label(stats_frame, text=text,
                                             font=("Segoe UI", 10), bg=self.config.colors['dark'],
                                             fg="white", anchor="w")
            self.stats_labels[key].grid(row=i, column=0, sticky="w", pady=2)
        
        # Control panel
        control_frame = tk.LabelFrame(content_frame, text="⚙️ System Control",
                                     font=("Segoe UI", 12, "bold"), bg=self.config.colors['dark'],
                                     fg="white", padx=15, pady=15)
        control_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 15))
        
        # Control buttons
        tk.Button(control_frame, text="🔄 Reset Statistics",
                 command=self.reset_statistics, bg=self.config.colors['warning'], 
                 fg="white", font=("Segoe UI", 10), relief=tk.FLAT, 
                 cursor="hand2", pady=5).grid(row=0, column=0, pady=5, sticky="ew")
        
        tk.Button(control_frame, text="🧹 Clear Logs",
                 command=self.clear_logs, bg=self.config.colors['danger'], 
                 fg="white", font=("Segoe UI", 10), relief=tk.FLAT,
                 cursor="hand2", pady=5).grid(row=1, column=0, pady=5, sticky="ew")
        
        tk.Button(control_frame, text="💾 Export Logs",
                 command=self.export_logs, bg=self.config.colors['success'], 
                 fg="white", font=("Segoe UI", 10), relief=tk.FLAT,
                 cursor="hand2", pady=5).grid(row=2, column=0, pady=5, sticky="ew")
        
        # Log display
        log_frame = tk.LabelFrame(content_frame, text="📝 System Logs",
                                 font=("Segoe UI", 12, "bold"), bg=self.config.colors['dark'],
                                 fg="white", padx=15, pady=15)
        log_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(15, 0))
        
        # Configure log_frame grid
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        # Log text area
        self.log_display = scrolledtext.ScrolledText(log_frame,
                                                    font=("Consolas", 9),
                                                    bg="#1e2832", fg="#ffffff",
                                                    wrap=tk.WORD, height=15)
        self.log_display.grid(row=0, column=0, sticky="nsew")
        
        # Populate initial log
        logs = self.comm_handler.get_logs()
        self.log_display.insert(tk.END, '\\n'.join(logs))
        self.log_display.see(tk.END)
    
    def update_stats(self):
        """Cập nhật thống kê"""
        stats = self.comm_handler.get_statistics()
        
        self.stats_labels['packets_sent'].config(text=f"Packets Sent: {stats['packets_sent']}")
        self.stats_labels['packets_received'].config(text=f"Packets Received: {stats['packets_received']}")
        self.stats_labels['connection_status'].config(text=f"Status: {stats['connection_status']}")
        self.stats_labels['raw_touch'].config(text=f"Raw Touch: {stats['raw_touch']}")
        self.stats_labels['value'].config(text=f"Value: {stats['value']}")
        self.stats_labels['threshold'].config(text=f"Threshold: {stats['threshold']}")
        
        # Update log display
        self.log_display.delete(1.0, tk.END)
        logs = self.comm_handler.get_logs()
        self.log_display.insert(tk.END, '\\n'.join(logs))
        self.log_display.see(tk.END)
    
    def reset_statistics(self):
        """Reset thống kê"""
        self.comm_handler.reset_statistics()
        self.update_stats()
    
    def clear_logs(self):
        """Xóa logs"""
        self.comm_handler.clear_logs()
        self.update_stats()
    
    def export_logs(self):
        """Xuất logs"""
        try:
            filename = self.comm_handler.export_logs()
            messagebox.showinfo("Export Success", f"Logs exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")
        
        self.update_stats()
    
    def winfo_exists(self):
        """Kiểm tra window có tồn tại không"""
        try:
            return self.window.winfo_exists()
        except tk.TclError:
            return False

class HybridCubeTouchGUI:
    """Hybrid GUI kết hợp classic và auto-discovery"""
    
    def __init__(self, root, comm_handler, auto_discovery_manager, config):
        self.root = root
        self.comm_handler = comm_handler
        self.auto_discovery_manager = auto_discovery_manager
        self.config = config
        
        # Controllers
        self.led_controller = LEDController(comm_handler)
        self.touch_controller = TouchController(comm_handler)
        
        # Mode tracking
        self.current_mode = "classic"  # "classic" or "auto_discovery"
        self.classic_gui = None
        self.auto_discovery_gui = None
        
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Thiết lập cửa sổ hybrid"""
        self.root.title("📻 Cube Touch - Hybrid Mode")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        self.root.minsize(1200, 800)
        
        # Center window
        self.center_window()
        
        # Configure grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def center_window(self):
        """Căn giữa cửa sổ"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Tạo widgets hybrid"""
        # Header with mode switcher
        self.create_mode_header()
        
        # Main content area
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Show classic mode by default
        self.switch_to_classic()
    
    def create_mode_header(self):
        """Tạo header với mode switcher"""
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title section
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.grid(row=0, column=0, sticky="w", padx=30, pady=20)
        
        title_label = tk.Label(title_frame, text="📻 CUBE TOUCH HYBRID", 
                              font=("Arial", 20, "bold"), 
                              bg="#2c3e50", fg="#ecf0f1")
        title_label.pack(side=tk.LEFT)
        
        # Mode indicator
        self.mode_indicator = tk.Label(title_frame, text="[Classic Mode]", 
                                      font=("Arial", 12), 
                                      bg="#2c3e50", fg="#3498db")
        self.mode_indicator.pack(side=tk.LEFT, padx=(20, 0))
        
        # Mode switcher buttons
        switcher_frame = tk.Frame(header_frame, bg="#2c3e50")
        switcher_frame.grid(row=0, column=2, sticky="e", padx=30, pady=15)
        
        self.classic_btn = tk.Button(switcher_frame, text="🎹 Classic Mode", 
                                    command=self.switch_to_classic,
                                    bg="#3498db", fg="white", 
                                    font=("Arial", 12, "bold"), 
                                    relief=tk.FLAT, cursor="hand2",
                                    padx=20, pady=8)
        self.classic_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.discovery_btn = tk.Button(switcher_frame, text="🔍 Auto-Discovery", 
                                      command=self.switch_to_auto_discovery,
                                      bg="#95a5a6", fg="white", 
                                      font=("Arial", 12, "bold"), 
                                      relief=tk.FLAT, cursor="hand2",
                                      padx=20, pady=8)
        self.discovery_btn.pack(side=tk.LEFT)
        
        # Status indicators
        status_frame = tk.Frame(header_frame, bg="#2c3e50")
        status_frame.grid(row=0, column=1, padx=20, pady=20)
        
        # Classic status
        self.classic_status = tk.Label(status_frame, text="🎹 Classic: Ready", 
                                      font=("Arial", 11), 
                                      bg="#2c3e50", fg="#27ae60")
        self.classic_status.pack()
        
        # Auto-discovery status
        self.discovery_status = tk.Label(status_frame, text="🔍 Discovery: Stopped", 
                                        font=("Arial", 11), 
                                        bg="#2c3e50", fg="#e74c3c")
        self.discovery_status.pack()
    
    def switch_to_classic(self):
        """Chuyển sang classic mode"""
        self.current_mode = "classic"
        
        # Update button states
        self.classic_btn.config(bg="#3498db", fg="white")
        self.discovery_btn.config(bg="#95a5a6", fg="white")
        self.mode_indicator.config(text="[Classic Mode]", fg="#3498db")
        
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create classic GUI within main frame
        if self.classic_gui is None:
            # Create a temporary root for classic GUI
            classic_container = tk.Frame(self.main_frame, bg="#f8f9fa")
            classic_container.grid(row=0, column=0, sticky="nsew")
            
            # Initialize classic GUI components manually
            self.create_classic_interface(classic_container)
        else:
            # Restore classic GUI
            self.classic_gui.grid(row=0, column=0, sticky="nsew")
        
        # Hide auto-discovery GUI if exists
        if self.auto_discovery_gui:
            self.auto_discovery_gui.grid_remove()
    
    def switch_to_auto_discovery(self):
        """Chuyển sang auto-discovery mode"""
        self.current_mode = "auto_discovery"
        
        # Update button states
        self.classic_btn.config(bg="#95a5a6", fg="white")
        self.discovery_btn.config(bg="#27ae60", fg="white")
        self.mode_indicator.config(text="[Auto-Discovery Mode]", fg="#27ae60")
        
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create auto-discovery GUI within main frame
        if self.auto_discovery_gui is None:
            # Create auto-discovery interface
            discovery_container = tk.Frame(self.main_frame, bg="#f0f0f0")
            discovery_container.grid(row=0, column=0, sticky="nsew")
            discovery_container.grid_rowconfigure(0, weight=1)
            discovery_container.grid_columnconfigure(0, weight=1)
            
            # Create AutoDiscoveryGUI but modify it to work within our container
            self.create_auto_discovery_interface(discovery_container)
        
        # Update discovery status
        self.update_discovery_status()
    
    def create_classic_interface(self, parent):
        """Tạo giao diện classic trong container"""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Create a canvas for scrolling
        canvas = tk.Canvas(parent, bg="#f8f9fa", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Scrollable frame
        scrollable_frame = tk.Frame(canvas, bg="#f8f9fa")
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure responsive grid
        for i in range(3):
            scrollable_frame.grid_columnconfigure(i, weight=1, minsize=300)
        scrollable_frame.grid_rowconfigure(1, weight=1)
        
        # Mouse wheel binding
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        parent.bind("<MouseWheel>", _on_mousewheel)
        
        # Canvas resize handler
        def on_canvas_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Store references
        self.classic_canvas = canvas
        self.classic_scrollable_frame = scrollable_frame
        
        # Create classic components
        self.create_classic_header(scrollable_frame)
        self.create_classic_led_control(scrollable_frame)
        self.create_classic_config_section(scrollable_frame)
        self.create_classic_realtime_section(scrollable_frame)
        self.create_classic_touch_section(scrollable_frame)
        self.create_classic_status_section(scrollable_frame)
        
        # Setup callback for classic mode
        self.comm_handler.on_data_update = self.update_classic_realtime_data
    
    def create_auto_discovery_interface(self, parent):
        """Tạo giao diện auto-discovery trong container"""
        # Use modified AutoDiscoveryGUI
        self.auto_discovery_gui_instance = EmbeddedAutoDiscoveryGUI(
            parent, self.auto_discovery_manager, self.config)
    
    def create_classic_header(self, parent):
        """Tạo header cho classic mode"""
        header_main = tk.Frame(parent, bg="#3498db", height=60)
        header_main.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        header_main.grid_propagate(False)
        header_main.grid_columnconfigure(1, weight=1)
        
        # Left - Title
        left_frame = tk.Frame(header_main, bg="#3498db")
        left_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        title_label = tk.Label(left_frame, text="🎹 CLASSIC CONTROL", 
                              font=("Arial", 16, "bold"), 
                              bg="#3498db", fg="white")
        title_label.pack()
        
        # Right - ESP Info
        info_frame = tk.Frame(header_main, bg="#3498db")
        info_frame.grid(row=0, column=2, sticky="e", padx=20, pady=15)
        
        esp_label = tk.Label(info_frame, text=f"ESP32: {self.config.esp_ip}", 
                            font=("Arial", 11), 
                            bg="#3498db", fg="white")
        esp_label.pack()
    
    def create_classic_led_control(self, parent):
        """Tạo LED control cho classic"""
        led_card = tk.Frame(parent, bg="white", relief="solid", bd=1)
        led_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = tk.Frame(led_card, bg="#e74c3c", height=40)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        
        tk.Label(header, text="💡 LED CONTROL", 
                font=("Arial", 12, "bold"), 
                bg="#e74c3c", fg="white").grid(row=0, column=0, pady=10)
        
        # Content
        led_frame = tk.Frame(led_card, bg="white", padx=20, pady=20)
        led_frame.grid(row=1, column=0, sticky="nsew")
        led_frame.grid_columnconfigure(0, weight=1)
        
        # LED Toggle
        self.classic_led_toggle = tk.Button(led_frame, text="🔴 LED: Tắt", 
                                           command=self.classic_toggle_led,
                                           font=("Arial", 11, "bold"), 
                                           bg=self.config.colors['danger'], fg="white",
                                           relief=tk.FLAT, cursor="hand2", pady=8)
        self.classic_led_toggle.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        
        # Color chooser
        tk.Button(led_frame, text="🎨 Chọn màu", command=self.classic_choose_color,
                 font=("Arial", 11), bg="#9b59b6", 
                 fg="white", relief=tk.FLAT, cursor="hand2", pady=8).grid(row=1, column=0, pady=(0, 15), sticky="ew")
        
        # Color preview
        self.classic_color_preview = tk.Label(led_frame, text="Color Preview", height=2,
                                             font=("Arial", 10), bg="#ecf0f1", 
                                             relief=tk.RAISED, bd=2)
        self.classic_color_preview.grid(row=2, column=0, pady=(0, 15), sticky="ew")
        
        # Brightness
        tk.Label(led_frame, text="💡 Độ sáng", 
                font=("Arial", 11, "bold"), bg="white").grid(row=3, column=0, sticky="w")
        
        self.classic_brightness_var = tk.IntVar(value=128)
        self.classic_brightness_scale = tk.Scale(led_frame, from_=1, to=255, orient="horizontal",
                                                variable=self.classic_brightness_var, 
                                                bg="white", command=self.classic_on_brightness_change)
        self.classic_brightness_scale.grid(row=4, column=0, pady=(5, 15), sticky="ew")
        
        # RGB info
        self.classic_rgb_label = tk.Label(led_frame, text="Chưa có màu được chọn",
                                         font=("Arial", 9), bg="white")
        self.classic_rgb_label.grid(row=5, column=0, sticky="ew")
    
    def create_classic_config_section(self, parent):
        """Tạo config section cho classic"""
        config_card = tk.Frame(parent, bg="white", relief="solid", bd=1)
        config_card.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = tk.Frame(config_card, bg="#f39c12", height=40)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        
        tk.Label(header, text="⚙️ CONFIG MODE", 
                font=("Arial", 12, "bold"), 
                bg="#f39c12", fg="white").grid(row=0, column=0, pady=10)
        
        # Content
        config_frame = tk.Frame(config_card, bg="white", padx=20, pady=20)
        config_frame.grid(row=1, column=0, sticky="nsew")
        config_frame.grid_columnconfigure(0, weight=1)
        
        # Config toggle
        self.classic_config_toggle = tk.Button(config_frame, text="🔵 Config: Tắt",
                                              command=self.classic_toggle_config_mode,
                                              font=("Arial", 11, "bold"),
                                              bg="#3498db", fg="white",
                                              relief=tk.FLAT, cursor="hand2", pady=8)
        self.classic_config_toggle.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        
        # Effects
        tk.Button(config_frame, text="🌈 Rainbow", command=self.classic_send_rainbow,
                 font=("Arial", 10), bg="#e91e63", fg="white",
                 relief=tk.FLAT, cursor="hand2", pady=6).grid(row=1, column=0, pady=(0, 10), sticky="ew")
        
        tk.Button(config_frame, text="💡 Test LED", command=self.classic_test_led,
                 font=("Arial", 10), bg="#f39c12", fg="white",
                 relief=tk.FLAT, cursor="hand2", pady=6).grid(row=2, column=0, pady=(0, 15), sticky="ew")
        
        # Resolume IP
        ip_frame = tk.LabelFrame(config_frame, text="🌐 Resolume IP", bg="white")
        ip_frame.grid(row=3, column=0, sticky="ew", pady=(15, 0))
        ip_frame.grid_columnconfigure(0, weight=1)
        
        self.classic_ip_entry = tk.Entry(ip_frame, font=("Arial", 10))
        self.classic_ip_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.classic_ip_entry.insert(0, self.config.resolume_ip)
        
        tk.Button(ip_frame, text="🔄 Cập nhật", command=self.classic_update_resolume_ip,
                 font=("Arial", 9), bg="#2196F3", fg="white",
                 relief=tk.FLAT, cursor="hand2").grid(row=1, column=0, pady=(0, 10))
    
    def create_classic_realtime_section(self, parent):
        """Tạo realtime section cho classic"""
        realtime_card = tk.Frame(parent, bg="white", relief="solid", bd=1)
        realtime_card.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = tk.Frame(realtime_card, bg="#27ae60", height=40)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        
        tk.Label(header, text="📊 REALTIME DATA", 
                font=("Arial", 12, "bold"), 
                bg="#27ae60", fg="white").grid(row=0, column=0, pady=10)
        
        # Content
        realtime_frame = tk.Frame(realtime_card, bg="white", padx=20, pady=20)
        realtime_frame.grid(row=1, column=0, sticky="nsew")
        realtime_frame.grid_columnconfigure(0, weight=1)
        
        # Metrics
        metrics_data = [
            ("raw_touch", "📱", "RAW TOUCH", "#3498db"),
            ("value", "📈", "VALUE", "#e74c3c"),
            ("threshold", "🎯", "THRESHOLD", "#f39c12")
        ]
        
        self.classic_metric_labels = {}
        
        for i, (key, icon, title, color) in enumerate(metrics_data):
            metric_frame = tk.Frame(realtime_frame, bg=color, relief="flat")
            metric_frame.grid(row=i, column=0, sticky="ew", pady=5)
            metric_frame.grid_columnconfigure(1, weight=1)
            
            # Icon
            tk.Label(metric_frame, text=icon, font=("Arial", 14),
                    bg=color, fg="white", width=3).grid(row=0, column=0, padx=10, pady=10)
            
            # Title and Value
            info_frame = tk.Frame(metric_frame, bg=color)
            info_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)
            
            tk.Label(info_frame, text=title, font=("Arial", 9, "bold"),
                    bg=color, fg="white", anchor="w").pack(anchor="w")
            
            self.classic_metric_labels[key] = tk.Label(info_frame, text="N/A", 
                                                      font=("Arial", 12, "bold"),
                                                      bg=color, fg="white", anchor="w")
            self.classic_metric_labels[key].pack(anchor="w")
        
        # Threshold control
        threshold_frame = tk.LabelFrame(realtime_frame, text="🎯 Threshold", bg="white")
        threshold_frame.grid(row=3, column=0, sticky="ew", pady=(15, 0))
        threshold_frame.grid_columnconfigure(0, weight=1)
        
        entry_frame = tk.Frame(threshold_frame, bg="white")
        entry_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        entry_frame.grid_columnconfigure(0, weight=1)
        
        self.classic_threshold_entry = tk.Entry(entry_frame, font=("Arial", 10), justify=tk.CENTER)
        self.classic_threshold_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.classic_threshold_entry.insert(0, "2932")
        
        tk.Button(entry_frame, text="📤 Gửi", command=self.classic_send_threshold,
                 font=("Arial", 9), bg="#9b59b6", fg="white",
                 relief=tk.FLAT, cursor="hand2").grid(row=0, column=1)
    
    def create_classic_touch_section(self, parent):
        """Tạo touch section cho classic"""
        touch_card = tk.Frame(parent, bg="white", relief="solid", bd=1)
        touch_card.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = tk.Frame(touch_card, bg="#16a085", height=40)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        
        tk.Label(header, text="📊 TOUCH SENSOR STATUS", 
                font=("Arial", 12, "bold"), 
                bg="#16a085", fg="white").grid(row=0, column=0, pady=10)
        
        # Content
        touch_frame = tk.Frame(touch_card, bg="white", padx=20, pady=15)
        touch_frame.grid(row=1, column=0, sticky="nsew")
        
        for i in range(3):
            touch_frame.grid_columnconfigure(i, weight=1)
        
        # Info cards
        info_data = [
            ("🔌", "CONNECTION", "ESP32 ↔ PIC16F887", "#27ae60"),
            ("⚡", "SAMPLING", "Real-time OSC", "#3498db"),
            ("🎲", "STATUS", "Auto-calibrated", "#f39c12")
        ]
        
        for i, (icon, title, desc, color) in enumerate(info_data):
            info_card = tk.Frame(touch_frame, bg=color, relief="flat")
            info_card.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            
            tk.Label(info_card, text=icon, font=("Arial", 16),
                    bg=color, fg="white").pack(pady=(10, 5))
            
            tk.Label(info_card, text=title, font=("Arial", 9, "bold"),
                    bg=color, fg="white").pack()
            
            tk.Label(info_card, text=desc, font=("Arial", 8),
                    bg=color, fg="white").pack(pady=(0, 10))
    
    def create_classic_status_section(self, parent):
        """Tạo status section cho classic"""
        footer = tk.Frame(parent, bg="#34495e", height=40)
        footer.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(15, 0))
        footer.grid_propagate(False)
        footer.grid_columnconfigure(1, weight=1)
        
        # Status
        tk.Label(footer, text="🌐 Classic Mode Active", 
                font=("Arial", 11, "bold"), 
                bg="#34495e", fg="#3498db").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # ESP Info
        tk.Label(footer, text=f"ESP32: {self.config.esp_ip}:{self.config.esp_port}", 
                font=("Arial", 9), 
                bg="#34495e", fg="#ecf0f1").grid(row=0, column=2, sticky="e", padx=20, pady=10)
    
    # Classic mode event handlers
    def classic_toggle_led(self):
        """Toggle LED cho classic mode"""
        enabled = self.led_controller.toggle_led()
        self.classic_led_toggle.config(
            text=f"{'🟢 LED: Bật' if enabled else '🔴 LED: Tắt'}",
            bg=self.config.colors['success'] if enabled else self.config.colors['danger']
        )
    
    def classic_choose_color(self):
        """Chọn màu cho classic mode"""
        color = colorchooser.askcolor(title="Chọn màu LED")
        if color and color[0]:
            r, g, b = map(int, color[0])
            self.led_controller.set_color(r, g, b)
            self.classic_color_preview.config(bg=color[1])
            
            brightness = self.classic_brightness_var.get()
            self.classic_rgb_label.config(text=f"RGB: ({r}, {g}, {b}) | Độ sáng: {brightness}")
    
    def classic_on_brightness_change(self, val):
        """Thay đổi độ sáng cho classic mode"""
        brightness = int(float(val))
        self.led_controller.set_brightness(brightness)
        
        state = self.led_controller.get_state()
        self.classic_rgb_label.config(text=f"RGB: ({state['r']}, {state['g']}, {state['b']}) | Độ sáng: {brightness}")
    
    def classic_toggle_config_mode(self):
        """Toggle config mode cho classic"""
        enabled = self.led_controller.toggle_config_mode()
        self.classic_config_toggle.config(
            text=f"{'🟡 Config: Bật' if enabled else '🔵 Config: Tắt'}",
            bg=self.config.colors['warning'] if enabled else self.config.colors['primary']
        )
    
    def classic_send_rainbow(self):
        """Gửi rainbow effect cho classic"""
        success = self.led_controller.send_rainbow_effect()
        if not success:
            messagebox.showwarning("Config Mode", "Vui lòng bật Config Mode trước!")
    
    def classic_test_led(self):
        """Test LED cho classic"""
        success = self.led_controller.send_led_test()
        if not success:
            messagebox.showwarning("Config Mode", "Vui lòng bật Config Mode trước!")
    
    def classic_update_resolume_ip(self):
        """Cập nhật Resolume IP cho classic"""
        new_ip = self.classic_ip_entry.get().strip()
        if new_ip:
            success = self.comm_handler.update_resolume_ip(new_ip)
            if success:
                messagebox.showinfo("Thành công", f"Đã cập nhật IP Resolume: {new_ip}")
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật IP")
    
    def classic_send_threshold(self):
        """Gửi threshold cho classic"""
        try:
            threshold = int(self.classic_threshold_entry.get())
            success = self.touch_controller.set_threshold(threshold)
            if success:
                messagebox.showinfo("Thành công", f"Đã gửi ngưỡng: {threshold}")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên hợp lệ")
    
    def update_classic_realtime_data(self, data):
        """Cập nhật dữ liệu realtime cho classic"""
        if self.current_mode == "classic" and hasattr(self, 'classic_metric_labels'):
            def update():
                self.classic_metric_labels['raw_touch'].config(text=str(data['raw_touch']))
                self.classic_metric_labels['value'].config(text=str(data['value']))
                self.classic_metric_labels['threshold'].config(text=str(data['threshold']))
            
            self.root.after(0, update)
    
    def update_discovery_status(self):
        """Cập nhật trạng thái discovery"""
        if hasattr(self, 'auto_discovery_gui_instance'):
            if self.auto_discovery_manager and hasattr(self.auto_discovery_manager, 'discovery_running'):
                if self.auto_discovery_manager.discovery_running:
                    self.discovery_status.config(text="🔍 Discovery: Running", fg="#27ae60")
                else:
                    self.discovery_status.config(text="🔍 Discovery: Stopped", fg="#e74c3c")

class EmbeddedAutoDiscoveryGUI:
    """AutoDiscoveryGUI được tích hợp trong HybridGUI"""
    
    def __init__(self, parent, manager, config):
        self.parent = parent
        self.manager = manager
        self.config = config
        
        # Auto-update state
        self.auto_update_running = False
        self.selected_esp_ip = None
        
        # Setup callbacks
        self.manager.on_esp_discovered = self.on_esp_discovered
        self.manager.on_esp_connected = self.on_esp_connected
        self.manager.on_esp_disconnected = self.on_esp_disconnected
        self.manager.on_data_received = self.on_data_received
        
        self.create_interface()
        self.start_auto_update()
    
    def create_interface(self):
        """Tạo giao diện embedded auto-discovery"""
        # Configure parent
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        
        # Header
        header_frame = tk.Frame(self.parent, bg="#27ae60", height=60)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        tk.Label(header_frame, text="🔍 AUTO-DISCOVERY CONTROL", 
                font=("Arial", 16, "bold"), 
                bg="#27ae60", fg="white").grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        # Discovery controls
        controls_frame = tk.Frame(header_frame, bg="#27ae60")
        controls_frame.grid(row=0, column=2, sticky="e", padx=20, pady=15)
        
        self.start_btn = tk.Button(controls_frame, text="🚀 Start", 
                                  command=self.start_discovery,
                                  bg="#2ecc71", fg="white", 
                                  font=("Arial", 10, "bold"), width=10)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(controls_frame, text="🛑 Stop", 
                                 command=self.stop_discovery,
                                 bg="#e74c3c", fg="white", 
                                 font=("Arial", 10, "bold"), width=10,
                                 state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Left panel - ESP list
        left_frame = tk.LabelFrame(self.parent, text="🔍 Discovered ESPs", 
                                  font=("Arial", 12, "bold"),
                                  bg="white", fg="#2c3e50", bd=2)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # ESP TreeView
        tree_frame = tk.Frame(left_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Name", "IP", "Port", "Status")
        self.esp_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.esp_tree.heading(col, text=col)
            self.esp_tree.column(col, width=80, minwidth=60)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.esp_tree.yview)
        self.esp_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.esp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.esp_tree.bind("<<TreeviewSelect>>", self.on_esp_select)
        
        # Center panel - ESP control
        center_frame = tk.LabelFrame(self.parent, text="🎮 ESP Control", 
                                    font=("Arial", 12, "bold"),
                                    bg="white", fg="#2c3e50", bd=2)
        center_frame.grid(row=1, column=1, sticky="nsew", padx=5)
        
        # Selected ESP info
        self.selected_esp_label = tk.Label(center_frame, 
                                          text="🔘 No ESP selected", 
                                          font=("Arial", 12, "bold"),
                                          bg="white", fg="#2c3e50")
        self.selected_esp_label.pack(pady=15)
        
        # Control buttons
        control_buttons = [
            ("💡 Test LED", self.test_led, "#f39c12"),
            ("🌈 Rainbow", self.send_rainbow, "#e91e63"),
            ("📡 Ping", self.ping_esp, "#3498db"),
            ("🔄 Refresh", self.refresh_esp, "#95a5a6")
        ]
        
        for text, command, color in control_buttons:
            tk.Button(center_frame, text=text, command=command,
                     bg=color, fg="white", font=("Arial", 10),
                     relief=tk.FLAT, cursor="hand2", pady=5).pack(fill=tk.X, padx=20, pady=5)
        
        # Right panel - Monitor
        right_frame = tk.LabelFrame(self.parent, text="📈 System Monitor", 
                                   font=("Arial", 12, "bold"),
                                   bg="white", fg="#2c3e50", bd=2)
        right_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0))
        
        # Statistics
        stats_frame = tk.Frame(right_frame, bg="white")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_labels = {}
        stats_items = [
            ("Total ESPs", "total_esps"),
            ("Connected", "connected_esps"),
            ("Active Ports", "active_ports")
        ]
        
        for label, key in stats_items:
            row_frame = tk.Frame(stats_frame, bg="white")
            row_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(row_frame, text=f"{label}:", bg="white", 
                    font=("Arial", 9)).pack(side=tk.LEFT)
            
            value_label = tk.Label(row_frame, text="0", bg="white", 
                                  font=("Arial", 9, "bold"), fg="#2c3e50")
            value_label.pack(side=tk.RIGHT)
            
            self.stats_labels[key] = value_label
        
        # Data display
        data_frame = tk.LabelFrame(right_frame, text="📁 Real-time Data", bg="white")
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.data_display = tk.Text(data_frame, height=8, bg="#1e1e1e", fg="#00ff41",
                                   font=("Consolas", 8), wrap=tk.WORD)
        self.data_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def start_discovery(self):
        """Bắt đầu discovery"""
        if self.manager.start_discovery():
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "Auto-Discovery started!")
    
    def stop_discovery(self):
        """Dừng discovery"""
        self.manager.stop_discovery()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
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
    
    def test_led(self):
        """Test LED ESP"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "LED_TEST")
    
    def send_rainbow(self):
        """Gửi hiệu ứng rainbow"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "RAINBOW:START")
    
    def ping_esp(self):
        """Ping ESP"""
        if self.selected_esp_ip:
            self.manager.send_command_to_esp(self.selected_esp_ip, "PING")
    
    def refresh_esp(self):
        """Refresh ESP"""
        self.refresh_esp_list()
    
    def refresh_esp_list(self):
        """Refresh danh sách ESP"""
        for item in self.esp_tree.get_children():
            self.esp_tree.delete(item)
        
        esps = self.manager.get_discovered_esps()
        for esp in esps:
            status_map = {
                "Discovered": "🔍 Discovered",
                "Assigned": "📡 Assigned", 
                "Connected": "🜢 Connected",
                "Offline": "🔴 Offline"
            }
            status_text = status_map.get(esp['status'], esp['status'])
            
            self.esp_tree.insert("", tk.END, values=(
                esp['name'],
                esp['ip'],
                esp['assigned_port'],
                status_text
            ))
    
    def start_auto_update(self):
        """Bắt đầu auto-update"""
        if self.auto_update_running:
            return
        
        self.auto_update_running = True
        
        def update_loop():
            import time
            while self.auto_update_running:
                try:
                    stats = self.manager.get_statistics()
                    
                    for key, label in self.stats_labels.items():
                        if key in stats:
                            label.config(text=str(stats[key]))
                    
                    self.refresh_esp_list()
                    
                except Exception as e:
                    print(f"Auto-update error: {e}")
                
                time.sleep(3)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    # Event callbacks
    def on_esp_discovered(self, esp_info):
        """Callback khi phát hiện ESP mới"""
        self.refresh_esp_list()
    
    def on_esp_connected(self, esp_info):
        """Callback khi ESP kết nối"""
        self.refresh_esp_list()
    
    def on_esp_disconnected(self, esp_info):
        """Callback khi ESP ngắt kết nối"""
        self.refresh_esp_list()
    
    def on_data_received(self, data):
        """Callback khi nhận dữ liệu"""
        if self.selected_esp_ip == data.get('esp_ip'):
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            data_str = f"[{timestamp}] {data.get('esp_name', 'Unknown')}: {data}\n"
            
            self.data_display.insert(tk.END, data_str)
            self.data_display.see(tk.END)
            
            # Limit display length
            lines = self.data_display.get(1.0, tk.END).split('\n')
            if len(lines) > 15:
                self.data_display.delete(1.0, f"{len(lines)-15}.0")