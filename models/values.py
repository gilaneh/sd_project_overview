# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta, date
# import random

from odoo import models, fields, api

from colorama import Fore


class SdProjectOverviewValues(models.Model):
    _name = 'sd_project_overview.values'
    _description = 'sd_project_overview.values'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'project,value_type asc'
    _rec_name = 'value_type'

    project = fields.Many2one('sd_project_overview.project', required=True,)
    value_type = fields.Many2one('sd_project_overview.value_types', required=True,)
    last_rec = fields.Boolean(default=True)
    plan = fields.Float(required=True)
    actual = fields.Float(required=True)

    @api.model
    def create(self, vals):
        res = super(SdProjectOverviewValues, self).create(vals)
        project = vals.get('project')
        value_type = vals.get('value_type')
        last_rec = self.search([('project', '=', project), ('value_type', '=', value_type)])
        for rec in last_rec:
            rec.last_rec = False
        #     todo: remove the old ones from diagram
            diagrams = self.env['sd_project_overview.diagram'].search([('project', '=', project), ('values', 'in', rec.id)])
            for diagram in diagrams:
                diagram.write({'values': [3, rec.id]})
                diagram.write({'values': [4, res.id]})
        return res

class SdProjectOverviewValueTypes(models.Model):
    _name = 'sd_project_overview.value_types'
    _description = 'sd_project_overview.value_types'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'project,name asc'

    name = fields.Char(required=True,)
    project = fields.Many2one('sd_project_overview.project', required=True, ondelete="cascade")



