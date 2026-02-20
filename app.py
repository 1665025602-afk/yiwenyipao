import io
from pathlib import Path
import streamlit as st
import segno

from db import init_db, get_box

st.set_page_config(page_title="一纹一泡 · 绿茶日常订阅盒", page_icon="🍵", layout="centered")
init_db()

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

if "user_key" not in st.session_state:
    st.session_state.user_key = "demo_user"

def get_site_base_url() -> str:
    # secrets.toml 存在时可读：.streamlit/secrets.toml  :contentReference[oaicite:5]{index=5}
    base = st.secrets.get("SITE_BASE_URL", "http://localhost:8501")
    return str(base).rstrip("/")

def qr_png_bytes(url: str) -> bytes:
    qr = segno.make(url)
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=8)
    return buf.getvalue()

st.title("🍵 一纹一泡 · 绿茶日常订阅盒")
st.caption("网页 + 图文 + 二维码（扫码打开同一套内容）")

# 读取 URL 参数：/?month=2026-02  :contentReference[oaicite:6]{index=6}
month = st.query_params.get("month", "2026-02")

box = get_box(month)
if not box:
    st.warning(f"未找到 {month} 的盒子内容，请到「管理后台」配置。")
    st.stop()

st.subheader(f"本月盒（{box['month']}）")
st.markdown(f"**绿茶**：{box['tea_name']}")
st.markdown(f"**风味**：{box['tea_desc']}")
st.markdown(f"**书签**：{box['bookmark_title']}")

# 图：书签图片（若已上传）
if box.get("bookmark_img_path"):
    img_path = ROOT / box["bookmark_img_path"]
    if img_path.exists():
        st.image(str(img_path), caption="本月纹样书签", width="stretch")  # 替换 use_container_width=True :contentReference[oaicite:7]{index=7}

st.markdown("---")
st.markdown(box["story_md"])

base = get_site_base_url()
target_url = f"{base}/?month={box['month']}"

st.markdown("---")
st.subheader("二维码（扫码打开本月图文）")
st.code(target_url)
st.image(qr_png_bytes(target_url), caption="扫码查看本月内容", width="content")  # 替换 use_container_width=False :contentReference[oaicite:8]{index=8}

st.info("左侧栏进入：订阅开通 / 我的订阅 / 管理后台（配置图文与二维码）")
