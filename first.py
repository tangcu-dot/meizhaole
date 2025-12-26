import streamlit as st
import pandas as pd
# 增加plotly导入异常处理，自动安装（可选）
try:
    import plotly.express as px
except ImportError:
    st.error("缺少plotly库，正在自动安装...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.express as px

def get_dataframe_from_excel():
    """读取Excel数据，兼容文件不存在的情况"""
    try:
        # 修正Excel文件名：从sjk.xlsx改为supermarket_sales.xlsx（匹配你之前的文件）
        df = pd.read_excel('supermarket_sales.xlsx',
                sheet_name="销售数据",
                skiprows=1,
                index_col="订单号"
                )
    except FileNotFoundError:
        # 生成更贴近真实场景的示例数据
        data = {
            "订单号": [1,2,3,4,5,6,7,8,9,10],
            "城市": ["太原","临汾","大同","太原","临汾","大同","太原","临汾","大同","太原"],
            "顾客类型": ["会员","普通","会员","普通","会员","普通","会员","普通","会员","普通"],
            "性别": ["男","女","男","女","男","女","男","女","男","女"],
            "产品类型": ["食品饮料","运动旅行","电子配件","时尚配饰","家居生活","健康美容","食品饮料","运动旅行","电子配件","时尚配饰"],
            "总价": [150.5, 280.8, 320.2, 180.9, 250.3, 190.7, 160.2, 290.5, 310.8, 170.4],
            "时间": ["10:30:00","11:15:00","12:45:00","13:20:00","14:50:00","15:10:00","16:30:00","17:40:00","18:20:00","19:10:00"],
            "评分": [7.2, 6.8, 7.5, 6.9, 7.1, 7.3, 6.7, 7.0, 7.4, 6.6]
        }
        df = pd.DataFrame(data)
        df.index = df["订单号"]  # 设置订单号为索引
        df.index.name = "订单号"
        df = df.drop("订单号", axis=1)  # 移除重复的订单号列
    
    # 修复小时数列名：从“小时数”改为“小时”（匹配图表函数中的列名）
    # 兼容不同时间格式，避免转换报错
    try:
        df['小时'] = pd.to_datetime(df["时间"], format="%H:%M:%S").dt.hour
    except:
        df['小时'] = pd.to_datetime(df["时间"], errors='coerce').dt.hour
    
    # 过滤空值
    df = df.dropna(subset=['小时'])
    return df

def add_sidebar_func(df):
    """创建侧边栏筛选器"""
    with st.sidebar:
        st.header("请筛选数据：")
        
        # 城市筛选
        city_unique = df["城市"].unique()
        city = st.multiselect(
            "请选择城市：",
            options=city_unique,
            default=city_unique,
            )
        
        # 顾客类型筛选
        customer_type_unique = df["顾客类型"].unique()
        customer_type = st.multiselect(
            "请选择顾客类型：",
            options=customer_type_unique,
            default=customer_type_unique,
            )
        
        # 性别筛选
        gender_unique = df["性别"].unique()
        gender = st.multiselect(
            "请选择性别：",  # 补充冒号，匹配UI样式
            options=gender_unique,
            default=gender_unique,
            )
    
    # 应用筛选条件（处理空筛选的情况）
    if not city:
        city = city_unique
    if not customer_type:
        customer_type = customer_type_unique
    if not gender:
        gender = gender_unique
    
    df_selection = df.query(
        "城市 == @city & 顾客类型 == @customer_type & 性别 == @gender"
        )
    return df_selection

def product_line_chart(df):
    """生成产品类型销售额横向柱状图"""
    # 处理空数据
    if df.empty:
        st.warning("暂无产品销售额数据")
        return px.bar(title="暂无数据")
    
    sales_by_product_line = (
        df.groupby(by=["产品类型"])[["总价"]].sum().sort_values(by="总价")
        )
    fig_product_sales = px.bar(
        sales_by_product_line,
        x="总价",
        y=sales_by_product_line.index,
        orientation="h",
        title="<b>按产品类型划分的销售额</b>",
        color_discrete_sequence=["#1f77b4"],  # 匹配图片的蓝色
        template="plotly_white"
        )
    # 优化图表样式
    fig_product_sales.update_layout(
        xaxis_title="销售额（元）",
        yaxis_title="产品类型",
        height=400
    )
    return fig_product_sales

def hour_chart(df):
    """生成小时销售额纵向柱状图"""
    # 处理空数据
    if df.empty:
        st.warning("暂无小时销售额数据")
        return px.bar(title="暂无数据")
    
    # 只展示10-20点的数据（匹配图片）
    df_hour = df[df["小时"].between(10, 20)]
    if df_hour.empty:
        st.info("10-20点暂无销售数据")
        return px.bar(title="10-20点暂无数据")
    
    sales_by_hour = df_hour.groupby(by=["小时"])[["总价"]].sum()
    fig_hour_sales = px.bar(
        sales_by_hour,
        y="总价",
        x=sales_by_hour.index,
        title="<b>按小时数划分的销售额</b>",
        color_discrete_sequence=["#1f77b4"],  # 匹配图片的蓝色
        template="plotly_white"
        )
    # 优化图表样式
    fig_hour_sales.update_layout(
        xaxis_title="小时数",
        yaxis_title="总价（元）",
        height=400
    )
    return fig_hour_sales

def main_page_demo(df):
    """主界面展示"""
    st.title('📊销售仪表板')
    
    # 计算核心指标（处理空数据）
    if df.empty:
        total_sales = 0
        average_rating = 0
        average_sale_by_transaction = 0
    else:
        total_sales = int(df["总价"].sum())
        average_rating = round(df["评分"].mean(), 1)
        average_sale_by_transaction = round(df["总价"].mean(), 2)
    
    # 核心指标展示（匹配图片样式）
    left_key_col, middle_key_col, right_key_col = st.columns(3)
    with left_key_col:
        st.subheader("总销售额：")
        st.subheader(f"RMB ¥ {total_sales:,}")
    with middle_key_col:
        st.subheader("顾客评分的平均值：")
        star_rating_string = ":star:" * int(round(average_rating, 0))
        st.subheader(f"{average_rating} {star_rating_string}")
    with right_key_col:
        st.subheader("每单的平均销售额：")
        st.subheader(f"RMB ¥ {average_sale_by_transaction}")
    
    st.divider()
    
    # 图表展示
    left_chart_col, right_chart_col = st.columns(2)
    with left_chart_col:
        hour_fig = hour_chart(df)
        st.plotly_chart(hour_fig, use_container_width=True)

    with right_chart_col:
        product_fig = product_line_chart(df)
        st.plotly_chart(product_fig, use_container_width=True)

def run_app():
    """启动应用"""
    st.set_page_config(
        page_title="销售仪表板",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 加载数据
    sale_df = get_dataframe_from_excel()
    # 侧边栏筛选
    df_selection = add_sidebar_func(sale_df)
    # 主界面展示
    main_page_demo(df_selection)

if __name__ == "__main__":
    run_app()
