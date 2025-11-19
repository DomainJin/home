#!/usr/bin/env python3
"""
Main Entry Point for Port-Per-ESP System
Điểm khởi động chính cho hệ thống Port-Per-ESP
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import argparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from port_per_esp_gui import PortPerESPGUI
from config import AppConfig

class EnhancedAppConfig(AppConfig):
    """Cấu hình mở rộng cho hệ thống Port-Per-ESP"""
    
    def __init__(self):
        super().__init__()
        
        # Port-Per-ESP specific settings
        self.use_port_per_esp = True
        self.port_base = 7000  # Base port for calculation
        self.port_range_min = 7001
        self.port_range_max = 7255
        
        # Default ESP configurations
        self.default_esps = [
            {
                'name': 'ESP_043',
                'ip': '192.168.0.43',
                'port': 7043,
                'description': 'Main Cube Touch Sensor'
            },
            {
                'name': 'ESP_044', 
                'ip': '192.168.0.44',
                'port': 7044,
                'description': 'Secondary Touch Sensor'
            }
        ]
        
        # Enhanced logging
        self.max_log_entries = 500  # Increased for multiple ESPs
        self.log_to_file = True
        self.log_file_prefix = "port_per_esp_logs"
        
        # Performance settings
        self.update_interval = 1.0  # GUI update interval (seconds)
        self.connection_timeout = 5.0  # ESP connection timeout
        self.queue_max_size = 1000  # Max queue size per ESP

def create_application():
    """Tạo ứng dụng chính"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Port-Per-ESP Communication Manager')
    parser.add_argument('--demo', action='store_true', 
                       help='Run in demo mode with simulators')
    parser.add_argument('--config', type=str, 
                       help='Path to custom config file')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Create main window
    root = tk.Tk()
    
    # Set window properties
    root.withdraw()  # Hide initially
    
    try:
        # Create configuration
        config = EnhancedAppConfig()
        
        if args.debug:
            config.debug_mode = True
            print("🐛 Debug mode enabled")
        
        # Create application
        app = PortPerESPGUI(root, config)
        
        # Setup demo mode if requested
        if args.demo:
            setup_demo_mode(app)
        
        # Show window after initialization
        root.deiconify()
        root.lift()
        root.focus_force()
        
        # Welcome message
        show_welcome_message(args.demo)
        
        return app, root
        
    except Exception as e:
        messagebox.showerror("Initialization Error", 
                           f"Failed to initialize application:\\n{str(e)}")
        root.destroy()
        sys.exit(1)

def setup_demo_mode(app):
    """Thiết lập chế độ demo"""
    print("🧪 Setting up demo mode...")
    
    # Add demo ESPs
    demo_esps = [
        ("Demo_ESP_043", "127.0.0.1"),  # Localhost for demo
        ("Demo_ESP_044", "127.0.0.1"),  
    ]
    
    for name, ip in demo_esps:
        # Modify IP to simulate different ESPs
        if "044" in name:
            demo_ip = "192.168.0.44"  # Will calculate to port 7044
        else:
            demo_ip = "192.168.0.43"  # Will calculate to port 7043
            
        app.manager.register_esp(demo_ip, name)
    
    app.refresh_esp_list()
    print("✅ Demo mode setup complete")

def show_welcome_message(demo_mode=False):
    """Hiển thị thông báo chào mừng"""
    
    mode_text = "DEMO MODE" if demo_mode else "PRODUCTION MODE"
    
    welcome_text = f"""🌐 Welcome to Port-Per-ESP Manager!

Running in: {mode_text}

Key Features:
✅ Dedicated port per ESP32 device
✅ Automatic port calculation (70XX format)  
✅ Independent communication channels
✅ Real-time monitoring and control
✅ Advanced ESP management

Port Convention:
• ESP IP: 192.168.0.43 → Port: 7043
• ESP IP: 192.168.0.44 → Port: 7044
• Pattern: Port = 7000 + last IP octet

Quick Start:
1. Click "➕ Add ESP" to register devices
2. Click "🚀 Start All" to begin communication
3. Select an ESP to control it individually

Ready to manage your ESP32 network!"""
    
    # Show in console
    print("\\n" + "="*60)
    print(welcome_text)
    print("="*60 + "\\n")

def main():
    """Hàm main"""
    
    print("🚀 Starting Port-Per-ESP Manager...")
    
    try:
        # Create application
        app, root = create_application()
        
        # Setup error handling
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                print("\\n⏹️ Application interrupted by user")
                return
            
            error_msg = f"Unexpected error:\\n{exc_type.__name__}: {exc_value}"
            print(f"❌ {error_msg}")
            
            try:
                messagebox.showerror("Unexpected Error", error_msg)
            except:
                pass  # GUI might not be available
        
        sys.excepthook = handle_exception
        
        # Setup cleanup on exit
        def on_closing():
            print("\\n🧹 Cleaning up...")
            
            try:
                # Stop auto-update
                app.auto_update_running = False
                
                # Stop communication
                app.manager.stop_communication()
                
                print("✅ Cleanup completed")
                
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")
            
            finally:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Run main loop
        print("🎯 Application ready! Starting GUI main loop...")
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\\n⏹️ Application stopped by user")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
        
    finally:
        print("👋 Port-Per-ESP Manager closed")

if __name__ == "__main__":
    main()