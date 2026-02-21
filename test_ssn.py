from faker import Faker
from faker_cn import PersonaProvider

fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

anomalies = 0

for i in range(10):
    p = fake.persona()
    
    # 1. Extract info from SSN
    ssn = p['ssn']
    area_code = ssn[0:6]
    birth_date_str = ssn[6:14]
    seq_str = ssn[14:17]
    gender_digit = int(ssn[16])
    
    # 2. Extract info from Persona
    hometown = p['hometown']
    b_date = p['birth_date'].replace("-", "")
    gender = p['gender']
    
    # 3. Validate
    # Gender (odd for male, even for female)
    expected_is_male = gender == '男'
    actual_is_male = gender_digit % 2 != 0
    
    # Birth date
    expected_b_date = birth_date_str
    
    if expected_is_male != actual_is_male:
        print(f"Error: Gender mismatch. Persona ({gender}) vs SSN ({gender_digit})")
        anomalies += 1
        
    if b_date != expected_b_date:
        print(f"Error: Birth date mismatch. Persona ({b_date}) vs SSN ({expected_b_date})")
        anomalies += 1
        
    if i < 10:
        print(f"{p['name']} | Sex:{p['gender']} | Birth:{p['birth_date']} | Hometown:{hometown['province']}{hometown['city']}{hometown['area']}")
        print(f"SSN: {ssn} (Area:{area_code} Birth:{birth_date_str} SexCode:{gender_digit})\n")

print(f"\nTotal Anomalies in 100 samples: {anomalies}")
