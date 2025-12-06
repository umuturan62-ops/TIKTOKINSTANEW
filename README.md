# TikTok → Instagram Otomatik Repost Botu (Playwright)

### 🚀 Özellikler
- TikTok profillerini Playwright ile tarar  
- Yeni videoları watermark’sız indirir  
- Instagram Reels olarak paylaşır  
- Railway veya Docker üzerinde 7/24 çalışır  

---

## 🔧 Kurulum (Railway)
1. Bu repo dosyalarını GitHub'a yükleyin  
2. Railway → New Project → Deploy from GitHub  
3. Environment Variables ekleyin:
IG_USERNAME=...
IG_PASSWORD=...
TIKTOK_USERS=bellapoarch,tatianakaer
CHECK_INTERVAL_SECONDS=600
4. Deploy → Worker başlat  
5. Loglarda botun çalıştığını görün  

---

## Notlar
- TikTok scraping Playwright ile yapıldığı için TikTok güncellemesinde bazı selector’lar değişebilir  
- Instagram “challenge_required” verebilir; ilk girişte IG hesabınızı tarayıcıdan doğrulayın  
