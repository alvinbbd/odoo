odoo.define('ks_toggle_switch.toggle_button', function(require)
{
  "use strict";
  var DEFAUL_TOGGLE_TYPE = "Rounded";

  return{
     /**
    * creates a toggle button.
    * @returns jQuery
    */
    createToggle: function(options){
      var id = _.uniqueId('ks_toggle_button-');
      var $label = $('<label/>', {
        for: id,
          class: 'ks-toggle-switch'
      });
      var $input = $('<input/>',{
        type: 'checkbox',
        id: id,
      });

      var $span = $('<span/>');
      var $el = $label.append($input, $span)

      switch(options.toggleType){
        case 'rectangular':
        case 'Rectangular':
        $el.find('span').addClass('ks-toggle-slider');
        break;
        case 'rounded':
        case 'Rounded':
        $el.find('span').addClass('ks-toggle-slider round')
        break;
      }

      if (!options || !options.text) {
        $el.find('label').html('&#8203;'); // BS checkboxes need some label content (so add a zero-width space when there is no text)
      }

      $el.find('input').prop(options.prop);
      return $el;

    },
  }
});