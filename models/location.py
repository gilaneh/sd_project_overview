# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta, date
# import random

from odoo import models, fields, api

from colorama import Fore


class SdProjectOverviewLoction(models.Model):
    _name = 'sd_project_overview.location'
    _description = 'sd_project_overview.location'
    _order = 'diagram asc'

    diagram = fields.Many2one('sd_project_overview.diagram', required=True, )
    task_id = fields.Many2one('project.task', required=False, )
    point_x = fields.Integer(default=0 )
    point_y = fields.Integer(default=-200)
    point_w = fields.Integer(default=300 )
    point_h = fields.Integer(default=200)
    point_size = fields.Integer(default=15)
    point_color = fields.Char(default='#71639e')
    point_border = fields.Char(default='#FF0000')

# class SdProjectOverviewValueTypesLocation(models.Model):
#     _inherit = 'sd_project_overview.value_types'
#
#     # #########################################################################
#     @api.model
#     def create(self, vals):
#         res = super(SdProjectOverviewValueTypesLocation, self).create(vals)
#         diagrams = self.env['sd_project_overview.diagram'].search([('project', '=', int(vals.get('project')))])
#         for diagram in diagrams:
#             self.env['sd_project_overview.location'].create({'diagram': diagram.id, 'task_id': task_id})
#
#         return res