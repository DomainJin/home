#!/usr/bin/env python3
"""
Multi-ESP GUI Module
Giao diện quản lý nhiều ESP32 đồng thời
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from multi_esp_communication import MultiESPCommunicationHandler

class MultiESPGUI:
    """GUI cho quản lý nhiều ESP32"""
    
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.comm_handler = MultiESPCommunicationHandler(config)
        
        # ESP management
        self.esp_widgets = {}  # {esp_ip: widget_dict}
        self.selected_esp = None
        
        # Setup callbacks
        self.comm_handler.on_data_update = self.update_esp_data
        self.comm_handler.on_esp_status_change = self.update_esp_status
        
        self.setup_window()
        self.create_widgets()
        self.start_auto_update()
    
    def setup_window(self):
        """Thiết lập cửa sổ"""
        self.root.title("Multi-ESP Cube Touch Monitor")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f0f0f0")
        
    def create_widgets(self):
        """Tạo giao diện"""
        # Main frame với 3 cột
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel - ESP List
        self.create_esp_list_panel(main_frame)
        
        # Center panel - Selected ESP Control
        self.create_esp_control_panel(main_frame)
        
        # Right panel - System Stats
        self.create_stats_panel(main_frame)
        
        # Bottom panel - Logs
        self.create_log_panel(main_frame)
        
        # Control buttons
        self.create_control_buttons(main_frame)
    
    def create_esp_list_panel(self, parent):
        """Tạo panel danh sách ESP"""
        esp_frame = tk.LabelFrame(parent, text="🌐 ESP32 Devices", 
                                 font=("Arial", 12, "bold"),
                                 bg="white", fg="#2c3e50")
        esp_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5), pady=(0,5))
        esp_frame.grid_rowconfigure(1, weight=1)
        
        # Add ESP button
        add_btn = tk.Button(esp_frame, text="➕ Add ESP32",
                           command=self.add_esp_dialog,
                           bg="#3498db", fg="white", font=("Arial", 10))
        add_btn.pack(pady=10)
        
        # ESP TreeView
        columns = ("Name", "IP", "Status", "Packets")
        self.esp_tree = ttk.Treeview(esp_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.esp_tree.heading(col, text=col)
            self.esp_tree.column(col, width=80)
        
        # Scrollbar for treeview
        esp_scrollbar = ttk.Scrollbar(esp_frame, orient=tk.VERTICAL, command=self.esp_tree.yview)
        self.esp_tree.configure(yscrollcommand=esp_scrollbar.set)
        
        self.esp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        esp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.esp_tree.bind("<<TreeviewSelect>>", self.on_esp_select)
    
    def create_esp_control_panel(self, parent):
        """Tạo panel điều khiển ESP được chọn"""
        control_frame = tk.LabelFrame(parent, text="🎛️ ESP Control", 
                                     font=("Arial", 12, "bold"),
                                     bg="white", fg="#2c3e50")
        control_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0,5))
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Selected ESP info
        self.selected_esp_label = tk.Label(control_frame, 
                                          text="Select an ESP32 to control",
                                          font=("Arial", 11), bg="white")
        self.selected_esp_label.pack(pady=10)
        
        # Control tabs
        self.control_notebook = ttk.Notebook(control_frame)
        self.control_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # LED Control tab
        led_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(led_frame, text="💡 LED Control")
        self.create_led_controls(led_frame)
        
        # Touch Control tab  
        touch_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(touch_frame, text="👆 Touch Sensor")
        self.create_touch_controls(touch_frame)
        
        # Config tab
        config_frame = tk.Frame(self.control_notebook, bg="white")
        self.control_notebook.add(config_frame, text="⚙️ Configuration")
        self.create_config_controls(config_frame)
        
        # Real-time data display
        self.create_realtime_display(control_frame)
    
    def create_led_controls(self, parent):
        """Tạo điều khiển LED"""
        # Color picker
        color_frame = tk.Frame(parent, bg="white")
        color_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(color_frame, text="Color:", bg="white").pack(side=tk.LEFT)
        
        self.color_preview = tk.Label(color_frame, text="   ", bg="red", 
                                     relief=tk.RAISED, cursor="hand2")
        self.color_preview.pack(side=tk.LEFT, padx=5)
        self.color_preview.bind("<Button-1>", lambda e: self.choose_color())
        
        # Brightness control
        brightness_frame = tk.Frame(parent, bg="white")
        brightness_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(brightness_frame, text="Brightness:", bg="white").pack(side=tk.LEFT)
        self.brightness_var = tk.IntVar(value=128)
        brightness_scale = tk.Scale(brightness_frame, from_=1, to=255, 
                                   orient=tk.HORIZONTAL, variable=self.brightness_var,
                                   command=self.on_brightness_change)
        brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # LED actions
        action_frame = tk.Frame(parent, bg="white")
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(action_frame, text="🌈 Rainbow", command=self.send_rainbow,
                 bg="#e91e63", fg="white").pack(side=tk.LEFT, padx=2)
        
        tk.Button(action_frame, text="💡 Test", command=self.test_led,
                 bg="#ff9800", fg="white").pack(side=tk.LEFT, padx=2)
        
        tk.Button(action_frame, text="🔴 Off", command=self.turn_off_led,
                 bg="#f44336", fg="white").pack(side=tk.LEFT, padx=2)
    
    def create_touch_controls(self, parent):
        """Tạo điều khiển cảm biến chạm"""
        # Threshold setting
        threshold_frame = tk.Frame(parent, bg="white")
        threshold_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(threshold_frame, text="Touch Threshold:", bg="white").pack()
        
        self.threshold_var = tk.StringVar(value="2932")
        threshold_entry = tk.Entry(threshold_frame, textvariable=self.threshold_var, 
                                  font=("Arial", 12), justify=tk.CENTER)
        threshold_entry.pack(pady=5)
        
        tk.Button(threshold_frame, text="📤 Send Threshold",
                 command=self.send_threshold,
                 bg="#4CAF50", fg="white").pack(pady=5)
    
    def create_config_controls(self, parent):
        """Tạo điều khiển cấu hình"""
        # Resolume IP config
        resolume_frame = tk.LabelFrame(parent, text="Resolume Configuration", bg="white")
        resolume_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(resolume_frame, text="Resolume IP:", bg="white").pack()
        
        self.resolume_ip_var = tk.StringVar(value=self.config.resolume_ip)
        ip_entry = tk.Entry(resolume_frame, textvariable=self.resolume_ip_var, 
                           font=("Arial", 10), justify=tk.CENTER)
        ip_entry.pack(pady=5)
        
        tk.Button(resolume_frame, text="🔄 Update IP",
                 command=self.update_resolume_ip,
                 bg="#2196F3", fg="white").pack(pady=5)
    
    def create_realtime_display(self, parent):
        """Tạo hiển thị dữ liệu realtime"""
        data_frame = tk.LabelFrame(parent, text="📊 Real-time Data", 
                                  font=("Arial", 10, "bold"), bg="white")
        data_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Data labels
        self.data_labels = {}
        data_items = ["Raw Touch", "Value", "Threshold", "Last Update"]
        
        for item in data_items:
            row_frame = tk.Frame(data_frame, bg="white")
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(row_frame, text=f"{item}:", bg="white", 
                    font=("Arial", 9)).pack(side=tk.LEFT)
            
            value_label = tk.Label(row_frame, text="N/A", bg="white", 
                                  font=("Arial", 9, "bold"), fg="#2c3e50")
            value_label.pack(side=tk.RIGHT)
            
            self.data_labels[item.lower().replace(" ", "_")] = value_label
    
    def create_stats_panel(self, parent):
        """Tạo panel thống kê"""
        stats_frame = tk.LabelFrame(parent, text="📈 System Statistics", 
                                   font=("Arial", 12, "bold"),
                                   bg="white", fg="#2c3e50")
        stats_frame.grid(row=0, column=2, sticky="nsew", padx=(5,0), pady=(0,5))
        
        # Performance metrics
        self.stats_labels = {}
        stats_items = [
            ("Total ESPs", "total_esp_count"),
            ("Online ESPs", "online_esp_count"), 
            ("Packets Received", "total_packets_received"),
            ("Packets Sent", "total_packets_sent"),
            ("Data Rate", "data_rate")
        ]
        
        for label, key in stats_items:
            row_frame = tk.Frame(stats_frame, bg="white")
            row_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(row_frame, text=f"{label}:", bg="white", 
                    font=("Arial", 9)).pack(side=tk.LEFT)
            
            value_label = tk.Label(row_frame, text="0", bg="white", 
                                  font=("Arial", 9, "bold"), fg="#27ae60")
            value_label.pack(side=tk.RIGHT)
            
            self.stats_labels[key] = value_label
    
    def create_log_panel(self, parent):
        """Tạo panel logs"""
        log_frame = tk.LabelFrame(parent, text="📜 System Logs", 
                                 font=("Arial", 10, "bold"),
                                 bg="white", fg="#2c3e50")
        log_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=5)
        parent.grid_rowconfigure(1, weight=1)
        
        # Log text widget
        self.log_text = tk.Text(log_frame, height=8, bg="#1e1e1e", fg="#00ff00",
                               font=("Consolas", 9))
        log_scrollbar = tk.Scrollbar(log_frame, orient=tk.VERTICAL, 
                                    command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def create_control_buttons(self, parent):
        """Tạo nút điều khiển chính"""
        btn_frame = tk.Frame(parent, bg="#f0f0f0")
        btn_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        tk.Button(btn_frame, text="🚀 Start Communication",
                 command=self.start_communication,
                 bg="#27ae60", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🛑 Stop Communication", 
                 command=self.stop_communication,
                 bg="#e74c3c", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="📢 Broadcast Command",
                 command=self.broadcast_dialog,
                 bg="#3498db", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🧹 Clear Logs",
                 command=self.clear_logs,
                 bg="#95a5a6", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
    
    # Event handlers
    def add_esp_dialog(self):
        """Dialog thêm ESP mới"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add ESP32")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="ESP32 IP Address:").pack(pady=10)
        ip_var = tk.StringVar()
        tk.Entry(dialog, textvariable=ip_var, font=("Arial", 12)).pack(pady=5)
        
        tk.Label(dialog, text="Device Name (optional):").pack(pady=(10,0))
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, font=("Arial", 12)).pack(pady=5)
        
        def add_esp():
            ip = ip_var.get().strip()
            name = name_var.get().strip() or None
            
            if ip and self.comm_handler.register_esp(ip, name):
                self.update_esp_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add ESP32")
        
        tk.Button(dialog, text="Add", command=add_esp,
                 bg="#27ae60", fg="white").pack(pady=10)
    
    def on_esp_select(self, event):
        """Xử lý khi chọn ESP"""
        selection = self.esp_tree.selection()
        if selection:
            item = self.esp_tree.item(selection[0])
            esp_ip = item['values'][1]  # IP column
            self.selected_esp = esp_ip
            self.selected_esp_label.config(
                text=f"Selected: {item['values'][0]} ({esp_ip})")
    
    def update_esp_data(self, data):
        """Cập nhật dữ liệu từ ESP"""
        if self.selected_esp and data.get('esp_ip') == self.selected_esp:
            # Update realtime display
            for key, label in self.data_labels.items():
                if key in data:
                    label.config(text=str(data[key]))
            
            # Update timestamp
            if 'timestamp' in data:
                self.data_labels['last_update'].config(
                    text=time.strftime("%H:%M:%S", time.localtime(data['timestamp'])))
    
    def update_esp_status(self, esp_ip, status):
        """Cập nhật trạng thái ESP"""
        self.update_esp_list()
        self.add_log(f"ESP {esp_ip} status changed: {status}")
    
    def update_esp_list(self):
        """Cập nhật danh sách ESP"""
        # Clear current items
        for item in self.esp_tree.get_children():
            self.esp_tree.delete(item)
        
        # Add ESP devices
        esp_list = self.comm_handler.get_esp_list()
        for esp in esp_list:
            self.esp_tree.insert("", tk.END, values=(
                esp['name'], esp['ip'], esp['status'], 
                f"R:{esp['packets_received']} S:{esp['packets_sent']}"
            ))
    
    def start_auto_update(self):
        """Bắt đầu cập nhật tự động"""
        def update_loop():
            while True:
                try:
                    # Update statistics
                    stats = self.comm_handler.get_performance_stats()
                    for key, label in self.stats_labels.items():
                        if key in stats:
                            label.config(text=str(stats[key]))
                    
                    # Update ESP list
                    self.update_esp_list()
                    
                    # Update logs
                    logs = self.comm_handler.log_messages[-10:]  # Last 10 logs
                    self.log_text.delete(1.0, tk.END)
                    for log in logs:
                        self.log_text.insert(tk.END, log + "\\n")
                    self.log_text.see(tk.END)
                    
                except Exception as e:
                    print(f"Update error: {e}")
                
                time.sleep(2)  # Update every 2 seconds
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def start_communication(self):
        """Bắt đầu giao tiếp"""
        self.comm_handler.start_communication()
    
    def stop_communication(self):
        """Dừng giao tiếp"""
        self.comm_handler.stop_communication()
    
    def choose_color(self):
        """Chọn màu LED"""
        if not self.selected_esp:
            messagebox.showwarning("Warning", "Please select an ESP32 first")
            return
        
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Choose LED Color")
        if color and color[0]:
            r, g, b = map(int, color[0])
            self.color_preview.config(bg=color[1])
            
            # Send color command
            command = f"LEDCTRL:ALL,{r},{g},{b}"
            self.comm_handler.send_command_to_esp(self.selected_esp, command)
    
    def send_rainbow(self):
        """Gửi hiệu ứng rainbow"""
        if self.selected_esp:
            self.comm_handler.send_command_to_esp(self.selected_esp, "RAINBOW:START")
    
    def add_log(self, message):
        """Thêm log"""
        self.comm_handler.add_log(message)

# Example usage
if __name__ == "__main__":
    # Simple config class for demo
    class Config:
        def __init__(self):
            self.osc_port = 7000
            self.esp_port = 4210
            self.resolume_ip = "192.168.0.241"
            self.max_log_entries = 100
    
    root = tk.Tk()
    config = Config()
    app = MultiESPGUI(root, config)
    root.mainloop()