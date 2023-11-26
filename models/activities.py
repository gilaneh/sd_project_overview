# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta, date
# import random

from odoo import models, fields, api

from colorama import Fore


class SdProjectOverviewActivities(models.Model):
    _name = 'sd_project_overview.activities'
    _description = 'sd_project_overview.activities'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'project,code asc'
    _rec_name = 'name'

    code = fields.Char()
    name = fields.Char()
    parent_id = fields.Many2one('sd_project_overview.activities', )
    project = fields.Many2one('sd_project_overview.project', required=True,)
    activities_type = fields.Many2one('sd_project_overview.activities_types', required=True,)
    plan = fields.Float(required=True)
    actual = fields.Float(required=True)


class SdProjectOverviewActivitiesTypes(models.Model):
    _name = 'sd_project_overview.activities_types'
    _description = 'sd_project_overview.activities_types'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'project,name asc'

    name = fields.Char(required=True,)
    project = fields.Many2one('sd_project_overview.project', required=True, ondelete="cascade")



