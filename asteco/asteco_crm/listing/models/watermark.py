from odoo import fields, models, api
from PIL import Image
import os
import io
from array import array

class ListingWatermark(models.Model):
	_inherit = 'listing.listing'

	@api.multi
	def watermarksss(self):
		base_image = Image.open("image.jpeg")
		watermark = Image.open("logo.png")
		output_image_path = "/opt/odoo/odoo-11.0/Asteco/asteco_crm/static/src/img/imageee.jpeg"
		position = (0,0)
		width, height = base_image.size

		transparent = Image.new('RGBA', (width, height), (0,0,0,0))
		transparent.paste(base_image, (0,0))
		transparent.paste(watermark, position, mask=watermark)
		transparent.show()
		transparent.save(output_image_path)

	@api.multi
	def watermark(self):
		base_image = Image.open("image.jpeg")
		# image = Image.frombytes('RGBA', (150,150), self.photo, 'raw')


		bytess = io.BytesIO(self.photo)

		image = Image.frombytes('RGBA', (150,150), bytess.read(), 'raw')

		img = Image.open("image.jpeg", mode='r')
		roiImg = img.crop()

		imgByteArr = io.BytesIO()
		roiImg.save(imgByteArr, format='PNG')
		imgByteArr = imgByteArr.getvalue()


		imgg = Image.frombytes('RGBA', (150,150), imgByteArr, 'raw')


		imgg.save("/opt/odoo/odoo-11.0/Asteco/asteco_crm/ldo.jpeg")

		# img = Image.open(BytesIO(requests.get("https://mamahelpers.co/assets/images/faq/32B.JPG").content))
		# img2 = img.crop((1,20,50,80))

		# b = BytesIO()
		# img2.save(b,format="jpeg")
		# img3 = Image.open(b)


		


