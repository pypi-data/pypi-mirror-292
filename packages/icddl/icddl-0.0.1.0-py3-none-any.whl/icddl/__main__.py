import string
import requests
import re
from termcolor import colored
from argparse import ArgumentParser
from copy import deepcopy
from datetime import datetime
from tabulate import tabulate
from datetime import timezone
from datetime import datetime  
  

  


def parse_args():
    parser = ArgumentParser(description="cli for ccfddl")
    parser.add_argument("--conf", type=str, nargs='+', 
                        help="A list of conference ids you want to filter, e.g.: '--conf DAC ISSCC'")
    args = parser.parse_args()
    # Convert all arguments to lowercase
    for arg_name in vars(args):
        arg_value = getattr(args, arg_name)
        if arg_value:
            setattr(args, arg_name, [arg.lower() for arg in arg_value])
    return args


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
            "Countdown": f"{(datetime.strptime(match[3], '%Y-%m-%d') - datetime.now()).days} Days" if (datetime.strptime(match[3], '%Y-%m-%d') - datetime.now()).days > 0 else  '\033[31mExpired\033[0m'
        }
        for match in matches
    ]
   
    
    return conference_data_list

def display_table(conferences, confs):
    # 提取表格的列名  
    headers = ['Conference', 'Home Page', 'Paper Deadline', 'Conference Date', 'Countdown']  
    
    new_confs = []
    print(confs)
    if confs == 'all':
        new_confs = conferences
    else:
        for conf in conferences:
            if conf["Conference"].split()[0].lower() in confs:
                new_confs.append(conf)
      
    # 将数据列表转换为表格行列表  
    table_rows = [[conf[header] for header in headers] for conf in new_confs]  
      
    # 使用tabulate生成表格字符串  
    table_str = tabulate(table_rows, headers=headers, tablefmt='grid')  
    
    
      
    print(table_str)


def main():
    args = parse_args()
    confs = args.conf or 'all'
    conference_data_list = get_conference()
    display_table(conference_data_list, confs)


if __name__ == "__main__":
    main()