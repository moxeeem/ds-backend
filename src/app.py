import io
import logging
from flask import Flask, request, jsonify
from models.plate_reader import PlateReader, InvalidImage
from image_provider_client import ImageProviderClient, ImageNotFoundError, ImageProviderTimeout, ImageProviderError


app = Flask(__name__)
plate_reader = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')
image_client = ImageProviderClient(base_url='http://89.169.157.72:8080', timeout=5)


def process_image(image_id):
    try:
        image_data = image_client.get_image(image_id)
        im = io.BytesIO(image_data)
        res = plate_reader.read_text(im)
        return {
            'plate_number': res,
            'error_type': None,
            'error_message': None
        }

    except ImageNotFoundError as e:
        return {
            'plate_number': None,
            'error_type': 'not_found',
            'error_message': str(e)
        }
    except ImageProviderTimeout as e:
        return {
            'plate_number': None,
            'error_type': 'timeout',
            'error_message': str(e)
        }
    except ImageProviderError as e:
        return {
            'plate_number': None,
            'error_type': 'provider_error',
            'error_message': str(e)
        }
    except InvalidImage as e:
        return {
            'plate_number': None,
            'error_type': 'invalid_image',
            'error_message': 'Invalid image'
        }


@app.route('/read_plate/<int:image_id>', methods=['GET'])
def read_plate(image_id):
    processed = process_image(image_id)
    if processed['error_type'] is None:
        return jsonify({'plate_number': processed['plate_number']}), 200
    else:
        error_type = processed['error_type']
        error_msg = processed['error_message']

        if error_type == 'not_found':
            return jsonify({'error': error_msg}), 404
        elif error_type == 'timeout':
            return jsonify({'error': error_msg}), 504
        elif error_type == 'invalid_image':
            return jsonify({'error': error_msg}), 400
        else:
            return jsonify({'error': error_msg}), 500


@app.route('/batch_read_plates', methods=['POST'])
def batch_read_plates():
    data = request.get_json()
    if not data or 'image_ids' not in data:
        return jsonify({'error': 'Missing image_ids in request'}), 400

    image_ids = data['image_ids']
    if not isinstance(image_ids, list):
        return jsonify({'error': 'image_ids must be a list'}), 400

    results = []
    for img_id in image_ids:
        if not isinstance(img_id, int):
            results.append({
                'image_id': img_id,
                'plate_number': None,
                'error': 'Invalid image ID format (must be integer)'
            })
            continue

        processed = process_image(img_id)

        if processed['error_type'] is None:
            results.append({
                'image_id': img_id,
                'plate_number': processed['plate_number'],
                'error': None
            })
        else:
            results.append({
                'image_id': img_id,
                'plate_number': None,
                'error': processed['error_message']
            })

    return jsonify({'results': results}), 200


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080)
