import json

with open('store_info.json', 'r', encoding='UTF-8') as f:
    crawling_list = json.load(f)
print(crawling_list)

new_list=[]
for crawling in crawling_list:
    new_data = {"model" : "main.store"}
    new_data["fields"] = {}
    new_data["fields"]["name"] = crawling
    new_list.append(new_data)

print(new_list)


    
with open('store_info3.json', 'w', encoding='UTF-8') as f:
    json.dump(new_list, f, ensure_ascii=False, indent=2)
