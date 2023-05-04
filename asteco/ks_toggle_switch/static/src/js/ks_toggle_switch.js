odoo.define('ks_toggle_switch.ks_toggle_switch', function(require)
{
  "use strict";
  var ks_registry = require('web.field_registry'),
  ks_basic_field= require('web.basic_fields'),
  ks_boolean = ks_basic_field.FieldBoolean,
  ks_toggle_button = require('ks_toggle_switch.toggle_button');
  var ks_form_controller = require('web.FormController');
  var DEFAULT_TOGGLE_TYPE = "Rounded";
  var ks_session = require('web.session');
  var ks_record_id = null;
  var ks_rpc = require('web.rpc');
  var ks_def_color = "#68c156";
    ks_boolean.include({
    events: _.extend(
    {    click: '_toggle_clicked',
    },
    ks_boolean.prototype.events),

    /**
    * Overridden the render function to render boolean button instead of checkbox for the form view.
    * @override
    */
    _render: function(){
                /*
                 * It will execute when Toggle switch is turned ON.
                 */

                if(ks_session.ks_toggle_status === false){
                     try{
                            // check for the ks_togg_ctrl and change its state off to on.
                             if(this.$el[0].children[0].className === "ks-toggle-switch" && this.name === "ks_togg_ctrl"){
                                   ks_toggleButtonSwitcher(this);
                             }

                             else{
                                    this._super();
                             }
                     }
                     catch(err){
                            this._super();
                     }
                }

                else {
                    /*
                     * It will execute when Toggle switch is turned ON.
                    */

                    try{
                        // check for the ks_togg_ctrl and change its state on to off.
                        if(this.$el[0].children[0].className === "custom-control-input" && this.name === "ks_togg_ctrl"){
                            this._super();
                        }
                        else{
                            ks_toggleButtonSwitcher(this);
                        }
                    }

                    catch(err){
                        ks_toggleButtonSwitcher(this);
                    }
                }

                 /* Function to render the Toggle Switch */

                function ks_toggleButtonSwitcher(ks_self){
                         var ks_options = {}
                         ks_options.toggleType = ks_self.nodeOptions.toggleType || DEFAULT_TOGGLE_TYPE
                           if(ks_session.ks_toggle_type === "Rectangular")
                                    ks_options.toggleType = "Rectangular";
                           else
                                    ks_options.toggleType = "Rounded";

                         if(!(["rounded","Rounded", "rectangular", "Rectangular"].includes(ks_options.toggleType)))
                            return this._super();

                         ks_options.prop = {
                                            disabled: ks_self.mode == 'readonly',
                                            checked: ks_self.value,
                         }
                         ks_self.$el.empty();
                         ks_self.$el.append(ks_toggle_button.createToggle(ks_options));
                         $("input:checked + .ks-toggle-slider").css("background-color",ks_def_color);
                }
    },

    /*
     * Overridden the start function to get the Toggle switch background color.
     * @override
     */
    start: function(){
        this._super();

        /*
         *  Function to get background color from ksSaveUser model.
         */

        function ks_get_color(){
            var ks_user_id = ks_session.uid;
            var ks_data = ks_rpc.query({
                        model: 'res.users',
                        method: 'ks_get_toggle_color',
                        args: [ks_user_id],
                    }).then (function(value){
                            return value;
            });
            return ks_data;
        }

        /*
         * Wait to apply the color after render the toggle switch.
         */
        async function ks_color(){
            try{
                ks_def_color = await ks_get_color();
                var ks_color_picker = $('#togg_color_picker').val();
                $("input:checked + .ks-toggle-slider").css("background-color",ks_def_color);
                if(ks_color_picker != undefined)
                {
                    document.getElementById("togg_color_picker").value = ks_def_color;
                }
            }

            catch(err){
                $("input:checked + .ks-toggle-slider").css("background-color",ks_def_color);
                console.log(err);
            }
        }
        ks_color();
    },

    /**
    * Handled click event on the toggle button.
    */

    _toggle_clicked: function(e){
                          if(this.mode == 'edit'){
                            this.$el.find('input').prop('checked', !this.value ? 'checked' : false);
                            this._setValue(!this.value);
                            $("input:checked + .ks-toggle-slider").css("background-color",ks_def_color);
                          }
    },

     /**
    * Handled click event on checkboxes.
    */
    _onChange: function () {
        if(ks_session.ks_toggle_status === false)
            this._setValue(this.$input[0].checked);
    },

 });

    ks_registry['map'].upgrade_boolean.include({
          /*
           * Handled reset function for dialogue box/popup
           */
         _resetValue: function () {
            if(ks_session.ks_toggle_status === false){
            this.$input.prop("checked", false).change();
            }
            else
            {
                this._setValue(false);
                this._render();         // To change the state of the toggle switch.
            }
         },
    });

    ks_form_controller.include({

            /*
             *  Handled click event on the Save button
             */

            _onButtonClicked: function (event) {

                if(event.data.attrs.class === "oe_highlight" && event.data.attrs.name === "execute")
                {
                    this.ks_applyColor();
                }
                this._super(event);
            },

            ks_applyColor(){
                var ks_color =  $("#togg_color_picker").val();
                ks_record_id = ks_session.uid;
                var ks_data = ks_rpc.query({
                    model: 'res.users',
                    method: 'write',
                    args: [[ks_record_id],{'id': ks_session.uid,
                                           'ks_togg_color': ks_color,
                    }],
                });
            },
    });
});
