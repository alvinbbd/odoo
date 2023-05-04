odoo.define('asteco_custom_theme.control_panel', function (require) {
    'use strict';
    var core = require('web.core');
    var ajax = require('web.ajax');
    var qweb = core.qweb;
    ajax.loadXML('/asteco_custom_theme/static/src/xml/custom.xml', qweb);
});