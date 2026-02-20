from faker import Faker
from faker_cn import PersonaProvider

fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

print("测试 web_home 逻辑验证采样：")
for i in range(20):
    p = fake.persona()
    job = p['social']['job']
    web = p['internet']['web_home']
    print(f"[{i+1:2}] 职业: {job:15} | WebHome: {web}")
