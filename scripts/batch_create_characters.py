"""批量创建角色卡 + 导入大纲"""
import subprocess, json, os
from pathlib import Path

PROJECT = Path("D:/Novel-Forge")
os.chdir(str(PROJECT))

# ============== 角色数据 ==============
characters = {
    # ===== 4 主角 =====
    "苏晚晴": {
        "core": "外柔内韧",
        "identity": "旧时光咖啡馆店主，28岁",
        "habits": "整理吧台时会把所有杯子把手朝同一方向摆；紧张时会摸左手无名指的旧茧（以前握笔的位置）；洗杯子时数数",
        "dialect": "标准普通话，语调偏平，着急时会轻微结巴",
        "mental": {"state": "慢性焦虑", "trigger": "财务压力/母亲遗物相关", "manifest": "失眠时反复核对账目"},
    },
    "陆沉舟": {
        "core": "克制内敛",
        "identity": "前开发商法务，独立执业律师，32岁",
        "habits": "思考时转笔，笔永远是同一支银色钢笔；抽烟只抽一个牌子，抽完一根会立刻把烟盒捏扁再扔",
        "dialect": "话少，逻辑严密，措辞精准，带轻微北方口音",
        "mental": {"state": "情感隔离", "trigger": "提及父亲/童年相关", "manifest": "遇到情绪冲击时会用工作逃避"},
    },
    "沈栀": {
        "core": "直率温暖",
        "identity": "独立书店老板，24岁",
        "habits": "说话时会用手比划；喜欢给别人推荐书，推荐时眼睛会发亮；收集各种奇怪的书签",
        "dialect": "语速快，爱用语气词，偶尔蹦英文单词",
        "mental": {"state": "轻度孤独", "trigger": "独自一人过节", "manifest": "会刻意延长营业时间"},
    },
    "林述": {
        "core": "沉稳清醒",
        "identity": "建筑师，陆沉舟大学室友，35岁",
        "habits": "随身带卷尺，看到建筑就会量；喝咖啡只喝美式，不喝任何花式咖啡",
        "dialect": "语调平淡，喜欢用比喻，引用建筑术语",
        "mental": {"state": "职业倦怠", "trigger": "面对不合理设计需求", "manifest": "频繁换项目组"},
    },
    # ===== 20 配角 =====
    "周姐": {
        "core": "热心泼辣",
        "identity": "老街五金店老板娘，52岁",
        "habits": "围裙口袋里永远装着零钱和创可贴",
        "dialect": "本地话，语速快，爱管闲事",
    },
    "陈伯": {
        "core": "固执念旧",
        "identity": "老街修表匠，68岁",
        "habits": "每天下午三点泡一壶铁观音",
        "dialect": "慢，带口音，说话像在念经",
    },
    "赵远": {
        "core": "老实本分",
        "identity": "苏晚晴的表弟，大学生，22岁",
        "habits": "紧张时会揪衣角",
        "dialect": "说话带网络用语，爱用'就是说'",
    },
    "开发商老张": {
        "core": "精明世故",
        "identity": "开发公司项目总监，50岁",
        "habits": "开会时不停转手上的金戒指",
        "dialect": "官腔十足，爱说'这个嘛'",
    },
    "孙秘书": {
        "core": "冷淡专业",
        "identity": "开发商行政秘书，30岁",
        "habits": "打字极快，从不抬头看人",
        "dialect": "标准职场用语，不带任何情绪",
    },
    "刘主任": {
        "core": "圆滑保守",
        "identity": "街道办事处主任，55岁",
        "habits": "保温杯不离手",
        "dialect": "打官腔，爱说'按程序来'",
    },
    "小陈": {
        "core": "热心乐观",
        "identity": "苏晚晴大学同学，记者，29岁",
        "habits": "采访时总是先请对方喝东西",
        "dialect": "语速快，跳跃性强",
    },
    "吴师傅": {
        "core": "沉默寡言",
        "identity": "老街修鞋匠，62岁",
        "habits": "修鞋时咬着一根没点燃的烟",
        "dialect": "几乎不说话，能用一个字回答绝不用两个",
    },
    "赵阿姨": {
        "core": "善良碎嘴",
        "identity": "老街早餐店老板娘，56岁",
        "habits": "给每个熟客多夹一个煎蛋",
        "dialect": "大嗓门，整条街都能听到她说话",
    },
    "陆母": {
        "core": "沉默隐忍",
        "identity": "陆沉舟母亲，60岁",
        "habits": "织毛衣，织了拆拆了织",
        "dialect": "话极少，声音很轻",
        "mental": {"state": "轻度抑郁", "trigger": "提及亡夫", "manifest": "长时沉默"},
    },
    "方律师": {
        "core": "仗义正直",
        "identity": "陆沉舟前同事，45岁",
        "habits": "办公室堆满案卷",
        "dialect": "中气十足，爱说'我跟你讲'",
    },
    "小叶": {
        "core": "活泼迷糊",
        "identity": "咖啡馆兼职学生，20岁",
        "habits": "总是打碎杯子",
        "dialect": "元气少女式,爱用'超~~~'拉长音",
    },
    "王叔": {
        "core": "温和务实",
        "identity": "房地产中介，48岁",
        "habits": "口袋里随时掏出户型图",
        "dialect": "职业微笑式语气",
    },
    "李大爷": {
        "core": "暴躁直率",
        "identity": "老街老住户，70岁",
        "habits": "每天早上遛狗，狗绳是红颜色的",
        "dialect": "骂骂咧咧但心肠好",
    },
    "许医生": {
        "core": "冷静温和",
        "identity": "社区医院医生，40岁",
        "habits": "白大褂口袋里总有一支笔",
        "dialect": "温和，语速中等",
    },
    "何老板": {
        "core": "精明算计",
        "identity": "老街面馆老板，48岁",
        "habits": "算账时打算盘，不用计算器",
        "dialect": "精明，爱讨价还价",
    },
    "顾老师": {
        "core": "儒雅博学",
        "identity": "退休大学教师，72岁",
        "habits": "随身带一本旧书",
        "dialect": "咬文嚼字，引经据典",
    },
    "小米": {
        "core": "单纯善良",
        "identity": "沈栀书店店员，22岁",
        "habits": "在书上画小插图",
        "dialect": "软糯，像在撒娇",
    },
    "侯法官": {
        "core": "公正严谨",
        "identity": "民庭法官，50岁",
        "habits": "开庭前会把法袍叠整齐",
        "dialect": "法言法语，一字一句",
    },
    "董会计": {
        "core": "严谨刻板",
        "identity": "开发公司财务，45岁",
        "habits": "桌面永远整整齐齐",
        "dialect": "数字式表达，精确到小数点后两位",
    },
    "小杨": {
        "core": "热心冲动",
        "identity": "陆沉舟助理，26岁",
        "habits": "爱喝功能饮料",
        "dialect": "年轻人口气，爱说'没问题'",
    },
    "周平": {
        "core": "沉默可靠",
        "identity": "老街水果摊主，35岁",
        "habits": "总是把最好的水果留给老顾客",
        "dialect": "说话简短实在",
    },
    "陈姐": {
        "core": "热心八卦",
        "identity": "街角理发店老板娘，45岁",
        "habits": "剪刀永远在手上转",
        "dialect": "大嗓门，喜欢打听消息",
    },
    "老孟": {
        "core": "洒脱通透",
        "identity": "流浪画家，约50岁",
        "habits": "只画这条老街",
        "dialect": "神神叨叨但说话有哲理",
    },
}

# ===== 批量创建角色卡 =====
for name, data in characters.items():
    # 创建角色
    r = subprocess.run(["python", "novel.py", "character", "create", name],
                      capture_output=True, text=True, timeout=10)
    if r.returncode != 0:
        print(f"  [ERROR] create {name}: {r.stderr.strip()[:100]}")
        continue
    
    # 设置字段
    for field in ["core", "identity", "habits", "dialect"]:
        if field in data:
            r2 = subprocess.run(["python", "novel.py", "character", "edit", name, field, data[field]],
                               capture_output=True, text=True, timeout=10)
    
    # 设置精神状态
    if "mental" in data:
        m = data["mental"]
        r3 = subprocess.run(["python", "novel.py", "character", "mental", name, "set", "焦虑", "轻度"],
                           capture_output=True, text=True, timeout=10)
    
    print(f"  ✅ {name} ({data.get('identity','')[:20]})")

print(f"\n共创建 {len(characters)} 个角色卡")
