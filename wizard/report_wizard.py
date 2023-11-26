# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import Command
from colorama import Fore
from datetime import datetime, date
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError

# #############################################################################
class SdHseReportWizard(models.TransientModel):
    _name = 'sd_project_overview.report.wizard'
    _description = 'Report Wizard'

    def _project_domain(self):
        partner_id = self.env.user.partner_id
        projects = self.env['sd_project_overview.project'].search(['|',
                                                      ('overview_managers', 'in', partner_id.id),
                                                      ('overview_officers', 'in', partner_id.id),])
        return [('id', 'in', projects.ids)]

    project = fields.Many2one('sd_project_overview.project', required=True,
                              domain=lambda self: self._project_domain(), tracking=True,
                              default=lambda self: self.project.search(
                                  ['|', ('overview_managers', 'in', self.env.user.partner_id.id),
                                   ('overview_officers', 'in', self.env.user.partner_id.id)], limit=1))

    start_date = fields.Date(required=True, default=lambda self: date.today() )
    calendar = fields.Selection([('fa_IR', 'Persian'), ('en_US', 'Gregorian')],
                                default=lambda self: 'fa_IR' if self.env.context.get('lang') == 'fa_IR' else 'en_US')

    # #############################################################################
    def overview_daily_report(self):
        read_form = self.read()[0]
        data = {'form_data': read_form}

        return self.env.ref('sd_project_overview.daily_report').report_action(self, data=data)


