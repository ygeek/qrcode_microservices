import json, os, io, requests, datetime, math, shutil, logging
from flask import Flask, request, send_from_directory
from MyQR import myqr
from pdf2image import convert_from_bytes, convert_from_path
from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw, ImageFont, ImageChops
from fpdf import FPDF
app = Flask(__name__)

ppi = 30

@app.route('/')
def hello():
	return 'CONNECT SUCCESS'

@app.route('/encode_qr', methods=['POST'])
def encode_qr():
	qr_code_string = request.json['qr_code_string']
	qr_dir = '{base_path}/qrimages/temp'
	img_lst = []
	for qr_code in (qr_code_string):
		if len(qr_code) == 1:
			code = qr_code[0]
			empoid = ""
			words = qr_code[0]
		else:
			code = qr_code[0]
			empoid = qr_code[1]
			words = "{code}-{empoid}".format(code = code, empoid = empoid)
		version, level, qr_name = myqr.run(
			words = words,
			version = 1,
			level = 'H',
			picture = None,
			colorized = False,
			contrast = 1.0,
			brightness = 1.0,
			save_name = ('{serial_no}.png').format(serial_no = words),
			save_dir = qr_dir.format(base_path = os.getcwd())
		)
		img_lst.append({
			'qr_code': code,
			'empoid': empoid,
			'path': qr_name
		})
	# 拼接图片
	# 创建图底 A4 210 * 297 30ppi 白色填充
	combine_img = Image.new('RGBA', (210 * ppi, 297 * ppi), (255,255,255,255))
	img_x_margin = round(48.5 * ppi)
	img_y_margin = round(25.4 * ppi)
	fnt = ImageFont.truetype(('{base_path}/asset/msyh.ttc').format(base_path = os.getcwd()), 80)
	pdf = FPDF("P", "mm", (210, 297))
	for idx, elem in enumerate(img_lst):
		# im = Image.open(elem['path'])
		# qr_img = trim(im)
		# im.show()
		qr_img = Image.open(elem['path'])
		x_order = idx % 4
		y_order = math.floor(idx % 40 / 4)
		# 添加序列号和类型
		txt = Image.new('RGBA', (23 * ppi, 25 * ppi), (255,255,255,255))
		d = ImageDraw.Draw(txt)
		d.text((1 * ppi, 5 * ppi), elem['qr_code'], font=fnt, fill=(0,0,0,255))
		d.text((1 * ppi, 15 * ppi), elem['empoid'], font=fnt, fill=(0,0,0,255))
		# qrcode 25 * 25 (25.4 * 48.5)
		qr_img = qr_img.resize((25 * ppi, 25 * ppi))
		# 拼接
		combine_img.paste(qr_img, (img_x_margin * x_order + 8 * ppi, img_y_margin * y_order + 21 * ppi))
		combine_img.paste(txt, (img_x_margin * x_order + 25 * ppi + 8 * ppi, img_y_margin * y_order + 21 * ppi) )
		combine_img = combine_img.convert("RGB")
		if (idx + 1) % 40 == 0 or (idx + 1) == len(img_lst) :
			combine_img.save(('{base_path}/qrimages/temp/res.jpg').format(base_path = os.getcwd()))
			pdf.add_page()
			pdf.image(('{base_path}/qrimages/temp/res.jpg').format(base_path = os.getcwd()),0, 0, 210, 297, 'jpg')

			combine_img = Image.new('RGBA', (210 * ppi, 297 * ppi), (255, 255, 255, 255))
	pdf.output(('{base_path}/qrimages/combine/res.pdf').format(base_path=os.getcwd()))
	for the_file in os.listdir(('{base_path}/qrimages/temp').format(base_path=os.getcwd())):
		file_path = os.path.join(('{base_path}/qrimages/temp').format(base_path=os.getcwd()), the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception as e:
			print(e)
	return send_from_directory(('{base_path}/qrimages/combine').format(base_path = os.getcwd()), 'res.pdf')

@app.route('/decode_qr', methods=['POST'])
def decode_qr():
	BACKEND_URL = os.getenv('BACKEND_URL')

	doc_type = request.json['doc_type']
	attachment_id = request.json['attachment_id']
	# token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJVc2VyIjp7InVzZXJfaWQiOjF9LCJleHAiOjE1MjczMDI4MDN9.Juu6qR2AmQVy7SJAIGXbKgDrOvzRdvicME8cmMeygMw'
	# api_url = 'http://suncity-backend.worklize.com/{attachment_id}/download'
	api_url = '{backend_url}/attachments/{attachment_id}/download?source=qrcode'


	# response = requests.get(headers = {'Token': token}, url = api_url.format(attachment_id = attachment_id))
	response = requests.get(url = api_url.format(attachment_id = attachment_id, backend_url = BACKEND_URL))
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
def trim(im):
	bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
	diff = ImageChops.difference(im, bg)
	diff = ImageChops.add(diff, diff, 2.0, -100)
	bbox = diff.getbbox()
	if bbox:
		return im.crop(bbox)

# images = convert_from_path(pdf_path, dpi=200, output_folder=None, first_page=None, last_page=None, fmt='ppm')

# from pyzbar.pyzbar import decode

# decode(images[0])

