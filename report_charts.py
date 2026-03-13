import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

def generate_report_charts(data_path):
    # 1. Đọc và tiền xử lý dữ liệu
    print("Đang tải dữ liệu...")
    df = pd.read_csv(data_path)
    
    # Chuyển YearsCode sang dạng số để vẽ biểu đồ tương quan
    df['YearsCode'] = pd.to_numeric(df['YearsCode'], errors='coerce')
    
    # Extract vai trò chính (DevType_Primary) để dùng cho Biểu đồ 1, vì DevType có thể chứa nhiều giá trị phân tách bằng dấu chấm phẩy
    df['DevType_Primary'] = df['DevType'].dropna().str.split(';').str[0].str.strip()

    # 2. Xây dựng Figure gồm 2 biểu đồ nằm ngang (1 hàng, 2 cột) để dễ dàng copy vào slide
    # Sử dụng theme whitegrid giúp biểu đồ nhìn sạch sẽ và chuyên nghiệp
    sns.set_theme(style="whitegrid", palette="muted")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # ==========================================
    # BIỂU ĐỒ 1: BOXPLOT (Phân bố & Phương sai)
    # ==========================================
    # Lọc data chỉ lấy đúng 3 vai trò
    target_roles = ["Data engineer", "Developer, back-end", "DevOps specialist"]
    df_box = df[df['DevType_Primary'].isin(target_roles)].dropna(subset=['SalaryUSD'])
    
    sns.boxplot(
        data=df_box, 
        x='DevType_Primary', 
        y='SalaryUSD', 
        ax=axes[0],
        palette="pastel", # Màu sắc nhẹ nhàng
        showfliers=False # Tuỳ chọn: Tạm ẩn Outlier (các điểm dị biệt quá cao) để dễ so sánh vùng IQR (tuỳ theo nhu cầu báo cáo)
    )
    
    # Tinh chỉnh biểu đồ 1
    axes[0].set_title('Phân bố Mức lương theo Vai trò\n(Trọng tâm xem xét Phương sai & Khoảng tin cậy IQR)', fontsize=14, fontweight='bold', pad=15)
    axes[0].set_xlabel('Vai trò chuyên môn', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Mức lương hàng năm (USD)', fontsize=12, fontweight='bold')
    
    # Format trục Y sang định dạng tiền tệ ($)
    formatter = ticker.FuncFormatter(lambda x, pos: f'${x:,.0f}')
    axes[0].yaxis.set_major_formatter(formatter)

    # ==========================================
    # BIỂU ĐỒ 2: SCATTER PLOT & REGRESSION LINE
    # ==========================================
    # Lọc những bản ghi mà DevType chứa "Data engineer" tĩnh hoặc "Data scientist"
    # Ignore NA flags giúp tránh lỗi missing vaule
    mask_data_roles = df['DevType'].astype(str).str.contains("Data engineer|Data scientist", case=False, na=False)
    df_reg = df[mask_data_roles].dropna(subset=['SalaryUSD', 'YearsCode'])
    
    # Xoá bớt các dữ liệu nhiễu (Ví dụ: Năm kinh nghiệm > 50 hoặc lương quá dị biệt)
    # df_reg = df_reg[(df_reg['YearsCode'] <= 40) & (df_reg['SalaryUSD'] < 1000000)]
    
    sns.regplot(
        data=df_reg, 
        x='YearsCode', 
        y='SalaryUSD', 
        ax=axes[1],
        scatter_kws={'alpha': 0.3, 'color': '#1f77b4', 's': 20}, # Điểm dữ liệu mờ (alpha=0.3) và nhỏ nhắn vừa vặn
        line_kws={'color': 'red', 'linewidth': 2, 'label': 'Đường xu hướng (Linear Regression)'} # Đường hồi quy màu đỏ rõ ràng
    )
    
    # Tinh chỉnh biểu đồ 2
    axes[1].set_title('Tương quan giữa Năm kinh nghiệm và Mức lương\n(Data Engineer & Data Scientist)', fontsize=14, fontweight='bold', pad=15)
    axes[1].set_xlabel('Năm kinh nghiệm (Years)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Mức lương hàng năm (USD)', fontsize=12, fontweight='bold')
    axes[1].yaxis.set_major_formatter(formatter)
    axes[1].legend()

    # ==========================================
    # HOÀN HIỆN & LƯU BIỂU ĐỒ
    # ==========================================
    plt.tight_layout() # Tránh việc 2 biểu đồ xô lẹch chữ vào nhau
    
    # Lưu ra dạng hình ảnh HD, nền trắng (trong suốt có thể dùng transparent=True)
    output_img = 'report_charts_visualization.png'
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    print(f"✅ Đã vẽ và xuất biểu đồ ra file: {output_img}")
    
    # Hiển thị biểu đồ
    plt.show()

if __name__ == "__main__":
    # Thay đường dẫn này đến file CSV đã qua xử lý của bạn
    DATA_PATH = "/home/ntt/cleandata/cleaned_stackoverflow_2025.csv"
    generate_report_charts(DATA_PATH)
