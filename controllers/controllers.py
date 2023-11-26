# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import datetime
from colorama import Fore
import jdatetime
import base64
from PIL import Image
import io

class Apps(http.Controller):
    @http.route(['/project/overview','/project/overview/<int:diagram_id>', ], type='http', auth="user", website=True)
    def sd_project_overview_http(self, diagram_id=0, **kwargs):
        # print(f'\n ssssssssssssssssssssss:  {diagram_id}\n')
        return http.request.render('sd_project_overview.overview', )

        diagram_records = request.env['sd_project_overview.diagram'].search([])
        if diagram_records:
            diagrams = list([{diagram.id : {'diagram_name': diagram.name,
                                            'project_id': diagram.project.id,
                                            'project_name': diagram.project.name,
                                            }} for diagram in diagram_records])

            return http.request.render('sd_project_overview.overview', {'diagrams': diagrams, })
        else:
            return http.request.render('sd_project_overview.overview_not_found', {})

    @http.route('/project/overviewimage/<int:diagram>/<string:filename>', type='http', auth="user", website=True)
    def sd_project_overview_image_http(self, diagram, filename, **kwargs):
        diagram_record = request.env['sd_project_overview.diagram'].sudo().browse( diagram)
        if filename == 'image.png':
            # javascript:
            # diagram_image.src = session.url('/project/overviewimage/' + diagram_id + '/image.png')
            output = base64.b64decode(diagram_record.image)
        elif filename == 'smallimage.png':
            image = diagram_record.image
            if image[-2:] != '==':
                image = image + b'=='

            img = Image.open(io.BytesIO(base64.b64decode(image)))
            w, h = img.size
            MAX_WIDTH = 128
            if w > MAX_WIDTH:
                w = MAX_WIDTH
                h = int(MAX_WIDTH * h / w)
                img = img.resize((w, h))

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            output = img_byte_arr

            # print(f'\n\n image: {len(image)}     img_byte_arr: {len(img_byte_arr)} ')

            # output = base64.b64decode('data:image/png;base64,' + str(img.tobytes()))
        else:
            output = False

        return output

