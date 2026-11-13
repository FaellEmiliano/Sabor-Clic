"""Small shared image library. Uploads live outside the source tree."""
from io import BytesIO
from pathlib import Path
from uuid import uuid4
import warnings

from flask import current_app, jsonify, request, send_from_directory
from PIL import Image, ImageOps, UnidentifiedImageError
from app.controllers.http import fail, permit

STOCK = Path(__file__).resolve().parents[3] / 'FrontEnd/assets/img/products'
MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 20_000_000


def upload_dir():
    return Path(current_app.config['UPLOAD_FOLDER'])


def library_items():
    stock = [dict(caminho='/assets/img/products/' + p.name,
                  nome=p.stem.replace('-', ' ').capitalize(), origem='biblioteca')
             for p in sorted(STOCK.glob('*.jpg'))]
    uploads = [dict(caminho='/media/' + p.name, nome='Foto enviada ' + p.stem[:8], origem='upload')
               for p in sorted(upload_dir().glob('*.webp'), key=lambda p: p.stat().st_mtime, reverse=True)]
    return stock + uploads


def validate_image_path(value):
    if value is None or value == '':
        return None
    if not isinstance(value, str) or value not in {item['caminho'] for item in library_items()}:
        fail('Escolha uma imagem da biblioteca ou envie uma foto.')
    return value


def images():
    permit('administrador')
    if request.method == 'GET':
        return jsonify(imagens=library_items())
    file = request.files.get('foto')
    if file is None:
        fail('Envie uma foto no campo foto.')
    raw = file.stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        fail('A foto deve ter no máximo 5 MB.', 413)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw)) as source:
                if source.format not in ('JPEG', 'PNG', 'WEBP'):
                    fail('Use uma foto JPEG, PNG ou WebP.')
                if source.width * source.height > MAX_PIXELS:
                    fail('A foto deve ter no máximo 20 megapixels.')
                image = ImageOps.exif_transpose(source)
                image.thumbnail((1200, 1200))
                image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
                output = BytesIO()
                image.save(output, format='WEBP', quality=82)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        fail('Arquivo inválido. Use uma foto JPEG, PNG ou WebP de até 20 megapixels.')
    directory = upload_dir()
    directory.mkdir(parents=True, exist_ok=True)
    filename = uuid4().hex + '.webp'
    (directory / filename).write_bytes(output.getvalue())
    return jsonify(imagem=dict(caminho='/media/' + filename,
                              nome='Foto enviada ' + filename[:8], origem='upload')), 201


def image_file(filename):
    # Only generated files are served here; stock assets use the existing static route.
    if len(filename) != 37 or not filename.endswith('.webp') or any(c not in '0123456789abcdef' for c in filename[:-5]):
        fail('Imagem não encontrada.', 404)
    return send_from_directory(upload_dir(), filename, max_age=86400)
