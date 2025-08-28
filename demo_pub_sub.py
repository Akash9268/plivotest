#!/usr/bin/env python3
"""
Demo: Publisher and Subscriber Views
Shows how to use the new dedicated publisher and subscriber interfaces
"""

import time
import webbrowser
import os

def main():
    print("🚀 Pub/Sub System - Publisher & Subscriber Demo")
    print("=" * 60)
    print()
    
    print("📱 This demo will open two browser windows:")
    print("   1. Publisher View - for publishing messages")
    print("   2. Subscriber View - for receiving messages")
    print()
    
    print("🔌 Make sure the WebSocket server is running on port 8000")
    print("   (docker-compose up -d)")
    print()
    
    # Wait a moment for user to read
    input("Press Enter to continue...")
    
    # Open publisher view
    print("📤 Opening Publisher View...")
    webbrowser.open('http://localhost:8000/api/publisher/')
    
    # Wait a moment
    time.sleep(2)
    
    # Open subscriber view
    print("👂 Opening Subscriber View...")
    webbrowser.open('http://localhost:8000/api/subscriber/')
    
    print()
    print("🎯 Demo Instructions:")
    print("   1. In the Publisher View:")
    print("      - Click 'Connect' to establish WebSocket connection")
    print("      - Enter a topic name (e.g., 'demo-topic')")
    print("      - Enter your publisher ID (e.g., 'demo-publisher')")
    print("      - Use the message templates or write your own JSON")
    print("      - Click '📤 Publish Message'")
    print()
    print("   2. In the Subscriber View:")
    print("      - Click 'Connect' to establish WebSocket connection")
    print("      - Enter the same topic name ('demo-topic')")
    print("      - Enter your subscriber ID (e.g., 'demo-subscriber')")
    print("      - Click 'Subscribe'")
    print("      - Watch for real-time messages!")
    print()
    print("   3. Test Multiple Subscribers:")
    print("      - Open multiple subscriber tabs")
    print("      - Subscribe different client IDs to the same topic")
    print("      - Publish messages and watch all receive them!")
    print()
    
    print("🔗 You can also access the main dashboard at:")
    print("   http://localhost:8000/api/")
    print()
    
    print("🎉 Happy publishing and subscribing!")

if __name__ == "__main__":
    main()
