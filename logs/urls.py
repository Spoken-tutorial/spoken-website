
EVENT_NAME_DICT={
    # maps root

    r'^/watch/([0-9a-zA-Z-+%\(\)., ]+)/([0-9a-zA-Z-+%\(\)., ]+)/([a-zA-Z-]+)/$' : {
        'name' : 'event.video.watch'
    },
    
    'home':{
        'name' : 'event.home.view'
    },
}