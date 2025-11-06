import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
from io import StringIO

sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.facecolor'] = '#0E1117'
plt.rcParams['axes.facecolor'] = '#0E1117'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['text.color'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'

st.set_page_config(
    page_title="AWS Cloud Economics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="☁️"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, #FFA07A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        color: white;
        text-align: center;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4ECDC4;
        border-left: 5px solid #FF6B6B;
        padding-left: 15px;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .insight-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E1E1E;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">☁️ AWS Cloud Economics Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #888;">Comprehensive Cost & Performance Analysis Dashboard</p>', unsafe_allow_html=True)

if not os.path.exists("aws_resources_compute.csv") or not os.path.exists("aws_resources_S3.csv"):
    st.error("❌ CSV files not found!")
    st.info("""
    **Please ensure the following files are in the same folder as this script:**
    - `aws_resources_compute.csv`
    - `aws_resources_S3.csv`
    
    **Or upload them using the file uploader below:**
    """)
    
    uploaded_ec2 = st.file_uploader("Upload EC2/Compute Data (CSV)", type=["csv"], key="ec2")
    uploaded_s3 = st.file_uploader("Upload S3 Data (CSV)", type=["csv"], key="s3")
    
    if uploaded_ec2 is not None and uploaded_s3 is not None:
        ec2_df = pd.read_csv(uploaded_ec2)
        s3_df = pd.read_csv(uploaded_s3)
        st.success("✅ Files loaded successfully!")
    else:
        st.stop()
else:
    ec2_df = pd.read_csv("aws_resources_compute.csv")
    s3_df = pd.read_csv("aws_resources_S3.csv")
    st.success("✅ CSV files loaded from local directory!")

with st.sidebar:
    st.markdown("### 🔍 Filters")
    st.markdown("---")
    
    st.markdown("#### 💻 EC2/Compute Filters")
    
    ec2_regions_list = sorted([x for x in ec2_df["Region"].dropna().unique() if pd.notna(x)])
    ec2_regions = st.multiselect(
        "Select Regions (EC2)",
        options=ec2_regions_list,
        default=ec2_regions_list,
        key="ec2_regions"
    )
    
    ec2_instance_types_list = sorted([x for x in ec2_df["InstanceType"].dropna().unique() if pd.notna(x)])
    ec2_instance_types = st.multiselect(
        "Select Instance Types",
        options=ec2_instance_types_list,
        default=ec2_instance_types_list,
        key="ec2_types"
    )
    
    ec2_states_list = sorted([x for x in ec2_df["State"].dropna().unique() if pd.notna(x)])
    ec2_states = st.multiselect(
        "Select States",
        options=ec2_states_list,
        default=ec2_states_list,
        key="ec2_states"
    )
    
    if "ResourceType" in ec2_df.columns:
        ec2_resource_types_list = sorted([x for x in ec2_df["ResourceType"].dropna().unique() if pd.notna(x)])
        ec2_resource_types = st.multiselect(
            "Select Resource Types",
            options=ec2_resource_types_list,
            default=ec2_resource_types_list,
            key="ec2_resource_types"
        )
    else:
        ec2_resource_types = []
    
    st.markdown("---")
    st.markdown("#### 📦 S3 Filters")
    
    s3_regions_list = sorted([x for x in s3_df["Region"].dropna().unique() if pd.notna(x)])
    s3_regions = st.multiselect(
        "Select Regions (S3)",
        options=s3_regions_list,
        default=s3_regions_list,
        key="s3_regions"
    )
    
    s3_storage_classes_list = sorted([x for x in s3_df["StorageClass"].dropna().unique() if pd.notna(x)])
    s3_storage_classes = st.multiselect(
        "Select Storage Classes",
        options=s3_storage_classes_list,
        default=s3_storage_classes_list,
        key="s3_storage"
    )
    
    if "Encryption" in s3_df.columns:
        s3_encryption_list = sorted([x for x in s3_df["Encryption"].dropna().unique() if pd.notna(x)])
        s3_encryption = st.multiselect(
            "Select Encryption",
            options=s3_encryption_list,
            default=s3_encryption_list,
            key="s3_encryption"
        )
    else:
        s3_encryption = []
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.markdown("---")
    
    ec2_filtered = ec2_df[
        (ec2_df["Region"].isin(ec2_regions) if len(ec2_regions) > 0 else True) &
        (ec2_df["InstanceType"].isin(ec2_instance_types) if len(ec2_instance_types) > 0 else True) &
        (ec2_df["State"].isin(ec2_states) if len(ec2_states) > 0 else True)
    ]
    
    if "ResourceType" in ec2_df.columns and len(ec2_resource_types) > 0:
        ec2_filtered = ec2_filtered[ec2_filtered["ResourceType"].isin(ec2_resource_types)]
    
    s3_filtered = s3_df[
        (s3_df["Region"].isin(s3_regions) if len(s3_regions) > 0 else True) &
        (s3_df["StorageClass"].isin(s3_storage_classes) if len(s3_storage_classes) > 0 else True)
    ]
    
    if "Encryption" in s3_df.columns and len(s3_encryption) > 0:
        s3_filtered = s3_filtered[s3_filtered["Encryption"].isin(s3_encryption)]
    
    st.metric("EC2 Instances", f"{len(ec2_filtered):,}", f"{len(ec2_filtered) - len(ec2_df):,} filtered")
    st.metric("S3 Buckets", f"{len(s3_filtered):,}", f"{len(s3_filtered) - len(s3_df):,} filtered")
    
    st.markdown("---")
    st.markdown("### 💰 Cost Overview")
    
    total_ec2_cost = ec2_filtered["CostUSD"].sum()
    total_s3_cost = s3_filtered["CostUSD"].sum()
    
    st.metric("Total EC2 Cost", f"${total_ec2_cost:,.2f}")
    st.metric("Total S3 Cost", f"${total_s3_cost:,.2f}")
    st.metric("Combined Cost", f"${total_ec2_cost + total_s3_cost:,.2f}")
    
    st.markdown("---")
    if st.button("🔄 Reset All Filters"):
        st.rerun()

st.markdown(f"**📊 Filtered Results:** EC2 Instances: **{len(ec2_filtered):,}** | S3 Buckets: **{len(s3_filtered):,}**")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Data Overview", "💻 EC2 Analysis", "📦 S3 Analysis", "🎯 Insights"])

with tab1:
    st.markdown('<div class="section-header">Dataset Exploration</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; text-align: center; color: white;">
            <h3 style="margin:0; color: white;">EC2 Records</h3>
            <h2 style="margin:0; color: white;">{:,}</h2>
        </div>
        """.format(len(ec2_filtered)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1rem; border-radius: 10px; text-align: center; color: white;">
            <h3 style="margin:0; color: white;">S3 Records</h3>
            <h2 style="margin:0; color: white;">{:,}</h2>
        </div>
        """.format(len(s3_filtered)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1rem; border-radius: 10px; text-align: center; color: white;">
            <h3 style="margin:0; color: white;">Avg EC2 Cost</h3>
            <h2 style="margin:0; color: white;">${:.2f}</h2>
        </div>
        """.format(ec2_filtered["CostUSD"].mean() if len(ec2_filtered) > 0 else 0), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 1rem; border-radius: 10px; text-align: center; color: white;">
            <h3 style="margin:0; color: white;">Total S3 Storage</h3>
            <h2 style="margin:0; color: white;">{:.1f} GB</h2>
        </div>
        """.format(s3_filtered["TotalSizeGB"].sum() if len(s3_filtered) > 0 else 0), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        with st.expander("🔍 EC2 Dataset Details", expanded=False):
            buffer = StringIO()
            ec2_filtered.info(buf=buffer)
            st.code(buffer.getvalue(), language=None)
            
            st.markdown("**Statistical Summary**")
            st.dataframe(ec2_filtered.describe(), width='stretch')
    
    with col_info2:
        with st.expander("🔍 S3 Dataset Details", expanded=False):
            buffer = StringIO()
            s3_filtered.info(buf=buffer)
            st.code(buffer.getvalue(), language=None)
            
            st.markdown("**Statistical Summary**")
            st.dataframe(s3_filtered.describe(), width='stretch')
    
    st.markdown("---")
    st.markdown("### 🧹 Data Cleaning Report")
    
    ec2_missing_before = ec2_filtered.isna().sum().sum()
    s3_missing_before = s3_filtered.isna().sum().sum()
    
    ec2_filtered = ec2_filtered.dropna()
    s3_filtered = s3_filtered.dropna()
    
    ec2_missing_after = ec2_filtered.isna().sum().sum()
    s3_missing_after = s3_filtered.isna().sum().sum()
    
    col_clean1, col_clean2 = st.columns(2)
    
    with col_clean1:
        st.info(f"**EC2:** Removed {ec2_missing_before} missing values | Final: {len(ec2_filtered):,} records")
    
    with col_clean2:
        st.info(f"**S3:** Removed {s3_missing_before} missing values | Final: {len(s3_filtered):,} records")

with tab2:
    st.markdown('<div class="section-header">EC2 Compute Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1, ax1 = plt.subplots(facecolor='#0E1117')
        ax1.set_facecolor('#0E1117')
        sns.histplot(ec2_filtered["CPUUtilization"], bins=20, kde=True, ax=ax1, color='#4ECDC4')
        ax1.set_title("CPU Utilization Distribution", color='white', fontsize=14, fontweight='bold')
        ax1.set_xlabel("CPU Utilization (%)", color='white')
        ax1.set_ylabel("Frequency", color='white')
        ax1.tick_params(colors='white')
        st.pyplot(fig1)
        plt.savefig("cpu_utilization_distribution.png", dpi=150, bbox_inches='tight', facecolor='#0E1117')
        plt.close()
    
    with col2:
        fig2, ax2 = plt.subplots(facecolor='#0E1117')
        ax2.set_facecolor('#0E1117')
        sns.boxplot(y=ec2_filtered["CostUSD"], ax=ax2, color='#FF6B6B')
        ax2.set_title("EC2 Cost Distribution (Outliers)", color='white', fontsize=14, fontweight='bold')
        ax2.set_ylabel("Cost (USD)", color='white')
        ax2.tick_params(colors='white')
        st.pyplot(fig2)
        plt.savefig("ec2_cost_outliers.png", dpi=150, bbox_inches='tight', facecolor='#0E1117')
        plt.close()
    
    fig3, ax3 = plt.subplots(facecolor='#0E1117')
    ax3.set_facecolor('#0E1117')
    scatter = ax3.scatter(ec2_filtered["CPUUtilization"], ec2_filtered["CostUSD"], 
                         c=ec2_filtered["CostUSD"], cmap='viridis', alpha=0.6, s=100)
    ax3.set_title("CPU Utilization vs Cost Relationship", color='white', fontsize=16, fontweight='bold')
    ax3.set_xlabel("CPU Utilization (%)", color='white', fontsize=12)
    ax3.set_ylabel("Cost (USD)", color='white', fontsize=12)
    ax3.tick_params(colors='white')
    plt.colorbar(scatter, ax=ax3, label='Cost (USD)')
    st.pyplot(fig3)
    plt.savefig("cpu_vs_cost.png", dpi=150, bbox_inches='tight', facecolor='#0E1117')
    plt.close()
    
    st.markdown("---")
    
    col_analysis1, col_analysis2 = st.columns(2)
    
    with col_analysis1:
        st.markdown("### 🏆 Top 5 Most Expensive Instances")
        top_ec2_data = ec2_filtered.nlargest(5, "CostUSD")[["ResourceId", "Region", "CostUSD", "CPUUtilization"]]
        top_ec2 = top_ec2_data.rename(columns={"ResourceId": "Resource ID", "CostUSD": "Cost (USD)", 
                                          "CPUUtilization": "CPU %"})
        st.dataframe(top_ec2, width='stretch', hide_index=True)
        
        if len(top_ec2_data) > 0:
            fig_top5, ax_top5 = plt.subplots(figsize=(10, 6), facecolor='#0E1117')
            ax_top5.set_facecolor('#0E1117')
            
            x_pos = range(len(top_ec2_data))
            bars = ax_top5.barh(x_pos, top_ec2_data["CostUSD"].values, color='#FF6B6B', alpha=0.8)
            
            ax_top5.set_yticks(x_pos)
            ax_top5.set_yticklabels([f"{row['ResourceId']}\n({row['Region']})" for _, row in top_ec2_data.iterrows()], 
                                    color='white', fontsize=10)
            ax_top5.set_xlabel("Cost (USD)", color='white', fontsize=12, fontweight='bold')
            ax_top5.set_title("Top 5 Most Expensive EC2 Instances", color='white', fontsize=14, fontweight='bold')
            ax_top5.tick_params(colors='white')
            ax_top5.invert_yaxis()
            
            for i, (idx, row) in enumerate(top_ec2_data.iterrows()):
                ax_top5.text(row["CostUSD"] + 0.01, i, f"${row['CostUSD']:.3f}\nCPU: {row['CPUUtilization']:.1f}%", 
                            color='white', va='center', fontsize=9, fontweight='bold')
            
            ax_top5.grid(axis='x', alpha=0.3, color='gray')
            plt.tight_layout()
            st.pyplot(fig_top5)
            plt.savefig("top_5_expensive_instances.png", dpi=150, bbox_inches='tight', facecolor='#0E1117')
            plt.close()
    
    with col_analysis2:
        st.markdown("### 📊 Average Cost by Region")
        avg_cost = ec2_filtered.groupby("Region")["CostUSD"].mean().sort_values(ascending=False)
        avg_cost_df = avg_cost.to_frame(name="Avg Cost (USD)")
        st.dataframe(avg_cost_df, width='stretch')

with tab3:
    st.markdown('<div class="section-header">S3 Storage Analysis</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        s3_region = s3_filtered.groupby("Region")["TotalSizeGB"].sum().sort_values(ascending=False)
        fig4, ax4 = plt.subplots(facecolor='#0E1117')
        ax4.set_facecolor('#0E1117')
        bars = ax4.barh(range(len(s3_region)), s3_region.values, color='#45B7D1')
        ax4.set_yticks(range(len(s3_region)))
        ax4.set_yticklabels(s3_region.index, color='white')
        ax4.set_title("Total S3 Storage by Region", color='white', fontsize=14, fontweight='bold')
        ax4.set_xlabel("Total Size (GB)", color='white')
        ax4.tick_params(colors='white')
        ax4.invert_yaxis()
        st.pyplot(fig4)
        plt.savefig("s3_storage_by_region.png", dpi=150, bbox_inches='tight', facecolor='#0E1117')
        plt.close()
    
    with col4:
        fig5, ax5 = plt.subplots(facecolor='#0E1117')
        ax5.set_facecolor('#0E1117')
        scatter2 = ax5.scatter(s3_filtered["TotalSizeGB"], s3_filtered["CostUSD"], 
                              c=s3_filtered["CostUSD"], cmap='plasma', alpha=0.7, s=120)
        ax5.set_title("S3 Cost vs Storage", color='white', fontsize=14, fontweight='bold')
        ax5.set_xlabel("Total Size (GB)", color='white')
        ax5.set_ylabel("Cost (USD)", color='white')
        ax5.tick_params(colors='white')
        plt.colorbar(scatter2, ax=ax5, label='Cost (USD)')
        st.pyplot(fig5)
        plt.savefig("s3_cost_vs_storage.png", dpi=150, bbox_inches='tight', facecolor='#0E1117')
        plt.close()
    
    st.markdown("---")
    
    col_s3_1, col_s3_2 = st.columns(2)
    
    with col_s3_1:
        st.markdown("### 🗂️ Top 5 Largest Buckets")
        top_s3 = s3_filtered.nlargest(5, "TotalSizeGB")[["BucketName", "Region", "TotalSizeGB", "CostUSD"]]
        top_s3 = top_s3.rename(columns={"BucketName": "Bucket Name", "TotalSizeGB": "Size (GB)", 
                                        "CostUSD": "Cost (USD)"})
        st.dataframe(top_s3, width='stretch', hide_index=True)
    
    with col_s3_2:
        st.markdown("### 📍 Total Storage by Region")
        total_storage = s3_filtered.groupby("Region")["TotalSizeGB"].sum().sort_values(ascending=False)
        total_storage_df = total_storage.to_frame(name="Total Size (GB)")
        st.dataframe(total_storage_df, width='stretch')

with tab4:
    st.markdown('<div class="section-header">Key Insights & Recommendations</div>', unsafe_allow_html=True)
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        if len(ec2_filtered) > 0:
            low_cpu_high_cost = ec2_filtered[(ec2_filtered["CPUUtilization"] < 30) & (ec2_filtered["CostUSD"] > ec2_filtered["CostUSD"].median())]
            potential_savings = low_cpu_high_cost["CostUSD"].sum() if len(low_cpu_high_cost) > 0 else 0.0
            st.markdown(f"""
            <div class="insight-box">
                <h3 style="margin-top:0; color: white;">⚠️ Underutilized Instances</h3>
                <h2 style="color: white;">{len(low_cpu_high_cost)}</h2>
                <p style="margin-bottom:0; color: white;">Low CPU (<30%) but high cost</p>
                <p style="margin-bottom:0; color: white;">Potential savings: ${potential_savings:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box">
                <h3 style="margin-top:0; color: white;">⚠️ No Data</h3>
                <p style="margin-bottom:0; color: white;">Adjust filters to see insights</p>
            </div>
            """, unsafe_allow_html=True)
    
    with insight_col2:
        if len(ec2_filtered) > 0:
            stopped_instances = len(ec2_filtered[ec2_filtered["State"] == "stopped"])
            st.markdown(f"""
            <div class="insight-box" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <h3 style="margin-top:0; color: white;">🛑 Stopped Instances</h3>
                <h2 style="color: white;">{stopped_instances}</h2>
                <p style="margin-bottom:0; color: white;">Consider terminating if unused</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <h3 style="margin-top:0; color: white;">🛑 No Data</h3>
                <p style="margin-bottom:0; color: white;">Adjust filters to see insights</p>
            </div>
            """, unsafe_allow_html=True)
    
    with insight_col3:
        if len(ec2_filtered) > 0:
            expensive_regions = ec2_filtered.groupby("Region")["CostUSD"].sum().sort_values(ascending=False).head(1)
            if len(expensive_regions) > 0:
                st.markdown(f"""
                <div class="insight-box" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);">
                    <h3 style="margin-top:0; color: white;">🌍 Highest Cost Region</h3>
                    <h2 style="color: white;">{expensive_regions.index[0]}</h2>
                    <p style="margin-bottom:0; color: white;">${expensive_regions.values[0]:.2f} total</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-box" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);">
                    <h3 style="margin-top:0; color: white;">🌍 No Data</h3>
                    <p style="margin-bottom:0; color: white;">Adjust filters to see insights</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);">
                <h3 style="margin-top:0; color: white;">🌍 No Data</h3>
                <p style="margin-bottom:0; color: white;">Adjust filters to see insights</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    opt_col1, opt_col2 = st.columns(2)
    
    with opt_col1:
        st.markdown("### 💡 EC2 Optimization Strategies")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white;">
            <ul style="color: white; line-height: 2;">
                <li><strong>Rightsize</strong> underutilized instances (low CPU but high cost)</li>
                <li><strong>Terminate</strong> stopped/idle instances that are no longer needed</li>
                <li><strong>Reserved Instances</strong> for predictable, steady workloads</li>
                <li><strong>Spot Instances</strong> for fault-tolerant, flexible applications</li>
                <li><strong>Auto Scaling</strong> to match demand and reduce waste</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with opt_col2:
        st.markdown("### 💡 S3 Optimization Strategies")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 12px; color: white;">
            <ul style="color: white; line-height: 2;">
                <li><strong>Lifecycle Policies</strong> to transition infrequent data to STANDARD_IA</li>
                <li><strong>Glacier/Deep Archive</strong> for rarely accessed data</li>
                <li><strong>Intelligent-Tiering</strong> for automatic optimization</li>
                <li><strong>Cleanup</strong> unused buckets and old versions</li>
                <li><strong>Compression</strong> to reduce storage requirements</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📥 Export Analysis Results")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        if len(ec2_filtered) > 0:
            top_ec2_export = ec2_filtered.nlargest(5, "CostUSD")[["ResourceId", "Region", "CostUSD"]]
            ec2_csv = top_ec2_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download Top EC2 Instances (CSV)",
                data=ec2_csv,
                file_name="top_ec2_instances.csv",
                mime="text/csv",
                width='stretch'
            )
        else:
            st.info("No EC2 data to export. Adjust filters.")
    
    with col_d2:
        if len(s3_filtered) > 0:
            top_s3_export = s3_filtered.nlargest(5, "TotalSizeGB")[["BucketName", "Region", "TotalSizeGB"]]
            s3_csv = top_s3_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download Top S3 Buckets (CSV)",
                data=s3_csv,
                file_name="top_s3_buckets.csv",
                mime="text/csv",
                width='stretch'
            )
        else:
            st.info("No S3 data to export. Adjust filters.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
    <h3 style="color: white; margin: 0;">✅ Analysis Complete!</h3>
    <p style="color: white; margin: 0.5rem 0 0 0;">All visualizations have been saved as PNG files</p>
</div>
""", unsafe_allow_html=True)
