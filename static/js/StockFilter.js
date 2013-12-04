(function(filter_menu){
    function menu() {
        this.Init = function () {
            $(window).load(function(){
                $('#filter_menu').html('&nbsp;').load('/filter_menu/', {'kind':'revenue'});

                $('#filter_menu_revenue').click(function(){
                    alert('hello');
                    $('#filter_menu').html('&nbsp;').load('/filter_menu/', {'kind':'revenue'});
                    $('button[id^="filter_menu"]').attr('class', 'btn btn-primary');
                    
                });
            });
        }
    }
    filter_menu.menu = menu;
}(window.filter_menu = window.filter_menu ||{}));

function show_filter_menu(kind) {
    $(document).ready(function() {
        $('#filter_menu').html('&nbsp;').load('/filter_menu/', {'kind':kind});
        
    });
    // var myObj = document.getElementsByClassName('btn btn-success');
    // if (myObj.length >= 0) {
    //     myObj[0].className = 'btn btn-primary';
    // }
}

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

            $('input[id^=con-]').each(function(){
                if($(this).attr('checked')){
                    var condition = $(this).attr('id').split('-')[1];
                    var params;
                    $('[id^=' + condition +'-]').each(function(){
                        conditions[$(this).attr('id')] = $(this).val();
                    });
                }
            });
            $('#Message').html('<b> | Processing...</b>');
            $('#FilterResult').load('/filter/start/', conditions, function(){
                //alert('finish');
                $('#Message').html('');
            });
        }

        this.Init = function() {
            //alert("Init");
            $(window).load(function() {
                $('input[id^=con-]').click(function(){
                    if($(this).attr('checked') == 'checked'){
                        $(this).attr('checked',false)
                    }else{
                        $(this).attr('checked',true)
                    }
                });

				$('#StartFilter').click(function(){
                    //FilterResult
                    startFilter();
                });
            });
        }
    }
    StockFilter.Filter = Filter;
} (window.StockFilter = window.StockFilter || {}));