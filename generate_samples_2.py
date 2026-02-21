import json
import sys
from faker import Faker
from faker_cn import PersonaProvider

fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

samples = []
for _ in range(20):
    samples.append(fake.persona())

with open('samples_output_2.txt', 'w', encoding='utf-8') as out:
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

print("Done generating 20 samples.")
