$("#id_search_foss, #id_search_language").change(
    function() {
        var foss = $('#id_search_foss').val();
        var lang = $('#id_search_language').val();
        if ((foss == '' || lang == '') && ($(this).val() != '')){
            $.ajax(
                {
                    url: "/get-language/main/", 
                    type: "POST",
                    data: {
                        foss : foss,
                        lang : lang,
                    },
                    beforeSend: function() {
                        if(foss == '')
                            $('.ajax-refresh-search-foss').show();
                        if(lang == '')
                            $('.ajax-refresh-search-language').show();
                    },
                    success: function(data) {
                        if(data[0] == 'foss'){
                            $('#id_search_language').html(data[1]);
                        } else if(data[0] == 'lang'){
                            $('#id_search_foss').html(data[1]);
                        } else if(data[0] == 'reset') {
                            $('#id_search_language').html(data[1]);
                            $('#id_search_foss').html(data[2]);
                        }
                        if(foss == '')
                            $('.ajax-refresh-search-foss').hide();
                        if(lang == '')
                            $('.ajax-refresh-search-language').hide();
                    }
                }
            );
        }
    }
);
$("#id_search_otherfoss, #id_search_otherlanguage").change(
    function() {
        var foss = $('#id_search_otherfoss').val();
        var lang = $('#id_search_otherlanguage').val();
        if ((foss == '' || lang == '') && ($(this).val() != '')){
            $.ajax(
                {
                    url: "/get-language/series/",
                    type: "POST",
                    data: {
                        foss : foss,
                        lang : lang,
                    },
                    beforeSend: function() {
                        if(foss == '')
                            $('.ajax-refresh-search-otherfoss').show();
                        if(lang == '')
                            $('.ajax-refresh-search-otherlanguage').show();
                    },
                    success: function(data) {
                        if(data[0] == 'foss'){
                            $('#id_search_otherlanguage').html(data[1]);
                        } else if(data[0] == 'lang'){
                            $('#id_search_otherfoss').html(data[1]);
                        } else if(data[0] == 'reset') {
                            $('#id_search_otherlanguage').html(data[1]);
                            $('#id_search_otherfoss').html(data[2]);
                        }
                        if(foss == '')
                            $('.ajax-refresh-search-otherfoss').hide();
                        if(lang == '')
                            $('.ajax-refresh-search-otherlanguage').hide();
                    }
                }
            );
        }
    }
);
$("#id_search_archivedfoss, #id_search_archivedlanguage").change(
    function() {
        var foss = $('#id_search_archivedfoss').val();
        var lang = $('#id_search_archivedlanguage').val();
        if ((foss == '' || lang == '') && ($(this).val() != '')){
            $.ajax(
                {
                    url: "/get-language/archived/",
                    type: "POST",
                    data: {
                        foss : foss,
                        lang : lang,
                    },
                    beforeSend: function() {
                        if(foss == '')
                            $('.ajax-refresh-search-archivedfoss').show();
                        if(lang == '')
                            $('.ajax-refresh-search-archivedlanguage').show();
                    },
                    success: function(data) {
                        if(data[0] == 'foss'){
                            $('#id_search_archivedlanguage').html(data[1]);
                        } else if(data[0] == 'lang'){
                            $('#id_search_archivedfoss').html(data[1]);
                        } else if(data[0] == 'reset') {
                            $('#id_search_archivedlanguage').html(data[1]);
                            $('#id_search_archivedfoss').html(data[2]);
                        }
                        if(foss == '')
                            $('.ajax-refresh-search-archivedfoss').hide();
                        if(lang == '')
                            $('.ajax-refresh-search-archivedlanguage').hide();
                    }
                }
            );
        }
    }
);
$('.reset-filter').click(
    function(evt) {
        evt.preventDefault();
        $('#id_search_foss').val('');
        $('#id_search_language').val('');
        $.ajax(
            {
                url: "/get-language/main/",
                type: "POST",
                data: {
                    foss : '',
                    lang : '',
                },
                beforeSend: function() {
                    $('.ajax-refresh-search-foss').show();
                    $('.ajax-refresh-search-language').show();
                },
                success: function(data) {
                    if(data[0] == 'reset') {
                        $('#id_search_language').html(data[1]);
                        $('#id_search_foss').html(data[2]);
                        $('.ajax-refresh-search-foss').hide();
                        $('.ajax-refresh-search-language').hide();
                    }
                }
            }
        );
    }
);

(function(i, s, o, g, r, a, m) {
    i['GoogleAnalyticsObject'] = r;
    i[r] = i[r] || function(){
        (i[r].q = i[r].q || []).push(arguments)
    }, i[r].l = 1 * new Date();
    a = s.createElement(o), m = s.getElementsByTagName(o)[0];
    a.async = 1;
    a.src = g;
    m.parentNode.insertBefore(a,m)
})(window, document, 'script', '//www.google-analytics.com/analytics.js', 'ga');
ga('create', 'UA-57761078-1', 'auto');
ga('send', 'pageview');
