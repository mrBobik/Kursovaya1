import requests
import datetime
import os.path
import progressbar
import json

results_json = []


class YaUploader:
    def __init__(self, token):
        self.token = TOKEN

    def get_headers(self):
        return {'Content-Type': 'application/json', 'Accept': 'application/json',
                'Authorization': f'OAuth {self.token}'}

    def _get_upload_link(self, file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': file_path, 'overwrite': 'true'}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def create_folder(self, path):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': path}
        response = requests.put(url, params=params, headers=headers)
        if response.status_code == 201:
            print(f'Создана папака "{"VK_Id_" + vk_id}" на Яндекс.Диске')
        else:
            print(response.json()['message'])

    def upload(self, file_path, file_name):
        result = self._get_upload_link(file_path=file_path)
        href = result.get('href', '')
        response = requests.put(href, data=open(file_name, 'rb'))
        response.raise_for_status()


def make_local_folder():
    if os.path.exists("VK_Id_" + vk_id):
        pass
    else:
        os.mkdir("VK_Id_" + vk_id)


def download_vk_photos():
    ya = YaUploader(token=TOKEN)
    with open('vk_token.txt', 'r') as file:
        token = file.read()
    url = 'https://api.vk.com/method/users.get'
    params = {'user_ids': vk_id, 'access_token': token, 'v': '5.131'}
    response_vk = requests.get(url, params=params)
    vk_id_photo = response_vk.json()['response'][0]['id']
    url = 'https://api.vk.com/method/photos.get'
    params = {'owner_id': vk_id_photo, 'album_id': 'profile', 'extended': '1', 'photo_sizes': '1',
              'count': photos_count,
              'access_token': token, 'v': '5.131'}
    response = requests.get(url, params=params)
    if 'error' in response.json():
        print(f'ОШИБКА: {response.json()["error"]["error_msg"]}')
    else:
        make_local_folder()
        ya.create_folder("VK_Id_" + vk_id)
        for i in response.json().values():
            bar_count = 0
            bar = progressbar.ProgressBar(maxval=photos_count).start()
            for j in i['items']:
                url = j['sizes'][-1]['url']
                filename = f"{j['likes']['count']}.jpg"
                date = datetime.datetime.fromtimestamp(j['date'])
                results = {}
                if os.path.isfile(f'{"VK_Id_" + vk_id}/{filename}') is False:
                    filename = f"{j['likes']['count']}.jpg"
                    response = requests.get(url)
                    # results ={}
                    if response.status_code == 200:
                        with open(f'{"VK_Id_" + vk_id}/{filename}', 'wb') as file:
                            file.write(response.content)
                            ya.upload(f'{"VK_Id_" + vk_id}/{filename}', f'{"VK_Id_" + vk_id}/{filename}')
                            results['file_name'] = filename
                            results['size'] = j['sizes'][-1]['type']
                            results_json.append(results)
                else:
                    filename = f"{j['likes']['count']}_{date.strftime('%d-%m-%Y')}.jpg"
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(f'{"VK_Id_" + vk_id}/{filename}', 'wb') as file:
                            file.write(response.content)
                            ya.upload(f'{"VK_Id_" + vk_id}/{filename}', f'{"VK_Id_" + vk_id}/{filename}')
                            results['file_name'] = filename
                            results['size'] = j['sizes'][-1]['type']
                            results_json.append(results)
                bar_count += 1
                bar.update(bar_count)
            bar.finish()
            upload_result_json()
            ya.upload(f'{"VK_Id_" + vk_id}/results_json.txt', f'{"VK_Id_" + vk_id}/results_json.txt')


def upload_result_json():
    with open(f'{"VK_Id_" + vk_id}/results_json.txt', 'w+') as file:
        file.write(json.dumps(results_json))


if __name__ == '__main__':
    photos_count = int(input('Введите число фотографий, которые вы хотите скачать: '))
    vk_id = input('Введите ВК ID: ')
    token = input('Введите токен с Полигона Яндекс.Диска: ')
    with open('ya-disk_token.txt', 'w+') as file:
        file.write(token)
    with open('ya-disk_token.txt', 'r') as file:
        TOKEN = file.read()
    download_vk_photos()
