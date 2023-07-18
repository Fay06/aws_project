import requests
import json

types = ['Chinese', 'Japanese', 'Cafe', 'American', 'Mediterranean', 'Mexican', 'Asian', 'Italian', 'Burgers', 'Thai', 'Vegan', 'England', 'Indian', 'Russian']
cuisineType = types[13]
headers = {
    "accept": "application/json",
    "Authorization": "Bearer bFtdp81KgHR6yq74_kaNdo2Towd-ZHqIfhjulpO8RY7x_YTNl4wnFKBJhjLPOxjyvhf-VFXuxEl5E-e79g4pgibPIJYOJyYIT1hz2t9gzxaEWjjP_H-4VnJU4JvqY3Yx"
}
idSet = set()
restaurantList = []
for i in range(20):
    url = "https://api.yelp.com/v3/businesses/search?location=manhattan&term={0}%20food&sort_by=best_match&limit=50&offset={1}".format(cuisineType, str(50 * i))
    response = requests.get(url, headers=headers)
    responseText = response.text
    #print(responseText)
    resListText = json.loads(responseText)
    resList = resListText['businesses']
    for ele in resList:
        nowId = ele['id']
        if nowId not in idSet:
            restaurantList.append(ele)
            idSet.add(nowId)
    print(i)
print('length:', len(restaurantList))
f = open('./{0}Res.txt'.format(cuisineType), 'a')
f.write(json.dumps(restaurantList))