import streamlit as st
from datetime import datetime, timedelta
from db import get_plans, set_subscription, get_box

st.title("✅ 订阅开通")

plans = get_plans()
plan_map = {p["title"]: p for p in plans}

choice = st.radio("选择订阅档位", list(plan_map.keys()), horizontal=True)
plan = plan_map[choice]

st.write(f"价格：**¥{plan['price']}**")
st.write(f"积分倍率：**{plan['points_multi']}x**")
st.write(f"订阅周期：**{plan['duration_days']} 天**")

st.markdown("---")
month = "2026-02"
box = get_box(month)
if box:
    st.subheader("你将收到")
    st.write(f"- 绿茶：{box['tea_name']}")
    st.write(f"- 书签：{box['bookmark_title']}")
    st.write("- 纹样故事卡 + 冲泡指南（在线可查看）")
else:
    st.warning("本月盒内容尚未配置。")

st.markdown("---")
st.caption("比赛/无商户号阶段：先用「模拟支付成功」跑通闭环，后续再接真实支付。")

if st.button("模拟支付成功并开通", type="primary"):
    start = datetime.now()
    end = start + timedelta(days=int(plan["duration_days"]))
    set_subscription(
        user_key=st.session_state.user_key,
        plan_id=plan["plan_id"],
        start_at=start.isoformat(timespec="seconds"),
        end_at=end.isoformat(timespec="seconds"),
        current_box_month=month,
        status="active",
    )
    st.success("已开通！去「我的订阅」查看。")
