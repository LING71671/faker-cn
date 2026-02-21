import sys
import json
import traceback
from datetime import datetime
from faker import Faker
from faker_cn import PersonaProvider

def check_logic(p):
    errors = []
    
    try:
        age = p['age']
        edu = p['social']['education']
        emp = p['social']['employment']
        job = p['social']['job']
        salary = p['social']['salary']
        workplace_addr = p['workplace']['address']
        plate = p['asset']['vehicle_plate']
        ssn = p['ssn']
        bd = p['birth_date']
        
        # 1. Age vs Education
        if age < 18 and edu in ["大专", "本科", "硕士", "博士", "MBA"]:
            errors.append(f"Age {age} is too young for {edu}")
        if age < 6 and edu not in ["幼儿", "无", "早教"]:
            errors.append(f"Age {age} should not have education '{edu}'")
            
        # 2. Age vs Employment
        if age < 16 and emp not in ["在读", "幼儿", "无"]:
            errors.append(f"Age {age} is illegal child labor, employment: {emp}, job: {job}")
            
        # 3. Employment / Job Matching
        if emp in ["在读", "全职学生"]:
            if job not in ["无", "学生", "幼儿"]:
                errors.append(f"Employment is '{emp}' but has job '{job}'")
            if salary != "￥0":
                errors.append(f"Student has salary '{salary}'")
            if workplace_addr != "无":
                errors.append(f"Student has workplace address '{workplace_addr}'")
                
        if emp in ["待业", "待就业", "无业"]:
            if job != "无":
                errors.append(f"Unemployed has job '{job}'")
            if salary != "￥0":
                errors.append(f"Unemployed has salary '{salary}'")
            if workplace_addr != "无":
                errors.append(f"Unemployed has workplace address '{workplace_addr}'")
                
        if emp == "退休":
            if job not in ["无", "退休人员", "退休"]:
                errors.append(f"Retired has job '{job}'")
            if salary == "￥0":
                pass # Retired people might have ￥0 or a pension
            if workplace_addr != "无":
                errors.append(f"Retired has workplace address '{workplace_addr}'")
                
        if emp in ["在职", "自由职业"]:
            if job in ["无", "学生", "幼儿", "退休人员"]:
                errors.append(f"Employed ({emp}) but no real job: '{job}'")
            if salary == "￥0":
                errors.append(f"Employed has salary '{salary}'")
            if emp == "在职" and workplace_addr == "无":
                errors.append(f"Formal employed but no workplace address")
                
        # 4. Vehicles
        if age < 18 and plate != "无":
            errors.append(f"Underage {age} has vehicle plate '{plate}'")
            
        # 5. SSN matching Birthday
        if bd.replace("-", "") not in ssn:
            errors.append(f"Birth date {bd} mismatch with SSN {ssn}")

        # 6. Web Home Logic
        is_tech = any(kw in job for kw in ["架构师", "程序员", "开发", "IT", "互联网", "软件", "系统", "算法", "后端", "前端", "网络"])
        web_home = p['internet']['web_home']
        if not is_tech and web_home != "无":
            errors.append(f"Non-tech job '{job}' has a web home '{web_home}'")
            
    except Exception as e:
        errors.append(f"Exception during validation: {str(e)}\n{traceback.format_exc()}")

    return errors

def run_test_round():
    fake = Faker('zh_CN')
    fake.add_provider(PersonaProvider)
    
    all_errors = []
    sample_records = []
    
    for i in range(100):
        try:
            p = fake.persona()
        except Exception as e:
            all_errors.append({"name": f"Item {i}", "errors": [f"Exception during generation: {str(e)}"], "persona": {}})
            continue
            
        sample_records.append(p)
        errs = check_logic(p)
        if errs:
            all_errors.append({"name": p.get('name', f"Item {i}"), "errors": errs, "persona": p})
            
    return all_errors, sample_records

if __name__ == "__main__":
    errors, samples = run_test_round()
    
    # Always save samples to review
    with open('marathon_samples.json', 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
        
    if errors:
        print(f"FOUND ERRORS IN {len(errors)} OUT OF 100 SAMPLES:")
        for e in errors:
            print(f"- {e['name']}:")
            for msg in e['errors']:
                print(f"  * {msg}")
        # Save errors to detail log
        with open('marathon_errors.json', 'w', encoding='utf-8') as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
        sys.exit(1)
    else:
        print("NO ERRORS FOUND in this round of 100 samples.")
        sys.exit(0)
