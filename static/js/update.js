(function(UpdateData) {
	function Update (){
		this.Init = function() {
			$(window).load(function() {
				$(".update_stockid").click(function(){
					$.get('/update_stockid/', function(jData){
						$('.stockid_updateDate').html(jData.updateDate);
						$('.stockid_dataDate').html(jData.dataDate);
						$('.stockid_notes').html(jData.notes);
					});
				});

				$(".update_mr").click(function() {
					$.get('/update_month_revenue/', {'date':$('.mr_date').val()}).done(function(jData) {
						$('.mr_updateDate').html(jData.updateDate);
						$('.mr_dataDate').html(jData.dataDate);
						$('.mr_notes').html(jData.notes);
					});
				});

				$(".check_mr").click(function() {
					$.get('/check_month_revenue', {'date':$('.mr_date').val()}).done(function(jData) {
						$('.mr_notes').html(jData.notes);
					});
				});

				$(".update_sr").click(function() {
					$.get('/update_season_revenue/', {'date':$('.sr_date').val()}).done(function(jData) {
						$('.sr_updateDate').html(jData.updateDate);
						$('.sr_dataDate').html(jData.dataDate);
						$('.sr_notes').html(jData.notes);
					});
				});

				$(".update_sis").click(function() {
					$.get('/update_season_income_statement/', {'date':$('.sis_date').val()}).done(function(jData) {
						$('.sis_updateDate').html(jData.updateDate);
						$('.sis_dataDate').html(jData.dataDate);
						$('.sis_notes').html(jData.notes);
					});
				});

				$(".update_sbs").click(function() {
					$.get('/update_season_balance_sheet/', {'date':$('.sbs_date').val()}).done(function(jData) {
						$('.sbs_lastUpdate').html(jData.updateDate);
						$('.sbs_dataDate').html(jData.dataDate);
						$('.sbs_notes').html(jData.notes);
					});
				});

				$(".update_scf").click(function () {
					$.get('/update_season_cashflow_statement/', {'date':$('.scf_date').val()}).done(function(jData) {
						$('.scf_lastUpdate').html(jData.updateDate);
						$('.scf_dataDate').html(jData.dataDate);
						$('.scf_notes').html(jData.notes);
					});
				});

				$(".update_sfr").click(function () {
					$.get('/update_season_financial_ratio/', {'date':$('.sfr_date').val()}).done(function(jData){
						$('.sfr_lastUpdate').html(jData.updateDate);
						
					});
				});

				$(".update_yis").click(function () {
					$.get('/update_year_income_statement/', {'date':$('.yis_date').val()}).done(function(jData) {
						$('.yis_lastUpdate').html(jData.updateDate);
						$('.yis_dataDate').html(jData.dataDate);
						$('.yis_notes').html(jData.notes);
					});
				});

				$(".update_ycf").click(function () {
					$.get('/update_year_cashflow_statement/', {'date':$('.ycf_date').val()}).done(function(jData) {
						$('.ycf_lastUpdate').html(jData.updateDate);
						$('.ycf_dataDate').html(jData.dataDate);
						$('.ycf_notes').html(jData.notes);
					});
				});
			});
		};
	}
	UpdateData.Update = Update;
}(window.UpdateData = window.UpdateData||{}));

