odoo.define('hrms_dashboard.Dashboard', function (require) {
"use strict";
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var rpc = require('web.rpc');
var Widget = require('web.Widget');
var _t = core._t;
var QWeb = core.qweb;


var ASTDashboardMain = Widget.extend({
    template: 'ASTDashboardMain',

    init: function(){
        this.all_dashboards = ['upcoming_actions','leads','lead_deal','agent_status','holding_time'];
        return this._super.apply(this, arguments);
    },

    start: function(){
        return this.load(this.all_dashboards);
    },

    load: function(dashboards){
        var self = this;
        var loading_done = new $.Deferred();
        this._rpc({route: '/ast/web_settings_dashboard/data'})
            .then(function (data) {
                // Load each dashboard
                var all_dashboards_defs = [];
                _.each(dashboards, function(dashboard) {
                    var dashboard_def = self['load_' + dashboard](data);
                    if (dashboard_def) {
                        all_dashboards_defs.push(dashboard_def);
                    }
                });

                // Resolve loading_done when all dashboards defs are resolved
                $.when.apply($, all_dashboards_defs).then(function() {
                    loading_done.resolve();
                });
            });
        return loading_done;
    },

    load_upcoming_actions: function(data){
        return  new AstDashboardUpcomingActions(this, data.actions).replace(this.$('.ast-dash-upcoming-action'));
    },

    load_leads: function(data){
        return  new AstDashboardLeads(this, data.leads).replace(this.$('.ast-lead-status'));
    },

    load_lead_deal: function(data){
        return  new AstDashboardLeadDealStatus(this, data.lead_deal).replace(this.$('.ast-lead-deal-status'));
    },

    load_agent_status: function(data){
        return  new AstDashboardAgentStatus(this, data.agent_status).replace(this.$('.ast-dash-team-performance'));
    },

    load_holding_time: function(data){
        return  new AstDashboardHoldingTime(this, data.holding_time).replace(this.$('.ast-dash-hold-time'));
    },
});

var AstDashboardUpcomingActions = Widget.extend({

    template: 'AstDashboardUpcomingActions',

    init: function(parent, data){
        this.data = data;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },
});

var AstDashboardLeads = Widget.extend({

    template: 'AstDashboardLeads',

    init: function(parent, data){
        this.data = data;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },
});

var AstDashboardLeadDealStatus = Widget.extend({

    template: 'AstDashboardLeadDealStatus',

    init: function(parent, data){
        this.data = data;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },
});

var AstDashboardAgentStatus = Widget.extend({

    template: 'AstDashboardAgentStatus',

    init: function(parent, data){
        this.data = data;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },
});

var AstDashboardHoldingTime = Widget.extend({

    template: 'AstDashboardHoldingTime',

    init: function(parent, data){
        this.data = data;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },
});


core.action_registry.add('ast_main_dashboard', ASTDashboardMain);

return {
    AstDashboardUpcomingActions: AstDashboardUpcomingActions,
    AstDashboardLeads: AstDashboardLeads,
    AstDashboardLeadDealStatus: AstDashboardLeadDealStatus,
    AstDashboardAgentStatus: AstDashboardAgentStatus,
    AstDashboardHoldingTime: AstDashboardHoldingTime,
};

});
