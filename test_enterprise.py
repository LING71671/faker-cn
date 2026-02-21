from faker import Faker
from faker_cn import PersonaProvider
import time

fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

print("Starting Enterprise Demographics Test...")
found_giants = 0
found_smes = 0

with open('test_output_enterprises.txt', 'w', encoding='utf-8') as fw:
    for i in range(500):
        p = fake.persona()
        work = p['workplace']
        
        # Analyze those who are actually working
        if p['social']['employment'] in ["在职", "自由职业"] and p['social']['job'] not in ["无", "学生", "幼儿", "退休人员"]:
            comp_name = work.get('company_name', '无')
            if comp_name != "无":
                if "腾讯" in comp_name or "阿里" in comp_name or "华为" in comp_name or "字节" in comp_name or "银行" in comp_name or "网易" in comp_name or "海康威视" in comp_name:
                    found_giants += 1
                else:
                    found_smes += 1
                    
            # Sample output for observation 
            if i < 40:
                fw.write(f"[{p['social']['employment']}] {p['social']['job']} -> {comp_name} ({work.get('company_uscc', '无')})\n    地址: {work['address']}\n")

    fw.write(f"\nStats after 500 samples: Giants matched: {found_giants}, SMEs matched: {found_smes}\n")
    print(f"\nStats after 500 samples: Giants matched: {found_giants}, SMEs matched: {found_smes}")
