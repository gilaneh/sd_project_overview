/** @odoo-module **/

import publicWidget from 'web.public.widget';
import Dialog from 'web.Dialog';
import session from 'web.session';
import { _t } from 'web.core';


publicWidget.registry.sdProjectOverviewFrontend = publicWidget.Widget.extend({
    selector: '.sd_project_overview_frontend',
//    xmlDependencies: ['/website_slides/static/src/xml/slide_management.xml'],
    events: {
        'change .project_list': '_onProjectList',
        'change .diagram_list': '_onDiagramList',
    },
    init(){
        this._super.apply(this, arguments);
        this.projects = [];
        this.diagrams = [];
    },
    start(){
        let self = this;
        const project_list = self.el.querySelector('.project_list');
        const diagram_list = self.el.querySelector('.diagram_list');
        let diagrams = this._getDiagrams()
        .then(function(data) {
            self.projects = data[0].data['projects']
            self.diagrams = data[0].data['diagrams']
        }).then(function(data){
            // create project and diagram dropdown selection lists
            let firstProjectDiagram = self.diagrams.filter(record => record['project_id'] == self.projects[0][0])
            self.projects.forEach(project =>
                                    project_list.innerHTML +=
                                    `<option id='${project[0]}' value='${project[0]}'>
                                        ${project[1]}
                                    </option>`
            );
            firstProjectDiagram.forEach(diagram =>
                                    diagram_list.innerHTML +=
                                        `<option id='${diagram["diagram_id"]}' value='${diagram["diagram_id"]}'>
                                            ${diagram["diagram_name"]}
                                        </option>`
            );

            // check the url for a diagram id
            let diagram_id = firstProjectDiagram[0]['diagram_id'];
            const urpParam = window.location.pathname.replace('/project/overview/', '')
            const requestedDiagramId = /^.*?[0-9]$/.test(urpParam) ? Number(urpParam) : 0;
//            console.log('started',requestedDiagramId, /^.*?[0-9]$/.test(requestedDiagramId) )
            let requestedDiagram = self.diagrams.filter(record => record['diagram_id'] == requestedDiagramId)
            if(requestedDiagram.length == 1){
                // project list
                diagram_id = requestedDiagramId;
                const project_list = self.el.querySelector('.project_list');
                const project_options = project_list.querySelectorAll('option');
                Array.from(project_options).filter(record => record.id == String(requestedDiagram[0]["project_id"]))[0].selected = true;

                // diagram list
                const diagram_list = self.el.querySelector('.diagram_list');
                let firstProjectDiagram = self.diagrams.filter(record => record['project_id'] == requestedDiagram[0]["project_id"]);
                diagram_list.innerHTML = '';
                firstProjectDiagram.forEach(diagram =>
                        diagram_list.innerHTML +=
                            `<option id='${diagram["diagram_id"]}' value='${diagram["diagram_id"]}'>
                                ${diagram["diagram_name"]}
                            </option>`
                );
                const diagram_options = diagram_list.querySelectorAll('option');
                Array.from(diagram_options).filter(record => record.id == String(requestedDiagram[0]["diagram_id"]))[0].selected = true;
            }

            // show the diagram data
            self._showImage(diagram_id)
            self._getDiagramValues(diagram_id).then(data => self._createBoxes(data))
        });
        return Promise.all([diagrams, this._super.apply(this, arguments)]);
    },
    _getDiagrams(){
        let self = this;
        return self._rpc({
                        model: 'sd_project_overview.diagram',
                        method: 'get_diagrams',
                        args: [false],
                    })
                    .then(data => JSON.parse(data))
                    .then(data =>  data)
                    .catch(e => console.log(e));
    },
    _onProjectList(ev){
        let self = this;
//        console.log(ev.target.value);
        const diagram_list = self.el.querySelector('.diagram_list');
        let selectedProject = self.diagrams.filter(record => record['project_id'] == Number(ev.target.value));
        if (selectedProject.length > 0) {
//            self._getDiagramImage(selectedProject[0]['diagram_id']).then(data => self._showImage(data))
            self._showImage(selectedProject[0]['diagram_id'])
            self._getDiagramValues(selectedProject[0]['diagram_id']).then(data => self._createBoxes(data))
            diagram_list.innerHTML = ''
            selectedProject.forEach(diagram =>
            diagram_list.innerHTML += `<option id='${diagram["diagram_id"]}' value='${diagram["diagram_id"]}'>${diagram["diagram_name"]}</option>`);
        }

    },
    _onDiagramList(ev){
        let self = this;
        self._showImage(Number(ev.target.value))
        self._getDiagramValues(Number(ev.target.value)).then(data => self._createBoxes(data))
    },
    _getDiagramValues(diagram_id){
        return this._rpc({
                        model: 'sd_project_overview.diagram',
                        method: 'get_diagram_values',
                        args: [false, diagram_id],
                        })
                        .then(data => JSON.parse(data))
                        .then(data => data)
                        .catch(err => console.log('_getDiagramValues encountered error:', err))
    },
    _getDiagramImage(diagram_id){
        return this._rpc({
                        model: 'sd_project_overview.diagram',
                        method: 'get_diagram_image',
                        args: [false, diagram_id],
                        })
                        .then(data => JSON.parse(data))
                        .then(data => data)
                        .catch(err => console.log('_getDiagramImage encountered error:', err))
    },
    _showImage(diagram_id){
        // update url based on diagram id
        if(window.location.pathname.replace('/project/overview/', '') != diagram_id){
            const url = location.origin + '/project/overview/' + diagram_id ;
            window.history.pushState({}, '', url);
        }
        // python:
        //       return base64.b64decode(diagram_record.image)
        const diagram_image = this.el.querySelector('.diagram_image')
        const diagram_image_preview = this.el.querySelector('.diagram_image_preview')
        diagram_image.src = '';
        diagram_image_preview.src = '';
        let smallimage = image => {image.src = session.url('/project/overviewimage/' + diagram_id + '/smallimage.png')}
        let image = image => {image.src = session.url('/project/overviewimage/' + diagram_id + '/image.png')}
        Promise.all([ smallimage(diagram_image_preview),image(diagram_image)])
//        Promise.all([ smallimage(diagram_image)])
    },
    _createBoxes: function(data){
    let self = this;
    let diagram = self.el.querySelector('.diagram_process_form_view_image');
    diagram.querySelectorAll('.draggable_div').forEach(record => record.remove());
    let diagramImage = diagram.querySelector('img');
        diagramImage.style.width = data[0].data[0].image_size[0] + 'px';
        diagramImage.style.height = data[0].data[0].image_size[1] + 'px';
    if(data[0] != undefined && data[0].data[0] != undefined ){
        let values = data[0].data[0].values
//                console.log('values: ', values, Array.from(values))
        values.forEach(value => {
//            pointer[value.loc_id] = value;
//                    console.log(pointer, value)
            let div = document.createElement("div");
            div.classList.add('draggable_div');

            diagram.appendChild(div);
            div.id = `data_box_${value.loc_id}`;
            let boxContent = document.createElement("div");
            div.appendChild(boxContent);

            boxContent.innerHTML = `
                <div ><span class="progress_name" >${value.name}</span></div>
                <div >P: <span class="progress_plan" >${value.plan}</span><span style="font-size: .6em">%</span></div>
                <div >A: <span class="progress_actual" >${value.actual}</span><span style="font-size: .6em">%</span></div>
            `;
            boxContent.classList.add('box_content');

            div.style.transform = `translate(${value.point_x}px, ${value.point_y}px)`
            div.style.width = value.point_w + 'px';
            div.style.height = value.point_h + 'px';
            div.style.color = value.point_color;
            div.style.borderColor = value.point_border;
            div.style.fontSize = value.point_size + 'px';

        });
    }
    let draggable_moves = self.el.querySelectorAll('draggable_move')
 },
});

export default {
    sdProjectOverviewFrontend: publicWidget.registry.sdProjectOverviewFrontend
};
