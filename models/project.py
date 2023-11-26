# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta, date
# import random

from odoo import models, fields, api

from colorama import Fore


class SdProjectOverview(models.Model):
    _name = 'sd_project_overview.project'
    _description = 'sd_project_overview.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _order = 'sequence,id asc'

    name = fields.Char(help='It can imply project name and its construction site', required=True,)
    project = fields.Many2one('project.project', required=True,)


# class SdProjectTask(models.Model):
#     _name = 'project.task_aa'
#     _inherits = {'project.task': 'name'}
#
#     aa = fields.Char()
#
#     @api.onchange('project_id')
#     def project_change(self):
#         self.name = ''

class SdProjectTaskOverview(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'

    bb = fields.Char()