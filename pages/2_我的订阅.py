import streamlit as st
from datetime import datetime
from db import get_subscription, get_box

st.title("👤 我的订阅")

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
if box:
    st.write(f"绿茶：**{box['tea_name']}**")
    st.write(f"风味：{box['tea_desc']}")
    st.write(f"书签：**{box['bookmark_title']}**")
    st.markdown("**故事与冲泡**：")
    st.markdown(box["story_md"])
else:
    st.info("本月盒内容还没配置。")
