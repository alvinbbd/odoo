odoo.define('ks_toggle_switch.ListRenderer', function (require){
  "use strict";

  var ksListRenderer = require('web.ListRenderer');
  var field_utils = require('web.field_utils');
  var ks_session = require('web.session');
  var ks_rpc = require('web.rpc');
  var ks_def_color = "#68c156";
  var ks_toggle_button = require('ks_toggle_switch.toggle_button');
  var ListRenderer = ksListRenderer.include({
    /**
    * Handled node.attrs.options coming from the view field in list view.
    * Processed them and converted into the json.
    * @private
    * @param {Object} record
    * @param {Object} node
    * @param {integer} colIndex
    * @param {Object} [options]
    * @param {Object} [options.mode]
    * @param {Object} [options.renderInvisible=false]
    *        force the rendering of invisible cell content
    * @param {Object} [options.renderWidgets=false]
    *        force the rendering of the cell value thanks to a widget
    * @returns {jQueryElement} a <td> element
    */
    /**
     * Override the method to handle the checkbox rendering in the listview.
     *
     * @override
     */


    _renderBodyCell: function (record, node, colIndex, options){
      if(record.fields[node.attrs.name]){
          if(record.fields[node.attrs.name].type != 'boolean' || node.tag === 'button' || node.tag === 'widget' || node.attrs.widget)
            return this._super.apply(this, arguments);
      }


      var nodeOptions = {};
      try{
        nodeOptions = JSON.parse(node.attrs.options.replace(/'/g, '"'));
      }
      catch(err){
        if(ks_session.ks_toggle_type === "Rectangular")
            nodeOptions.toggleType = "Rectangular";
        else
            nodeOptions.toggleType = "Rounded";
      }

      if(ks_session.ks_toggle_status === false)
        return this._super.apply(this, arguments)

      _.extend(options, nodeOptions)
      var tdClassName = 'o_data_cell';
      var $td = $('<td>', { class: tdClassName });
      var modifiers = this._registerModifiers(node, record, $td, _.pick(options, 'mode'));
      if (modifiers.invisible && !(options && options.renderInvisible)){
        return $td;
      }

       if (node.attrs.widget || (options && options.renderWidgets)) {
            var $el = this._renderFieldWidget(node, record, _.pick(options, 'mode'));
            this._handleAttributes($el, node);
            return $td.append($el.$el);
        }

      var name = node.attrs.name;
      var field = this.state.fields[name];
      var value = record.data[name];
      var formattedValue = field_utils.format['booleanToggle'](value, field,
        _.extend(
          options, 
          {
            data: record.data,
            escape: true,
            isPassword: 'password' in node.attrs,
          }
        )
      );

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

      async function ks_color(){
            try{
                ks_def_color = await ks_get_color();
                $("input:checked + .ks-toggle-slider").css("background-color",ks_def_color);
            }
            catch(err){
                console.log(err);
            }
        }

      ks_color();

      this._handleAttributes($td, node);

      return $td.html(formattedValue);

    },

  });
});