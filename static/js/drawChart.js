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
                //alert('finish');
                //$('#Result').html(jData);
                $('#Result').highcharts({
                    chart: {
                        zoomType: 'xy'
                    },
                    title: jData.title,
                    subtitle: jData.subtitle,
                    xAxis: [{
                            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
                            max:23,
                            labels: {
                                step: 3
                            }
                    }],
                    yAxis: [{ // Primary yAxis
                        labels: {
                            format: '{value}',
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

                $('#revenue').click(function(){
                    GetData('url2');
                    alert('revenue data');
                });
    			$('#Data2').click(function(){
                    //FilterResult
                    GetData('url2');
                });

                $('#Data3').click(function(){
                    //FilterResult
                    GetData('url3');
                });
            });
        }
    }
    Draw.Tool = Tool;
} (window.Draw = window.Draw || {}));
