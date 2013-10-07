(function(Draw) {

    function Tool() {

        var doFilter = function() {
            $.post('{% url "dofilter" %}' , 
                function(data, status) { 
                    alert("after load, get data=" + data + ", status=" + status); 
                    $('#FilterResult').css('display','block');
                }).fail(function(xhr){alert('error=' + xhr.statusText);});
        }

        var GetData = function(url) {
            $.get(url, function(jData){
                //alert(JSON.stringify(jData));
                //$('#Result').html(jData);
                $('#Result').highcharts({
                    chart: {
                        zoomType: 'xy'
                    },
                    title: jData.title,
                    subtitle: jData.subtitle,
                    xAxis: [{
                            categories: jData.categories, 
                            labels: {
                                step: 4
                            }
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
                        }
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
                        type: 'spline',
                        data: jData.growth_rate,
                        tooltip: {
                            valueSuffix: '%'
                        }
                    }]//,
                    //scrollbar: {
                    //    enabled: true
                    //}
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
                text: 'Stacked column chart'
            },
            xAxis: {
                categories: ['Apples', 'Oranges', 'Pears', 'Grapes', 'Bananas']
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Total fruit consumption'
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
                name: 'John',
                data: [5, 3, 4, 7, 2]
            }, {
                name: 'Jane',
                data: [2, 2, 3, 2, 1]
            }, {
                name: 'Joe',
                data: [3, 4, 4, 2, 5]
            }]
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
    DrawDividend.Tool = Tool;
} (window.DrawDividend = window.DrawDividend || {}));
