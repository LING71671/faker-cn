import json
from faker import Faker
from faker_cn import PersonaProvider

fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

# Test older traditional name
print("--- 60-year-old ---")
p1 = fake.persona(age_range=(60, 65))
print(json.dumps(p1, ensure_ascii=False, indent=2))

# Test young modern name
print("\n--- 15-year-old ---")
p2 = fake.persona(age_range=(15, 18))
print(json.dumps({k: v for k, v in p2.items() if k in ['name', 'asset', 'email', 'internet', 'social']}, ensure_ascii=False, indent=2))

print("\n--- High salary exec ---")
p3 = fake.persona(job="架构师", age_range=(35, 45))
print(json.dumps({k: v for k, v in p3.items() if k in ['name', 'social', 'asset', 'internet']}, ensure_ascii=False, indent=2))

print("\n--- Student ---")
p4 = fake.persona(employment="在读", age_range=(18, 22))
print(json.dumps({k: v for k, v in p4.items() if k in ['name', 'social', 'asset', 'internet']}, ensure_ascii=False, indent=2))
