odoo.define('ks_toggle_switch.field_utils', function (require)
{
  "use strict";

  var ks_utils =  require('web.field_utils');
  var ks_toggle_button = require('ks_toggle_switch.toggle_button');
  /**
  * @param {boolean} value
  * @param {Object} [field]
  *        a description of the field (note: this parameter is ignored)
  * @param {Object} [options] additional options
  * @param {boolean} [options.forceString=false] if true, returns a string
  *    representation of the boolean rather than a jQueryElement
  * @returns {jQuery|string}
  */
  function formatBooleanToggle(value, field, options){
    if (options && options.forceString) {
      return value ? _t('True') : _t('False');
    }
    return ks_toggle_button.createToggle(
      _.extend(
        options, 
        {
          prop:{
            checked: value,
            disabled: true,
          }
        }
      )
    )
  };
  ks_utils['format']['booleanToggle'] = formatBooleanToggle;
});