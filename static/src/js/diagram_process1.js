odoo.define('sd_project_overview.diagram_process', function (require) {
"use strict";
    var Dialog = require('web.Dialog');
    var FormController = require('web.FormController');
    var FormRenderer = require('web.FormRenderer');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');
    var core = require('web.core');
    var _t = core._t;
    var DiagramProcessFormController = FormController.extend({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
//        showEquipmentIcon: '_showEquipmentIcon',
        showEquipmentIcon: '_showEquipmentIconPlay',
    }),
    events: {
//        'load': '_imageClicked',
        'click .work_place_form_view_image img': function(e){
            console.log(e);
        },
    },
    /**
     * @override
     */

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            console.log('diagram_process_form_view')
        });
    },
    _applyChanges: async function () {
        let self = this;
        const result = await this._super.apply(this, arguments);
        self._mouseDown();
        return result;
    },
    _onEdit: function () {
        let self = this;
        this._super.apply(this, arguments);
        $(this).ready( function(){
            self._mouseDown();
            });
    },
    _saveRecord: function () {
        let self = this;
        let res = this._super.apply(this, arguments);
        let image_e = self.el.querySelector('.diagram_process_form_view img');
        image_e.addEventListener('load', function(){
            self._showEquipmentIcon('show', 0, 0);
            });
        return res
    },
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------



    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    _mouseDown: function(){
        let self = this;
        this._showEquipmentIcon('show', 0, 0);
        let image_e = self.el.querySelector('.work_place_form_view_image img');
        let view_only = self.el.querySelector('.work_place_form_view_only');
        if(view_only == null){
            image_e.addEventListener('mousedown', function(e){
                self._showEquipmentIcon('edit', e.offsetX, e.offsetY);
            });
        }
    },
    _onBarcodeScanned: function(barcode) {
        const self = this;
//        console.log('_onValueInputChange', barcode);
//        const barcode_scanned = this.el.querySelector('[name="_barcode_scanned"]');
//        console.log(this)

//        let equipment = this.el.querySelector('div[name="equipment"] div div input');
//        if (equipment){
//            equipment.value = barcode;
////            $('div[name="equipment"] div div input').trigger("change");
////            var e = $.Event( "keyup", { which: 13, keyCode: 13 } );
////            $('div[name="equipment"] div div input').trigger(e);
////            const ke = new KeyboardEvent('keydown', {
////                bubbles: true, cancelable: true, keyCode: 13
////            });
////            document.body.dispatchEvent(ke);
//
//
//            //todo it needed an enter key to hit !
//        }

    },
    _showEquipmentIcon: async function(show='show', workAreaX=0, workAreaY=0){
        const self = this;
        const assetDivSize = 10;
        const iconColor = '#fe4b0a';
        const assetDiv_id = "assetDiv";
//        document.addEventListener('DOMContentLoaded', function(e){
//        $(this).ready(function(){
            let image = await self.el.querySelector('.work_place_form_view_image img');
//                image.classList.remove('img-fluid');
                let model_image = await self.el.querySelector('.sd_maintenance_model_image img');

                const assetDiv = model_image.cloneNode(true);


                const myDivOld = document.querySelector('#' + assetDiv_id);
                if (myDivOld){
                    myDivOld.parentNode.removeChild(myDivOld);
                }

                let naturalWidth = image.naturalWidth;
                let naturalHeight = image.naturalHeight;
                let data = self.renderer.state.data;
//                console.log(data);
                let area_x = self.el.querySelector('.mnt_work_area_x')
                let area_y = self.el.querySelector('.mnt_work_area_y')
                let place_x = Number(self.el.querySelector('.mnt_work_place_x').innerText)
                let place_y = Number(self.el.querySelector('.mnt_work_place_y').innerText)
                let area_x_value = Number(data.work_area_x);
                let area_y_value = Number(data.work_area_y);
//                console.log( show, 'pint', workAreaX, workAreaY, 'image',
//                naturalWidth, naturalHeight, 'area', area_x_value, area_y_value, 'place', place_x, place_y)
//                const assetDiv = document.createElement('div');
                const model_width = data.plan_x * data.model_width / data.work_place_x
                const model_depth = data.plan_y * data.model_depth / data.work_place_y
                assetDiv.id = assetDiv_id;
                assetDiv.style.width =  model_width + 'px';
                assetDiv.style.height =  model_depth + 'px';
                assetDiv.style.backgroundColor = iconColor;

//                assetDiv.style.borderRadius = '50%';
                assetDiv.style.position = 'absolute';
                if(show == 'show'){
                    assetDiv.style.left = Math.round( naturalWidth * area_x_value / place_x ) - model_width / 2 + 'px';
                    assetDiv.style.top = naturalHeight - Math.round( naturalHeight * area_y_value / place_y ) - model_depth / 2 + 'px';
                }else{
                    assetDiv.style.left = workAreaX - model_width / 2 + 'px';
                    assetDiv.style.top = workAreaY - model_depth / 2 + 'px';
                    if($('.mnt_work_area_x').is('input')){
                        area_x.value = Math.round(10 * place_x * workAreaX / naturalWidth) / 10;
                        area_y.value = Math.round(10 * place_y * (naturalHeight - workAreaY) / naturalHeight) / 10;
                        $('.mnt_work_area_x').trigger("change");
                        $('.mnt_work_area_y').trigger("change");
                    }
        //            console.log(work_area_wizard_x.value, work_area_wizard_y.value)
                }
//                image.parentNode.appendChild(model_image_clone);
                image.parentNode.appendChild(assetDiv);
//            });
//        });
        },
    _showEquipmentIconPlay: function(e){
//        console.log('_showEquipmentIconPlay', e, this)
        this._showEquipmentIcon();
    },

    });

    var DiagramProcessRenderer = FormRenderer.extend({

        _updateView: function () {
            let self = this;
            var res = this._super.apply(this, arguments);
//            let image_e = self.el.querySelector('.work_place_form_view_image img');
//            image_e.addEventListener('load', function(){
//                self.trigger_up('showEquipmentIcon');
//            });
            return res
        },
    });

    var DiagramProcessFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: DiagramProcessFormController,
            Renderer: DiagramProcessRenderer,

        }),
    });

    viewRegistry.add('diagram_process_form_view', DiagramProcessFormView);
});
