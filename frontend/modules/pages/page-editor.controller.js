angular.module('startup.pages').controller('PageEditorController', ['$scope', '$timeout', 'BlockRegistry', 'PageEditorApi', function ($scope, $timeout, BlockRegistry, PageEditorApi) {
  var editor = this;
  editor.slug = 'home';
  editor.page = { name: 'Trang chủ', status: 'draft' };
  editor.template = {
    regions: [
      { id: 'header', label: 'Header', locked: true, allowedBlocks: ['hero-slider'] },
      { id: 'hero', label: 'Hero', maxBlocks: 1, allowedBlocks: ['hero-slider'] },
      { id: 'main', label: 'Main content', allowedBlocks: ['product-cards', 'news-list', 'cta-banner'] },
      { id: 'footer', label: 'Footer', locked: true, allowedBlocks: ['cta-banner'] }
    ]
  };
  editor.regions = {
    header: [BlockRegistry.create('hero-slider')],
    hero: [],
    main: [BlockRegistry.create('product-cards'), BlockRegistry.create('news-list')],
    footer: [BlockRegistry.create('cta-banner')]
  };
  editor.library = BlockRegistry.all();
  editor.selected = null;
  editor.notice = 'Local draft ready';
  editor.dragged = null;
  var saveTimer;

  editor.canAdd = function (type, region) {
    return !region.locked && BlockRegistry.isAllowed(type, region) && (!region.maxBlocks || (editor.regions[region.id] || []).length < region.maxBlocks);
  };
  editor.add = function (type, region) {
    if (!editor.canAdd(type, region)) { editor.notice = 'This block is not allowed in this region.'; return; }
    var block = BlockRegistry.create(type);
    editor.regions[region.id].push(block);
    editor.select(block);
    editor.notice = 'Draft changed';
  };
  editor.remove = function (region, block) {
    var index = editor.regions[region.id].indexOf(block);
    if (index !== -1) { editor.regions[region.id].splice(index, 1); editor.selected = null; }
  };
  editor.select = function (block) { editor.selected = block; };
  editor.startDrag = function (block, region) { editor.dragged = { block: block, region: region }; };
  editor.drop = function (targetRegion, targetBlock) {
    var drag = editor.dragged;
    editor.dragged = null;
    if (!drag || targetRegion.locked || !BlockRegistry.isAllowed(drag.block.type, targetRegion)) { editor.notice = 'Drop rejected by template rules.'; return; }
    var source = editor.regions[drag.region.id];
    var target = editor.regions[targetRegion.id];
    if (targetRegion.maxBlocks && drag.region.id !== targetRegion.id && target.length >= targetRegion.maxBlocks) { editor.notice = 'This region is full.'; return; }
    source.splice(source.indexOf(drag.block), 1);
    var index = targetBlock ? target.indexOf(targetBlock) : target.length;
    target.splice(index < 0 ? target.length : index, 0, drag.block);
    editor.notice = 'Draft changed';
  };
  editor.previewSource = function (block) {
    PageEditorApi.preview(editor.slug, block).then(function (response) {
      block.props = response.data.block.props;
      editor.notice = 'Source preview loaded';
    }, function () { block.props.items = []; editor.notice = 'Source unavailable; showing an empty result.'; });
  };
  editor.save = function () {
    editor.notice = 'Saving draft...';
    PageEditorApi.save(editor.slug, editor.regions).then(function () { editor.notice = 'Draft saved'; }, function () { editor.notice = 'Local draft saved; API authentication is required for persistence.'; });
  };
  editor.publish = function () {
    editor.save();
    PageEditorApi.publish(editor.slug).then(function () { editor.page.status = 'published'; editor.notice = 'Published'; }, function () { editor.notice = 'Publish requires an authenticated API session.'; });
  };
  editor.load = function () {
    PageEditorApi.draft(editor.slug).then(function (response) {
      editor.page = response.data.page;
      editor.regions = response.data.version.regions;
      editor.notice = 'Draft loaded';
    });
  };
  editor.template.regions.forEach(function (region) {
    $scope.$watchCollection('editor.regions.' + region.id, function () {
      if (!editor._ready) return;
      $timeout.cancel(saveTimer);
      saveTimer = $timeout(editor.save, 1000);
    });
  });
  editor._ready = true;
}]);
