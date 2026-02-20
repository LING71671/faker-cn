# faker-cn: 中国大陆高保真虚拟数据生成引擎

`faker-cn` 是官方原版 [Python Faker](https://github.com/joke2k/faker) 的完全独立第三方提供者 (Provider)。
> **注意**：本项目作为原生扩展独立运行，与任何修改了 Faker 源码且未提交 PR 的个人魔改版**均无关联**，您可以直接在官方标准版的 Faker 环境中无缝挂载使用。

它专门针对中国大陆身份数据进行了**高精度的严谨构造和校验**。所有的设定不仅为了“随机字符串”，更是为了实现社会逻辑的**绝对自洽**。

---

## � 核心独家特性 (Why faker-cn?)

区别于传统的随机生成，`faker-cn` 注入了大量符合现实国情的逻辑判断：

1. **具有时代感的姓名 (Era-based Probabilistic Names)**
   - 抛弃生硬的穷举。70后有 50% 概率叫“建军、淑兰”；10后有超 90% 的概率叫“子涵、宇轩”。姓名分布严格吻合年代缩影。
2. **逻辑自洽的财产与车辆 (Contextual Assets & Vehicle Plates)**
   - 模拟真实 25% 车主比例，车主身份与**年龄（25-55岁）和月薪（>15k概率极高）强绑定**。
   - **真实人生轨迹的车牌**：车牌前缀 60% 落实在工作地，30% 落实在户籍地，10% 模拟在教育大省（如湖北、江苏）上牌。更有 15% 的几率生成新能源绿牌（带 D/F 标识）。
3. **特化的国内网络足迹 (Digital Footprint Dynamics)**
   - **分层的主力邮箱**：年轻人（<25岁）大量分配 `@qq.com`；中年及职场人多为 `@163.com`。
   - **拒绝盲目的 Gmail**：只有“程序员、高管、外贸、科学家”等涉外强相关职业，才有几率生成 `gmail.com`。
   - **逻辑自洽的个人主页 (WebHome)**：不再盲目生成 URL。**只有计算机/互联网相关从业者**（程序员、架构师等）才会分配个人主页（如 `github.io` 或 `.me`），且域名与用户名严格锁定。其余行业人员默认为“无”。
   - **专属 Yopmail 临时邮箱**：每个人物都会携带一个 `yopmail` 邮箱及一键直达链接 (`yopmail_url`)。
   - **基于画像的设备拟合**：根据收入动态分配设备。高层管理分配 macOS/iOS 概率更高，普通岗位则覆盖 Windows 11 与 Android 14。
4. **AI 赋能：人生轨迹与超写实证件照 (AI-Powered Stories & Realism Photos)**
   - **自动化人生长卷**：接入人工智能（DeepSeek/OpenAI 等），根据字段自动编写逻辑自洽的人物生平。
   - **超写实 3:4 蓝底证件照**：通过生图引擎生成**符合 3:4 比例**、**极其写实（真人类质感）**的正面免冠蓝底证件照（色码：`#438EDB`）。
5. **硬核的底层规则校验**
   - **完美的身份证生成**：18位全准，严格 GB11643-1999 校验码算法（Mod 11-2），前 6 位与生成的出生地**分毫不差**。
   - 带有内置的高准度中国行政区划字典。

---

## 📦 保姆级安装指南

本库专为 Python 开发者和测试工程师设计，推荐在 Python 3.7+ 的环境中使用。

**1. 安装原生 Faker 和本项目：**
```bash
pip install Faker faker-cn
```

**2. 在代码中无缝接入：**
```python
import json
from faker import Faker
from faker_cn import PersonaProvider

# 第一步：初始化官方的 Faker（指定语言为中文）
fake = Faker('zh_CN')

# 第二步：将我们强大的 faker-cn 引擎挂载进去
fake.add_provider(PersonaProvider)
```

就是这么简单！您已经解锁了最高级别的虚拟数据生成能力。

---

## 🚀 保姆级使用教程

### 场景一：一键生成一个完整的“真实人类”
当你不传入任何参数时，`faker-cn` 会像上帝掷骰子一样，完全随机但又极其严谨地捏造一个完整的人生长卷。

```python
# 生成完整的人物档案字典
person = fake.persona()

print(f"姓名: {person['name']}, 身份证: {person['ssn']}")
print(f"他/她的主邮箱是: {person['email']}")
print(f"你还能直接去查看他的收件箱 (Yopmail): {person['yopmail_url']}")
print(f"他的车牌号是: {person['asset']['vehicle_plate']}")
print(f"他有 {person['asset']['deposit']} 存款")
```

### 场景二：我想接入人工智能 (人生轨迹+证件照)
如果你填入了 AI 的 API 密钥，`faker-cn` 将摇身一变为“赛博造物主”，为你补充照片和生平。

```python
# 传入您的 AI keys
ai_config = {
    "api_key": "您的_DeepSeek_密钥",
    "image_api_key": "您的_SiliconFlow_密钥" # 用于生成蓝底证件照
}

person = fake.persona(use_ai=True, ai_config=ai_config)

print(f"人生经历: {person['life_story']}")
print(f"证件照 URL: {person['avatar_url']}")
```

### 场景三：我想定制特定的人设（按需生成）
比如，你正在测试一个只针对年轻女性高端用户的系统功能，你可以这样写：

```python
# 生成一名 22-26岁，高管/外贸相关，北京户口的女性
custom_person = fake.persona(
    gender='女', 
    age_range=(22, 26), 
    job='跨国企业高管'
)
print(json.dumps(custom_person, ensure_ascii=False, indent=2))
```
你会惊奇地发现，由于设定了“跨国高管”且年龄较轻：
- 她的邮箱极有可能是 `gmail.com` 或高端企业邮箱。
- 设备参数 (`os`, `user_agent`) 大概率会是最新版 iPhone 或 Mac。
- 薪水数字被动态拉高。

### 场景三：极简模式（我只要特定的某几个字段）
在做大批量写入数据库的压力测试时，你可能不需要巨大的完整字典集，只要几个关键字段。可以利用 `fields` 参数，支持**深层嵌套提取**！

```python
mini_person = fake.persona(
    gender='男',
    fields=[
        'name',                     # 姓名
        'social.education',         # 学历 (原样在 social 字典里)
        'hometown.city',            # 老家的城市
        'temp_email_url',           # 仅提取临时邮箱直达车
        'asset.vehicle_plate'       # 深层嵌套：仅要车牌号
    ]
)
print(mini_person)
# 输出示例: {'name': '张伟', 'education': '本科', 'city': '南京市', 'temp_email_url': '...', 'vehicle_plate': '苏A·829F5'}
```

---

## 📖 返回字段全景字典 (Data Structure)

调用 `fake.persona()` 默认返回的完整 JSON 结构如下，包含四大核心模块：基础信息、户口与常驻地、社会身份与账号、资金与资产。

| 主字段 (Root Key) | 类型 | 说明 |
| :--- | :--- | :--- |
| `name` | String | 姓名（附带时代感概率分布） |
| `life_story` | String | **(AI 特有)** 自动生成的人生轨迹故事 |
| `avatar_url` | String | **(AI 特有)** 自动生成的 AI 蓝底证件照 URL |
| `gender` | String | 性别（男/女） |
| `age` | Int | 年龄 |
| `birth_date` | String | 出生年月日（YYYY-MM-DD，跟身份证完全吻合） |
| `ssn` | String | 完美的 18 位大陆身份证号 |
| `email` | String | 常规主邮箱（年轻人偏 QQ，高阶偏 Gmail/163） |
| `yopmail` / `yopmail_url` | String | **神器**：必定生成的一个 Yopmail 邮箱及一键直达浏览器的收看链接 |
| `username` / `password` | String | 用户名与密码 |
| `web_home` | String | **逻辑分配**：仅限 IT 行业人员的个人主页 URL，其余人员为“无” |
| `os` / `user_agent` | String | 随工资浮动的电脑/手机设备系统与 UA |
| `hometown` | Dict | **户籍信息** (包含 `province`, `city`, `district`, `postcode` 以及原生地坐标 `geo`) |
| `primary_phone` | Dict | **主手机号** (归属地严格绑定 `hometown` 相同) |
| `workplace` | Dict | **常驻工作地** (同样包含完整的省市区街道路、邮编、经纬度) |
| `social` | Dict | **社会背景** (包含 `education` 教育程度, `job` 职位, `salary` 薪水, `mbti` 人格, `blood_type` 血型等) |
| `asset` | Dict | **资产信息** (包含 `bank_card` 银行卡号, `deposit` 存款预估, `vehicle_plate` 具有轨迹逻辑的车牌号等) |

---

## 🛠️ 数据字典更新维护
内部集成的中国地名与区划等统计数据可能随物理世界政策变更。你可以使用仓库自带脚本重新抓取、聚合本地数据：
```bash
python build_dicts.py
```

## 📜 协议声明 (License)
本项目拥抱开源，采用 **[GPL-3.0 License](LICENSE)** 进行分发。您可以自由使用、修改与研究。
