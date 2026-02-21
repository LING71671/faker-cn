import json

with open('real_world_test.json', 'r', encoding='utf-8') as f:
    samples = json.load(f)

with open('samples_output.txt', 'w', encoding='utf-8') as out:
    for i, p in enumerate(samples):
        name = p['name']
        gender = p['gender']
        age = p['age']
        edu = p['social']['education']
        emp = p['social']['employment']
        job = p['social']['job']
        salary = p['social']['salary']
        home = p['hometown']['address']
        work = p['workplace']['address']
        plate = p['asset']['vehicle_plate']
        
        out.write(f"[{i+1}] {name} ({gender}, {age}岁, {edu}, {emp})\n")
        out.write(f"    职业: {job}, 月薪: {salary}\n")
        out.write(f"    家乡: {home}\n")
        out.write(f"    工作地: {work}\n")
        out.write(f"    车辆: {plate}\n")
        out.write("-" * 40 + "\n")
