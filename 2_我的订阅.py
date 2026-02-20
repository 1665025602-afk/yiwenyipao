import io
from pathlib import Path
import streamlit as st
import segno

from db import get_subscription, get_box

st.title("👤 我的订阅")

ROOT = Path(__file__).resolve().parent.parent

def get_site_base_url() -> str:
    base = st.secrets.get("SITE_BASE_URL", "http://localhost:8501")
    return str(base).rstrip("/")

def qr_png_bytes(url: str) -> bytes:
    qr = segno.make(url)
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=7)
    return buf.getvalue()

sub = get_subscription(st.session_state.user_key)
if not sub or sub["status"] != "active":
    st.warning("你还没有有效订阅。去「订阅开通」先开通一个吧。")
    st.stop()

st.subheader("订阅状态")
st.write(f"档位：**{sub['plan_id']}**")
st.write(f"开始：{sub['start_at']}")
st.write(f"到期：{sub['end_at']}")

box = get_box(sub["current_box_month"])
st.markdown("---")
st.subheader(f"本月盒（{sub['current_box_month']}）")
if not box:
    st.info("本月盒内容还没配置。")
    st.stop()

st.write(f"绿茶：**{box['tea_name']}**")
st.write(f"风味：{box['tea_desc']}")
st.write(f"书签：**{box['bookmark_title']}**")

if box.get("bookmark_img_path"):
    img_path = ROOT / box["bookmark_img_path"]
    if img_path.exists():
        st.image(str(img_path), caption="本月纹样书签", width="stretch")

st.markdown("**故事与冲泡**：")
st.markdown(box["story_md"])

base = get_site_base_url()
target_url = f"{base}/?month={box['month']}"

st.markdown("---")
st.subheader("二维码（分享/扫码打开同一套内容）")
st.code(target_url)
st.image(qr_png_bytes(target_url), caption="扫码打开本月图文", width="content")
