import re

with open("faker_cn/__init__.py", "r", encoding="utf-8") as f:
    text = f.read()

# Logic Hardening: Education ceiling for blue-collar / basic service jobs
# We can insert this right after the existing logic hardening block.

old_edu_logic = """        # Logic Hardening: Base Education Age Floor"""

new_edu_logic = """        # Logic Hardening: Education Ceiling for Blue-Collar / Service
        blue_collar_kw = ["普工", "操作", "车间", "流水线", "装配", "纺织", "细纱", "包装", "厨师", "服务员", "营业员", "保安", "保洁", "家政", "保姆", "洗碗", "店员", "前台", "收银", "司机", "快递", "外卖", "配送", "理发", "美容", "美发", "美体", "泥瓦工", "钢筋工", "搬运", "清洁"]
        if any(kw in job for kw in blue_collar_kw):
            if education in ["博士", "硕士", "MBA"]:
                education = self.random_element(["初中", "高中", "中专", "大专", "职业技能培训"])
            elif education == "本科" and self.random_int(1, 100) > 10:  # 90% chance to downgrade Bachelors in these roles
                education = self.random_element(["初中", "高中", "中专", "大专", "职业技能培训"])
                
        # Logic Hardening: Base Education Age Floor"""
        
text = text.replace(old_edu_logic, new_edu_logic)

with open("faker_cn/__init__.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Patch5 successful!")
