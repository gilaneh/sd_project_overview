# -*- coding: utf-8 -*-
from datetime import  datetime, timedelta, date
# import random

from odoo import models, fields, api

from colorama import Fore
import json
import logging
import base64
from PIL import Image
import io
class SdProjectOverviewDiagram(models.Model):
    _name = 'sd_project_overview.diagram'
    _description = 'sd_project_overview.diagram'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _order = 'sequence,id asc'

    name = fields.Char(required=True, )
    project = fields.Many2one('project.project', required=True, )
    task = fields.Many2many('project.task', required=False, )
    image = fields.Image(required=True, )

    # #########################################################################
    @api.onchange('project')
    def _onchange_project(self):
        for rec in self:
            rec.task = False
            pass

    # #########################################################################
    @api.onchange('task')
    def _onchange_task(self):
        pass
    # todo: this function is working partially. It works for adding tasks.
    #       but when you remove a task from task items in many2many field of the diagram, it has an unusual behavior.
    #       In this case, if you click on x to remove a task, it does not show any action.

    #     print(f'>>>>>>>>>>>>>>>\n task: {self.task}\n {self.task.ids}')
    #     location_module = self.env['sd_project_overview.location']
    #     locations = location_module.search([('diagram', '=', self._origin.id)])
    #     locations_tasks = dict([(loc.task_id.id, loc.id) for loc in locations])
    # #     # print(f'\n location_tasks: {locations_tasks.keys()}')
    # #
    #     task_ids = self.task.ids
    #     add_ids = set(task_ids).difference(set(locations_tasks.keys()))
    #     del_ids = set(locations_tasks.keys()).difference(set(task_ids))
    # #     #
    #     print(f'----.-.-.-.-.-.\n task_ids: \n{task_ids} \ndel_ids: {del_ids} \nadd_ids: {add_ids}')
    #     del_loc_ids = list(map(lambda x: x[1] if x[0] in del_ids else False, locations_tasks.items()))
    #     for location in location_module.browse(del_loc_ids):
    #         location.unlink()
    #     for task in add_ids:
    #         location_module.create({'diagram': self._origin.id, 'task_id': task})

    # #########################################################################
    @api.model
    def create(self, vals):
        res = super(SdProjectOverviewDiagram, self).create(vals)
        task_module = self.env['project.task']
        location_module = self.env['sd_project_overview.location']
        task_ids = vals.get('task')[0][2] if vals.get('task') else []
        tasks = task_module.browse(task_ids)
        # project_value_types = list([v.id for v in value_types])
        for task in tasks:
            location_module.create({'diagram': res.id, 'task_id': task.id})
        return res

    # #########################################################################
    def write(self, vals):
        res = super(SdProjectOverviewDiagram, self).write(vals)
        location_module = self.env['sd_project_overview.location']
        locations = location_module.search([('diagram', '=', self._origin.id)])
        location_ids = locations.ids
        locations_tasks = dict([(loc.task_id.id, loc.id) for loc in locations])
        # print(f'\n location_tasks: {locations_tasks.keys()}')

        task_ids = vals.get("task", [[0, 0, []]])[0][2]
        add_ids = set(task_ids).difference(set(locations_tasks.keys()))
        del_ids = set(locations_tasks.keys()).difference(set(task_ids))
        #
        # print(f'----.-.-.-.-.-.\n diagram: \n{vals.get("task")} \ndel_ids: {del_ids} \nadd_ids: {add_ids}')
        del_loc_ids = list(map(lambda x: x[1] if x[0] in del_ids else False, locations_tasks.items()))
        for location in location_module.browse(del_loc_ids):
            location.unlink()
        for task in add_ids:
            location_module.create({'diagram': self._origin.id, 'task_id': task})

        return res

    # #########################################################################
    def set_diagram_locations(self, pointer):
    # def set_diagram_locations(self, pointer, point_x=[], point_y=[], point_w=[], point_h=[], point_size=[], point_color=[]):
        location_model = self.env['sd_project_overview.location']
        # print(f'!!!!!!!!!!!!!!!!!!!!!\n{pointer}')
        # print('!!!!!!!!!!!!!!!!!!!!!\n')
        # for loc_id, value in pointer.items():
            # print(f'pointer\n{loc_id}\n{value}')
        # print(f'\n set_diagram_locations {self} \n point_x: {point_x} \n point_y: {point_y} \n point_w: {point_w} \n point_h: {point_h} \n point_size: {point_size} \n point_color: {point_color}')
        # point_x: {'data_box_16': 300, 'data_box_14': 200}
        # point_y: {'data_box_16': -400, 'data_box_14': -100}
        # point_x = dict(point_x)
        # point_y = dict(point_y)
        # point_size = dict(point_size)
        for loc_id, values in pointer.items():
        #     # todo: int(key.replace('data_box_', '')) is value id not the value_type id!!!
        #     print(f'\n key.find("data_box_"): \n{key.find("data_box_")} \n key.replace("data_box_", "").isdigit(): {key.replace("data_box_", "").isdigit()}')
        #     if not key.replace('data_box_', '').isdigit():
        #         continue
            try:
                # location_id = int(key.replace('data_box_', ''))
                location_model.browse(loc_id).write({'point_x': values.get('point_x', 100),
                                                     'point_y': values.get('point_y', -200),
                                                     'point_w': values.get('point_w', 100),
                                                     'point_h': values.get('point_h', 100),
                                                     'point_size': values.get('point_size', 20),
                                                     'point_color': values.get('point_color', 8),
                                                     'point_border': values.get('point_border', 8),
                                                     })
            except Exception as e:
                logging.error(f'ERROR: {e}')

        return json.dumps('set_diagram_locations')

    # #########################################################################
    def get_diagram_values(self, diagram_id=0):
        if diagram_id:
            diagram_id = diagram_id
        else:
            diagram_id = self._origin.id

        diagram = self.browse(diagram_id)
        if len(diagram) != 1:
            return json.dumps([{'data': '', }])

        if diagram.image[-2:] != '==':
            padded_data = diagram.image + b'=='
        else:
            padded_data = diagram.image
        image_file = base64.b64decode(padded_data)
        im = Image.open(io.BytesIO(image_file))
        w, h = im.size

        locations = self.env['sd_project_overview.location'].search([('diagram', '=', diagram_id)])
        # print(f'>>>>>>>>>>>>>>>>> diagram_id: {diagram_id} \n locations: {locations}\n {w}, {h}')
        locations_list = list([{'id': lo.id,
                                'task': lo.task_id,
                                'point_x': lo.point_x,
                                'point_y': lo.point_y,
                                'point_w': lo.point_w,
                                'point_h': lo.point_h,
                                'point_size': lo.point_size,
                                'point_color': lo.point_color,
                                'point_border': lo.point_border,
                                'diagram': lo.diagram
                                } for lo in locations])
        # print(f'\n locations_list: \n{locations_list}')

        data = [{
            'id': diagram_id,
            'image_size': (w, h),
            'values': list([{'loc_id': location.get('id'),
                             'diagram_id': location.get('diagram').id,
                             'name': location.get('task').name,
                             'plan': location.get('task').progress_plan,
                             'actual': location.get('task').progress_actual,
                             'point_x': location.get('point_x'),
                             'point_y': location.get('point_y'),
                             'point_w': location.get('point_w'),
                             'point_h': location.get('point_h'),
                             'point_size': location.get('point_size'),
                             'point_color': location.get('point_color'),
                             'point_border': location.get('point_border'),
                             } for location in locations_list])
        }]

        return json.dumps([{'data': data, }])


    # #########################################################################
    def get_diagrams(self, this_id=0):
        diagrams_all = self.search([])
        # projects = list(set({'project_id': diagram.project.id, 'project_name': diagram.project.name } for diagram in diagrams_all))
        projects = list(set((diagram.project.id, diagram.project.name ) for diagram in diagrams_all))
        diagrams = list({'diagram_id': diagram.id,
                         'diagram_name': diagram.name,
                         'project_id': diagram.project.id,
                         'project_name': diagram.project.name,
                         }for diagram in diagrams_all)
        data = {
            'projects': projects,
            'diagrams': diagrams,
        }

        # print(f'))))))))))))))\n data\n {data} \n')
        return json.dumps([{'data': data, }])

    # #########################################################################
    def get_diagram_image(self, diagram_id=0):

        diagram = self.browse(diagram_id)
        # # projects = list(set({'project_id': diagram.project.id, 'project_name': diagram.project.name } for diagram in diagrams_all))
        # projects = list(set((diagram.project.id, diagram.project.name ) for diagram in diagrams_all))
        # diagrams = list({'diagram_id': diagram.id,
        #                  'diagram_name': diagram.name,
        #                  'project_id': diagram.project.id,
        #                  'project_name': diagram.project.name,
        #                  }for diagram in diagrams_all)
        # data = {
        #     'image': diagram.image,
        # }
        imageBase64 = base64.b64encode(diagram.image)
        # print(f'))))))))))))))\n diagram_id: {diagram_id} \n data: {data} \n')
        return json.dumps({'image': imageBase64,})
