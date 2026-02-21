import re

with open("faker_cn/__init__.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Enhance Job Reality Check in persona()
old_job_hardening = """        # Logic Hardening: Education/Age Door for Specific Jobs
        if any(kw in job for kw in ["总", "CEO", "总裁", "主任"]):
            if age < 30: age = 30 + (age % 10) # Enforce age
            if education in ["幼儿", "小学", "初中", "高中", "中专", "大专"]: 
                education = self.random_element(["本科", "硕士", "MBA"])
        if any(kw in job for kw in ["架构师", "专家", "研究员", "科学家"]):
            if education in ["幼儿", "小学", "初中", "高中", "中专", "大专"]:
                education = self.random_element(["本科", "硕士", "博士"])"""

new_job_hardening = """        # Logic Hardening: Education/Age Door for Specific Jobs
        # Always fix '研究生' to be realistic
        if "研究生" in job:
            if age > 35: age = self.random_int(22, 28)
            employment = "在读"
            job = "学生"
            education = "本科"
        
        # Specific high-end jobs require older age and higher education
        if any(kw in job for kw in ["总", "CEO", "总裁", "主任", "总监", "经理"]):
            if age < 25: age = self.random_int(26, 45)
            if education in ["幼儿", "小学", "初中", "高中", "中专", "大专", "职业技能培训"]: 
                education = self.random_element(["本科", "硕士", "MBA"])
                
        if any(kw in job for kw in ["架构师", "专家", "研究员", "科学家", "教授", "算法"]):
            if age < 28: age = self.random_int(28, 50)
            if education in ["幼儿", "小学", "初中", "高中", "中专", "大专", "职业技能培训"]:
                education = self.random_element(["本科", "硕士", "博士"])
                
        if any(kw in job for kw in ["工程师", "开发", "程序员"]):
            if age < 22: age = self.random_int(22, 40)
            if education in ["幼儿", "小学", "初中"]:
                education = self.random_element(["大专", "本科"])
"""
text = text.replace(old_job_hardening, new_job_hardening)

# 2. Add freelance address support and fix the general 'else' address in _generate_full_address

# We need to pass `employment` to _generate_full_address
text = text.replace(
    "def _generate_full_address(self, p_data, c_data, a_data, villages, f_urban=False, job=None):",
    "def _generate_full_address(self, p_data, c_data, a_data, villages, f_urban=False, job=None, employment=None):"
)

text = text.replace(
    "workplace_data = self._generate_full_address(wp_data, wc_data, wa_data, villages, f_urban=is_high_end, job=job)",
    "workplace_data = self._generate_full_address(wp_data, wc_data, wa_data, villages, f_urban=is_high_end, job=job, employment=employment)"
)

# Replace the specific else logic in _generate_full_address
# Find the else block for workplace
old_else_block = """            else:
                b_estate = self.random_element(["人民政府", "教育局", "公安局", "税务局", "工商局", "建设局", "环保局", "文化局", "卫健委", "发改委", "民政局", "财政局", "居委会", "街道办事处", "派出所", "法院", "检察院", "交警大队", "消防大队", "广播电视台", "报社"])
                if any(kw in b_estate for kw in ["局", "委", "政府", "处", "所", "院", "大队"]): b_estate = f"{c_data['name']}{a_data['name']}{b_estate}"
                r_name = self.random_element(["朝阳", "建设", "胜利", "解放", "中山", "人民", "新华", "和平", "文化", "青年", "红星", "光明", "幸福", "团结", "前进", "东风", "红旗", "五一", "八一", "长安", "北京", "南京", "广州", "上海", "政法", "府前", "广场"]) + self.random_element(["路", "街", "大道"])
                full_street = f"{t_n}{r_name}{self.random_int(1,200)}号{b_estate}"
"""

new_else_block = """            else:
                if employment == "自由职业":
                    # Freelancers work at home, cafes, workspaces
                    b_estate = self.random_element(["创客空间", "共享办公", "SOHO", "咖啡厅", "工作室", "公寓", "社区"])
                    c_name = self.random_element(["星巴克", "瑞幸", "漫咖啡", "WeWork", "优客工场", "左岸", "时光", "理想", "阳光", "世纪"])
                    if b_estate in ["工作室", "公寓", "社区"]:
                        e_suffix = self.random_element(["小区", "花园", "苑", "家园", "新村"])
                        b_estate = f"{self.random_element(['阳光', '时代', '世纪', '滨江', '华府'])}{e_suffix}"
                    else:
                        b_estate = f"{c_name}{b_estate}"
                    r_name = self.random_element(["朝阳", "建设", "中山", "人民", "新华", "创业", "创新"]) + self.random_element(["路", "街"])
                    full_street = f"{t_n}{r_name}{self.random_int(1,200)}号{b_estate}"
                elif any(kw in job_v for kw in ["公务员", "行政", "局", "委", "办", "政府", "事业", "书记"]):
                    b_estate = self.random_element(["人民政府", "教育局", "公安局", "税务局", "工商局", "建设局", "环保局", "文化局", "卫健委", "发改委", "民政局", "财政局", "居委会", "街道办事处", "派出所", "法院", "检察院", "交警大队", "消防大队"])
                    if any(kw in b_estate for kw in ["局", "委", "政府", "处", "所", "院", "大队"]): b_estate = f"{c_data['name']}{a_data['name']}{b_estate}"
                    r_name = self.random_element(["朝阳", "建设", "胜利", "解放", "中山", "人民", "新华", "政法", "府前", "民主"]) + self.random_element(["路", "街", "大道"])
                    full_street = f"{t_n}{r_name}{self.random_int(1,200)}号{b_estate}"
                else:
                    # General white-collar / commercial for unmatched jobs
                    suffix = self.random_element(["大厦", "写字楼", "商务中心", "商办大楼", "大楼", "国贸"])
                    c_name = self.random_element(["时代", "卓越", "绿城", "万象", "金融", "财富", "环球", "恒丰", "嘉里", "宝龙", "银泰", "万达"])
                    b_estate = f"{c_name}{suffix}"
                    r_name = self.random_element(["北京", "南京", "中山", "解放", "建国", "复兴", "和平", "新华", "人民"]) + self.random_element(["路", "街", "大道"])
                    full_street = f"{t_n}{r_name}{self.random_int(1,200)}号{b_estate}{self.random_int(1,30)}层{self.random_int(1,20)}0{self.random_int(1,9)}室"
"""
text = text.replace(old_else_block, new_else_block)

with open("faker_cn/__init__.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Patch3 successful!")
