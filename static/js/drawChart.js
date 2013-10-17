(function(Draw) {

    function Tool() {

        var doFilter = function() {
            $.post('{% url "dofilter" %}' , 
                function(data, status) { 
                    alert("after load, get data=" + data + ", status=" + status); 
                    $('#FilterResult').css('display','block');
                }).fail(function(xhr){alert('error=' + xhr.statusText);});
        }

        String.prototype.endsWith = function(pattern) {
            var d = this.length - pattern.length;
            return d >= 0 && this.lastIndexOf(pattern) === d;
        };

        var GetData = function(url) {
            $.get(url, function(jData){
                //alert(JSON.stringify(jData));
                //$('#Result').html(jData);
                $('#Result').highcharts({
                    chart: {
                        zoomType: 'xy',
                        plotBorderWidth: 1
                    },
                    title: jData.title,
                    subtitle: jData.subtitle,
                    xAxis: [{
                        categories: jData.categories, 
                        labels: {
                            //step: 6,
                            formatter: function() {
                                if (this.value.endsWith('01') || this.value.endsWith('06')){
                                    return this.value;
                                }
                            },
                            max: 12,
                            minRange: 12
                    }],
                    yAxis: [{ // Primary yAxis
                        labels: {
                            format: '{value}%',
                            style: {
                                color: '#89A54E'
                            }
                        },
                        title: {
                            text: '',
                            style: {
                                color: '#89A54E'
                            }
                        },
                        max : 200,
                        min : -50
                    }, { // Secondary yAxis
                        title: {
                            text: '',
                            style: {
                                color: '#4572A7'
                            }
                        },
                        labels: {
                            format: '{value} 仟元',
                            style: {
                                color: '#4572A7'
                            }
                        },
                        min : 0,
                        opposite: true
                    }],
                    tooltip: {
                        shared: true
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'left',
                        x: 120,
                        verticalAlign: 'top',
                        y: 100,
                        floating: true,
                        backgroundColor: '#FFFFFF'
                    },
                    series: [{
                        name: '營收',
                        color: '#4572A7',
                        type: 'column',
                        yAxis: 1,
                        data: jData.revenue,
                        tooltip: {
                            valueSuffix: '(仟元)'
                        }
                    }, {
                        name: '成長率',
                        color: '#89A54E',
                        type: 'line',
                        data: jData.growth_rate,
                        tooltip: {
                            valueSuffix: '%'
                        }
                    }],
                    scrollbar: {
                        enabled: true
                    }
                });    
            });
        }

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
                //Default figure
                GetData('/getRevenueChart/');

                //$('#Data').click(function(){
                //    GetData('url2');
                //    alert('revenue data');
                //});
    			//$('#Data2').click(function(){
                //    //FilterResult
                //    GetData('url2');
                //});

                //$('#Data3').click(function(){
                //    //FilterResult
                //    GetData('url3');
                //});
            });
        }
    }
    Draw.Tool = Tool;
} (window.Draw = window.Draw || {}));

(function(DrawDividend) {

    function Tool() {

        var GetData = function(url) {
            $.get(url, function(jData){
                //alert(JSON.stringify(jData));
                //$('#Result').html(jData);
                $('#Result').highcharts({
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: ''
                    },
                    xAxis: {
                        categories: jData.categories,
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: ''
                        },
                        stackLabels: {
                            enabled: true,
                            style: {
                                fontWeight: 'bold',
                                color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                            }
                        }
                    },
                    legend: {
                        align: 'right',
                        x: -70,
                        verticalAlign: 'top',
                        y: 20,
                        floating: true,
                        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColorSolid) || 'white',
                        borderColor: '#CCC',
                        borderWidth: 1,
                        shadow: false
                    },
                    tooltip: {
                        formatter: function() {
                            return '<b>'+ this.x +'</b><br/>'+
                                this.series.name +': '+ this.y +'<br/>'+
                                'Total: '+ this.point.stackTotal;
                        }
                    },
                    plotOptions: {
                        column: {
                            stacking: 'normal',
                            dataLabels: {
                                enabled: true,
                                color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
                            }
                        }
                    },
                    series: [{
                        name: '現金股利',
                        data: jData.cash_dividends
                    }, {
                        name: '股票股利',
                        data: jData.stock_dividends
                    }],
                });
            });
        }

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
                //Default figure
                GetData('/getDividendChart/');

                //$('#Data').click(function(){
                //    GetData('url2');
                //    alert('revenue data');
                //});
                //$('#Data2').click(function(){
                //    //FilterResult
                //    GetData('url2');
                //});

                //$('#Data3').click(function(){
                //    //FilterResult
                //    GetData('url3');
                //});
            });
        }
    }
    DrawDividend.Tool = Tool;
} (window.DrawDividend = window.DrawDividend || {}));

(function(DrawProfitbility) {

    function Tool() {

        var GetData = function(url) {
            $.get(url, function(jData){
                //alert(JSON.stringify(jData));
                //$('#Result').html(jData);
                $('#Result').highcharts({
                    title: {
                        text: '獲利能力',
                        x: -20 //center
                    },
                    xAxis: {
                        categories: jData.categories
                    },
                    yAxis: {
                        title: {
                            text: ''
                        },
                        labels: {
                                    format: '{value}%'
                                },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    tooltip: {
                        valueSuffix: ''
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        borderWidth: 0
                    },
                    series: [{
                        name: '毛利率',
                        data: jData.gross_profit_margins
                    }, {
                        name: '營益率',
                        data: jData.operating_profit_margins
                    }, {
                        name: '稅前淨利率',
                        data: jData.net_before_tax_profit_margins
                    }, {
                        name: '稅後淨利率',
                        data: jData.net_after_tax_profit_margins
                    }]
                });
            });
        }

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
                //Default figure
                GetData('/getProfitabilityChart/');

                
            });
        }
    }
    DrawProfitbility.Tool = Tool;
} (window.DrawProfitbility = window.DrawProfitbility || {}));

(function(DrawPerformancePerShare) {
    function Tool () {
        // body...
    }
    DrawPerformancePerShare.Tool = Tool;
} (window.DrawPerformancePerShare = window.DrawPerformancePerShare || {}));
