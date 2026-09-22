angular.module('startup.pages').factory('PageEditorApi', ['$http', function ($http) {
  return {
    published: function (slug) { return $http.get('/api/pages/' + encodeURIComponent(slug) + '/'); },
    draft: function (slug) { return $http.get('/api/pages/' + encodeURIComponent(slug) + '/draft/'); },
    save: function (slug, regions) { return $http.patch('/api/pages/' + encodeURIComponent(slug) + '/draft/', { regions: regions }); },
    publish: function (slug) { return $http.post('/api/pages/' + encodeURIComponent(slug) + '/publish/'); },
    preview: function (slug, block) { return $http.post('/api/pages/' + encodeURIComponent(slug) + '/preview-content/', { block: block }); }
  };
}]);
