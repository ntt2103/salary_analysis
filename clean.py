import pandas as pd
import numpy as np

# ==========================================
# BƯỚC 1: KHÁM PHÁ VÀ HIỂU DỮ LIỆU
# ==========================================
print("--- Bước 1: Đọc dữ liệu ---")
# Đảm bảo file 'survey_results_public.csv' nằm cùng thư mục với script
df = pd.read_csv('survey_results_public_2024.csv')

pd.set_option('display.max_columns', None)
print(f"Số dòng và cột ban đầu: {df.shape}")

# ==========================================
# BƯỚC 2: CHỌN LỌC VÀ ĐỔI TÊN CỘT
# ==========================================
print("\n--- Bước 2: Chọn lọc và đổi tên cột ---")

columns_to_keep = [
    'ResponseId', 'MainBranch', 'Employment', 'RemoteWork', 
    'EdLevel', 'YearsCode', 'YearsCodePro', 'DevType', 
    'Country', 'ConvertedCompYearly', 'LanguageHaveWorkedWith'
]
df = df[columns_to_keep]

df = df.rename(columns={
    'ConvertedCompYearly': 'SalaryUSD',
    'LanguageHaveWorkedWith': 'Languages'
})

# ==========================================
# BƯỚC 3: XỬ LÝ DỮ LIỆU CHUỖI VÀ ÉP KIỂU SỐ
# ==========================================
print("\n--- Bước 3: Ép kiểu Số năm kinh nghiệm ---")

def clean_years_code(x):
    if pd.isna(x):
        return np.nan
    if x == 'Less than 1 year':
        return 0.5
    if x == 'More than 50 years':
        return 51.0
    return float(x)

df['YearsCode'] = df['YearsCode'].apply(clean_years_code)
df['YearsCodePro'] = df['YearsCodePro'].apply(clean_years_code)

# ==========================================
# BƯỚC 4: XỬ LÝ MISSING VALUES (TRƯỚC KHI TÍNH NGOẠI LỆ)
# ==========================================
print("\n--- Bước 4: Xóa dữ liệu khuyết thiếu quan trọng ---")
# Bắt buộc drop NaN ở 3 cột cốt lõi để không làm méo mó mô hình phân tích
df = df.dropna(subset=['DevType', 'YearsCodePro', 'SalaryUSD'])
print(f"Số dòng sau khi xóa NaN ở các cột trọng yếu: {df.shape[0]}")

# ==========================================
# BƯỚC 5: XỬ LÝ NGOẠI LỆ (OUTLIERS) BẰNG PHƯƠNG PHÁP IQR
# ==========================================
print("\n--- Bước 5: Lọc ngoại lệ Lương và Kinh nghiệm ---")

# Tính Q1, Q3 và IQR cho cột Lương
Q1 = df['SalaryUSD'].quantile(0.25)
Q3 = df['SalaryUSD'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Giữ lại những người có mức lương nằm trong dải phân bố hợp lý
df = df[(df['SalaryUSD'] >= lower_bound) & (df['SalaryUSD'] <= upper_bound)]

# Loại bỏ các trường hợp troll data (ví dụ: khai code 100 năm)
df = df[df['YearsCodePro'] <= 50] 

print(f"Số dòng chuẩn sau khi lọc ngoại lệ: {df.shape[0]}")

# ==========================================
# BƯỚC 6: XỬ LÝ CÂU HỎI CHỌN NHIỀU ĐÁP ÁN
# ==========================================
print("\n--- Bước 6: Tách cột Languages (One-Hot Encoding) ---")

df['Languages'] = df['Languages'].fillna('None')
language_dummies = df['Languages'].str.get_dummies(sep=';')
language_dummies = language_dummies.add_prefix('Lang_')

df = pd.concat([df, language_dummies], axis=1)
df = df.drop(columns=['Languages'])

# ==========================================
# BƯỚC 7: CHUẨN HÓA CÁC BIẾN PHÂN LOẠI
# ==========================================
print("\n--- Bước 7: Chuẩn hóa EdLevel và Country ---")

def shorten_education(x):
    if pd.isna(x):
        return x
    if 'Bachelor’s degree' in x:
        return 'Bachelor'
    if 'Master’s degree' in x:
        return 'Master'
    if 'Professional degree' in x or 'Other doctoral' in x:
        return 'Post grad'
    if 'Associate degree' in x or 'Some college' in x:
        return 'Some college'
    return 'Less than Bachelors'

df['EdLevel'] = df['EdLevel'].apply(shorten_education)

def shorten_country(country_col, cutoff):
    country_counts = country_col.value_counts()
    countries_to_group = country_counts[country_counts < cutoff].index
    return country_col.replace(countries_to_group, 'Other')

# Gom những nước có dưới 100 người tham gia vào nhóm 'Other'
# Điền tạm 'Unknown' nếu Country bị trống trước khi gom nhóm
df['Country'] = df['Country'].fillna('Unknown')
df['Country'] = shorten_country(df['Country'], 100)

# ==========================================
# BƯỚC 8: KIỂM TRA LẠI VÀ LƯU DỮ LIỆU
# ==========================================
print("\n--- Bước 8: Hoàn tất và lưu file ---")
print(f"Số dòng và cột cuối cùng: {df.shape}")

# Lưu ra file CSV mới
df.to_csv('cleaned_stackoverflow_2024.csv', index=False)
print("\nĐã lưu thành công file 'cleaned_stackoverflow_2024.csv'!")