from instagrapi import Client
import pandas as pd

cl = Client()
cl.load_settings("session.json")

# Refresh session if expired
try:
    cl.get_timeline_feed()
except:
    cl.relogin()

# Now continue scraping
username = "dvaausgov"
user_id = cl.user_id_from_username(username)
posts = cl.user_medias_v1(user_id, 10)

post_data = []
for post in posts:
    post_data.append({
        "post_url": f"https://www.instagram.com/p/{post.code}/",
        "caption": post.caption_text,
        "likes": post.like_count,
        "comments": post.comment_count,
    })

df = pd.DataFrame(post_data)
df.to_csv("Instagram DVA.csv", index=False, encoding="utf-8-sig")
print("✅ Scraped and saved to Instagram DVA.csv")
