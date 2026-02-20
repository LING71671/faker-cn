import json
import argparse
from faker import Faker
from faker_cn import PersonaProvider

def test_ai(api_key, image_api_key):
    print("初始化 Faker 中文和 PersonaProvider...")
    fake = Faker('zh_CN')
    fake.add_provider(PersonaProvider)
    
    config = {
        "api_key": api_key,
        "image_api_key": image_api_key
    }
    
    print("\n开始生成完全随机的人物画像并附带 AI 证件照与人生经历...")
    print("这可能需要占用几秒到一分钟的时间（等待大模型和生图 API），请耐心等待...\n")
    
    person = fake.persona(use_ai=True, ai_config=config)
    
    print("==== 生成结果 ====")
    print(json.dumps(person, ensure_ascii=False, indent=2))
    
    if "life_story" in person:
        print("\n\033[92m[成功]\033[0m 已生成由于大模型驱动的人生经历 (life_story)!")
    else:
        print("\n\033[91m[失败]\033[0m 未发现 life_story 字段。")
        
    if "avatar_url" in person:
        print(f"\n\033[92m[成功]\033[0m 已生成蓝底证件照 URL: {person['avatar_url']}")
        print("您可点击上述链接查验证件照是否满足特征 (深蓝底 #438EDB，正面免冠)。")
    else:
        print("\n\033[91m[失败]\033[0m 未发现 avatar_url (证件照) 字段。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test faker-cn AI integrations (Text & Image)")
    parser.add_argument("--api-key", required=True, help="Your DeepSeek (or OpenAI compatible) API Key")
    parser.add_argument("--image-api-key", required=True, help="Your SiliconFlow API Key")
    args = parser.parse_args()
    
    test_ai(args.api_key, args.image_api_key)
