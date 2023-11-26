# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import pytz
import jdatetime


# ########################################################################################
class ReportSdHseDailyReport(models.AbstractModel):
    _name = 'report.sd_project_overview.daily_report_template'
    _description = 'Project Overview Daily Report'

    # ########################################################################################
    @api.model
    def _get_report_values(self, docids, data=None):
        errors = []
        form_data = data.get('form_data')
        context = self.env.context
        time_z = pytz.timezone(context.get('tz'))
        date_time = datetime.now(time_z)
        date_time = self.date_converter(date_time, context.get('lang'))
        project_name = form_data.get('project')[1]
        project_id = form_data.get('project')[0]
        project_data = self.env['sd_project_overview.project'].search([('id', '=', project_id)])

        # [DATE] ############
        calendar = form_data.get('calendar')
        start_date = form_data.get('start_date') if 'start_date' in form_data.keys() else False
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(start_date, date_format).date()
        record_date = self.date_converter(start_date, calendar)['date']

        # ERROR: Report date is less than project valid date
        if project_data.record_date and start_date < project_data.record_date:
            record_date = self.date_converter(project_data.record_date, calendar)['date']
            errors.append(_(f'{project_name}'))
            errors.append(_(f'Report older than Base Date cannot be created!'))
            errors.append(_(f'Selected data: {record_date } is less than project "Base Date": {record_date}'))

            return {
                'doc_ids': docids,
                'doc_model': 'sd_project_overview.personnel',
                'errors': errors,
            }
        if calendar == 'fa_IR':
            first_day = jdatetime.date.fromgregorian(date=start_date).replace(day=1)
            next_month = first_day.replace(day=28) + timedelta(days=5)
            last_day = (next_month - timedelta(days=next_month.day)).togregorian()
            first_day = first_day.togregorian()

        else:
            first_day = start_date.replace(day=1)
            next_month = first_day.replace(day=28) + timedelta(days=5)
            last_day = next_month - timedelta(days=next_month.day)

        # [WEATHER] ############
        weather = {}
        weather_data = self.env['sd_project_overview.weather'].search([('record_date', '=', start_date),
                                                          ('project', '=', project_id)])
        if len(weather_data) == 1:
            # todo: temp_scale and speed_scale
            weather = {'status': weather_data.record_type.name,
                       'max_temp': weather_data.max_temperature,
                       'min_temp': weather_data.min_temperature,
                       'temp_scale': 'C',
                       'wind_speed': weather_data.wind_speed,
                       'speed_scale': 'km/h'}

        # ERROR: There is no record for the report date
        elif len(weather_data) == 0:
            errors.append(_(f'{project_name}'))
            errors.append(_(f'{record_date} '))
            errors.append(_(f'There is no personnel record for the day'))

        # ERROR: More than one record has found for the project on the report date
        elif len(weather_data) > 1:
            errors.append(_(f'{project_name}'))
            errors.append(_(f'{record_date} '))
            errors.append(_(f'More than one weather record for the day'))

        # form and reference code ############
        # todo: form and ref
        mis_ref = {'form': 'HS-FR-80-00','ref': 'HS-WI-28'}

        # [PERSONNEL] ############
        personnel_data_all = self.env['sd_project_overview.personnel'].search([('project', '=', project_id)])
        personnel_data = list(filter(lambda p: p.record_date == start_date, personnel_data_all))
        personnel = {}
        man_hr = {}
        if len(personnel_data) == 1:
            personnel_data = personnel_data[0]
            personnel = {'subcont': {'daily': personnel_data.subcontractor, 'average': 0},
                         'cont': {'daily': personnel_data.contractor, 'average': 0},
                         'local': {'daily': personnel_data.local, 'average': 0},
                         'client': {'daily': personnel_data.client, 'average': 0},
                         # 'total': personnel_data.subcontractor + personnel_data.contractor + personnel_data.local + personnel_data.client ,
                         'total': personnel_data.total,
                         'arrival': 0,
                         'departure': 0,
                         }
            personnel_day = personnel_data.total
            # todo:
            personnel_month = sum(list([p.total for p in personnel_data_all
                                        if p.record_date >= first_day and p.record_date <= start_date]))
            personnel_cum = sum(list([p.total for p in personnel_data_all if p.record_date <= start_date]))
            personnel_cum += project_data.total_personnel
            # personnel_cum += project_data.personnel_subcontractor +\
            #                  project_data.personnel_contractor +\
            #                  project_data.personnel_local +\
            #                  project_data.personnel_client

            man_hr = {'daily': project_data.daily_work_hours * personnel_day,
                      'monthly': project_data.daily_work_hours * personnel_month,
                      'cum': project_data.daily_work_hours * personnel_cum}
        # ERROR: More than one record has found for the project on the report date
        elif len(personnel_data) > 1:
            errors.append(_(f'{project_name}'))
            errors.append(_(f'{record_date} '))
            errors.append(_(f'More than one personnel record for the day'))

        # ERROR: There is no record for the report date
        elif len(personnel_data) == 0:
            errors.append(_(f'{project_name}'))
            errors.append(_(f'{record_date} '))
            errors.append(_(f'There is no personnel record for the day'))

        # [INCIDENT] ############
        incident_all = self.env['sd_project_overview.incident'].search([('project', '=', project_id)])
        incident_types = self.env['sd_project_overview.incident.types'].search([])
        statis_header = ['Project Overview Cases']
        statis_daily = ['Daily  ']
        statis_month = ['Monthly']
        statis_total = ['Total  ']
        # calculates the total incidents and put it after legend
        day, month, total = self._table_record(incident_all, start_date, first_day, last_day, False)
        statis_header.append('Total')
        statis_daily.append(day)
        statis_month.append(month)
        # statis_total.append(total)
        statis_total.append(total + project_data.total_incidents)

        # calculates the incidents based on incident types and put them after total column
        for record_type in incident_types:
            day, month, total = self._table_record(incident_all, start_date, first_day, last_day, record_type.name,)
            statis_header.append(record_type.name)
            statis_daily.append(day)
            statis_month.append(month)
            statis_total.append(total)

        # calculates the medical rest. Each incident has a medical rest field.
        day, month, total = self._table_record_sum_of_records(incident_all, start_date, first_day, last_day, 'Medical Rest',)


        # medical_rest_day = sum(list([inci.medical_rest for inci in incident_all
        #                          if inci.record_date == start_date]))
        # medical_rest_month = sum(list([inci.medical_rest for inci in incident_all
        #                            if inci.record_date >= first_day
        #                            and inci.record_date <= start_date ]))
        # # todo project medical rest
        # medical_rest_total = sum(list([inci.medical_rest for inci in incident_all])) + project_data.medical_rest

        statis_header.append('Medical Rest')
        statis_daily.append(day)
        statis_month.append(month)
        statis_total.append(total)
        header_list = {'Fatality': 'fatality',
                       'PTD&PPD': 'ptd_ppd',
                       'LTI': 'lti',
                       'RWC': 'rwc',
                       'MTC': 'mtc',
                       'FAC': 'fac',
                       'RVA': 'rva',
                       'Fire': 'fire',
                       'Near Miss': 'near_miss',
                       'Medical Rest': 'medical_rest',}
        for header_name, project_record in header_list.items():
            index = statis_header.index(header_name)
            statis_total[index] += project_data[project_record]

        statistics = [statis_daily, statis_month, statis_total]

        # [TRAINING] ############
        training_all = self.env['sd_project_overview.training'].search([('project', '=', project_id)])
        training_types = self.env['sd_project_overview.training.types'].search([])
        train_header = ['Training']
        train_daily = ['Daily  ']
        train_month = ['Monthly']
        train_total = ['Total  ']

        day, month, total = self._table_record(training_all, start_date, first_day, last_day,  False)
        train_header.append('Total')
        train_daily.append(day)
        train_month.append(month)
        train_total.append(total + project_data.training  + project_data.tbm  + project_data.induction )

        # day, month, total = self._table_record_sum_of_records(training_all, start_date, first_day, last_day,
        #                                                       record_type.name)
        # train_header.append(f'{record_type.name}(h)')
        # train_daily.append(f'{day} h')
        # train_month.append(f'{month} h')
        # train_total.append(f'{total} h')

        for record_type in training_types:
            day, month, total = self._table_record(training_all, start_date, first_day, last_day,  record_type.name)
            train_header.append(record_type.name)
            train_daily.append(day)
            train_month.append(month)
            if record_type.name.lower() == 'tbm':
                total += project_data.tbm
            elif record_type.name.lower() == 'induction':
                total += project_data.induction
            elif record_type.name.lower() == 'special':
                total += project_data.training

            train_total.append(total )
            # day, month, total = self._table_record_sum_of_records(training_all, start_date, first_day, last_day,  record_type.name)
            # train_header.append(f'{record_type.name}(h)')
            # train_daily.append(f'{day} h')
            # train_month.append(f'{month} h')
            # train_total.append(f'{total} h')

        # train_total[1] += project_data.training + project_data.tbm + project_data.induction
        # train_total[1] += project_data.training + project_data.tbm + project_data.induction

        print(f'+++++++++++++\n {train_total}')
        train_table = [train_daily, train_month, train_total]

        # [REPORT] ############
        drill_all = self.env['sd_project_overview.drill'].search([('project', '=', project_id)])
        anomaly_all = self.env['sd_project_overview.anomaly'].search([('project', '=', project_id)])
        permit_all = self.env['sd_project_overview.permit'].search([('project', '=', project_id)])
        report_header = ['Reports']
        report_daily = ['Daily  ']
        report_month = ['Monthly']
        report_total = ['Total  ']

        for name, record in [('Drill', drill_all), ('Anomaly', anomaly_all), ('PTW', permit_all)]:
            day, month, total = self._table_record(record, start_date, first_day, last_day,  False)
            report_header.append(name)
            report_daily.append(day)
            report_month.append(month)

            if name == 'Drill':
                total += project_data.drill
            elif name == 'Anomaly':
                total += project_data.anomaly
            elif name == 'PTW':
                total += project_data.ptw
            report_total.append(total)
        report_table = [report_daily, report_month, report_total]

        # [DAILY ACTIONS] ############
        actions_all = self.env['sd_project_overview.actions'].search([('project', '=', project_id),
                                                         ('record_date', '=', start_date)])
        daily_actions = []
        for action in actions_all:
            daily_actions.append(action.description)

        client_logo = f'/web/image/res.partner/{project_data.project.partner_id.id}/image_128/'
        return {
            'doc_ids': docids,
            'doc_model': 'sd_project_overview.personnel',
            'client_logo': client_logo,
            'project': project_name,
            'form_data': form_data,
            'record_date': record_date,
            'weather': weather,
            'mis_ref': mis_ref,
            'personnel': personnel,
            'man_hr': man_hr,
            'st_header': statis_header,
            'statistics': statistics,
            'train_header': train_header,
            'train_table': train_table,
            'report_header': report_header,
            'report_table': report_table,
            'daily_actions': daily_actions,
            'errors': errors,
            }

    # ########################################################################################
    def date_converter(self, date_time, lang):
        if lang == 'fa_IR':
            date_time = jdatetime.datetime.fromgregorian(datetime=date_time)
            date_time = {'date': date_time.strftime("%Y/%m/%d"),
                  'time': date_time.strftime("%H:%M:%S")}
        else:
            date_time = {'date': date_time.strftime("%Y/%m/%d"),
                        'time': date_time.strftime("%H:%M:%S")}
        return date_time

    # ########################################################################################
    def _table_record(self, items, start_date, first_day, last_day, record_type=False):
        day = len(list([item for item in items
                        if (not record_type or item.record_type.name == record_type)
                        and item.record_date == start_date]))

        month = len(list([item for item in items
                          if (not record_type or item.record_type.name == record_type)
                          and item.record_date <= start_date
                          and item.record_date >= first_day ]))

        total = len(list([item for item in items if (not record_type or item.record_type.name == record_type)
                          and item.record_date <= start_date]))
        return day, month, total

    # ########################################################################################
    def _table_record_sum_of_records(self, items, start_date, first_day, last_day,  record_type=False):
        day = sum(list([item.man_hours for item in items
                        if (not record_type or item.record_type.name == record_type)
                        and item.record_date == start_date]))

        month = sum(list([item.man_hours for item in items
                          if (not record_type or item.record_type.name == record_type)
                          and item.record_date <= start_date
                          and item.record_date >= first_day ]))

        total = sum(list([item.man_hours for item in items if (not record_type or item.record_type.name == record_type)
                          and item.record_date <= start_date]))
        day = int(round(day, 0))
        month = int(round(month, 0))
        total = int(round(total, 0))
        return day, month, total