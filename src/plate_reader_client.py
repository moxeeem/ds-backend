import requests


class PlateReaderClient:
    def __init__(self, host):
        self.host = host

    def read_plate(self, image_id):
        response = requests.get(f'{self.host}/read_plate/{image_id}')
        response.raise_for_status()
        return response.json()

    def batch_read_plates(self, image_ids):
        response = requests.post(
            f'{self.host}/batch_read_plates',
            json={'image_ids': image_ids}
        )
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    client = PlateReaderClient('http://89.169.157.72:8080')
    print(client.read_plate(10022))
    print(client.batch_read_plates([10022, 9965]))
