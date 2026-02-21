import json

with open('real_world_test.json', 'r', encoding='utf-8') as f:
    samples = json.load(f)

for i, p in enumerate(samples):
    print(f"[{i+1}] {p['name']} ({p['gender']}, {p['age']}岁, {p['social']['education']}, {p['social']['employment']})")
    print(f"    职业: {p['social']['job']}, 月薪: {p['social']['salary']}")
    print(f"    家乡: {p['hometown']['address']}")
    print(f"    工作地: {p['workplace']['address']}")
    print(f"    车辆: {p['asset']['vehicle_plate']}")
    print('-' * 40)
