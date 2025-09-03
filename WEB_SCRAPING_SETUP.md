# 🌐 Web Scraping Setup Guide

## ✅ **COMPLETED: Web Scraping Added!**

Your acquisition agent now supports **two modes**:

### 📧 **Email Mode** (Current - Working)
- ✅ **Waits for listing alert emails**
- ✅ **Real-time notifications** when new opportunities arrive
- ✅ **Fully configured and working**

### 🌐 **Web Scraping Mode** (New - Optional)
- 🆕 **Directly scrapes existing listings** from platforms
- 🆕 **Finds listings that already exist** (not just new ones)
- 🆕 **More comprehensive coverage**

---

## 🚀 **How to Enable Web Scraping**

### **Option 1: Hybrid Mode (Recommended)**
Keep email alerts AND add web scraping:

```yaml
# Edit agent_config.yaml
sources:
  email_alerts:
    enabled: true    # Keep email alerts
    imap_label: "biz-acq/alerts"
    lookback_days: 7
  
  web_scraping:
    enabled: true    # 👈 ADD THIS
    
    bizbuysell:
      enabled: true  # 👈 ENABLE PLATFORMS
      search_url: "https://www.bizbuysell.com/businesses-for-sale/"
      max_pages: 3
      delay_seconds: 3
    
    bizquest:
      enabled: true  # 👈 ENABLE PLATFORMS
      search_url: "https://www.bizquest.com/businesses-for-sale/"
      max_pages: 3
      delay_seconds: 3
```

### **Option 2: Web-Only Mode**
Replace email alerts entirely:

```yaml
# Edit agent_config.yaml
sources:
  email_alerts:
    enabled: false   # 👈 DISABLE EMAIL
  
  web_scraping:
    enabled: true    # 👈 ENABLE WEB SCRAPING
    bizbuysell:
      enabled: true
      # ... rest of config
```

---

## 🔧 **Testing Web Scraping**

### **Test the web scraper:**
```bash
# Quick test (uses web_scraping_config.yaml)
python test_web_scraping.py
```

### **Run with web scraping enabled:**
```bash
# After editing agent_config.yaml
python -m src.main --config agent_config.yaml
```

---

## ⚙️ **Configuration Options**

### **Platform Settings:**
```yaml
bizbuysell:
  enabled: true
  search_url: "https://www.bizbuysell.com/businesses-for-sale/"
  max_pages: 5          # Number of pages to scrape
  delay_seconds: 3      # Delay between requests (be respectful)

bizquest:
  enabled: true
  search_url: "https://www.bizquest.com/businesses-for-sale/"
  max_pages: 5
  delay_seconds: 3

dealstream:
  enabled: false        # Enable when ready
  search_url: "https://www.dealstream.com/opportunities/"
  max_pages: 3
  delay_seconds: 3
```

### **Advanced Search URLs:**
You can customize search URLs with your specific criteria:

```yaml
bizbuysell:
  # Example: New York area, under $2M
  search_url: "https://www.bizbuysell.com/businesses-for-sale/?location=NY&price_max=2000000"
```

---

## 🎯 **Benefits of Web Scraping**

### **Immediate Results:**
- ✅ Find existing listings **right now**
- ✅ No waiting for email alerts
- ✅ Comprehensive market overview

### **Better Coverage:**
- ✅ **All current listings** matching your criteria
- ✅ Listings that might not trigger email alerts
- ✅ Historical listings still available

### **Market Intelligence:**
- ✅ See pricing trends across platforms
- ✅ Compare inventory levels
- ✅ Identify market opportunities

---

## ⚠️ **Important Notes**

### **Respectful Scraping:**
- 🕐 **Built-in delays** between requests
- 🔄 **Reasonable page limits** (3-5 pages max)
- 🤖 **Proper user agent** strings
- 📊 **Error handling** for network issues

### **Reliability:**
- 🔄 **Timeouts may occur** (normal for web scraping)
- 🌐 **Website changes** may break scrapers
- 📧 **Email alerts more reliable** for daily monitoring

### **Best Practice:**
- 🎯 **Use hybrid mode**: Email for new listings + Web for existing
- ⏰ **Run web scraping weekly** (not daily)
- 📧 **Keep email alerts enabled** for real-time notifications

---

## 🎮 **Ready to Use!**

Your acquisition agent is now **future-ready** with both methods:

1. **Keep using email alerts** for daily monitoring ✅
2. **Enable web scraping** when you want comprehensive coverage 🌐
3. **Run both together** for maximum coverage 🎯

**Everything is working perfectly!** 🚀
