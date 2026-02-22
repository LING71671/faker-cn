import areasData from '../data/areas.json';

// Simple JS implementation of faker-cn core logic for the frontend
export class FakerCN {
    constructor() {
        this.areas = areasData;
    }

    randomElement(arr) {
        if (!arr || arr.length === 0) return null;
        return arr[Math.floor(Math.random() * arr.length)];
    }

    randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    generateName(gender) {
        const surnames = "王李张刘陈杨黄赵吴周徐孙马朱胡林郭何高罗郑梁谢唐宋韩曹许邓萧冯曾程蔡潘袁于董余苏叶吕魏蒋田杜丁沈姜范".split("");
        const maleNames = "伟强勇明涛军国建华平英浩宇轩子涵浩然梓轩".split("");
        const femaleNames = "华秀珍娟芳丽敏静雪燕琴婷曼凡佳蕾".split("");

        const surname = this.randomElement(surnames);
        const length = this.randomElement([1, 2]);
        let name = surname;
        const charPool = gender === '男' ? maleNames : femaleNames;

        for (let i = 0; i < length; i++) {
            name += this.randomElement(charPool);
        }
        return name;
    }

    generateSSN(areaCode, birthDateStr, isMale) {
        const seqCode = String(this.randomInt(0, 99)).padStart(2, '0');
        const genderDigit = isMale ? this.randomElement([1, 3, 5, 7, 9]) : this.randomElement([0, 2, 4, 6, 8]);
        const ssn17 = `${areaCode}${birthDateStr}${seqCode}${genderDigit}`;

        const weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2];
        const checkCode = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2'];

        let sumVal = 0;
        for (let i = 0; i < 17; i++) {
            sumVal += parseInt(ssn17[i]) * weight[i];
        }
        const checksum = checkCode[sumVal % 11];
        return `${ssn17}${checksum}`;
    }

    generateEmail(age, hasGmail = false) {
        const prefixes = ['xiaoming', 'zhangwei', 'lihua', 'coolboy', 'sunshine', 'dreamer', 'super', 'lucky'];
        const prefix = this.randomElement(prefixes) + this.randomInt(1980, 2010);

        if (hasGmail && Math.random() < 0.3) {
            return `${prefix}@gmail.com`;
        }

        if (age < 28) {
            return `${this.randomInt(100000000, 999999999)}@qq.com`; // Young prefer QQ
        }

        return `${prefix}@163.com`; // Older prefer 163
    }

    generatePersona() {
        // 1. Gender & Age
        const isMale = Math.random() < 0.51;
        const gender = isMale ? '男' : '女';
        const age = this.randomInt(18, 65);

        // 2. Birthdate
        const today = new Date();
        const birthYear = today.getFullYear() - age;
        const birthMonth = String(this.randomInt(1, 12)).padStart(2, '0');
        const birthDay = String(this.randomInt(1, 28)).padStart(2, '0');
        const birthDateStr = `${birthYear}${birthMonth}${birthDay}`;

        // 3. Hometown (Province -> City -> Area)
        const province = this.randomElement(this.areas);
        const city = this.randomElement(province.children || [province]);
        const area = this.randomElement(city.children || [city]);
        const areaCode = area.code || '110101';

        // 4. Name & SSN
        const name = this.generateName(gender);
        const ssn = this.generateSSN(areaCode, birthDateStr, isMale);

        // 5. Job & Assets
        const jobs = ["程序员", "产品经理", "外卖员", "网约车司机", "企业高管", "教师", "医生", "自由职业者", "保安", "UI设计师"];
        const job = this.randomElement(jobs);

        const isHighEnd = ["企业高管", "程序员", "医生"].includes(job);
        let salary = isHighEnd ? this.randomInt(15000, 50000) : this.randomInt(3000, 10000);

        const email = this.generateEmail(age, isHighEnd);

        // Asset
        const vehiclePrefixes = ["京A", "沪A", "粤B", "浙A", "苏A", "川A", "鄂A", "陕A"];
        const hasCar = salary > 8000 || Math.random() < 0.2;
        const isEV = Math.random() < 0.3;
        const platePrefix = this.randomElement(vehiclePrefixes);
        let vehiclePlate = "无";
        if (hasCar) {
            const letters = "ABCDEFGHJKLMNPQRSTUVWXYZ";
            const nums = "0123456789";
            let p = platePrefix + "·";
            if (isEV) p += "D";
            for (let i = 0; i < (isEV ? 5 : 5); i++) {
                p += this.randomElement(Math.random() > 0.3 ? nums.split('') : letters.split(''));
            }
            vehiclePlate = p;
        }

        const deposit = Math.round((salary * this.randomInt(5, 50)) / 10000) + "万";

        return {
            name,
            gender,
            age,
            birth_date: `${birthYear}-${birthMonth}-${birthDay}`,
            ssn,
            email,
            yopmail_login: email.split('@')[0],
            hometown: {
                province: province.name,
                city: city.name,
                area: area.name
            },
            social: {
                job,
                salary: `¥${salary}/月`
            },
            asset: {
                vehicle_plate: vehiclePlate,
                deposit
            }
        };
    }
}

export const fakerCN = new FakerCN();
