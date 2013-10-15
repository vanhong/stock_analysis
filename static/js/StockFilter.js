(function(StockFilter) {

    function Filter() {

        var doFilter = function() {
            $.post('{% url "dofilter" %}' , 
                function(data, status) { 
                    alert("after load, get data=" + data + ", status=" + status); 
                    $('#FilterResult').css('display','block');
                }).fail(function(xhr){alert('error=' + xhr.statusText);});
        }

        var doFilter3 = function() {
            var postUrl = "/filter/start/";
            values = [1, 2];
            var jsonText = JSON.stringify(values);
            $.ajax({
                url: postUrl,
                type: 'POST',
                success: function(result){
                    alert('finish');
                }
            });       
        }

        var startFilter = function() {
            var conditions = {};

            $('input[id^=Con-]').each(function(){
                if($(this).attr('checked')){
                    var condition = $(this).attr('id').split('-')[1];
                    var params;
                    $('[id^=' + condition +'-]').each(function(){
                        conditions[$(this).attr('id')] = $(this).val();
                    });
                }
            });
            
            $('#FilterResult').html('&nbsp;').load('/filter/start/', conditions, function(){
                //alert('finish');
            });
        }

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
				$('#StartFilter').click(function(){
                    //FilterResult
                    startFilter();
                });
            });
        }
    }
    StockFilter.Filter = Filter;
} (window.StockFilter = window.StockFilter || {}));