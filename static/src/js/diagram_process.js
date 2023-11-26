/** @odoo-module **/

    /**
     * This From Controller creates monitoring data boxes on the diagram image
     */
//    console.log('aaa start')
    import FormController from 'web.FormController';
    import FormView from 'web.FormView';
    import FormRenderer from 'web.FormRenderer';
    import viewRegistry from 'web.view_registry';

//    let point_x = {}
//    let point_y = {}
//    let point_w = {}
//    let point_h = {}
//    let point_size = {}
//    let point_color = {}
    let pointer = Object();
    let editMode = false
    let moveMode = false

    var DiagramProcessFormController = FormController.extend({
        events: {
            'click .sd_project_overview_image_page': '_onClickImagePage',

        },
        /**
        *   As many2many field is not
        */
        _onClickImagePage: function(e){
            let self = this;
            setTimeout(function(){
                let saveButton = self.el.querySelector('.o_form_button_save');
                if(saveButton){
                    saveButton.click();
                }
            }, 200);
        },

        saveRecord: function (recordID, options) {
            let self = this;
            recordID = recordID || this.handle;
            const localData = this.model.localData[recordID];
            const changes = localData._changes || {};
//            console.log('arash',recordID,localData,changes, pointer)
                let def = self._savePointerLocation(localData.data.id).then(data => console.log('_savePointerLocation', data));
                editMode = false;

//            return this._super(...arguments).then((modifiedFields) => {
//
//            });
            return Promise.all([def, this._super.apply(this, arguments), ]);

        },
        _savePointerLocation: function(res_id){
            let self = this;
//            console.log('pointer', pointer)
            return self._rpc({
                                model: 'sd_project_overview.diagram',
                                method: 'set_diagram_locations',
                                args: [false, pointer],
                            })
                            .then(data => JSON.parse(data))
                            .then(data => data)
                            .catch(e => console.log(e));
        },
        _onEdit: function () {
            let self = this;
            this._super.apply(this, arguments);
            editMode = true;
        },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Apply change may be called with 'event.data.force_save' set to True.
     * This typically happens when directly clicking in the statusbar widget on a new stage.
     * If it's the case, we check for a modified stage_id field and if we need to display a
     * rainbowman message.
     *
     * @param {string} dataPointID
     * @param {Object} changes
     * @param {OdooEvent} event
     * @override
     * @private
     */
        _applyChanges: function (dataPointID, changes, event) {
            let self = this;
//            let saveIt = setTimeout(function(){
//                                                    self.saveChanges(self.handle);
//                                                }, 300);
            return Promise.all([this._super.apply(this, arguments)]);

//            return this._super(...arguments).then(() => {
////                if (event.data.force_save && 'stage_id' in changes) {
//                if ( 'task' in changes) {
//                console.log('_applyChanges: ',self.handle, changes, )
//
//            /** todo: the boxs must be render again.
//            *   But there is an issue. The function _getLocation gets data from the database which is not updated
//            *   while it is not saved.
//            */
//
//                }
//            });
        },

    });

    var DiagramProcessRenderer = FormRenderer.extend({

        /**
         * @override
         */
         start: function(){
            let self = this;
            var res = this._super.apply(this, arguments);
//            console.log('START, initialState', this.initialState.res_id)
            console.log('DiagramProcessFormController', this)
            interact('.draggable_move')
                .draggable({
                // enable inertial throwing
                inertia: true,
                // keep the element within the area of it's parent
                modifiers: [
                  interact.modifiers.restrictRect({
                    restriction: 'parent',
                    endOnly: true
                  })
                ],
                // enable autoScroll
                autoScroll: true,

                listeners: {
                  // call this function on every dragmove event
                  move (event){
                    self._dragMoveListener(event);
                  },

                  // call this function on every dragend event
                  end (event) {
                    var textEl = event.target.querySelector('.drag-results')

                    textEl && (textEl.innerText =
                      'rect: ' + Math.round(event.rect.left) + ' x ' + Math.round(event.rect.top) +
                      // '\npage: ' + Math.round(event.pageX) + ' x ' + Math.round(event.pageY) +
                      // '\nclient: ' + Math.round(event.client.x) + ' x ' + Math.round(event.client.y) +
                      // '\nx0: ' + Math.round(event.x0) + ' x ' + Math.round(event.y0) +
                      // '\nmoved a distance of ' +
                      (Math.sqrt(Math.pow(event.pageX - event.x0, 2) +
                                 Math.pow(event.pageY - event.y0, 2) | 0))
                        .toFixed(2) + 'px')
//                        console.log('interact: point_x',point_x,'point_y',point_y)

                  }
                }
              })
                .resizable({
                    preserveAspectRatio: true,
                    edges: { left: false, right: true, bottom: true, top: false }
                })
                .on('mouseover', function(event){
                    if (event.originalEvent.srcElement.classList.contains('draggable_font_size')){
                        moveMode = true;
                    }

                })
                .on('input', function(event){
                    const box_id = Number(event.currentTarget.id.replace('data_box_', ''));
                    if (event.originalEvent.srcElement.classList.contains('draggable_font_size')){
                        let value = Number(event.originalEvent.srcElement.value);
                        event.currentTarget.style.fontSize = value + 'px';
                            pointer[box_id]['point_size'] = value;
                    } else if (event.originalEvent.srcElement.classList.contains('draggable_font_color')){
                        let value = event.originalEvent.srcElement.value;
                        event.currentTarget.style.color = value;
                        pointer[box_id]['point_color'] = value;
                    } else if (event.originalEvent.srcElement.classList.contains('draggable_border_color')){
                        let value = event.originalEvent.srcElement.value;
                        event.currentTarget.style.borderColor = value;
                            pointer[box_id]['point_border'] = value;
                    }
                })
                .on('resizemove', function (event) {
                    if(moveMode){
                        return
                    }
                    const box_id = Number(event.target.id.replace('data_box_', ''));
                    var target = event.target;
//                        x = (parseFloat(target.getAttribute('data-x')) || localStorage.getItem('x')),
//                        y = (parseFloat(target.getAttribute('data-y')) || localStorage.getItem('y'));
//                        console.log(Math.round(x), Math.round(parseFloat(target.getAttribute('data-x'))), Math.round(event.dx),localStorage.getItem('x'))

                    // update the element's style
                    target.style.width  = event.rect.width + 'px';
                    target.style.height = event.rect.height + 'px';

                    // translate when resizing from top or left edges
//                    x += event.deltaRect.left;
//                    y += event.deltaRect.top;
                    pointer[box_id]['point_w'] = Math.round(event.rect.width);
                    pointer[box_id]['point_h'] = Math.round(event.rect.height);

                    // localStorage.setItem('x', x)
                    // localStorage.setItem('y', y)
                    // target.style.webkitTransform = target.style.transform =
                    //     'translate(' + x + 'px,' + y + 'px)';

                    // target.setAttribute('data-x', x);
                    // target.setAttribute('data-y', y);
//                    target.style.fontSize = .15 * event.rect.width + 'px';
//                    localStorage.setItem('width', event.rect.width + 'px')
//                    localStorage.setItem('height', event.rect.height + 'px')
//                    localStorage.setItem('fontSize', target.style.fontSize)
                    // target.textContent = Math.round(event.rect.width) + '\u00D7' + Math.round(event.rect.height)
                    // target.textContent = event.rect.width + '×' + event.rect.height;
                    });
            // this function is used later in the resizing and gesture demos
//            self.dragMoveListener = self._dragMoveListener
            return res
        },
        _dragMoveListener: function(event) {
            if(moveMode){
                return
            }
//            let self = this;
            const box_id = Number(event.target.id.replace('data_box_', ''));
            var target = event.target
            // keep the dragged position in the data-x/data-y attributes
            var x = target.getAttribute('data-x') ? (parseFloat(target.getAttribute('data-x'))) + event.dx : pointer[box_id]['point_x'] || 0;
            var y = target.getAttribute('data-y') ? (parseFloat(target.getAttribute('data-y'))) + event.dy : pointer[box_id]['point_y'] || 0;
            // translate the element
            target.style.transform = 'translate(' + x + 'px, ' + y + 'px)';
            pointer[box_id]['point_x'] = Math.round(x);
            pointer[box_id]['point_y'] = Math.round(y);
            // update the position attributes
            target.setAttribute('data-x', x);
            target.setAttribute('data-y', y);
        },
        _updateView: function (a) {
            let self = this;
            var res = this._super.apply(this, arguments);
            self.updateBoxes()
            return res
        },
        updateBoxes: function(){
            let self = this;
            setTimeout(function(){
                self._getLocation().then(data => self._createBoxes(data));

            }, 100)
        },
        _getLocation: function(){
            let self = this;
            return self._rpc({
                                model: 'sd_project_overview.diagram',
                                method: 'get_diagram_values',
                                args: [self.state.res_id],
                            })
                            .then(data => JSON.parse(data))
                            .then(data => data)
                            .catch(e => console.log(e));
         },
        _createBoxes: function(data){
            let self = this;
            let diagram = self.el.querySelector('.diagram_process_form_view_image');
            let diagramImage = diagram.querySelector('img');
            diagramImage.classList.remove('img-fluid');
            if(data[0] != undefined && data[0].data[0] != undefined ){
                let values = data[0].data[0].values
//                console.log('values: ', values, Array.from(values))
                values.forEach(value => {
                    pointer[value.loc_id] = value;
//                    console.log(pointer, value)
                    let div = document.createElement("div");
                    div.classList.add('draggable_div');
                    if (editMode) {
                        div.classList.add('draggable_move');

                        //font color picker
                        let fontColor = document.createElement("input");
                        fontColor.type = 'color';
                        fontColor.id = `fontColor_${value.loc_id}`;
                        fontColor.classList.add('draggable_font_color')
                        fontColor.setAttribute('value', value.point_color);
                        div.appendChild(fontColor);

                        //border color picker
                        let borderColor = document.createElement("input");
                        borderColor.type = 'color';
                        borderColor.id = `fontColor_${value.loc_id}`;
                        borderColor.classList.add('draggable_border_color')
                        borderColor.setAttribute('value', value.point_border);
                        div.appendChild(borderColor);

                        //font size slider
                       let fontSlider = document.createElement("input");
                       fontSlider.type = 'range';
                       fontSlider.id = `fontSlider_${value.loc_id}`;
                       fontSlider.classList.add('draggable_font_size');
                       fontSlider.setAttribute('value', value.point_size);
                       fontSlider.setAttribute('step', '1');
                       fontSlider.setAttribute('min', '10');
                       fontSlider.setAttribute('max', '100');
                       div.appendChild(fontSlider);

                       fontSlider.addEventListener('mouseleave', e => moveMode = false)
                    }

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
         _fontSlider: function(fontSlider){
            fontSlider.addEventListener('change', e => {
                console.log(e.currentTarget.value);
            })
         },

    });

    var DiagramProcessFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: DiagramProcessFormController,
            Renderer: DiagramProcessRenderer,

        }),
    });

    viewRegistry.add('diagram_process_form_view', DiagramProcessFormView);

    export default {
        DiagramProcessFormController: DiagramProcessFormController,
        DiagramProcessFormView: DiagramProcessFormView,
        DiagramProcessRenderer: DiagramProcessRenderer,

    };
