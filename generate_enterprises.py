import json
import random
import os

# Real Top Companies Database
REAL_GIANTS = [
    {"name": "深圳市腾讯计算机系统有限公司", "uscc": "91440300708461136T", "province": "广东", "city": "深圳市", "address": "深圳市南山区深南大道10000号腾讯大厦", "industry": "信息传输、软件和信息技术服务业"},
    {"name": "华为技术有限公司", "uscc": "91440300192203821Y", "province": "广东", "city": "深圳市", "address": "深圳市龙岗区坂田华为总部办公楼", "industry": "制造业"},
    {"name": "北京字节跳动科技有限公司", "uscc": "91110108592343242X", "province": "北京", "city": "北京市", "address": "北京市海淀区紫金数码园4号楼", "industry": "信息传输、软件和信息技术服务业"},
    {"name": "阿里巴巴（中国）有限公司", "uscc": "91330100799655058B", "province": "浙江", "city": "杭州市", "address": "杭州市滨江区网商路699号", "industry": "信息传输、软件和信息技术服务业"},
    {"name": "网易（杭州）网络有限公司", "uscc": "91330108653130541C", "province": "浙江", "city": "杭州市", "address": "杭州市滨江区长河街道网商路599号", "industry": "信息传输、软件和信息技术服务业"},
    {"name": "北京三快在线科技有限公司 (美团)", "uscc": "91110108575152342J", "province": "北京", "city": "北京市", "address": "北京市朝阳区望京东路6号望京国际研发园", "industry": "信息传输、软件和信息技术服务业"},
    {"name": "杭州海康威视数字技术股份有限公司", "uscc": "9133000073600620X", "province": "浙江", "city": "杭州市", "address": "杭州市滨江区阡陌路555号", "industry": "制造业"},
    {"name": "中国工商银行股份有限公司", "uscc": "91100000100003962T", "province": "北京", "city": "北京市", "address": "北京市西城区复兴门内大街55号", "industry": "金融业"},
    {"name": "中国建设银行股份有限公司", "uscc": "911000001000044477", "province": "北京", "city": "北京市", "address": "北京市西城区金融大街25号", "industry": "金融业"},
    {"name": "国家电网有限公司", "uscc": "91110000710920838N", "province": "北京", "city": "北京市", "address": "北京市西城区西长安街86号", "industry": "电力、热力、燃气及水生产和供应业"},
    {"name": "中国石油天然气集团有限公司", "uscc": "91110000100010433L", "province": "北京", "city": "北京市", "address": "北京市东城区东直门北大街9号", "industry": "采矿业"},
    {"name": "中国移动通信集团有限公司", "uscc": "91110000710925032P", "province": "北京", "city": "北京市", "address": "北京市西城区金融大街29号", "industry": "信息传输、软件和信息技术服务业"},
    {"name": "上海汽车集团股份有限公司", "uscc": "91310000132260250X", "province": "上海", "city": "上海市", "address": "上海市静安区威海路489号", "industry": "制造业"},
    {"name": "中国平安保险（集团）股份有限公司", "uscc": "91440300192189148B", "province": "广东", "city": "深圳市", "address": "深圳市福田区益田路5033号平安金融中心", "industry": "金融业"},
    {"name": "招商银行股份有限公司", "uscc": "9144030010001686XA", "province": "广东", "city": "深圳市", "address": "深圳市福田区深南大道7088号招商银行大厦", "industry": "金融业"},
    {"name": "格力电器股份有限公司", "uscc": "91440400192548256N", "province": "广东", "city": "珠海市", "address": "珠海市前山金鸡西路", "industry": "制造业"},
    {"name": "美的集团股份有限公司", "uscc": "91440606722473344C", "province": "广东", "city": "佛山市", "address": "佛山市顺德区北滘镇美的大道6号", "industry": "制造业"},
    {"name": "比亚迪股份有限公司", "uscc": "91440300192317458F", "province": "广东", "city": "深圳市", "address": "深圳市坪山新区比亚迪路3009号", "industry": "制造业"},
    {"name": "内蒙古伊利实业集团股份有限公司", "uscc": "91150000114093082R", "province": "内蒙古", "city": "呼和浩特市", "address": "呼和浩特市金川开发区金四路8号", "industry": "制造业"},
    {"name": "贵州茅台酒股份有限公司", "uscc": "91520000714304481T", "province": "贵州", "city": "遵义市", "address": "贵州省仁怀市茅台镇", "industry": "制造业"}
]

INDUSTRY_MAP = {
    "IT/软件": ["信息系统", "软件技术", "网络科技", "数字科技", "云数据", "智能科技", "信息技术", "互联网服务"],
    "商贸/批发": ["贸易", "百货", "商贸", "进出口", "物资", "供应链", "贸易发展"],
    "制造/工业": ["制造", "机械", "精密仪器", "科技", "五金", "塑胶", "新材料", "电子科技", "服装", "纺织"],
    "建筑/地产": ["建筑工程", "建设", "房地产开发", "装饰工程", "工程", "建设集团"],
    "餐饮/住宿": ["餐饮管理", "大酒店", "饮食", "酒楼", "餐饮服务", "食品"],
    "文体/教育": ["教育科技", "文化传媒", "文化传播", "影视传媒", "体育发展", "娱乐"]
}

USCC_CHARS = "0123456789ABCDEFGHJKLMNPQRTUWXY"
def generate_uscc(prov_code):
    # gb32100 logic simulation
    org_type = random.choice(["91", "92", "93"]) # 91: enterprise, 92: individual, 93: farmer coop
    area_code = str(prov_code) + str(random.randint(10,99)) + str(random.randint(10,99))
    org_code = "".join(random.choices(USCC_CHARS, k=9))
    pre_checksum = org_type + area_code + org_code
    # Calculate checksum
    W = [1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]
    checksum = 0
    for i, char in enumerate(pre_checksum):
        checksum += USCC_CHARS.index(char) * W[i]
    mod = checksum % 31
    check_char = USCC_CHARS[31 - mod] if mod != 0 else '0'
    return pre_checksum + check_char

def generate_sme_database(prov_name, prov_code, city_list, count):
    res = []
    for _ in range(count):
        ind_category = random.choice(list(INDUSTRY_MAP.keys()))
        suf = random.choice(["有限公司", "有限责任公司", "股份有限公司", "合伙企业"])
        corp_kw = random.choice(INDUSTRY_MAP[ind_category])
        brand_str = "".join(random.choices("泰星阳华耀鑫源信光宏瑞祥丰顺伟昌成康盛聚发联利科", k=2))
        
        city_name = random.choice(city_list)
        comp_name = f"{city_name}{brand_str}{corp_kw}{suf}"
        uscc = generate_uscc(prov_code)
        
        # approximate strict industry mapping based on National Standards
        if ind_category == "IT/软件": real_ind = "信息传输、软件和信息技术服务业"
        elif ind_category == "商贸/批发": real_ind = "批发和零售业"
        elif ind_category == "制造/工业": real_ind = "制造业"
        elif ind_category == "建筑/地产": real_ind = "建筑业"
        elif ind_category == "餐饮/住宿": real_ind = "住宿和餐饮业"
        else: real_ind = "文化、体育和娱乐业"
            
        res.append({
            "name": comp_name,
            "uscc": uscc,
            "province": prov_name,
            "city": city_name,
            "address": "", 
            "industry": real_ind
        })
    return res

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from faker_cn.data import areas
    
    db = {"_giants": REAL_GIANTS, "_sme": {}}
    
    prov_dict = {}
    for p in areas:
        p_name = p['name'].replace("省", "").replace("市", "").replace("自治区", "").replace("壮族", "").replace("回族", "").replace("维吾尔", "")
        prov_dict[p_name] = {"code": "11", "cities": []} # Code fallback
        for c in p.get('children', [p]):
            prov_dict[p_name]["cities"].append(c['name'])
            
    # Base GB2260 manual mappings for correct social credit prefix
    gb_map = {"北京":11, "天津":12, "河北":13, "山西":14, "内蒙古":15, "辽宁":21, "吉林":22, "黑龙江":23, "上海":31, "江苏":32, "浙江":33, "安徽":34, "福建":35, "江西":36, "山东":37, "河南":41, "湖北":42, "湖南":43, "广东":44, "广西":45, "海南":46, "重庆":50, "四川":51, "贵州":52, "云南":53, "西藏":54, "陕西":61, "甘肃":62, "青海":63, "宁夏":64, "新疆":65}
    
    for p_name, p_data in prov_dict.items():
        if p_name not in gb_map: continue
        count = 1000
        if p_name in ["广东", "江苏", "山东", "浙江", "上海", "北京"]: count = 3000
        elif p_name in ["西藏", "青海", "宁夏", "海南"]: count = 300
        
        db["_sme"][p_name] = generate_sme_database(p_name, gb_map[p_name], p_data["cities"], count)
        
    os.makedirs("faker_cn/data", exist_ok=True)
    with open("faker_cn/data/enterprises.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
        
    print("enterprises.json generated successfully. Size: {:.2f} MB".format(os.path.getsize("faker_cn/data/enterprises.json") / 1024 / 1024))
