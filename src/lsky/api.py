import requests
from conf.config import LSKY_API


class LskyAPI:
    def __init__(self):
        self.url = LSKY_API

    def headers(self,token) -> dict:
        return {
            'Authorization': 'Bearer '+ token,
            'User-Agent': 'yaoyue/lsky-api-client',
            'Accept': 'application/json'
        }
    
    def get(self, endpoint, token) -> dict:
        url = self.url + endpoint
        headers = self.headers(token)
        try:
            response = requests.get(url, headers=headers)
            return response.json()
        except:
            return {'status': 'error', 'message': response.text}
    
    def post(self, endpoint, token, data, files=None, headers=None) -> dict:
        url = self.url + endpoint
        if headers is None:
            headers = self.headers(token)
        try:
            response = requests.post(url, headers=headers, data=data, files=files)
            return response.json()
        except:
            return {'status': 'error', 'message': response.text}
    
    def upload_image(self, token, datas) -> dict:
        endpoint = '/upload'
        with open(datas['file'], 'rb') as file:
            files = {'file': file}
            try:
                response = self.post(endpoint, token, datas, files=files)
                links = response['data']['links']
                return {'status': 'True', 'links': links}
            except:
                return response
    
    def me(self, token) -> dict:
        ori = self.get('/profile', token)
        if ori['status'] == 'error':
            return ori
        elif ori['status'] == False:
            return {'status': False}
        return {
            'status': True,
            'username': ori['data']['username'],
            'name': ori['data']['name'],
            'email': ori['data']['email'],
            'capacity': ori['data']['capacity'],
            'used': ori['data']['size'],
            'image_num': ori['data']['image_num'],
            'albume_num': ori['data']['album_num']
        }
    
    def albums(self, token) -> list:
        ori = self.get('/albums', token)
        if ori['status'] == 'error':
            return ori
        albums = []
        for album in ori['data']['data']:
            albums.append({
                'id': album['id'],
                'name': album['name']
            })
        return {'status': True,'albums':albums}
    
    


# token = '3|yJCrAL6D5YulzzKkeGSn2aQECEaPLBtp9iEt4UCX'
# lsky = LskyAPI()
# # res = lsky.upload_image(token, {'file': 'data/hkhk.png', 'album_id': 8})
# res = lsky.me(token)['status']
# print(res)