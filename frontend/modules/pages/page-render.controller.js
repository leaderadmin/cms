angular.module('startup.pages').controller('PageRenderController', ['PagePublicApi', 'BlockRegistry', function (PagePublicApi, BlockRegistry) {
  var renderer = this;
  renderer.page = { name: 'Loading page' };
  renderer.template = { regions: [] };
  renderer.regions = {};
  renderer.loading = true;
  renderer.error = '';

  function slugFromPath() {
    var path = window.location.pathname.replace(/^\/+|\/+$/g, '');
    return decodeURIComponent(path.split('/').pop() || 'home');
  }

  function normalizeRegion(region) {
    return angular.extend({}, region, {
      id: region.id || region.key,
      allowedBlocks: region.allowedBlocks || region.allowed_blocks || []
    });
  }

  renderer.load = function () {
    renderer.loading = true;
    renderer.error = '';
    PagePublicApi.published(slugFromPath()).then(function (response) {
      renderer.page = response.data.page;
      renderer.template = response.data.template || { regions: [] };
      renderer.template.regions = (renderer.template.regions || []).map(normalizeRegion);
      renderer.regions = response.data.version.regions || {};
      (response.data.components || []).forEach(function (component) {
        BlockRegistry.registerComponent(component.component_key, component);
      });
      renderer.loading = false;
    }, function (response) {
      renderer.loading = false;
      renderer.error = response.status === 404 ? 'Page not found.' : 'Unable to load this page.';
    });
  };

  renderer.blocks = function (region) {
    return renderer.regions[region.id] || [];
  };

  renderer.load();
}]);
