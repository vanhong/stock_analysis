(function(UpdateData) {
	function Update (){
		this.Init = function() {
			$(window).load(function() {
				$(".update_stockid").click(function(){
					$.get('/update_stockid/', function(jData){
						$('.stockid_lastUpdateDate').html(jData.lastUpdateDate);
						$('.stockid_lastDataDate').html(jData.lastDataDate);
						$('.stockid_notes').html(jData.notes);
					});
				});

				$(".update_monthrevenue").click(function() {
					$.get('/update_month_revenue/', {'date':$('.monthrevenue_date').val()}).done(function(jData) {
						$('.monthrevenue_lastUpdateDate').html(jData.lastUpdateDate);
						$('.monthrevenue_lastDataDate').html(jData.lastDataDate);
						$('.monthrevenue_notes').html(jData.notes);
					})
				});

				$(".check_monthrevenue").click(function() {
					$.get('/check_month_revenue', {'date':$('.monthrevenue_date').val()}).done(function(jData) {
						$('.monthrevenue_notes').html(jData.notes);
					})
				});

				$(".update_seasonrevenue").click(function() {
					$.get('/update_season_revenue/', {'date':$('.seasonrevenue_date').val()}).done(function(jData) {
						$('.seasonrevenue_lastUpdateDate').html(jData.lastUpdateDate);
						$('.seasonrevenue_lastDataDate').html(jData.lastDataDate);
						$('.seasonrevenue_notes').html(jData.notes);
					})
				});

				$(".update_seasonincomestatement").click(function() {
					$.get('/update_season_income_statement/', {'date':$('.seasonincomestatement_date').val()}).done(function(jData) {
						$('.seasonincomestatement_lastUpdateDate').html(jData.lastUpdateDate);
						$('.seasonincomestatement_lastDataDate').html(jData.lastDataDate);
						$('.seasonincomestatement_notes').html(jData.notes);
					})
				});

				$(".update_seasonbalancesheet").click(function() {
					$.get('/update_season_balance_sheet/', {'date':$('.seasonbalancesheet_date').val()}).done(function(jData) {
						$('.seasonbalancesheet_lastUpdate').html(jData.lastUpdateDate);
						$('.seasonbalancesheet_lastDataDate').html(jData.lastDataDate);
						$('.seasonbalancesheet_notes').html(jData.notes);
					})
				});

				$(".update_seasoncashflow").click(function () {
					$.get('/update_season_cashflow_statement/', {'date':$('.seasoncashflow_date').val()}).done(function(jData) {
						$('.seasoncashflow_lastUpdate').html(jData.lastUpdateDate);
						$('.seasoncashflow_lastDataDate').html(jData.lastDataDate);
						$('.seasoncashflow_notes').html(jData.notes);
					})
				});

				$(".update_yearincomestatement").click(function () {
					$.get('/update_year_income_statement/', {'date':$('.yearincomestatement_date').val()}).done(function(jData) {
						$('.yearincomestatement_lastUpdate').html(jData.lastUpdateDate);
						$('.yearincomestatement_lastDataDate').html(jData.lastDataDate);
						$('.yearincomestatement_notes').html(jData.notes);
					})
				});
			});
		}
	}
	UpdateData.Update = Update;
}(window.UpdateData = window.UpdateData||{}));

