import streamlit as st
from db import upsert_box, get_box

st.title("🛠️ 管理后台：盒子配置（你自己用）")

month = st.text_input("月份（YYYY-MM）", value="2026-02")
existing = get_box(month)
if existing:
    st.info("已存在配置，将会覆盖更新。")

tea_name = st.text_input("绿茶名称", value=(existing["tea_name"] if existing else "绿茶 · 日常清爽款"))
tea_desc = st.text_input("风味描述", value=(existing["tea_desc"] if existing else "清鲜｜豆香｜回甘"))
bookmark_title = st.text_input("书签标题", value=(existing["bookmark_title"] if existing else "本月纹样书签：蝶影"))
story_md = st.text_area("故事/冲泡指南（Markdown）", height=220, value=(existing["story_md"] if existing else "## 冲泡建议\n- 80–85℃\n\n## 纹样故事\n..."))

st.markdown("---")
st.caption("图片上传（可选）：比赛 MVP 可以先不做长期存储，只用于展示。")
img = st.file_uploader("上传书签图片（png/jpg）", type=["png","jpg","jpeg"])

if st.button("保存本月盒", type="primary"):
    upsert_box(month, tea_name, tea_desc, bookmark_title, story_md)
    st.success("已保存！回到主页/我的订阅页查看。")

if img is not None:
    st.image(img, caption="预览：本月书签图", use_container_width=True)
