import io
from pathlib import Path
import streamlit as st
import segno

from db import upsert_box, get_box, list_boxes

st.title("🛠️ 管理后台：配置图文 + 二维码")

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

def get_site_base_url() -> str:
    base = st.secrets.get("SITE_BASE_URL", "http://localhost:8501")
    return str(base).rstrip("/")

def preview_qr(url: str):
    qr = segno.make(url)
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=7)
    st.image(buf.getvalue(), caption="预览：二维码（扫码打开本月图文）", width="content")

months = [b["month"] for b in list_boxes()]
default_month = months[0] if months else "2026-02"

col1, col2 = st.columns([2, 1])
with col1:
    picked = st.selectbox("选择已有月份（或下面手动改）", options=months if months else [default_month])
with col2:
    month = st.text_input("编辑月份（YYYY-MM）", value=picked)

existing = get_box(month)

tea_name = st.text_input("绿茶名称", value=(existing["tea_name"] if existing else "绿茶 · 日常清爽款"))
tea_desc = st.text_input("风味描述（建议3-5个词）", value=(existing["tea_desc"] if existing else "清鲜｜豆香｜回甘"))
bookmark_title = st.text_input("书签标题", value=(existing["bookmark_title"] if existing else "本月纹样书签：蝶影"))
story_md = st.text_area(
    "故事/冲泡指南（Markdown）",
    height=220,
    value=(existing["story_md"] if existing else "## 冲泡建议\n- 80–85℃\n\n## 纹样故事\n..."),
)

st.markdown("---")
st.subheader("上传书签图片（用于图文展示）")
uploaded = st.file_uploader("选择图片（png/jpg）", type=["png", "jpg", "jpeg"])

bookmark_img_path = existing.get("bookmark_img_path") if existing else None
if uploaded is not None:
    suffix = Path(uploaded.name).suffix.lower()
    save_path = ASSETS / f"bookmark_{month}{suffix}"
    save_path.write_bytes(uploaded.getvalue())
    bookmark_img_path = str(save_path.relative_to(ROOT))
    st.image(uploaded.getvalue(), caption="预览：书签图", width="stretch")
elif bookmark_img_path:
    p = ROOT / bookmark_img_path
    if p.exists():
        st.image(str(p), caption="当前已保存的书签图", width="stretch")

st.markdown("---")
st.subheader("二维码链接（自动生成，指向你的 Streamlit 网站）")
base = get_site_base_url()
qr_url = f"{base}/?month={month}"
st.code(qr_url)
preview_qr(qr_url)

if st.button("保存/更新本月盒（含图片路径与二维码链接）", type="primary"):
    upsert_box(
        month=month,
        tea_name=tea_name,
        tea_desc=tea_desc,
        bookmark_title=bookmark_title,
        story_md=story_md,
        bookmark_img_path=bookmark_img_path,
        qr_url=qr_url,
    )
    st.success("已保存！去主页或我的订阅页查看效果。")
