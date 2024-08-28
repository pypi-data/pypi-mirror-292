import string
import requests
import re
import yaml
import arxiv
from termcolor import colored
from argparse import ArgumentParser
from copy import deepcopy
from datetime import datetime, timedelta
from tabulate import tabulate
from datetime import timezone


def parse_args():
    parser = ArgumentParser(description="cli for ChatEDA")
    parser.add_argument('command', choices=['conference', 'journal', 'job', 'summit', 'competition', 'arxiv'], help='command to run') 
    
    # parser.add_argument("--job", type=str, nargs='+',
    #                     help="e.g.: '--job company'")
    # parser.add_argument("--summit", type=str, nargs='+',
    #                     help="e.g.: '--summit ai'")
    # parser.add_argument("--paper", type=str, nargs='+',
    #                     help="e.g.: '--paper arxiv'")
    # parser.add_argument("--competition", type=str, nargs='+',
    #                     help="e.g.: '--competition ic'")

    
    args = parser.parse_args()
    # # Convert all arguments to lowercase
    # for arg_name in vars(args):
    #     arg_value = getattr(args, arg_name)
    #     if arg_value:
    #         setattr(args, arg_name, [arg.lower() for arg in arg_value])
    return args


def color_days(ddl_time):
    days_dis = (datetime.strptime(ddl_time, '%Y-%m-%d') - datetime.now()).days
    if days_dis < 30 and days_dis > 0:
        countdown_time = f'\033[36m{days_dis} Days\033[0m'
    elif days_dis >= 30:
        countdown_time = f'\033[32m{days_dis} Days\033[0m'
    else:
        countdown_time = '\033[31mExpired\033[0m'
    
    return countdown_time


def get_conference():
    path = "https://www.cse.chalmers.se/research/group/vlsi/conference/"
    response = requests.get(path)
    response.raise_for_status()
    html = response.text
    pattern = r'<td><small><center>(.*?)</td>\s*<td><small><center><i><a href="(.*?)"[^>]*>(.*?)</a></td>\s*<td[^>]*><small><center><b>(.*?)</b></td>\s*<td[^>]*><small><center>(.*?)</td>'

    # 使用正则表达式提取信息
    matches = re.findall(pattern, html, re.DOTALL)
    
    conference_data_list = [
        {
            "Conference": match[0],
            "Home Page": match[1],
            "Paper Deadline": match[3],
            "Conference Date": match[4],
            "Countdown": color_days(match[3]),
        }
        for match in matches
    ]
    

    yml_str = requests.get("https://ccfddl.github.io/conference/allconf.yml").content.decode("utf-8")
    pattern = r'(?<!\n)\s*-title: NOMS(?:.*\n)+?(?=\s*-\s*title:|$)'  
    yml_str_list = yml_str.split('\n')
    for i,x in enumerate(yml_str_list):
        if "NOMS" in x:
            index_start = i
    yml_str_list_new = yml_str_list[0:index_start] + yml_str_list[index_start+18:]
    yml_str = '\n'.join(yml_str_list_new)  

    all_conf = yaml.safe_load(yml_str)
    
    architecture = ["ISCA", "HPCA", "MICRO", "ASPLOS"]
    robot = ["ICRA"]
    
    
    for cf in architecture+robot:
        for conf_ccf in all_conf:
            latest_conference = None  
            title = conf_ccf['title']  
            for conference in conf_ccf['confs']:  
                year = conference['year']  
                if latest_conference is None or year > latest_conference['year']:  
                    latest_conference = conference  
            
            conference = latest_conference  
            link = conference['link']  
            date = conference['date']  
            ddl_time = conference['timeline'][0]['deadline'].split()[0]
            
            if date not in ['TBD', 'Extended', 'To be announced']:
                date_year = date.split(", ")[1]
                
            if cf.lower() in conf_ccf["title"].lower():
                if date in ['TBD', 'Extended', 'To be announced']:
                    countdown_time = date
                else:
                    if ddl_time in ['TBD', 'Extended', 'To be announced']:
                        countdown_time = 'TBD'
                    else:
                        countdown_time = color_days(ddl_time)
                        
                conference_data_list.append({
                        "Conference": title,
                        "Home Page": link,
                        "Paper Deadline": ddl_time,
                        "Conference Date": date,
                        "Countdown": countdown_time,
                    })
    
    conference_data_list.append({
        "Conference": "MLCAD 2025",
        "Home Page": "https://mlcad.org/symposium/",
        "Paper Deadline": "2024-05-25",
        "Conference Date": "2024-09-09",
        "Countdown": '\033[31mExpired\033[0m'}
        )
    
    conference_data_list.append({
        "Conference": "ISEDA 2025",
        "Home Page": "https://www.eda2.com/conferenceHome/homePage?redirect=%2F",
        "Paper Deadline": "TBD",
        "Conference Date": "TBD",
        "Countdown": "TBD",}
        )
    
    
    
    return conference_data_list

def display_table(conferences):
    # 提取表格的列名  
    headers = ['Conference', 'Home Page', 'Paper Deadline', 'Conference Date', 'Countdown']  
    # print(confs)
    # new_confs = []
    # if confs == ['all']:
    #     new_confs = conferences
    # else:
    #     for conf in conferences:
    #         if conf["Conference"].split()[0].lower() in confs:
    #             new_confs.append(conf)
      
    table_rows = [[conf[header] for header in headers] for conf in conferences]  
    table_rows = sorted(table_rows, key=lambda row: row[2], reverse=True)
      
    table_str = tabulate(table_rows, headers=headers, tablefmt='grid')  
    
    
    
      
    print(table_str)



def journal_display():
    journals = [
            {"Journal": "Nature", "Type": "Comprehensive"},
            {"Journal": "Science", "Type": "Comprehensive"},
            {"Journal": "Nature Nanotechnology", "Type": "Comprehensive"},
            {"Journal": "Nature Physics", "Type": "Comprehensive"},
            {"Journal": "Nature Communication", "Type": "Comprehensive"},
            {"Journal": "Nature Electronics", "Type": "Comprehensive"},
            {"Journal": "IEEE Electron Device Letters", "Type": "Device"},
            {"Journal": "Journal of Solid-State Circuits", "Type": "Design"},
            {"Journal": "Transactions on circuits and systems I & II", "Type": "Design"},
            {"Journal": "IEEE Transactions on Very Large Scale Integration (VLSI) Systems", "Type": "Design"},
            {"Journal": "IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems", "Type": "EDA"},
            {"Journal": "Journal of Microelectromechanical Systems", "Type": "MEMS"},
        ]
    headers = ['Journal', 'Type']  
    
      
    table_rows = [[jour[header] for header in headers] for jour in journals]  
      
    table_str = tabulate(table_rows, headers=headers, tablefmt='grid')  
      
    print(table_str)



def show_company():
    # 省份和对应公司的列表  
    provinces_info = {  
        '上海': [  
            "概伦电子", "芯钬量子", "芯思维",  
            "弘快科技", "隼瞻科技", "曼光科技",  
            "思尔芯", "芯和半导体", "芯璐科技",  
            "鸿之微", "芯易荟", "冉普微",  
            "芯瑞微", "Max-Optics", "阿卡思微电子",  
            "伴芯科技", "合见工软", "立芯",  
            "巨霖科技", "速石科技"  
        ],  
        '江苏': [  
            "芯华章(南京)", "芯行纪(南京)", "九霄智能(南京)",  
            "培风图南(苏州)", "复鹄科技(苏州)",  
            "玖熠半导体(无锡)", "飞谱电子(无锡)", "汤谷智能(无锡)",  
            "亚科鸿禹(无锡)"  
        ],  
        '广东': [  
            "奇捷科技(深圳)", "比昂芯(深圳)",  
            "国微芯(深圳)", "鸿芯微纳(深圳)",  
            "嘉立创(深圳)", "睿晶聚源(珠海)", "硅芯科技(珠海)"  
        ],  
        '浙江': [  
            "广立微(杭州)", "行芯科技(杭州)",  
            "四维映射(杭州)", "华芯巨数(杭州)",  
            "弈芯科技(杭州)", "法动科技(杭州)",  
            "德图科技(宁波)", "为昕科技(宁波)",  
            "芯启元(湖州)", "雷娜科技(义乌)"  
        ],  
        '湖南': ["泛联新安(长沙)"],  
        '北京': [  
            "华大九天", "东方晶源",  
            "超逸达", "芯愿景",  
            "中科鉴芯", "智芯仿真",  
            "深维科技"  
        ],  
        '天津': ["蓝海微科技"],  
        '安徽': ["全芯智造(合肥)"],  
        '山东': ["启芯软件(济南)", "若贝电子(青岛)"],  
        '四川': ["英诺达(成都)", "派兹互连(成都)", "逍遥科技(成都)"],  
        '湖北': ["若贝科技(武汉)", "九同方(武汉)"]  
    }  
      
    # 创建一个列表，用于存储省份和对应公司的字符串表示  
    table_data = []  
      
    for province, companies in provinces_info.items():  
        # 将公司列表转换为由逗号分隔的字符串  
        company_str = ', '.join(companies)  
        company_count = len(companies)
        # 将省份和公司字符串添加到表格数据中  
        table_data.append([f"{province}({company_count})", company_str])  
      
    # 定义列标题  
    headers = ["省份", "公司列表"]  
      
    # 使用tabulate打印表格  
    print(tabulate(table_data, headers=headers, tablefmt='pretty'))




def display_summit():
    summit_info = [
            {"name":"第二届设计自动化产业峰会IDAS 2024", "time": "2024-0923-0924", "location": "上海"},
            {"name": "RISC_V中国峰会", "time": "2024-0821", "location": "杭州"},
            {"name": "2024全球AI芯片峰会（GACS 2024）", "time": "2024-0906-0907", "location": "北京"}
        ]
    
    headers = ['name', 'time', 'location']  
    
      
    table_rows = [[summit[header] for header in headers] for summit in summit_info]  
      
    table_str = tabulate(table_rows, headers=headers, tablefmt='grid')  
      
    print(table_str)


def display_competition():
    comp_info = [
            {"name": "EDA精英挑战赛", "link": "https://eda.icisc.cn/"},
            {"name": "全国大学生集成电路创新创业大赛", "link": "http://univ.ciciec.com/"},
            {"name": "ICCAD CAD Contest", "link": "https://www.iccad-contest.org/"},
            {"name": "ISPD", "link": "https://ispd.cc/"},
            {"name": "中国研究生创芯大赛", "link": "https://cpipc.acge.org.cn/cw/hp/10"},
            {"name": "复微杯", "link": "https://fuweibei.com/"},
        ]
    
    headers = ['name', 'link']  
    
      
    table_rows = [[comp[header] for header in headers] for comp in comp_info]  
      
    table_str = tabulate(table_rows, headers=headers, tablefmt='grid')  
      
    print(table_str)
    
    
def search_paper():
    now = datetime.now()   
    ten_days_ago = now - timedelta(days=10)  
    start_date = ten_days_ago.strftime("%Y%m%d")  
    end_date = now.strftime("%Y%m%d")

    keywords = ["circuit", "analog", "optimization", "layout", "automation", "sizing", "synthesis", "Chiplet", "3DIC", "Routing", "OPAMP"]  

    client = arxiv.Client()  
    results = []  

    for keyword in keywords:  
        search = arxiv.Search(
          query = f"submittedDate:[{start_date} TO {end_date}] AND {keyword}",
          max_results = 5,
          sort_by = arxiv.SortCriterion.SubmittedDate
        )
        try:  
            # 获取查询结果  
            for result in client.results(search):  
                if result not in results:  
                    results.append(result)  
        except Exception as e:  
            print(f"Error querying for '{keyword}': {e}")  
      
     
    res = []
    for result in results:  
        title = result.title  
        link = result.pdf_url
        res.append([title, link])  
        
    print(tabulate(res, headers=["Title", "Link"], tablefmt="pretty", colalign=("left", "left")))  



  
def main():

    args = parse_args()
    # if args.cj == ["conference"]:
    #     conference_data_list = get_conference()
    #     display_table(conference_data_list)
    # elif args.cj == ["journal"]:
    #     journal_display()
    # elif args.job == ["company"]:
    #     show_company()
    # elif args.summit == ["ai"]:
    #     display_summit()
    # elif args.competition == ["ic"]:
    #     display_competition()
    # elif args.paper == ["arxiv"]:
    #     search_paper()
    if args.command == "conference":
        conference_data_list = get_conference()
        display_table(conference_data_list)
    elif args.command == "journal":
        journal_display()
    elif args.command == "job":
        show_company()
    elif args.command == "summit":
        display_summit()
    elif args.command == "competition":
        display_competition()
    elif args.command == "arxiv":
        search_paper()
    else:
        print("hellow world!")


if __name__ == "__main__":
    main()