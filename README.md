# faker-cn

`faker-cn` 是官方原版 [Python Faker](https://github.com/joke2k/faker) 的完全独立第三方提供者 (Provider)。
> **注意**：本项目作为原生扩展独立运行，与任何修改了 Faker 源码且未提交 PR 的个人魔改版**均无关联**，您可以直接在官方标准版的 Faker 环境中无缝挂载使用。

它专门针对中国大陆身份数据进行了高精度的严谨构造和校验，最初从强大的 [faker-plus](https://github.com/LING71671/faker-plus) 命令行工具底层剥离抽出，现作为核心数据生成引擎独立维护。

## 🎯 核心能力
与官方 Faker 默认的随机字符串拼凑不同，`faker-cn` 专注于数据的**强社会逻辑自洽**：
- **真正的18位身份证**：严格遵循 GB11643-1999 校验码算法生成（Mod 11-2），前 6 位与生成的出生地完全对应。
- **全要素行政区划大字典**：内置了超大规模的真实中国省市区划与对应的真实**邮政编码**信息。
- **智能就业状态闭环**：退休者匹配合法年龄、初中生不会变成高管、星探/CEO仅占据 2% 低概率。
- **动态属性自洽**：基于年龄拟合真实身高体重区间；MBTI、薪水锚定学历职业；主卡手机号归属地严格等于户籍地。
- **全量字段一键提取**：支持多层级嵌套路径（如 `hometown.postcode`，`primary_phone.number`）的内存级极净提取。

## 📦 安装

此库专为 Python 开发者和数据科学家设计。

```bash
pip install faker-cn
```

## 🚀 快速开始

将 `PersonaProvider` 挂载到标准的 `Faker` 实例上：

```python
import json
from faker import Faker
from faker_cn import PersonaProvider

# 1. 初始化 Faker
fake = Faker('zh_CN')
fake.add_provider(PersonaProvider)

# 2. 基础生成 (包含基本信息、户籍、工作、账号库)
p = fake.persona()
print(p['name'])
print(p['ssn'])

# 3. 指定条件生成
# 生成一名 28岁的男性大专生，仅返回纯净指定的深层字段组合
p_mini = fake.persona(
    gender='男', 
    age_range=(28, 28), 
    education='大专',
    fields=['name', 'age', 'social.education', 'social.job']
)
print(json.dumps(p_mini, ensure_ascii=False, indent=2))
```

## 🛠️ 数据字典更新
内部集成的中国地名与区划可能随政策变更。你可以使用仓库自带脚本重新聚合本地数据：
```bash
python build_dicts.py
```

## 协议
[GPL-3.0 License](LICENSE)
