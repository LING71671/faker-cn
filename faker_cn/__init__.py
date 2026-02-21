import json
import os
import random
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
from textwrap import dedent

from faker.providers import BaseProvider


class PersonaProvider(BaseProvider):
    """
    Provider for generating a logically consistent Chinese Persona.
    """
    _enterprises_db = None

    def _load_enterprises(self):
        if self.__class__._enterprises_db is None:
            db_path = os.path.join(os.path.dirname(__file__), 'data', 'enterprises.json')
            if os.path.exists(db_path):
                with open(db_path, 'r', encoding='utf-8') as f:
                    self.__class__._enterprises_db = json.load(f)
            else:
                self.__class__._enterprises_db = {"_giants": [], "_sme": {}}
        return self.__class__._enterprises_db

    _areas_data = None
    _phones_data = None
    _postcodes_data = None
    _villages_data = None
    _pinyin_map = {
        "王": "wang", "李": "li", "张": "zhang", "刘": "liu", "陈": "chen",
        "杨": "yang", "黄": "huang", "赵": "zhao", "吴": "wu", "周": "zhou",
        "徐": "xu", "孙": "sun", "马": "ma", "朱": "zhu", "胡": "hu",
        "林": "lin", "郭": "guo", "何": "he", "高": "gao", "罗": "luo",
        "郑": "zheng", "梁": "liang", "谢": "xie", "唐": "tang", "宋": "song",
        "韩": "han", "曹": "cao", "许": "xu", "邓": "deng", "萧": "xiao",
        "冯": "feng", "曾": "zeng", "程": "cheng", "蔡": "cai", "潘": "pan",
        "袁": "yuan", "于": "yu", "董": "dong", "余": "yu", "苏": "su",
        "叶": "ye", "吕": "lv", "魏": "wei", "蒋": "jiang", "田": "tian",
        "杜": "du", "丁": "ding", "沈": "shen", "姜": "jiang", "范": "fan",
        "军": "jun", "国": "guo", "建": "jian", "华": "hua", "平": "ping",
        "伟": "wei", "强": "qiang", "勇": "yong", "明": "ming", "涛": "tao",
        "英": "ying", "华": "hua", "秀": "xiu", "珍": "zhen", "娟": "juan"
    }

    def _filter_by_fields(self, data: dict, fields: list) -> dict:
        """
        根据用户指定的 fields 列表过滤生成的画像字典，支持诸如 'hometown.postcode' 等嵌套路径。
        """
        filtered_p = {}
        for f in fields:
            f = f.strip()
            if not f:
                continue
            
            parts = f.split('.')
            current_src = data
            current_dest = filtered_p
            
            valid = True
            for i, part in enumerate(parts):
                if isinstance(current_src, dict) and part in current_src:
                    if i == len(parts) - 1:
                        current_dest[part] = current_src[part]
                    else:
                        if part not in current_dest:
                            current_dest[part] = {}
                        current_dest = current_dest[part]
                        current_src = current_src[part]
                else:
                    valid = False
                    break
        return filtered_p

    @classmethod
    def _load_areas(cls) -> List[Dict]:
        if cls._areas_data is None:
            path = os.path.join(os.path.dirname(__file__), 'areas.json')
            with open(path, 'r', encoding='utf-8') as f:
                cls._areas_data = json.load(f)
        return cls._areas_data

    @classmethod
    def _load_phones(cls) -> Dict:
        if cls._phones_data is None:
            path = os.path.join(os.path.dirname(__file__), 'phones.json')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    cls._phones_data = json.load(f)
            except FileNotFoundError:
                cls._phones_data = {}
        return cls._phones_data

    @classmethod
    def _load_postcodes(cls):
        if cls._postcodes_data is None:
            import os, json
            path = os.path.join(os.path.dirname(__file__), "postcodes.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                index = {}
                for pc, addr in raw_data.items():
                    index[addr] = pc
                cls._postcodes_data = index
            else:
                cls._postcodes_data = {}
        return cls._postcodes_data

    @classmethod
    def _load_villages(cls) -> Dict:
        if cls._villages_data is None:
            import gzip
            path = os.path.join(os.path.dirname(__file__), 'villages.json.gz')
            try:
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    cls._villages_data = json.load(f)
            except FileNotFoundError:
                cls._villages_data = {}
        return cls._villages_data

    def _ssn_checksum(self, s):
        weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_code = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        sum_val = sum(int(s[i]) * weight[i] for i in range(17))
        return check_code[sum_val % 11]

    def strict_ssn(
        self,
        hometown_province: Optional[str] = None,
        hometown_city: Optional[str] = None,
        hometown_area: Optional[str] = None,
        gender: Optional[str] = None,
        birth_date: Optional[date] = None,
        age_range: Optional[tuple] = None
    ) -> str:
        """
        Generate a strictly valid 18-digit Chinese Resident Identity Card Number (SSN).
        Parameters:
            hometown_province: (Optional) Limit geographic province for the first 6 digits.
            hometown_city: (Optional) Limit geographic city for the first 6 digits.
            hometown_area: (Optional) Limit geographic area/county for the first 6 digits.
            gender: (Optional) '男', 'M' or '女', 'F'. Affects the 17th digit (odd for male).
            birth_date: (Optional) datetime.date object. Overrides age_range.
            age_range: (Optional) (min_age, max_age). Ignored if birth_date is provided.
        Returns:
            A mathematically correct 18-digit string matching the requested constraints.
        """
        areas = self._load_areas()

        # 1. Resolve Geography (First 6 digits)
        prov_list = areas
        if hometown_province:
            filtered = [p for p in prov_list if hometown_province in p['name']]
            prov_list = filtered if filtered else prov_list
            prov_data = self.random_element(prov_list)
        else:
            # Reusing the existing population weights for demographic parity fallback
            prov_weights_dict = {
                "广东": 8.93, "山东": 7.19, "河南": 7.04, "江苏": 6.00, "四川": 5.93,
                "河北": 5.28, "湖南": 4.71, "浙江": 4.57, "安徽": 4.32, "湖北": 4.09,
                "广西": 3.55, "云南": 3.34, "江西": 3.20, "辽宁": 3.02, "福建": 2.94,
                "陕西": 2.80, "贵州": 2.73, "新疆": 1.83, "甘肃": 1.77, "上海": 1.76,
                "吉林": 1.71, "内蒙古": 1.70, "北京": 1.55, "重庆": 2.27, "黑龙江": 2.26,
                "山西": 2.47, "天津": 0.98, "海南": 0.71, "宁夏": 0.51, "青海": 0.42,
                "西藏": 0.26
            }
            w_list = [prov_weights_dict.get(p['name'].replace("省", "").replace("市", "").replace("自治区", "").replace("壮族", "").replace("回族", "").replace("维吾尔", ""), 1.0) for p in prov_list]
            prov_data = random.choices(prov_list, weights=w_list, k=1)[0]

        city_list = prov_data.get('children', [])
        if not city_list: city_list = [prov_data]

        if hometown_city:
            filtered = [c for c in city_list if hometown_city in c['name']]
            if filtered: city_list = filtered
        city_data = self.random_element(city_list)

        area_list = city_data.get('children', [])
        if not area_list: area_list = [city_data]
            
        if hometown_area:
            filtered = [a for a in area_list if hometown_area in a['name']]
            if filtered: area_list = filtered
        
        area_data = self.random_element(area_list)
        area_code = area_data.get('code', '110101') # Absolute fallback constraint

        # 2. Resolve Birth Date (Middle 8 digits)
        if birth_date:
            b_date = birth_date
        else:
            if not age_range or len(age_range) != 2:
                # Same demographic pyramid fallback
                age_bucket = random.choices(["0-14", "15-59", "60-90"], weights=[17.95, 63.35, 18.70], k=1)[0]
                if age_bucket == "0-14": age_range = (1, 14)
                elif age_bucket == "15-59": age_range = (15, 59)
                else: age_range = (60, 90)
            b_date = self._random_date_between(age_range[0], age_range[1])
            
        date_str = b_date.strftime('%Y%m%d')

        # 3. Resolve Gender (17th digit)
        if gender not in ['男', '女', 'M', 'F']:
            gender_val = random.choices(['男', '女'], weights=[51.24, 48.76], k=1)[0]
        else:
            gender_val = '男' if gender in ['男', 'M'] else '女'
            
        is_male = gender_val == '男'
        gender_digit = self.random_element([1, 3, 5, 7, 9]) if is_male else self.random_element([0, 2, 4, 6, 8])

        # 4. Generate & Validation Checksum
        seq_code = f"{self.random_int(min=0, max=99):02d}"
        ssn_17 = f"{area_code}{date_str}{seq_code}{gender_digit}"
        checksum = self._ssn_checksum(ssn_17)
        return f"{ssn_17}{checksum}"

    def _random_date_between(self, min_age: int, max_age: int) -> date:
        today = date.today()
        start = today.replace(year=today.year - max_age)
        end = today.replace(year=today.year - min_age)
        delta = end - start
        random_days = self.random_int(min=0, max=delta.days)
        return start + timedelta(days=random_days)

    def _generate_full_address(self, p_data, c_data, a_data, villages, f_urban=False, job=None, employment=None):
        # 7th Census: Urban vs Rural
        # Target: Urban 63.89%, Rural 36.11%
        is_u = random.random() < 0.6389
        if f_urban: is_u = True
        
        t_list = a_data.get('children', [])
        
        urban_t = []
        rural_t = []
        if t_list:
            urban_t = [t for t in t_list if any(kw in t['name'] for kw in ["街道", "区", "镇", "开发区"])]
            rural_t = [t for t in t_list if any(kw in t['name'] for kw in ["乡", "村", "林场", "农场"])]
            
            if is_u and urban_t:
                t_list = urban_t
            elif not is_u and rural_t:
                t_list = rural_t
                
        if not t_list:
            t_n, t_c = "", ""
        else:
            t_obj = self.random_element(t_list)
            t_n, t_c = t_obj['name'], t_obj.get('code', '')

        # Town-level villages logic
        v_list = villages.get(t_c, []) if t_c else []
        if job is not None:
            # Generate Workplace specific address
            job_v = str(job)
            if any(kw in job_v for kw in ["总", "高管", "CEO", "CTO", "CFO", "总裁", "主任", "架构师", "专家", "研究员", "科学家", "开发", "程序员", "IT", "互联网", "软件", "系统"]):
                suffix = self.random_element(["大厦", "国际中心", "科技园", "广场", "中心", "软件园", "CBD", "创新中心"])
                c_name = self.random_element(["星河", "腾讯", "阿里", "百度", "字节", "华为", "小米", "美团", "京东", "网易", "新浪", "天猫", "搜狐", "360", "金山", "滴滴", "平安", "万达", "绿地", "保利", "恒大", "融创", "富力", "华润", "中海", "招商", "万科", "金地", "龙湖", "绿城", "世茂", "新城", "阳光城", "佳兆业", "中南", "阳光", "时代", "世纪", "国际", "理想", "滨江", "华府", "环球", "财富", "金融", "世贸", "国贸"])
                if c_name not in suffix and suffix not in c_name: b_estate = f"{c_name}{suffix}"
                else: b_estate = suffix
                r_name = self.random_element(["高新", "科技", "创业", "创新", "软件", "信息", "数据", "云", "智能", "智慧", "数字", "网络", "创客", "软件园", "科创", "科技园", "高新区", "开发区"]) + self.random_element(["路", "街", "大道"])
                if self.random_int(0, 1) > 0: full_street = f"{t_n}{r_name}{self.random_int(1,500)}号{b_estate}{self.random_int(1,50)}层"
                else: full_street = f"{t_n}{b_estate}{self.random_int(1,60)}楼{self.random_int(1,30)}0{self.random_int(1,9)}室"
            elif any(kw in job_v for kw in ["司机", "快递", "外卖", "配送", "厨师", "服务员", "营业员", "保安", "保洁", "家政", "保姆", "销售", "业务", "店员", "前台", "客服", "收银"]):
                # Distinguish a bit between pure sales and food service
                if "销售" in job_v or "业务" in job_v:
                    suffix = self.random_element(["服务中心", "大卖场", "专卖店", "门店", "营业厅", "门店", "广场", "时代广场"])
                else:
                    suffix = self.random_element(["商业街", "步行街", "购物中心", "百货", "广场", "商场", "超市", "连锁店", "餐饮", "酒店", "宾馆", "饭店", "餐馆", "快餐", "小吃", "面馆"])

                if any(kw in suffix for kw in ["商业", "街", "广场", "中心", "商场"]):
                    c_name = self.random_element(["万达", "大悦城", "万象城", "吾悦", "宝龙", "银泰", "印象城", "天街", "恒隆", "太古", "万科", "金鹰", "百联", "王府井", "茂业", "新百", "银座"])
                else:
                    c_name = self.random_element(["老王", "小李", "张记", "赵家", "刘阿姨", "王老板", "李师傅", "张大哥", "赵大姐", "陈大妈", "周村", "吴记", "郑家", "何氏", "好运", "发财", "吉祥", "如意", "平安", "顺发", "宏鼎", "鼎盛", "旺铺", "客家人", "老乡", "姐妹", "兄弟", "老地方", "相聚", "缘分", "天天", "开心"])
                b_estate = f"{c_name}{suffix}"
                r_name = self.random_element(["朝阳", "建设", "胜利", "解放", "中山", "人民", "新华", "和平", "文化", "青年", "红星", "光明", "幸福", "团结", "前进", "东风", "红旗", "五一", "八一", "长安", "北京", "南京", "广州", "上海", "商业", "步行", "小吃", "美食", "女人", "古玩", "花鸟", "电子"]) + self.random_element(["路", "街", "巷", "弄", "道"])
                full_street = f"{t_n}{r_name}{self.random_int(1,500)}号{b_estate}"
            elif any(kw in job_v for kw in ["工人", "厂", "制造", "生产", "流水线", "车间", "装配", "普工", "质检", "维修", "机修", "电工", "焊工", "钳工"]):
                suffix = self.random_element(["工业园", "制造厂", "加工厂", "机械厂", "服装厂", "电子厂", "塑料厂", "模具厂", "食品厂", "鞋厂", "玩具厂", "五金厂", "家具厂", "化工厂", "印刷厂", "纸箱厂", "包材厂", "纺织厂", "钢铁厂", "水泥厂", "砖厂"])
                c_name = self.random_element(["富士康", "立讯", "比亚迪", "长城", "美的", "格力", "海尔", "海信", "TCL", "创维", "康佳", "长虹", "老板", "方太", "苏泊尔", "九阳", "华帝", "万和", "宏观", "格兰仕", "红牛", "康师傅", "统一", "娃哈哈", "农夫山泉"])
                b_estate = f"{c_name}{suffix}"
                r_name = self.random_element(["工业", "振兴", "创业", "发展", "腾飞", "开拓", "创新", "科技", "高新", "开发", "新村", "红星", "向阳", "东方", "迎宾", "世纪", "时代", "阳光", "星火", "火炬", "滨海", "沿海", "港口"]) + self.random_element(["路", "街", "大道", "园区", "二路", "三路"])
                if self.random_int(0, 1) > 0: full_street = f"{t_n}{r_name}{self.random_int(1,500)}号{b_estate}{self.random_int(1,5)}车间"
                else: full_street = f"{t_n}{b_estate}{self.random_int(1,10)}号厂房"
            elif any(kw in job_v for kw in ["学校", "老师", "教授", "讲师", "教育", "培训"]):
                suffix = self.random_element(["大学", "学院", "中学", "小学", "幼儿园", "培训中心", "教育机构", "重点高级中学", "职业技术学院"])
                c_name = self.random_element(["第一", "第二", "第三", "第四", "第五", "实验", "外国语", "师范", "理工", "科技", "工商", "财经", "政法", "艺术", "体育", "医科", "农业", "林业", "联合", "交通", "星火"])
                b_estate = f"{c_name}{suffix}"
                r_name = self.random_element(["学院", "学府", "大学", "科教", "育才", "文化"]) + self.random_element(["路", "街"])
                full_street = f"{t_n}{r_name}{self.random_int(1,200)}号{b_estate}"
            elif any(kw in job_v for kw in ["医院", "医生", "护士", "医疗", "卫生", "保健"]):
                suffix = self.random_element(["人民医院", "中心医院", "妇幼保健院", "中医院", "附属医院", "协和医院", "第一医院", "第二医院", "骨科医院", "眼科医院", "口腔医院", "卫生院", "社区卫生服务中心", "仁爱医院", "博爱医院", "康复医院"])
                if "中心医院" in suffix or "卫生院" in suffix or "服务中心" in suffix: b_estate = f"{a_data['name']}{suffix}"
                elif "社区" in suffix: b_estate = f"{t_n}{suffix}"
                else: b_estate = f"{self.random_element(['市', '省', '区', '县', '军区', '铁路', '职工', '红十字', '协和', '同济', '华山', '中山', '瑞金', '湘雅', '齐鲁', '华西', '南方'])}{suffix}"
                r_name = self.random_element(["健康", "康复", "白衣", "爱民", "天使", "人民", "红十字"]) + self.random_element(["路", "街"])
                full_street = f"{t_n}{r_name}{self.random_int(1,200)}号{b_estate}"
            else:
                if employment == "自由职业":
                    # Freelancers work at home, cafes, workspaces
                    b_estate = self.random_element(["创客空间", "共享办公", "SOHO", "咖啡厅", "工作室", "公寓", "社区"])
                    c_name = self.random_element(["星巴克", "瑞幸", "漫咖啡", "WeWork", "优客工场", "左岸", "时光", "理想", "阳光", "世纪"])
                    if b_estate in ["工作室", "公寓", "社区"]:
                        e_suffix = self.random_element(["小区", "花园", "苑", "家园", "新村"])
                        b_estate = f"{self.random_element(['阳光', '时代', '世纪', '滨江', '华府'])}{e_suffix}"
                    else:
                        b_estate = f"{c_name}{b_estate}"
                    r_name = self.random_element(["朝阳", "建设", "中山", "人民", "新华", "创业", "创新"]) + self.random_element(["路", "街"])
                    full_street = f"{t_n}{r_name}{self.random_int(1,200)}号{b_estate}"
                elif any(kw in job_v for kw in ["公务员", "行政", "局", "委", "办", "政府", "事业", "书记"]):
                    b_estate = self.random_element(["人民政府", "教育局", "公安局", "税务局", "工商局", "建设局", "环保局", "文化局", "卫健委", "发改委", "民政局", "财政局", "居委会", "街道办事处", "派出所", "法院", "检察院", "交警大队", "消防大队"])
                    if any(kw in b_estate for kw in ["局", "委", "政府", "处", "所", "院", "大队"]): b_estate = f"{c_data['name']}{a_data['name']}{b_estate}"
                    r_name = self.random_element(["朝阳", "建设", "胜利", "解放", "中山", "人民", "新华", "政法", "府前", "民主"]) + self.random_element(["路", "街", "大道"])
                    full_street = f"{t_n}{r_name}{self.random_int(1,200)}号{b_estate}"
                else:
                    # General white-collar / commercial for unmatched jobs
                    suffix = self.random_element(["大厦", "写字楼", "商务中心", "商办大楼", "大楼", "国贸"])
                    c_name = self.random_element(["时代", "卓越", "绿城", "万象", "金融", "财富", "环球", "恒丰", "嘉里", "宝龙", "银泰", "万达"])
                    b_estate = f"{c_name}{suffix}"
                    r_name = self.random_element(["北京", "南京", "中山", "解放", "建国", "复兴", "和平", "新华", "人民"]) + self.random_element(["路", "街", "大道"])
                    full_street = f"{t_n}{r_name}{self.random_int(1,200)}号{b_estate}{self.random_int(1,30)}层{self.random_int(1,20)}0{self.random_int(1,9)}室"
        else:
            if is_u:
                b_estate = ""
                if v_list:
                    u_vp = [v for v in v_list if any(kw in v for kw in ["社区", "居委会"])]
                    if not u_vp: u_vp = v_list
                    b_estate = self.random_element(u_vp)
                    for s in ["居民委员会", "社区居委会", "居委会", "社区", "村民委员会", "村委会"]:
                        b_estate = b_estate.replace(s, "")
                if not b_estate or len(b_estate) < 2:
                    b_estate = self.random_element(["阳光", "时代", "世纪", "国际", "理想", "中心", "滨江", "华府", "万科", "金地"])
                e_suffix = self.random_element(["小区", "花园", "苑", "家园", "新村", "府"])
                e_name = f"{b_estate}{e_suffix}"
                r_name = self.random_element(["朝阳", "建设", "胜利", "解放", "中山", "人民", "新华"]) + self.random_element(["路", "街"])
                full_street = f"{t_n}{r_name}{e_name}{self.random_int(1,50)}号楼{self.random_int(1,5)}单元{self.random_int(1,30)}0{self.random_int(1,4)}室"
            else:
                v_name = ""
                if v_list:
                    r_vp = [v.replace("村民委员会", "").replace("村委会", "").replace("居委会", "") for v in v_list]
                    v_name = self.random_element(r_vp)
                    if v_name and not any(v_name.endswith(s) for s in ["村", "庄", "队"]): v_name += "村"
                if not v_name:
                    v_name = f"{self.random_element(['张家', '李家', '王家', '赵家', '大', '小', '新'])}{self.random_element(['村', '庄', '屯'])}"
                    if not v_name.endswith("村"): v_name += "村"
                full_street = f"{t_n}{v_name}{self.random_int(1,100)}号"

        # Vehicle Plate prefix mapping
        plate_prefixes = {
            "北京": "京", "天津": "津", "上海": "沪", "重庆": "渝", "河北": "冀",
            "山西": "晋", "辽宁": "辽", "吉林": "吉", "黑龙江": "黑", "江苏": "苏",
            "浙江": "浙", "安徽": "皖", "福建": "闽", "江西": "赣", "山东": "鲁",
            "河南": "豫", "湖北": "鄂", "湖南": "湘", "广东": "粤", "海南": "琼",
            "四川": "川", "贵州": "贵", "云南": "云", "陕西": "陕", "甘肃": "甘",
            "青海": "青", "台湾": "台", "内蒙古": "蒙", "广西": "桂", "西藏": "藏",
            "宁夏": "宁", "新疆": "新", "香港": "港", "澳门": "澳"
        }
        
        plate_prefix = "京"
        for k, v in plate_prefixes.items():
            if k in p_data['name']:
                plate_prefix = v
                break
        
        # Simple random city letter (A-Z except I and O usually)
        city_letter = self.random_element("ABCDEFGHJKLMNPQRSTUVWXYZ")

        return {
            "province": p_data['name'],
            "city": c_data['name'],
            "area": a_data['name'],
            "town": t_n,
            "is_urban": is_u,
            "address": f"{p_data['name']}{c_data['name']}{a_data['name']}{full_street}",
            "plate_prefix": f"{plate_prefix}{city_letter}"
        }


    def persona(
        self,
        gender: Optional[str] = None,
        age_range: Optional[tuple] = None,
        hometown_province: Optional[str] = None,
        hometown_city: Optional[str] = None,
        has_second_phone: bool = False,
        work_province: Optional[str] = None,
        work_city: Optional[str] = None,
        use_ai: bool = False,
        ai_config: Optional[Dict] = None,
        fields: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a Chinese virtual persona strictly adhering to geographic, logical and ID verification constraints.
        Supports extensive detail fields via kwargs: 
        (height, weight, blood_type, username, password, education, job, salary, security_question, security_answer, etc.)
        """
        areas = self._load_areas()
        phones = self._load_phones()

        # 1. Resolve geographic constraints (Hometown)
        prov_list = areas
        if hometown_province:
            filtered = [p for p in prov_list if hometown_province in p['name']]
            if filtered:
                prov_list = filtered
                prov_data = self.random_element(prov_list)
            else:
                prov_data = self.random_element(prov_list)
        else:
            # 7th Census: Province Population Weighting
            prov_weights_dict = {
                "广东": 8.93, "山东": 7.19, "河南": 7.04, "江苏": 6.00, "四川": 5.93,
                "河北": 5.28, "湖南": 4.71, "浙江": 4.57, "安徽": 4.32, "湖北": 4.09,
                "广西": 3.55, "云南": 3.34, "江西": 3.20, "辽宁": 3.02, "福建": 2.94,
                "陕西": 2.80, "贵州": 2.73, "新疆": 1.83, "甘肃": 1.77, "上海": 1.76,
                "吉林": 1.71, "内蒙古": 1.70, "北京": 1.55, "重庆": 2.27, "黑龙江": 2.26,
                "山西": 2.47, "天津": 0.98, "海南": 0.71, "宁夏": 0.51, "青海": 0.42,
                "西藏": 0.26
            }
            # Fallback weight for missing provinces
            w_list = [prov_weights_dict.get(p['name'].replace("省", "").replace("市", "").replace("自治区", "").replace("壮族", "").replace("回族", "").replace("维吾尔", ""), 1.0) for p in prov_list]
            prov_data = random.choices(prov_list, weights=w_list, k=1)[0]
            
        prov_name = prov_data['name']

        city_list = prov_data.get('children', [])
        if not city_list:
            city_list = [prov_data]

        if hometown_city:
            filtered = [c for c in city_list if hometown_city in c['name']]
            if filtered:
                city_list = filtered

        city_data = self.random_element(city_list)
        city_name = city_data['name']

        area_list = city_data.get('children', [])
        if not area_list:
            area_list = [city_data]

        area_data = self.random_element(area_list)
        area_code = area_data['code']
        area_name = area_data['name']

        town_list = area_data.get('children', [])
        if town_list:
            town_data = self.random_element(town_list)
            town_name = town_data['name']
            town_code = town_data.get('code', '')
        else:
            town_name = ""
            town_code = ""

        # 2. Resolve Gender, Age and Marital Status
        if gender not in ['男', '女', 'M', 'F']:
            # 7th Census: General Sex Ratio 105.07 (Male 51.24%, Female 48.76%)
            gender_val = random.choices(['男', '女'], weights=[51.24, 48.76], k=1)[0]
        else:
            gender_val = '男' if gender in ['男', 'M'] else '女'

        is_male = gender_val == '男'

        if not age_range or len(age_range) != 2:
            # 7th Census: Age Pyramid -> 0-14: 17.95%, 15-59: 63.35%, 60+: 18.70%
            age_bucket = random.choices(["0-14", "15-59", "60-90"], weights=[17.95, 63.35, 18.70], k=1)[0]
            if age_bucket == "0-14":
                age_range = (1, 14)
            elif age_bucket == "15-59":
                age_range = (15, 59)
            else:
                age_range = (60, 90)

        birth_date = self._random_date_between(age_range[0], age_range[1])
        age = date.today().year - birth_date.year - ((date.today().month, date.today().day) < (birth_date.month, birth_date.day))

        # Infer Marital Status based on Age Profile
        if age < 22:
            marital_status = "未婚"
        elif age < 30:
            # ~60% un-married, ~39% married, ~1% divorced
            marital_status = random.choices(["未婚", "已婚", "离异"], weights=[60, 39, 1], k=1)[0]
        elif age < 50:
            # High marriage rate, some divorce
            marital_status = random.choices(["未婚", "已婚", "离异", "丧偶"], weights=[15, 75, 9, 1], k=1)[0]
        else:
            # Older cohorts
            marital_status = random.choices(["未婚", "已婚", "离异", "丧偶"], weights=[5, 75, 5, 15], k=1)[0]
        
        marital_status = kwargs.get("marital_status") or marital_status

        # 3. Generate Strict SSN
        ssn = self.strict_ssn(
            hometown_province=hometown_province,
            hometown_city=hometown_city,
            gender=gender_val,
            birth_date=birth_date
        )

        # 4. Address Logic extracted to class method

        # Generate Hometown
        villages = self._load_villages()
        hometown_data = self._generate_full_address(prov_data, city_data, area_data, villages)

        # Social / background with age constraints
        if age < 7:
            education = "幼儿"
            employment = "在读"
        elif age < 13:
            education = "小学"
            employment = "在读"
        elif age < 16:
            education = "初中"
            employment = "在读"
        elif age < 19:
            education = random.choices(["高中", "中专"], weights=[60, 40], k=1)[0]
            employment = "在读"
        elif age < 23:
            # College years: some are learning, some are working.
            # Real world: highly weighted to Highschool/Vocational/Assosiates
            education = random.choices(["初中", "高中", "中专", "职业技能培训", "大专", "本科"], weights=[10, 15, 10, 15, 30, 20], k=1)[0]
            employment = random.choices(["在职", "待业", "在读"], weights=[40, 5, 55], k=1)[0]
        elif age < 60:
            # Core working population. Parity: Below Highschool ~50%, Highschool/Voc ~20%, Assoc 15%, Bach 12%, Mas/PhD 3%
            edu_opts = ["初中", "高中", "中专", "职业技能培训", "大专", "本科", "硕士", "MBA", "博士"]
            edu_weights = [50, 10, 10, 5, 15, 10, 2, 1, 0.5]
            education = random.choices(edu_opts, weights=edu_weights, k=1)[0]
            
            # Employment: Enployed 70%, Free 15%, Unem 15% (including housewives, disabled, etc.)
            emp_opts = ["在职", "待业", "自由职业"]
            emp_weights = [70, 15, 15]
            employment = random.choices(emp_opts, weights=emp_weights, k=1)[0]
        else: # 60+
            education = random.choices(["初中", "高中", "大专", "本科", "硕士", "博士"], weights=[70, 15, 10, 4, 0.8, 0.2], k=1)[0]
            employment = random.choices(["退休", "自由职业"], weights=[95, 5], k=1)[0]

        education = kwargs.get("education") or education
        employment = kwargs.get("employment") or employment
        user_job = kwargs.get("job")
        if user_job and user_job not in ["无", "幼儿", "学生", "退休人员"]:
            if not kwargs.get("employment"):
                employment = "在职"


        # Job deduction based strictly on employment status
        if employment in ["在读", "全职学生"]:
            job_val = "无" if age < 7 else "学生"
        elif employment in ["待业", "待就业", "无业"]:
            job_val = "无"
        elif employment == "退休":
            job_val = "退休人员"
        else:
            job_val = self._get_realistic_job()

        job = kwargs.get("job") or job_val

        # Logic Hardening: Education Ceiling for Blue-Collar / Service
        blue_collar_kw = ["普工", "操作", "车间", "流水线", "装配", "纺织", "细纱", "包装", "厨师", "服务员", "营业员", "保安", "保洁", "家政", "保姆", "洗碗", "店员", "前台", "收银", "司机", "快递", "外卖", "配送", "理发", "美容", "美发", "美体", "泥瓦工", "钢筋工", "搬运", "清洁", "维修", "机修", "钳工", "焊工", "木工", "电工", "水管工", "修理", "足疗", "推拿", "按摩", "传菜", "门卫", "导购", "促销", "保洁", "钟点工", "月嫂", "保安", "后厨", "切配", "迎宾", "收银", "杂工", "收发", "工人", "混凝土", "挖掘机", "砌筑", "抹灰", "水电工", "架子工", "电梯工", "钣金", "喷漆", "锅炉", "保安", "保洁", "环卫", "绿化", "搬运", "装卸", "分拣"]
        if any(kw in job for kw in blue_collar_kw):
            if education in ["博士", "硕士", "MBA"]:
                education = self.random_element(["初中", "高中", "中专", "大专", "职业技能培训"])
            elif education == "本科" and self.random_int(1, 100) > 10:  # 90% chance to downgrade Bachelors in these roles
                education = self.random_element(["初中", "高中", "中专", "大专", "职业技能培训"])
                
        # Logic Hardening: Base Education Age Floor
        if education == "博士" and age < 27:
            age = self.random_int(27, 45)
        elif education in ["硕士", "MBA"] and age < 24:
            age = self.random_int(24, 40)
        elif education == "本科" and age < 22:
            age = self.random_int(22, 35)
            
        # Logic Hardening: Education/Age Door for Specific Jobs
        # Always fix '研究生' to be realistic
        if "研究生" in job:
            if age > 35: age = self.random_int(22, 28)
            employment = "在读"
            job = "学生"
            education = "本科"
        
        # Specific high-end jobs require older age and higher education
        if any(kw in job for kw in ["总", "CEO", "总裁", "主任", "总监", "经理"]):
            if age < 25: age = self.random_int(26, 45)
            if education in ["幼儿", "小学", "初中", "高中", "中专", "大专", "职业技能培训"]: 
                education = self.random_element(["本科", "硕士", "MBA"])
                
        if any(kw in job for kw in ["架构师", "专家", "研究员", "科学家", "教授", "算法"]):
            if age < 28: age = self.random_int(28, 50)
            if education in ["幼儿", "小学", "初中", "高中", "中专", "大专", "职业技能培训"]:
                education = self.random_element(["本科", "硕士", "博士"])
                
        if any(kw in job for kw in ["工程师", "开发", "程序员"]):
            if age < 22: age = self.random_int(22, 40)
            if education in ["幼儿", "小学", "初中"]:
                education = self.random_element(["大专", "本科"])



        # 5. Resolve Social/Job constraints to determine Workplace
        company_name = "无"
        company_uscc = "无"
        
        if employment in ["在读", "待业", "无业", "待就业", "退休"] or job in ["无", "幼儿", "学生", "退休人员"]:
            workplace_data = {
                "province": "无",
                "city": "无",
                "area": "无",
                "address": "无",
                "company_name": company_name,
                "company_uscc": company_uscc
            }
        else:
            is_high_end = any(kw in job for kw in ["总", "CEO", "CTO", "高管", "总裁", "架构师", "专家"])

            if work_province:
                w_prov_list = [p for p in areas if work_province in p['name']] if work_province else areas
                wp_data = self.random_element(w_prov_list)
                wc_list = wp_data.get('children', [wp_data])
                wc_data = self.random_element([c for c in wc_list if work_city in c['name']]) if work_city else self.random_element(wc_list)
                wa_list = wc_data.get('children', [wc_data])
                wa_data = self.random_element(wa_list)
            elif is_high_end and not hometown_data['is_urban']:
                t1_provs = ["北京", "上海", "广东", "江苏", "浙江"]
                wp_data = self.random_element([p for p in areas if any(t1 in p['name'] for t1 in t1_provs)])
                wc_data = self.random_element(wp_data.get('children', [wp_data]))
                wa_data = self.random_element(wc_data.get('children', [wc_data]))
            else:
                wp_data, wc_data, wa_data = prov_data, city_data, area_data

            # Match enterprise based on industry mapping
            ent_db = self._load_enterprises()
            matched_company = None
            is_tech = any(kw in job for kw in ["架构师", "专家", "研究员", "研发", "科学家", "总监", "经理", "开发", "程序员", "IT", "互联网", "软件", "系统", "产品", "运营"])
            is_finance = any(kw in job for kw in ["银行", "出纳", "财务", "金融", "投资", "风控", "保险", "理财", "资金", "信贷"])
            is_manufacture = any(kw in job for kw in ["质量", "车间", "工人", "普工", "机修", "制造", "产线", "组装", "仓管", "包装", "纺织", "焊接", "操作"])
            
            target_industry = ""
            if is_tech: target_industry = "信息传输、软件和信息技术服务业"
            elif is_finance: target_industry = "金融业"
            elif is_manufacture: target_industry = "制造业"
                
            # Try to catch a giant if high end or pure luck
            if target_industry and random.random() < 0.05:
                giant_cands = [c for c in ent_db.get("_giants", []) if c["industry"] == target_industry and c["province"] in wp_data["name"]]
                if giant_cands:
                    matched_company = random.choice(giant_cands)
                    
            if not matched_company:
                # Fallback to local SMEs
                local_smes = ent_db.get("_sme", {}).get(wp_data["name"].replace("省", "").replace("市", "").replace("自治区", "").replace("壮族", "").replace("回族", "").replace("维吾尔", ""), [])
                if local_smes:
                    valid_smes = [c for c in local_smes if not target_industry or c["industry"] == target_industry]
                    city_matched_smes = [c for c in valid_smes if c["city"] == wc_data["name"]]
                    
                    if city_matched_smes:
                        matched_company = random.choice(city_matched_smes)
                    elif valid_smes:
                        matched_company = random.choice(valid_smes)
                    else:
                        matched_company = random.choice(local_smes)
            
            base_address = self._generate_full_address(wp_data, wc_data, wa_data, villages, f_urban=is_high_end, job=job, employment=employment)
            
            if matched_company:
                company_name = matched_company["name"]
                company_uscc = matched_company["uscc"]
                if matched_company.get("address"):
                    # Giant company has hardcoded real address
                    workplace_address_str = matched_company["address"]
                else:
                    # Sync city back from company so name matches the address if we had a fallback
                    if matched_company["city"] != wc_data["name"]:
                        wc_data = next((c for c in wp_data.get('children', [wp_data]) if c['name'] == matched_company["city"]), wc_data)
                        wa_list = wc_data.get('children', [wc_data])
                        wa_data = self.random_element(wa_list)
                        base_address = self._generate_full_address(wp_data, wc_data, wa_data, villages, f_urban=is_high_end, job=job, employment=employment)
                        
                    if any(kw in job for kw in ["医生", "护士", "老师", "教授", "公务员"]):
                        workplace_address_str = base_address["address"] # Keep logic for hospitals/schools
                    else:
                        if "号" in base_address["address"]:
                            workplace_address_str = base_address["address"].split("号")[0] + f"号{company_name}"
                        else:
                            workplace_address_str = base_address["address"] + f"附楼{company_name}"
            else:
                workplace_address_str = base_address["address"]

            workplace_data = {
                "province": wp_data['name'],
                "city": wc_data['name'],
                "area": wa_data['name'],
                "address": workplace_address_str,
                "company_name": company_name,
                "company_uscc": company_uscc
            }

        # 6. Generate Primary Phone based on Workplace
        primary_phone = self._get_phone_number(self._load_phones(), str(workplace_data['province']), str(workplace_data['city']))

        # 7. Determine Name (Gender already known) with Era-based Probabilities
        if kwargs.get("name"):
            name = kwargs.get("name")
        else:
            name = self.era_name(birth_date.year, gender_val)

        # 8. Ethnicity and Identity (Geo-aware distribution)
        ethnicity = kwargs.get("ethnicity")
        if not ethnicity:
            e_weights = {"汉族": 91}
            p_n = str(prov_name)
            if "西藏" in p_n: e_weights["藏族"] = 50
            elif "新疆" in p_n: e_weights["维吾尔族"] = 45; e_weights["哈萨克族"] = 5
            elif "内蒙古" in p_n: e_weights["蒙古族"] = 20
            elif "宁夏" in p_n: e_weights["回族"] = 30
            elif "广西" in p_n: e_weights["壮族"] = 35
            elif "云南" in p_n: e_weights["傣族"] = 10; e_weights["彝族"] = 10; e_weights["白族"] = 5
            elif "吉林" in p_n or "辽宁" in p_n: e_weights["满族"] = 15; e_weights["朝鲜族"] = 5
            
            others = ["苗族", "回族", "土家族", "彝族", "满族", "壮族", "布依族"]
            for o in others:
                if o not in e_weights: e_weights[o] = 1
            
            total_w = sum(e_weights.values())
            r_val = random.uniform(0, total_w)
            cursor = 0
            for e_name, w in e_weights.items():
                cursor += w
                if r_val <= cursor:
                    ethnicity = e_name
                    break
        
        # Postcode Logic: Load Full Database
        full_pc_index = self._load_postcodes()
        

        # 8. Physical attributes with realistic distributions
        # Blood types in China: O~32%, A~28%, B~30%, AB~10%
        # Rh- is rare in China: ~0.3%

        # 8. Physical attributes with realistic distributions (分段式生长曲线)
        # Pediatric Growth Curve (18.5 - 27 BMI for adults, specific for minors)
        if age < 3:
            h_min, h_max = 50, 100
            bmi_min, bmi_max = 14, 19
        elif age < 7:
            h_min, h_max = 90, 130
            bmi_min, bmi_max = 13, 18
        elif age < 13:
            h_min, h_max = 120, 165
            bmi_min, bmi_max = 14, 21
        elif age < 18:
            h_min, h_max = (155, 185) if is_male else (150, 175)
            bmi_min, bmi_max = 16, 24
        else: # Adult
            h_min, h_max = (165, 190) if is_male else (155, 175)
            bmi_min, bmi_max = 18.5, 27
            
        h_val = self.random_int(min=h_min, max=h_max)
        bmi = random.uniform(bmi_min, bmi_max)
        w_val = int(bmi * (h_val/100)**2)
            
        height = kwargs.get("height") or f"{h_val}cm"
        weight = kwargs.get("weight") or f"{w_val}kg"
        blood_type = kwargs.get("blood_type") or self._get_realistic_blood()

        # Web / Account attributes (姓名-账号耦合)
        # Simple name-based username logic

        username = kwargs.get("username") or self._get_linked_identity(name)
        
        # 密码逻辑强化：区分强密码与真实常用密码 (Common Habits: BirthDate + Initials)
        initials = self._get_pinyin_initials(name).lower()
        common_password_base = f"{birth_date.strftime('%Y%m%d')}{initials}"
        
        common_password = kwargs.get("common_password") or common_password_base
        common_password_upper = kwargs.get("common_password_upper") or common_password_base.upper()
        strong_password = kwargs.get("password") or self.generator.password()
        
        guid = kwargs.get("guid") or str(self.generator.uuid4())
        
        temp_mail_configs = {
            'yopmail.com': 'https://yopmail.com/zh/?',
            'yopmail.net': 'https://yopmail.com/zh/?',
            'cool.fr.nf': 'https://yopmail.com/zh/?',
            'jetable.fr.nf': 'https://yopmail.com/zh/?'
        }
        temp_domain = self.random_element(list(temp_mail_configs.keys()))
        temp_email = kwargs.get("temp_email") or f"{username}@{temp_domain}"
        # Dynamic Email Domain Weights based on Age and Job
        
        # New: Salary constraint based on Job
        job_salary_mapping = [
            # High priority specific overrides
            (["车间主任", "护理主任", "护士长", "大堂经理", "客服经理", "物业经理", "前台", "迎宾", "钟点工"], (4000, 15000)),
            (["洗碗", "清洁", "搬运", "杂工", "收废品", "足疗", "推拿", "按摩", "泥瓦工", "钢筋工", "纺织", "细纱"], (3000, 8000)),
            (["护士", "护理", "药剂师"], (4000, 15000)),
            (["医生", "医师", "主任医师", "法医"], (8000, 45000)),
            (["教师", "老师", "教授", "讲师", "教员", "助教", "教练"], (4000, 25000)),
            (["工程师", "开发", "程序员", "技术", "IT", "设计"], (8000, 45000)),
            (["架构师", "专家", "科学家", "研究员"], (20000, 80000)),
            (["客服", "行政", "文员", "专员", "出纳", "助理", "人事"], (3500, 10000)),
            (["销售", "业务", "代理", "市场", "公关", "媒介", "采购"], (4000, 30000)),
            (["司机", "快递", "外卖", "配送", "骑手", "乘务", "船员"], (5000, 12000)),
            (["厨师", "服务员", "营业员", "保安", "店员", "导购", "促销", "理发", "美容"], (3000, 8000)),
            (["保洁", "家政", "保姆", "月嫂"], (3000, 9000)),
            (["工人", "普工", "操作工", "钳工", "焊工", "木工", "电工", "水管工", "维修", "机修", "制造"], (4000, 10000)),
            (["总监", "CEO", "CTO", "CFO", "总裁", "总经理", "副总", "行长"], (30000, 150000)),
            (["经理", "主管", "主任", "领班", "组长", "厂长"], (8000, 35000)),
            (["会计", "审计", "金融", "投资", "分析师", "顾问", "律师", "法务"], (8000, 40000)),
            (["翻译", "编辑", "记者", "策划", "编导", "导演"], (6000, 25000)),
            (["演员", "模特", "歌手", "主播", "摄影", "后期", "剪辑"], (5000, 30000)),
            (["公务员", "干事", "书记", "局长", "科长", "处长", "警", "官", "军", "检察", "法官"], (5000, 18000)),
            (["退休"], (2500, 10000)),
            (["学生", "小学", "初中", "高中", "幼儿", "无"], (0, 0))
        ]

        # New: Geo-Salary Multiplier based on Job Location
        tier1_cities = ["北京", "上海", "广州", "深圳"]
        new_tier1_cities = ["成都", "杭州", "武汉", "南京", "天津", "西安", "苏州", "郑州", "长沙", "东莞", "沈阳", "青岛", "合肥", "佛山", "宁波"]
        
        # Determine City Tier Factor for Workplace
        city_factor = 1.0
        loc_prov = str(workplace_data.get('province', ''))
        loc_city = str(workplace_data.get('city', ''))

        if any(c in loc_prov or c in loc_city for c in tier1_cities):
            city_factor = random.uniform(1.3, 1.6)
        elif any(c in loc_prov or c in loc_city for c in new_tier1_cities):
            city_factor = random.uniform(1.1, 1.3)
        elif "省" in loc_prov or "自治区" in loc_prov:
            city_factor = random.uniform(0.8, 1.0)
        else:
            city_factor = random.uniform(0.6, 0.8)

        # Rural factor (based on workplace environment)
        rural_factor = random.uniform(0.6, 0.8) if workplace_data.get('is_urban') is False else 1.0


        if "在读" in employment or "待业" in employment or job in ["无", "幼儿", "学生"]:
            salary = "￥0"
        else:
            salary = kwargs.get("salary") or self._get_salary_by_job(job, job_salary_mapping, city_factor, rural_factor)
            
        email = kwargs.get("email") or self._generate_weighted_email(username, age, job)
        
        yopmail_account = kwargs.get("yopmail") or f"{username}@yopmail.com"
        yopmail_url = f"https://yopmail.com/zh/?login={username}"
        
        # MBTI personality type
        mbti_list = [
            "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"
        ]
        mbti = kwargs.get("mbti") or self.random_element(mbti_list)

        # Bank Card (Luhn standard)

        bank_name = "无"
        bank_card = "无"
        if age >= 10:
            bank_bins = {
                "中国工商银行": ["622202", "621226", "622208"],
                "中国农业银行": ["622848", "622845", "622822"],
                "中国银行": ["621661", "621660", "456350"],
                "中国建设银行": ["621700", "621081", "623668"]
            }
            bank_name = self.random_element(list(bank_bins.keys()))
            bin_val = self.random_element(bank_bins[bank_name])
            bank_card = kwargs.get("bank_card") or self._generate_luhn(bin_val)
            
        # Vehicle Plates based on realistic Chinese socio-economic statistics
        # Statistically, 1 in 4 people in China owns a car (approx 25%).
        # Highly correlated with age (25-55 peak) and income.
        if age < 20 or age > 75 or "在读" in employment:
            vehicle_plate = "无"
        else:
            final_salary = float(salary.replace("￥", "").replace(",", "")) if salary != "￥0" else 0
            # Tiered ownership probability
            if final_salary > 30000: car_prob = 0.90
            elif final_salary > 15000: car_prob = 0.65
            elif final_salary > 8000: car_prob = 0.35
            elif final_salary > 5000: car_prob = 0.10
            else: car_prob = 0.01
            
            # Slightly reduce probability in Tier 1 cities due to license plate lottery/restrictions
            if any(t1 in str(workplace_data.get('city', '')) for t1 in ["北京", "上海", "广州", "深圳"]):
                car_prob *= 0.7 
            
            if random.random() < car_prob:
                # Plate location strictly tied to life trajectory:
                # 60% chance it's registered in workplace city
                # 30% chance it's registered in hometown city
                # 10% chance it's registered in a random "education/other" city (simulating college/previous job)
                loc_choice = random.random()
                if loc_choice < 0.60:
                    plate_source = workplace_data
                elif loc_choice < 0.90:
                    plate_source = hometown_data
                else:
                    # Pick a completely random Tier 1/2 province to simulate college/previous work
                    edu_prov = self.random_element([p for p in areas if any(name in p['name'] for name in ["湖北", "江苏", "四川", "陕西", "广东", "山东", "辽宁"])])
                    plate_source = {
                        "province": edu_prov['name'], 
                        "plate_prefix": edu_prov.get('children', [{'name': 'A'}])[0].get('name', 'A') # Fallback roughly
                    }
                    # Re-resolve the actual plate prefix for this random province
                    plate_prefixes = {
                        "北京": "京", "天津": "津", "上海": "沪", "重庆": "渝", "河北": "冀",
                        "山西": "晋", "辽宁": "辽", "吉林": "吉", "黑龙江": "黑", "江苏": "苏",
                        "浙江": "浙", "安徽": "皖", "福建": "闽", "江西": "赣", "山东": "鲁",
                        "河南": "豫", "湖北": "鄂", "湖南": "湘", "广东": "粤", "海南": "琼",
                        "四川": "川", "贵州": "贵", "云南": "云", "陕西": "陕", "甘肃": "甘",
                        "青海": "青", "台湾": "台", "内蒙古": "蒙", "广西": "桂", "西藏": "藏",
                        "宁夏": "宁", "新疆": "新", "香港": "港", "澳门": "澳"
                    }
                    p_prefix = "京"
                    for k, v in plate_prefixes.items():
                        if k in edu_prov['name']:
                            p_prefix = v
                            break
                    city_ltr = self.random_element("ABCDEFGHJKLMNPQRSTUVWXYZ")
                    plate_source['plate_prefix'] = f"{p_prefix}{city_ltr}"
                
                # New Energy Vehicles (Green Plates) account for roughly 10% currently, but growing.
                is_nev = random.random() < 0.15
                
                if is_nev:
                    # NEV plates are 6 digits (e.g., 粤B·D12345 or 粤B·12345D)
                    # D means pure electric, F means hybrid
                    nev_type = self.random_element(["D", "F"])
                    suffix = f"{nev_type}{self.random_int(10000, 99999)}" if random.random() > 0.5 else f"{self.random_int(10000, 99999)}{nev_type}"
                else:
                    # Standard 5 chars, omitting I and O
                    suffix = "".join(self.random_element("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789") for _ in range(5))
                    
                target_prefix = "京A"
                if 'plate_prefix' in plate_source:
                    target_prefix = plate_source['plate_prefix']
                else:
                    plate_prefixes = {
                        "北京": "京", "天津": "津", "上海": "沪", "重庆": "渝", "河北": "冀",
                        "山西": "晋", "辽宁": "辽", "吉林": "吉", "黑龙江": "黑", "江苏": "苏",
                        "浙江": "浙", "安徽": "皖", "福建": "闽", "江西": "赣", "山东": "鲁",
                        "河南": "豫", "湖北": "鄂", "湖南": "湘", "广东": "粤", "海南": "琼",
                        "四川": "川", "贵州": "贵", "云南": "云", "陕西": "陕", "甘肃": "甘",
                        "青海": "青", "台湾": "台", "内蒙古": "蒙", "广西": "桂", "西藏": "藏",
                        "宁夏": "宁", "新疆": "新", "香港": "港", "澳门": "澳"
                    }
                    p_prefix = "京"
                    for k, v in plate_prefixes.items():
                        if k in str(plate_source.get('province', '')):
                            p_prefix = v
                            break
                    target_prefix = f"{p_prefix}{self.random_element('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
                    
                vehicle_plate = f"{target_prefix}·{suffix}"
            else:
                vehicle_plate = "无"

        # Web Devices Based on Persona properties
        final_salary = float(salary.replace("￥", "").replace(",", "")) if salary != "￥0" else 0
        if final_salary > 15000 or any(kw in job for kw in ["高管", "CEO", "总裁", "总监"]):
            # High income: iOS highly popular, Harmony strong, Android less dominant
            os_choices_weights = [("iOS 17", 0.45), ("HarmonyOS 4", 0.35), ("macOS Sonoma", 0.1), ("Android 14", 0.1)]
            ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" if random.random() > 0.5 else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        elif final_salary > 6000:
            # Middle income: Android leading, Harmony and iOS balanced
            os_choices_weights = [("Android 14", 0.50), ("HarmonyOS 4", 0.25), ("iOS 17", 0.20), ("Windows 11", 0.05)]
            ua = self.generator.user_agent()
        else:
            # Low income / Students: Android dominant (~75%), some HarmonyOS/iOS
            os_choices_weights = [("Android 13", 0.45), ("Android 14", 0.30), ("HarmonyOS 3", 0.15), ("iOS 16", 0.08), ("Windows 10", 0.02)]
            ua = self.generator.user_agent()
            
        r_val = random.random()
        upto = 0
        os_name = os_choices_weights[-1][0]
        for v, w in os_choices_weights:
            if upto + w > r_val:
                os_name = v
                break
            upto += w
            
        os_name = kwargs.get("os") or os_name
        ua = kwargs.get("user_agent") or ua
        
        # Only computer industry workers get a personal web home domain
        is_tech = any(kw in job for kw in ["架构师", "程序员", "开发", "IT", "互联网", "软件", "系统", "算法", "后端", "前端", "网络"])
        if is_tech:
            web_home_domain = self.random_element(["github.io", "me", "com", "net", "org", "io"])
            web_home = kwargs.get("web_home") or f"https://{username}.{web_home_domain}"
        else:
            web_home = kwargs.get("web_home") or "无"

        # Contextual Security Question/Answer
        sec_pairs = [
            ("你母亲的名字叫什么？", self.random_element(["王淑芳", "李美玲", "张爱华", "刘兰英"])),
            ("你出生在哪个城市？", hometown_data['city']),
            ("你的首只宠物的中文名字？", self.random_element(["小花", "大黄", "球球", "皮皮"])),
            ("你的小学老师姓什么？", self.random_element(["陈", "周", "吴", "郑", "何"]))
        ]
        chosen_pair = self.random_element(sec_pairs)
        sec_q = kwargs.get("security_question") or chosen_pair[0]
        sec_a = kwargs.get("security_answer") or chosen_pair[1]

        result = {
            "name": name,
            "gender": gender_val,
            "age": age,
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "ssn": ssn,
            "email": email,
            "yopmail": yopmail_account,
            "yopmail_url": yopmail_url,
            "username": username,
            "password": strong_password,
            "strong_password": strong_password,
            "common_password": common_password,
            "common_password_upper": common_password_upper,
            "ethnicity": ethnicity,
            "bank_card": bank_card,
            "bank_name": bank_name,
            "mbti": mbti,
            "physical": {
                "height": height,
                "weight": weight,
                "blood_type": blood_type
            },
            "hometown": {
                "province": hometown_data['province'],
                "city": hometown_data['city'],
                "area": hometown_data['area'],
                "address": hometown_data['address'],
                "postcode": self._generate_realistic_postcode(
                    full_pc_index,
                    hometown_data['province'], 
                    hometown_data['city'], 
                    hometown_data['area']
                )
            },
            "workplace": {
                "province": workplace_data['province'],
                "city": workplace_data['city'],
                "area": workplace_data['area'],
                "address": workplace_data['address'],
                "company_name": workplace_data.get('company_name', "无"),
                "company_uscc": workplace_data.get('company_uscc', "无")
            },
            "asset": {
                "vehicle_plate": vehicle_plate
            },
            "primary_phone": {
                "number": primary_phone,
                "location": workplace_data['city'] if workplace_data['city'] not in ["市辖区", "县", "省直辖县级行政区划"] else workplace_data['province']
            },
            "social": {
                "education": education,
                "employment": employment,
                "job": job,
                "salary": salary,
                "marital_status": marital_status,
                "security_question": sec_q,
                "security_answer": sec_a
            },
            "internet": {
                "guid": guid,
                "user_agent": ua,
                "os": os_name,
                "web_home": web_home
            }
        }

        # 7. Secondary Phone / Work location
        if has_second_phone:
            if not work_province:
                other_provs = [p for p in areas if p['name'] != prov_name]
                if not other_provs:
                    other_provs = areas
                w_prov = self.random_element(other_provs)
                work_prov_name = w_prov['name']
                w_city_list = w_prov.get('children', [w_prov])
                w_city = self.random_element(w_city_list)['name']
            else:
                work_prov_name = work_province
                work_city_list = next((p.get('children', [p]) for p in areas if work_province in p['name']), areas)
                w_city = work_city if work_city else self.random_element(work_city_list)['name']

            w_addr_prov_key = work_prov_name.replace("市", "").replace("省", "").replace("自治区", "")
            w_addr_city = w_city
            if w_addr_prov_key in ["北京", "上海", "天津", "重庆"] and w_city in ["市辖区", "县"]:
                w_addr_city = ""
            elif w_city in ["省直辖县级行政区划", "自治区直辖县级行政区划"]:
                w_addr_city = ""

            secondary_phone = self._get_phone_number(phones, work_prov_name, w_city)
            result["secondary_phone"] = {
                "number": secondary_phone,
                "location": f"{work_prov_name}{w_addr_city}" if w_addr_city else work_prov_name
            }
            result["work_location"] = {
                "province": work_prov_name,
                "city": w_city
            }
        elif not has_second_phone and "secondary_phone" in result:
            del result["secondary_phone"]

        # 8. Add AI story
        if use_ai:
            from .ai_story import generate_ai_story, generate_ai_image
            config = ai_config or {}
            ai_data = generate_ai_story(result, config)
            if ai_data:
                result.update(ai_data)
                
            # 9. Optional: Generate AI Avatar Image
            img_key = config.get("image_api_key")
            if img_key and "image_prompt" in result:
                img_url = generate_ai_image(result["image_prompt"], img_key)
                if img_url:
                    result["avatar_url"] = img_url

        if fields:
            return self._filter_by_fields(result, fields)

        return result

    def _get_phone_number(self, phones, p_name: str, c_name: str):
        p_key = p_name.replace("市", "").replace("省", "").replace("自治区", "")
        matched_prov = next((k for k in phones.keys() if p_key in k or k in p_key), None)
        if matched_prov:
            city_dict = phones[matched_prov]
            c_key = c_name.replace("市", "").replace("地区", "").replace("盟", "")
            if p_key in ["北京", "上海", "天津", "重庆"] and c_key in ["辖区", "市辖区", "县"]:
                c_key = p_key
            matched_city = next((k for k in city_dict.keys() if c_key in k or k in c_key), None)
            if matched_city:
                prefixes = city_dict[matched_city]
                if prefixes:
                    prefix = self.random_element(prefixes)
                    suffix = f"{self.random_int(min=0, max=9999):04d}"
                    return f"{prefix}{suffix}"
        try: return self.generator.phone_number()
        except AttributeError: return f"13{self.random_int(min=0,max=9)}{self.random_int(min=0,max=99999999):08d}"

    def era_given_name(self, birth_year: Optional[int] = None, gender: Optional[str] = None) -> str:
        if not gender:
            gender = random.choices(['男', '女'], weights=[51.24, 48.76], k=1)[0]
        is_m = gender in ['男', 'M']

        if birth_year is None:
            age_bucket = random.choices(["0-14", "15-59", "60-90"], weights=[17.95, 63.35, 18.70], k=1)[0]
            if age_bucket == "0-14":
                age = self.random_int(1, 14)
            elif age_bucket == "15-59":
                age = self.random_int(15, 59)
            else:
                age = self.random_int(60, 90)
            birth_year = date.today().year - age

        # 1. 性别与时代的特征字库 (Strict Era & Gender Separation)
        # 传统 (Pre-1970)：倾向于强壮、报国、温婉、家务
        traditional_m = ["军", "国", "建", "华", "平", "伟", "强", "勇", "明", "涛", "正", "辉", "力", "永", "才", "援朝", "跃进", "胜", "卫东", "志", "德", "宝", "铁", "贵", "根"]
        traditional_f = ["兰", "梅", "英", "珍", "芬", "芳", "秀", "娟", "萍", "琴", "云", "莲", "玲", "巧", "桂", "芝", "秀英", "桂兰", "玉华", "凤", "香", "红", "霞", "娣", "妹"]
        
        # 中期 (1970-1990)：单字多，追求中性、稳重或文雅
        mid_m = ["杰", "磊", "超", "斌", "鹏", "鑫", "峰", "健", "新", "飞", "博", "涛", "洋", "明", "毅", "宇", "帅", "辉", "亮", "伟", "勇", "刚", "强", "平"]
        mid_f = ["静", "敏", "燕", "雪", "婷", "莉", "娜", "丹", "倩", "莹", "琳", "慧", "洁", "微", "露", "丽", "芳", "娟", "艳", "秀", "萍", "梅", "玲", "云"]
        
        # 千禧 (1990-2010)：双字增多，注重文化氛围
        millennium_m = ["宇", "航", "浩", "轩", "泽", "睿", "渊", "皓", "哲", "晨", "铭", "豪", "俊", "杰", "凡", "鑫", "宇轩", "浩宇", "俊杰", "子轩", "浩然"]
        millennium_f = ["欣", "怡", "涵", "萱", "彤", "琪", "悦", "馨", "瑶", "语", "妍", "玥", "雨", "佳", "欣怡", "梓涵", "紫涵", "可馨", "梦瑶", "诗涵"]

        # 现代 (2010+)：古风、诗意、偏网文气质
        modern_m = ["浩宇", "子轩", "宇轩", "浩然", "梓睿", "铭泽", "子墨", "宇航", "嘉木", "一凡", "子安", "沐宸", "俊熙", "奕辰", "宇辰", "浩轩", "沐阳", "亦辰"]
        modern_f = ["梓涵", "欣怡", "梓萱", "语彤", "雨琪", "芯冉", "子涵", "诗涵", "梦瑶", "思语", "若曦", "语珂", "悠然", "婉清", "芷若", "沐瑶", "语嫣"]

        generic_prob = 0.2
        if birth_year < 1970:
            trad_prob, mid_prob, mil_prob = 0.70, 0.10, 0.0
        elif birth_year < 1990:
            trad_prob, mid_prob, mil_prob = 0.10, 0.60, 0.10
        elif birth_year < 2010:
            trad_prob, mid_prob, mil_prob = 0.05, 0.15, 0.40
        else: # 2010+
            trad_prob, mid_prob, mil_prob = 0.01, 0.04, 0.15

        r_val = random.random()
        if r_val < generic_prob:
             return self.generator.first_name_male() if is_m else self.generator.first_name_female()
        elif r_val < generic_prob + trad_prob:
             return self.random_element(traditional_m) if is_m else self.random_element(traditional_f)
        elif r_val < generic_prob + trad_prob + mid_prob:
             return self.random_element(mid_m) if is_m else self.random_element(mid_f)
        elif r_val < generic_prob + trad_prob + mid_prob + mil_prob:
             return self.random_element(millennium_m) if is_m else self.random_element(millennium_f)
        else:
             return self.random_element(modern_m) if is_m else self.random_element(modern_f)

    def era_name(self, birth_year: Optional[int] = None, gender: Optional[str] = None) -> str:
        """
        Generate a highly realistic Chinese full name matching the historical era and gender.
        """
        surname = self.generator.last_name()
        given_name = self.era_given_name(birth_year, gender)
        return f"{surname}{given_name}"

    def name(self) -> str:
        return self.era_name()

    def name_male(self) -> str:
        return self.era_name(gender='男')

    def name_female(self) -> str:
        return self.era_name(gender='女')
        
    def first_name(self) -> str:
        return self.era_given_name()

    def first_name_male(self) -> str:
        return self.era_given_name(gender='男')

    def first_name_female(self) -> str:
        return self.era_given_name(gender='女')

    def _generate_realistic_postcode(self, full_pc_index, p_n, c_n, a_n):
        # Precision candidates (Specific to General)
        # Handle Municipality redundancy (e.g., Beijing Beijing)
        clean_p = p_n.replace('省','').replace('市','').replace('自治区','')
        clean_c = c_n.replace('市','').replace('地区','').replace('盟','')
        
        candidates = [
            f"{p_n}{c_n}{a_n}",
            f"{clean_p}{c_n}{a_n}",
            f"{c_n}{a_n}",
            a_n, # Direct County/District match (vulnerable to duplicate names, but usually fine in context)
            f"{p_n}{c_n}",
            p_n
        ]
        for cand in candidates:
            if cand in full_pc_index:
                return full_pc_index[cand]
        
        # Fallback to prefix-based random generation if not in DB
        prefix = "00"
        postcode_map = {
            "北京": "10", "上海": "20", "天津": "30", "重庆": "40",
            "辽宁": "11", "吉林": "13", "黑龙江": "15", "江苏": "21",
            "浙江": "31", "安徽": "23", "福建": "35", "内蒙古": "01",
            "江西": "33", "山东": "25", "河南": "45", "湖北": "43",
            "湖南": "41", "广东": "51", "广西": "53", "海南": "57",
            "四川": "61", "贵州": "55", "云南": "65", "西藏": "85",
            "陕西": "71", "甘肃": "73", "青海": "81", "宁夏": "75",
            "新疆": "83", "河北": "05", "山西": "03"
        }
        for k, v in postcode_map.items():
            if k in p_n:
                prefix = v
                break
        return f"{prefix}{self.random_int(min=0, max=9999):04d}"

    def _get_realistic_blood(self):
        bt = self.random_element(["O"] * 32 + ["A"] * 28 + ["B"] * 30 + ["AB"] * 10)
        rh = "-" if random.random() < 0.003 else "+"
        return f"{bt}{rh}"

    def _get_pinyin_initials(self, name: str) -> str:
        res = ""
        for char in name:
            p = self._pinyin_map.get(char, "")
            if p:
                res += p[0]
            else:
                # Fallback to a random consonant if not in map to maintain structure
                res += self.random_element("abcdefghjklmnopqrstuvwxyz")
        return res

    def _get_linked_identity(self, full_name: str):
        # If name is '张三', try 'zhangsan', 'san.zhang', etc.
        surname = full_name[0]
        pinyin_prefix = self._pinyin_map.get(surname, "")
        if pinyin_prefix:
            variant = self.random_element([
                f"{pinyin_prefix}.{self.random_int(10, 999)}",
                f"{pinyin_prefix}{self.random_int(1980, 2010)}",
                f"{self.generator.user_name()[:3]}.{pinyin_prefix}"
            ])
            return variant
        return self.generator.user_name()

    def _generate_weighted_email(self, un: str, a: int, job_title: str):
        r = random.random()
        
        # Identify if the job requires/allows access to international services
        is_tech_foreign = any(kw in job_title for kw in ["架构师", "程序员", "开发", "IT", "研究员", "科学家", "外贸", "外资"])
        
        if a < 25:
            # Young/Student: Extreme QQ dominance (approx 80%), some 163 (15%)
            providers = [("qq.com", 0.80), ("163.com", 0.15), ("outlook.com", 0.04)]
            if is_tech_foreign: providers.append(("gmail.com", 0.01))
            else: providers.append(("126.com", 0.01))
        elif a < 45:
            # Working age: Mixed. QQ heavily popular but 163/126 catches up for work.
            providers = [("qq.com", 0.50), ("163.com", 0.35), ("126.com", 0.05), ("foxmail.com", 0.05), ("outlook.com", 0.03)]
            if is_tech_foreign: providers.append(("gmail.com", 0.02))
            else: providers.append(("yeah.net", 0.02))
        else:
            # Older: 163, qq dominant
            providers = [("163.com", 0.45), ("qq.com", 0.40), ("sina.com", 0.10), ("126.com", 0.03), ("hotmail.com", 0.02)]
        
        total = sum(w for p, w in providers)
        rand_val = random.uniform(0, total)
        upto = 0
        chosen_domain = providers[0][0]
        for p, w in providers:
            if upto + w >= rand_val:
                chosen_domain = p
                break
            upto += w
        return f"{un}@{chosen_domain}"

    def _get_realistic_job(self):
        rare_keywords = [
            "星探", "经纪人", "体验师", "鉴定师", "潜水", "飞行", "演艺", "教练", 
            "CEO", "总裁", "总经理", "总监", "首席", "外交", "基金经理", "操盘手", 
            "架构师", "科学家", "研究员", "高级", "专家", "舰长", "法官", "检察", "市长"
        ]
        # Statistically shift jobs to grassroots level
        for _ in range(50):  # Prevent infinite loop, increased attempts to find normal jobs
            candidate = self.generator.job()
            if not any(kw in candidate for kw in rare_keywords):
                # To enforce "70% < 5000", if it's a regular white-collar job, slightly decrease its chance compared to blue collar
                # We skip this deep filtering logic here as salaries are bound directly, but keeping high-end role scarcity is enough
                return candidate
            if random.random() < 0.005:  # 0.5% drop rate for rare / elite jobs
                return candidate
        return "销售员" # Fallback to a very common job if loop fails

    def _get_salary_by_job(self, job_name, job_salary_mapping, city_factor, rural_factor):
        base_val = 8000
        for keywords, range_vals in job_salary_mapping:
            if any(kw in job_name for kw in keywords):
                base_val = self.random_int(min=range_vals[0], max=range_vals[1])
                break
        
        # Apply multipliers
        final_val = float(base_val) * city_factor * rural_factor
        return f"￥{int(final_val // 100 * 100)}"

    def _generate_luhn(self, prefix, length=19):
        digits = [int(d) for d in str(prefix)]
        while len(digits) < length - 1:
            digits.append(self.random_int(0, 9))
        
        # Luhn calculation
        checksum = 0
        for i, d in enumerate(reversed(digits)):
            if i % 2 == 0:
                d *= 2
                if d > 9: d -= 9
            checksum += d
        check_digit = (10 - (checksum % 10)) % 10
        digits.append(check_digit)
        return "".join(map(str, digits))

class Provider(PersonaProvider):
    pass

