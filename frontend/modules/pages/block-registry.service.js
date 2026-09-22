angular.module('startup.pages').factory('BlockRegistry', [function () {
  var definitions = {
    'hero-slider': { directive: 'hero-slider-block', label: 'Hero slider', icon: 'H', props: { title: 'Welcome to Startup', subtitle: 'A flexible landing page for your business.' } },
    'product-cards': { directive: 'product-cards-block', label: 'Product cards', icon: 'P', props: { title: 'Featured products', items: [{ name: 'Everyday account', detail: 'Simple banking for daily life.' }, { name: 'Growth account', detail: 'Make more of your savings.' }] } },
    'news-list': { directive: 'news-list-block', label: 'News list', icon: 'N', props: { title: 'Latest news', source: { collection: 'articles', filter: { show_home: true }, limit: 3 }, items: [] } },
    'cta-banner': { directive: 'cta-banner-block', label: 'CTA banner', icon: 'C', props: { title: 'Need a hand?', text: 'Talk to our team today.', label: 'Contact us', url: '/contact' } }
  };

  return {
    get: function (type) { return definitions[type] || null; },
    registerComponent: function (type, component) { definitions[type] = { type: type, label: component.name, component: component }; },
    all: function () { return Object.keys(definitions).map(function (key) { return angular.extend({ type: key }, definitions[key]); }); },
    create: function (type) {
      var definition = definitions[type];
      return definition ? { type: type, props: angular.copy(definition.props) } : null;
    },
    isAllowed: function (type, region) {
      return !!this.get(type) && (!region.allowedBlocks || region.allowedBlocks.indexOf(type) !== -1);
    }
  };
}]);

angular.module('startup.pages').directive('dynamicBlock', ['$compile', 'BlockRegistry', function ($compile, BlockRegistry) {
  return {
    restrict: 'A',
    scope: { block: '=dynamicBlock' },
    link: function (scope, element) {
      function render() {
        var definition = BlockRegistry.get(scope.block && scope.block.type);
        element.empty();
        if (!definition) {
          element.append('<div class="block-warning">This block type is not available.</div>');
          return;
        }
        if (definition.component) {
          var component = definition.component;
          var html = (component.prehtml || '') + (component.html || '') + (component.backhtml || '');
          element.empty();
          if (component.css) { element.append('<style>' + component.css + '</style>'); }
          element.append(html || '<div class="block-warning">This component has no HTML.</div>');
          $compile(element.contents())(scope);
          return;
        }
        var child = angular.element('<' + definition.directive + '></' + definition.directive + '>');
        child.attr('block', 'block');
        element.append(child);
        $compile(child)(scope);
      }
      scope.$watch('block.type', render);
    }
  };
}]);

function registerPageBlock(name, template, controller) {
  angular.module('startup.pages').directive(name, [function () {
    return { restrict: 'E', scope: { block: '=' }, template: template, controller: controller || angular.noop };
  }]);
}

registerPageBlock('heroSliderBlock', '<section class="block-hero"><span class="block-kicker">Featured</span><h2>{{ block.props.title }}</h2><p>{{ block.props.subtitle }}</p></section>');
registerPageBlock('productCardsBlock', '<section class="block-products"><h3>{{ block.props.title }}</h3><div class="product-grid"><article ng-repeat="item in block.props.items"><strong>{{ item.name }}</strong><span>{{ item.detail }}</span></article></div></section>');
registerPageBlock('newsListBlock', '<section class="block-news"><h3>{{ block.props.title }}</h3><ul><li ng-repeat="item in block.props.items"><strong>{{ item.title || item.name }}</strong><span>{{ item.description || item.detail }}</span></li></ul><small ng-if="!block.props.items.length">Connect a source to load articles.</small></section>');
registerPageBlock('ctaBannerBlock', '<section class="block-cta"><div><h3>{{ block.props.title }}</h3><p>{{ block.props.text }}</p></div><a ng-href="{{ block.props.url }}">{{ block.props.label }}</a></section>');
