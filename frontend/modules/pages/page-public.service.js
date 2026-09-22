angular.module('startup.pages').factory('PagePublicApi', ['$http', function ($http) {
  return {
    published: function (slug) { return $http.get('/api/pages/' + encodeURIComponent(slug) + '/'); }
  };
}]);
