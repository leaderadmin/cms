angular.module('startup.pages').directive('ngDragstart', [function () {
  return function (scope, element, attrs) {
    element.on('dragstart', function (event) {
      scope.$evalAsync(attrs.ngDragstart);
      if (event.originalEvent && event.originalEvent.dataTransfer) event.originalEvent.dataTransfer.effectAllowed = 'move';
    });
  };
}]).directive('ngDrop', [function () {
  return function (scope, element, attrs) {
    element.on('dragover', function (event) { event.preventDefault(); });
    element.on('drop', function (event) {
      event.preventDefault();
      scope.$evalAsync(attrs.ngDrop);
    });
    scope.$on('$destroy', function () { element.off('dragover drop'); });
  };
}]);
