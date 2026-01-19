"""
Google Gemini API Usage Monitor

This script helps you check your Gemini API usage and monitor when you're approaching limits.
It uses the Google Generative AI library to test your API key and provides usage information.

Usage:
    python check_gemini_usage.py

Requirements:
    pip install google-generativeai
"""

import os
import sys
from datetime import datetime
import google.generativeai as genai

def check_api_key():
    """Check if API key is set and valid."""
    api_key = os.environ.get('GOOGLE_AI_API_KEY')
    
    if not api_key:
        print("❌ ERROR: GOOGLE_AI_API_KEY environment variable not set!")
        print("\nTo set it:")
        print("  Windows: set GOOGLE_AI_API_KEY=your-api-key")
        print("  Linux/Mac: export GOOGLE_AI_API_KEY=your-api-key")
        print("  Or create a .env file with: GOOGLE_AI_API_KEY=your-api-key")
        return None
    
    # Check if it's the default/example key
    if api_key.startswith('AIzaSy') and len(api_key) < 50:
        print("⚠️  WARNING: Using a default/example API key. Please set your actual API key.")
    
    return api_key

def test_api_call(api_key):
    """Test if the API key works by making a simple API call."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        print("🔄 Testing API connection...")
        response = model.generate_content("Say 'API is working' if you can read this.")
        
        if response and response.text:
            print("✅ API connection successful!")
            return True
        else:
            print("⚠️  API call returned empty response")
            return False
            
    except Exception as e:
        error_msg = str(e).lower()
        
        if 'quota' in error_msg or '429' in str(e):
            print("❌ QUOTA EXCEEDED!")
            print("   Your API quota has been reached. Please:")
            print("   - Wait for the quota to reset (usually at midnight UTC)")
            print("   - Check Google Cloud Console for usage details")
            print("   - Consider upgrading to a paid plan")
        elif 'rate limit' in error_msg:
            print("❌ RATE LIMIT EXCEEDED!")
            print("   Too many requests per minute. Please wait a moment and try again.")
        elif 'api key' in error_msg or 'invalid' in error_msg:
            print("❌ INVALID API KEY!")
            print("   Please check your API key in Google AI Studio:")
            print("   https://aistudio.google.com/")
        elif 'permission' in error_msg or '403' in str(e):
            print("❌ PERMISSION DENIED!")
            print("   Your API key may not have access to Gemini API.")
            print("   Enable 'Generative Language API' in Google Cloud Console:")
            print("   https://console.cloud.google.com/apis/library")
        else:
            print(f"❌ API Error: {e}")
            print("   Check your API key and internet connection.")
        
        return False

def get_usage_info():
    """Display information about checking usage."""
    print("\n" + "="*60)
    print("📊 HOW TO CHECK YOUR API USAGE")
    print("="*60)
    
    print("\n1. Google Cloud Console (Recommended):")
    print("   → Visit: https://console.cloud.google.com/")
    print("   → Go to: APIs & Services → Dashboard")
    print("   → Search for: 'Generative Language API'")
    print("   → Check: Quotas and Metrics tabs")
    
    print("\n2. Google AI Studio:")
    print("   → Visit: https://aistudio.google.com/")
    print("   → Click on your profile icon")
    print("   → Navigate to: API Usage or Billing")
    
    print("\n3. Set Up Alerts:")
    print("   → Google Cloud Console → APIs & Services → Quotas")
    print("   → Select quota → Edit Quotas")
    print("   → Set alerts at 50%, 75%, 90% of limit")
    print("   → Add email addresses for notifications")
    
    print("\n" + "="*60)
    print("📈 FREE TIER LIMITS (Approximate)")
    print("="*60)
    print("   • Requests per minute: 60 RPM")
    print("   • Requests per day: 1,500 RPD")
    print("   • Tokens per minute: 32,000 TPM")
    print("   • Tokens per day: 1,500,000 TPD")
    print("\n   Note: Limits may vary. Check Google Cloud Console for exact limits.")
    
    print("\n" + "="*60)
    print("⚠️  WHAT TO DO WHEN YOU HIT LIMITS")
    print("="*60)
    print("   • Rate Limit (429): Wait 1 minute and retry")
    print("   • Daily Quota: Wait until midnight UTC for reset")
    print("   • Upgrade: Consider paid tier for higher limits")
    print("   • Optimize: Cache responses, reduce token usage")

def main():
    """Main function to check API usage."""
    print("="*60)
    print("🔍 Google Gemini API Usage Monitor")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check API key
    api_key = check_api_key()
    if not api_key:
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    # Test API call
    if test_api_call(api_key):
        print("\n✅ Your API key is working correctly!")
    else:
        print("\n❌ API test failed. Please check the error above.")
    
    # Display usage information
    get_usage_info()
    
    print("\n" + "="*60)
    print("✅ Check complete!")
    print("="*60)
    print("\nFor more information, see: GEMINI_API_MONITORING_GUIDE.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)




