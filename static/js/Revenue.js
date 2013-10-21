(function(Revenue) {

	function Tool(){
		var drawTool = new Draw.Tool();
		this.Init = function(){
			$(window).load(function(){
				$( '#season_revenue' ).click( function() {
					drawTool.DrawSeason();
				});
				$( '#month_revenue' ).click( function() {
					drawTool.DrawMonth();
				});
			});
		}
	}
	
	Revenue.Tool = Tool;
}(window.Revenue = window.Revenue || {}));