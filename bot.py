import os
import json
import time
import pathlib
import requests
from datetime import datetime
from instagrapi import Client
from playwright.sync_api import sync_playwright

LAST_POSTS_FILE = "last_posts.json"
CHECK_INTERVAL_SECONDS = int(os.environ.get("CHECK_INTERVAL_SECONDS", 600))  # 10 dakika
TIKTOK_USERS = os.environ.get("TIKTOK_USERS", "bellapoarch,tatianakaer")
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
TEMP_DIR = pathlib.Path("temp_videos")
TEMP_DIR.mkdir(exist_ok=True)


def load_last_posts():
    try:
        if os.path.exists(LAST_POSTS_FILE):
            with open(LAST_POSTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}


def save_last_posts(data):
    with open(LAST_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_new(username, video_id, last_posts):
    return video_id not in last_posts.get(username, [])


def mark_posted(username, video_id, last_posts):
    last_posts.setdefault(username, [])
    last_posts[username].append(video_id)
    last_posts[username] = last_posts[username][-100:]
    save_last_posts(last_posts)


def download_file(url, path):
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as e:
        print("⬇️ İndirme hatası:", e)
        return False


def login_instagram():
    if not IG_USERNAME or not IG_PASSWORD:
        raise Exception("IG_USERNAME veya IG_PASSWORD tanımlı değil.")
    client = Client()
    client.login(IG_USERNAME, IG_PASSWORD)
    return client


def upload_instagram(client, video_path, caption):
    try:
        print("📤 Instagram'a yükleniyor:", video_path)
        client.video_upload(video_path, caption)
        print("✅ Instagram'a yüklendi")
        return True
    except Exception as e:
        print("❌ Instagram yükleme hatası:", e)
        return False


def extract_videos_from_profile(page, username, limit=10):
    profile_url = f"https://www.tiktok.com/@{username}"
    print(f"🔍 Profil açılıyor: {profile_url}")
    page.goto(profile_url, timeout=60000)
    page.wait_for_timeout(3000)

    anchors = page.query_selector_all('a[href*="/video/"]')
    video_links = []
    for a in anchors:
        href = a.get_attribute("href")
        if href and "/video/" in href:
            video_links.append(href.split("?")[0])

    unique = []
    for l in video_links:
        if l not in unique:
            unique.append(l)
        if len(unique) >= limit:
            break
    return unique


def extract_video_src(page, video_page_url):
    try:
        page.goto(video_page_url, timeout=60000)
        page.wait_for_timeout(2000)

        video = page.query_selector("video")
        if video:
            src = video.get_attribute("src")
            if src:
                return src

        og = page.query_selector('meta[property="og:video"]')
        if og:
            src = og.get_attribute("content")
            if src:
                return src

        content = page.content()
        import re
        m = re.search(r'playAddr":"(https[^"]+?)"', content)
        if m:
            return m.group(1).replace("\\u0026", "&").replace("\\/", "/")

        return None
    except Exception as e:
        print("❌ Video source hata:", e)
        return None


def safe_filename(url):
    import hashlib
    h = hashlib.sha1(url.encode()).hexdigest()
    return f"{h}.mp4"


def run_once():
    last_posts = load_last_posts()
    tik_users = [u.strip() for u in TIKTOK_USERS.split(",") if u.strip()]
    print("Takip edilenler:", tik_users)

    try:
        ig_client = login_instagram()
    except Exception as e:
        print("Instagram login hata:", e)
        ig_client = None

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
        )
        page = context.new_page()

        for username in tik_users:
            try:
                videos = extract_videos_from_profile(page, username, limit=12)
                print(f"{username}: {len(videos)} video bulundu")

                for vp in videos:
                    video_id = vp.rstrip("/").split("/")[-1]

                    if not is_new(username, video_id, last_posts):
                        continue

                    print("🆕 Yeni video:", vp)

                    src = extract_video_src(page, vp)
                    if not src:
                        print("⚠️ kaynak yok:", vp)
                        continue

                    file_path = TEMP_DIR / safe_filename(src)
                    if not download_file(src, file_path):
                        continue

                    caption = f"Repost @{username}\n\nKaynak: {vp}"

                    if ig_client:
                        uploaded = upload_instagram(ig_client, str(file_path), caption)
                        if uploaded:
                            mark_posted(username, video_id, last_posts)

                    try:
                        file_path.unlink()
                    except:
                        pass

                    time.sleep(15)

            except Exception as e:
                print("Profil hata:", username, e)
                continue

        context.close()
        browser.close()


if __name__ == "__main__":
    print("=== TikTok → Instagram BOT Başladı ===")
    while True:
        try:
            run_once()
        except Exception as e:
            print("Beklenmeyen hata:", e)
        print(f"{CHECK_INTERVAL_SECONDS} sn bekleniyor...")
        time.sleep(CHECK_INTERVAL_SECONDS)
