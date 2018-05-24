import json, os, io, requests, datetime, math, shutil
from flask import Flask, request, send_from_directory
from MyQR import myqr
from pdf2image import convert_from_bytes, convert_from_path
from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw, ImageFont


app = Flask(__name__)

ppi = 30

@app.route('/')
def hello():
	return 'CONNECT SUCCESS'

@app.route('/encode_qr', methods=['POST'])
def encode_qr():
	category_no = request.json['category_no']
	generate_count = request.json['generate_count']
	start_no = request.json['start_no']

	qr_dir = '{base_path}/qrimages/temp'
	timestamp = datetime.datetime.now().strftime('%Y%m%d')
	save_name = '{category_no}-{timestamp}{number}'

	img_lst = []
	for i in range(int(start_no) - 1, int(start_no) - 1 + int(generate_count)):
		qualtity_no = "%04d" %(i + 1)
		serial_no = save_name.format(category_no = category_no, timestamp = timestamp, number= qualtity_no)
		message = ('\'category_no\': \'{category_no}\', \'serial_no\': \'{serial_no}\'').format(category_no = category_no, serial_no = serial_no)
		version, level, qr_name = myqr.run(
			words = message,
			version = 1,
			level = 'H',
			picture = None,
			colorized = False,
			contrast = 1.0,
			brightness = 1.0,
			save_name = ('{serial_no}.png').format(serial_no = serial_no),
			save_dir = qr_dir.format(base_path = os.getcwd())
		)
		img_lst.append({
			'category_no': category_no,
			'serial_no': ('{timestamp}{number}').format(timestamp = timestamp, number = qualtity_no),
			'path': qr_name
		})
	
	# 拼接图片
	# 创建图底 A4 210 * 297 30ppi 白色填充
	combine_img = Image.new('RGBA', (210 * ppi, 297 * ppi), (255,255,255,255))
	combine_img_2 = Image.new('RGBA', (210 * ppi, 297 * ppi), (255,255,255,255))
	img_x_margin = round((48.5 + 3.2) * ppi)
	img_y_margin = round((25.4 + 3.9) * ppi)
	fnt = ImageFont.truetype(('{base_path}/asset/msyh.ttc').format(base_path = os.getcwd()), 80)

	for idx, elem in enumerate(img_lst):
		qr_img = Image.open(elem['path'])
		x_order = idx % 4
		y_order = math.floor(idx / 4)
		# 添加序列号和类型
		txt = Image.new('RGBA', (23 * ppi, 25 * ppi), (255,255,255,255))
		d = ImageDraw.Draw(txt)
		d.text((3 * ppi, 5 * ppi), elem['category_no'], font=fnt, fill=(0,0,0,255))
		d.text((3 * ppi, 15 * ppi), elem['serial_no'], font=fnt, fill=(0,0,0,255))
		# qrcode 25 * 25 (25.4 * 48.5)
		qr_img = qr_img.resize((25 * ppi, 25 * ppi))
		# 拼接
		combine_img.paste(qr_img, (img_x_margin * x_order, img_y_margin * y_order))
		combine_img.paste(txt, (img_x_margin * x_order + 25 * ppi, img_y_margin * y_order))
		combine_img = combine_img.convert("RGB")

	combine_img.save(('{base_path}/qrimages/combine/res.pdf').format(base_path = os.getcwd()))

	for elem in img_lst:
		os.remove(elem['path'])

	return send_from_directory(('{base_path}/qrimages/combine').format(base_path = os.getcwd()), 'res.pdf')

@app.route('/decode_qr', methods=['POST'])
def decode_qr():
	BACKEND_URL = os.getenv('BACKEND_URL')

	doc_type = request.json['doc_type']
	attachment_id = request.json['attachment_id']
	token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJVc2VyIjp7InVzZXJfaWQiOjF9LCJleHAiOjE1MjczMDI4MDN9.Juu6qR2AmQVy7SJAIGXbKgDrOvzRdvicME8cmMeygMw'
	# api_url = 'http://suncity-backend.worklize.com/{attachment_id}/download'
	api_url = '{backend_url}/attachments/{attachment_id}/download'


	# response = requests.get(headers = {'Token': token}, url = api_url.format(attachment_id = attachment_id))
	response = requests.get(headers = {'Token': token}, url = api_url.format(attachment_id = attachment_id, backend_url = BACKEND_URL))
	decode_res = []
	if doc_type == 'png' or doc_type == 'jpg':
		__image__ = Image.open(io.BytesIO(response.content))
		__data__ = decode(__image__)
		for qr_txt in __data__:
			decode_res.append(qr_txt.data.decode('UTF-8'))

	if doc_type == 'pdf':
		__imgages__ = convert_from_bytes(response.content)
		for img in __imgages__:
			__data__ = decode(img)
			for qr_txt in __data__:
				decode_res.append(qr_txt.data.decode('UTF-8'))
	return json.dumps(decode_res)

# images = convert_from_path(pdf_path, dpi=200, output_folder=None, first_page=None, last_page=None, fmt='ppm')

# from pyzbar.pyzbar import decode

# decode(images[0])

