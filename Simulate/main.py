#!/usr/bin/env python3
"""
Main entry point for Cube Touch Monitor Application
Khởi tạo và chạy ứng dụng chính
"""

import sys
import os
import threading
import tkinter as tk
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

# Import các module riêng
from gui import CubeTouchGUI, HybridCubeTouchGUI
from communication import CommunicationHandler
from config import AppConfig
from auto_discovery_manager import AutoDiscoveryManager
from auto_discovery_gui import AutoDiscoveryGUI

class CubeTouchApp:
    def __init__(self):
        """Khởi tạo ứng dụng chính"""
        self.config = AppConfig()
        self.comm_handler = CommunicationHandler(self.config)
        self.auto_discovery_manager = AutoDiscoveryManager(self.config)
        self.root = None
        self.gui = None
        self.auto_gui = None
        self.osc_thread = None
        self.mode = "hybrid"  # "classic", "auto_discovery", "hybrid"
        
    def setup_osc_server(self):
        """Thiết lập OSC server để nhận dữ liệu từ ESP32"""
        dispatcher = Dispatcher()
        dispatcher.map("/debug", self.comm_handler.handle_osc_data)
        
        def run_osc_server():
            try:
                server = BlockingOSCUDPServer(("0.0.0.0", self.config.osc_port), dispatcher)
                self.comm_handler.add_log(f"OSC Server started on port {self.config.osc_port}")
                server.serve_forever()
            except Exception as e:
                self.comm_handler.add_log(f"Error starting OSC server: {str(e)}")
        
        self.osc_thread = threading.Thread(target=run_osc_server, daemon=True)
        self.osc_thread.start()
    
    def run(self):
        """Chạy ứng dụng"""
        # Tạo cửa sổ chính
        self.root = tk.Tk()
        
        if self.mode == "hybrid":
            self.run_hybrid_mode()
        elif self.mode == "auto_discovery":
            self.run_auto_discovery_mode()
        else:
            self.run_classic_mode()
    
    def run_hybrid_mode(self):
        """Chạy chế độ hybrid - kết hợp classic và auto-discovery"""
        # Tạo hybrid GUI với cả hai chức năng
        self.gui = HybridCubeTouchGUI(self.root, self.comm_handler, self.auto_discovery_manager, self.config)
        
        # Thiết lập OSC server cho classic mode
        self.setup_osc_server()
        
        # Log khởi tạo
        self.comm_handler.add_log("🚀 Hybrid Application started")
        self.comm_handler.add_log(f"Classic ESP32: {self.config.esp_ip}:{self.config.esp_port}")
        self.comm_handler.add_log(f"OSC Port: {self.config.osc_port}")
        self.comm_handler.add_log(f"Auto-Discovery Port: 7000")
        
        # Chạy giao diện
        self.root.mainloop()
    
    def run_auto_discovery_mode(self):
        """Chạy chế độ auto-discovery only"""
        self.auto_gui = AutoDiscoveryGUI(self.root, self.config)
        self.root.mainloop()
    
    def run_classic_mode(self):
        """Chạy chế độ classic only"""
        # Khởi tạo giao diện classic
        self.gui = CubeTouchGUI(self.root, self.comm_handler, self.config)
        
        # Thiết lập OSC server
        self.setup_osc_server()
        
        # Log khởi tạo
        self.comm_handler.add_log("Application started")
        self.comm_handler.add_log(f"ESP32 IP: {self.config.esp_ip}:{self.config.esp_port}")
        self.comm_handler.add_log(f"OSC Port: {self.config.osc_port}")
        
        # Chạy giao diện
        self.root.mainloop()

def main():
    """Entry point chính"""
    try:
        # Parse command line arguments
        mode = "hybrid"  # default
        if len(sys.argv) > 1:
            if sys.argv[1] == "--classic":
                mode = "classic"
            elif sys.argv[1] == "--auto-discovery":
                mode = "auto_discovery"
            elif sys.argv[1] == "--hybrid":
                mode = "hybrid"
        
        app = CubeTouchApp()
        app.mode = mode
        app.run()
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()