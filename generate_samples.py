import json
from faker import Faker
from faker_cn import PersonaProvider

def generate_samples():
    # Initialize Faker with Chinese locale
    fake = Faker('zh_CN')
    
    # Add PersonaProvider
    fake.add_provider(PersonaProvider)
    
    print("="*20 + " Sample 1: Default Persona " + "="*20)
    person1 = fake.persona()
    print(json.dumps(person1, ensure_ascii=False, indent=2))
    print("\n")
    
    print("="*20 + " Sample 2: Senior Female Executive " + "="*20)
    person2 = fake.persona(
        gender='女',
        age_range=(35, 50),
        job='首席执行官 CEO'
    )
    print(json.dumps(person2, ensure_ascii=False, indent=2))
    print("\n")
    
    print("="*20 + " Sample 3: Tech Specialist (Minimal Fields) " + "="*20)
    person3 = fake.persona(
        job='高级架构师',
        fields=[
            'name',
            'gender',
            'age',
            'social.job',
            'social.salary',
            'web_home',
            'email',
            'hometown.city',
            'asset.vehicle_plate'
        ]
    )
    print(json.dumps(person3, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    generate_samples()
