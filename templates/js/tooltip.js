var Tooltip = (function() {
	var $tooltip = $('[data-toggle="tooltip"]');
	function init() {
		$tooltip.tooltip();
	}
	if ($tooltip.length) {
		init();
	}
})();
