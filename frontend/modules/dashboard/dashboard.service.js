angular.module('startup.dashboard')
  .factory('DashboardApi', ['$http', function ($http) {
    return {
      getHealth: function () {
        return $http.get('/api/health/');
      },
      getStats: function () {
        return $http.get('/api/stats/');
      }
    };
  }]);
