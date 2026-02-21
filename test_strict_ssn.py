from faker import Faker
from faker_cn import PersonaProvider
from datetime import date

fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

print("Starting Strict SSN Validation Tests...\n")

# Test 1: Full specification
print("Test 1: Full specification (Beijing Xicheng, Male, 1990-01-01)")
ssn = fake.strict_ssn(
    hometown_province="北京",
    hometown_city="北京",
    hometown_area="西城",
    gender="M",
    birth_date=date(1990, 1, 1)
)
print(f"Result: {ssn}\nVerified? {ssn.startswith('11010219900101') and int(ssn[16]) % 2 != 0}\n")
assert ssn.startswith('11010219900101'), "Area or Date code mismatch"
assert int(ssn[16]) % 2 != 0, "Gender code mismatch"

# Test 2: Only specify Province (Fallback engine should handle the rest properly)
print("Test 2: Only Province (Guangdong)")
ssn = fake.strict_ssn(hometown_province="广东")
print(f"Result: {ssn}\nVerified? {ssn.startswith('44')}\n")
assert ssn.startswith('44'), "Province code mismatch"

# Test 3: Only specify Gender and Age Range
print("Test 3: Female, aged between 10-15")
ssn = fake.strict_ssn(gender="女", age_range=(10, 15))
birth_year = int(ssn[6:10])
current_year = date.today().year
print(f"Result: {ssn}\nVerified? {10 <= current_year - birth_year <= 15 and int(ssn[16]) % 2 == 0}\n")
assert 10 <= current_year - birth_year <= 15, "Age range constraint failed"
assert int(ssn[16]) % 2 == 0, "Gender code constraint failed"

# Test 4: Completely random empty call (should still be 100% mathematically valid)
print("Test 4: No parameters specified (Random generation)")
ssn = fake.strict_ssn()
print(f"Result: {ssn}")

def validate_checksum(ssn_val):
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_code = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    sum_val = sum(int(ssn_val[i]) * weight[i] for i in range(17))
    return check_code[sum_val % 11] == ssn_val[17]

print(f"Checksum Valid? {validate_checksum(ssn)}")
assert validate_checksum(ssn), "Mathematical Checksum verification failed"

print("\nALL TESTS PASSED SUCCESSFULLY.")
