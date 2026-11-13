import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image
from app import criar_app
from app.extensions import db
from app import models as m


class ImageTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.app = criar_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://',
                              'UPLOAD_FOLDER': self.temp.name})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        m.Usuario_model.inserir_administrador('Admin', 'admin@teste.com', 'senha1234')
        m.Usuario_model.inserir_cliente('Cliente', 'cliente@teste.com', 'senha1234')
        self.client = self.app.test_client()
        self.login('admin@teste.com')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()
        self.temp.cleanup()

    def login(self, email):
        self.csrf = self.client.post('/api/login', json={'email': email, 'senha': 'senha1234'}).json['csrf_token']

    def upload(self, raw, filename='foto.png', csrf=True):
        return self.client.post('/api/imagens', data={'foto': (BytesIO(raw), filename)},
                                headers={'X-CSRF-Token': self.csrf} if csrf else {})

    def write(self, path, data, method='POST'):
        return self.client.open('/api/'+path, method=method, json=data, headers={'X-CSRF-Token': self.csrf})

    def test_upload_compresses_and_is_reusable_for_both_catalogs(self):
        original = BytesIO()
        Image.new('RGB', (2400, 1600), 'green').save(original, format='JPEG')
        response = self.upload(original.getvalue(), '../../foto.jpg')
        self.assertEqual(response.status_code, 201, response.json)
        image = response.json['imagem']['caminho']
        with self.client.get(image) as served:
            self.assertEqual(served.status_code, 200)
            self.assertEqual(served.mimetype, 'image/webp')
            with Image.open(BytesIO(served.data)) as converted:
                self.assertEqual(converted.size, (1200, 800))
        self.assertIn(image, [i['caminho'] for i in self.client.get('/api/imagens').json['imagens']])
        for resource, singular, fields in [('pratos','prato',{'preco':12}), ('ingredientes','ingrediente',{'unidade_medida':'kg'})]:
            created = self.write(resource, dict(nome='Com foto', imagem=image, **fields))
            self.assertEqual(created.status_code, 201, created.json)
            key = created.json[singular]['id_'+singular]
            detail = f'{resource}/{key}'
            self.assertEqual(self.client.get('/api/'+detail).json[singular]['imagem'], image)
            stock = self.client.get('/api/imagens').json['imagens'][0]['caminho']
            self.assertEqual(self.write(detail, {'imagem':stock}, 'PATCH').json[singular]['imagem'], stock)
            self.assertIsNone(self.write(detail, {'imagem':None}, 'PATCH').json[singular]['imagem'])
        with self.client.get(image) as response:
            self.assertEqual(response.status_code, 200)  # Reused images are retained.

    def test_invalid_uploads_and_size_limit(self):
        for raw in [b'<svg onload="alert(1)"></svg>', b'not a picture']:
            self.assertEqual(self.upload(raw).status_code, 400)
        self.assertEqual(self.upload(b'x'*(5*1024*1024+1)).status_code, 413)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_library_is_seeded_and_rejects_arbitrary_paths(self):
        stock = self.client.get('/api/imagens').json['imagens']
        self.assertEqual(len(stock), 8)
        for path in ['https://example.com/image.jpg', '/media/../../secret', '/assets/img/products/missing.jpg', 42]:
            self.assertEqual(self.write('pratos', {'nome':'Teste','preco':10,'imagem':path}).status_code, 400)
        with self.client.get(stock[0]['caminho']) as response:
            self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/media/not-a-generated-file.webp').status_code, 404)

    def test_pixel_limit_and_camera_orientation(self):
        raw = BytesIO()
        Image.new('L', (6000, 4000)).save(raw, format='PNG')
        self.assertEqual(self.upload(raw.getvalue()).status_code, 400)
        raw = BytesIO()
        exif = Image.Exif()
        exif[274] = 6  # Rotate a portrait camera image before discarding metadata.
        exif[270] = 'Private camera metadata'
        Image.new('RGB', (64, 32)).save(raw, format='JPEG', exif=exif)
        response = self.upload(raw.getvalue())
        self.assertEqual(response.status_code, 201, response.json)
        with self.client.get(response.json['imagem']['caminho']) as served:
            with Image.open(BytesIO(served.data)) as image:
                self.assertEqual(image.size, (32, 64))
                self.assertFalse(image.getexif())

    def test_upload_requires_admin_and_csrf(self):
        self.assertEqual(self.upload(b'bad', csrf=False).status_code, 403)
        self.login('cliente@teste.com')
        self.assertEqual(self.upload(b'bad').status_code, 403)
        self.assertEqual(self.client.get('/api/imagens').status_code, 403)
