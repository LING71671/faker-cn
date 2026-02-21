import re

with open("faker_cn/__init__.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Enhance Age vs Education reality
old_edu_age = """        # Logic Hardening: Education/Age Door for Specific Jobs
        # Always fix '研究生' to be realistic
        if "研究生" in job:
            if age > 35: age = self.random_int(22, 28)
            employment = "在读"
            job = "学生"
            education = "本科"
"""

new_edu_age = """        # Logic Hardening: Base Education Age Floor
        if education == "博士" and age < 27:
            age = self.random_int(27, 45)
        elif education in ["硕士", "MBA"] and age < 24:
            age = self.random_int(24, 40)
        elif education == "本科" and age < 22:
            age = self.random_int(22, 35)
            
        # Logic Hardening: Education/Age Door for Specific Jobs
        # Always fix '研究生' to be realistic
        if "研究生" in job:
            if age > 35: age = self.random_int(22, 28)
            employment = "在读"
            job = "学生"
            education = "本科"
"""
text = text.replace(old_edu_age, new_edu_age)

# 2. Fix Sales taking Restaurant addresses
# In `_generate_full_address`
old_service = """            elif any(kw in job_v for kw in ["司机", "快递", "外卖", "配送", "厨师", "服务员", "营业员", "保安", "保洁", "家政", "保姆", "销售", "业务", "店员", "前台", "客服", "收银"]):
                suffix = self.random_element(["商业街", "步行街", "购物中心", "百货", "广场", "商场", "大卖场", "超市", "连锁店", "专卖店", "餐饮", "酒店", "宾馆", "旅馆", "饭店", "餐馆", "快餐", "小吃", "面馆"])"""

new_service = """            elif any(kw in job_v for kw in ["司机", "快递", "外卖", "配送", "厨师", "服务员", "营业员", "保安", "保洁", "家政", "保姆", "销售", "业务", "店员", "前台", "客服", "收银"]):
                # Distinguish a bit between pure sales and food service
                if "销售" in job_v or "业务" in job_v:
                    suffix = self.random_element(["服务中心", "大卖场", "专卖店", "门店", "营业厅", "门店", "广场", "时代广场"])
                else:
                    suffix = self.random_element(["商业街", "步行街", "购物中心", "百货", "广场", "商场", "超市", "连锁店", "餐饮", "酒店", "宾馆", "饭店", "餐馆", "快餐", "小吃", "面馆"])
"""
text = text.replace(old_service, new_service)

with open("faker_cn/__init__.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Patch4 (Third round) successful!")
