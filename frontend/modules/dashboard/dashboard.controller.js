angular.module('startup.dashboard')
  .controller('DashboardController', ['DashboardApi', function (DashboardApi) {
    var dashboard = this;
    dashboard.health = {};
    dashboard.stats = {};

    dashboard.refresh = function () {
      DashboardApi.getHealth().then(function (response) {
        dashboard.health = response.data;
      });
      DashboardApi.getStats().then(function (response) {
        dashboard.stats = response.data;
      });
    };

    dashboard.lastRunLabel = function () {
      return dashboard.stats.last_cron_run
        ? dashboard.stats.last_cron_run.ran_at
        : 'Waiting for job';
    };

    dashboard.refresh();
  }]);
