import re

stringa = '"Anchor_Text": "Li Wei"anChair Professormore"} "Anchor_Text": "Another Text"Another Professormore"}'
pattern = re.compile(r'"Anchor_Text": "(.*?)"}')

# 使用 findall 查找所有匹配
matches = pattern.findall(stringa)

# 如果有匹配，则去除匹配到的内容中的引号
if matches:
    for match in matches:
        replaced_match = match.replace('"', "'")
        stringa = stringa.replace(match, replaced_match)

    print(stringa)  # 打印修改后的字符串
else:
    print("No matches found.")
#
