
EVENT_NAME_DICT={
    # maps root

    r'^/watch/([0-9a-zA-Z-+%\(\)., ]+)/([0-9a-zA-Z-+%\(\)., ]+)/([a-zA-Z-]+)/$' : {
        'name' : 'event.video.watch'
    },

    r'^/cdcontent/$' : {
        'name' : 'event.cdcontent.download'
    },

    r'^/tutorial-search/$' : {
        'name' : 'event.tutorial.search'
    },

    r'^/news/' : {
        'name' : 'event.news'
    },

    r'^/accounts/login/$' : {
        'name' : 'event.login'
    },

    r'^/accounts/logout/$' : {
        'name' : 'event.logout'
    },

    r'^/accounts/register/$' : {
        'name' : 'event.register'
    },

    r'^/software-training/$' : {
        'name' : 'event.software.training'
    },

    r'^/software-training/training-planner/$' : {
        'name' : 'event.software.training.planner'
    },

    r'^/software-training/student-batch/$' : {
        'name' : 'event.software.training.student.batch'
    },

    r'^/software-training/select-participants/$' : {
        'name' : 'event.software.training.select.participants'
    },

    r'^/software-training/resource-center/$' : {
        'name' : 'event.software.training.resource.center'
    },

    r'^/participant/login/$' : {
        'name' : 'event.participant.login'
    },


    r'^/statistics/$' : {
        'name' : 'event.statistics'
    },

    r'^/statistics/training/$' : {
        'name' : 'event.statistics.training'
    },

    r'^/statistics/pmmmnmtt/fdp/$' : {
        'name' : 'event.statistics.fdp.training'
    },

    r'^/statistics/tutorial-content/$' : {
        'name' : 'event.statistics.tutorial.content'
    },

    r'^/statistics/online-test/$' : {
        'name' : 'event.statistics.online.test'
    },

    r'^/statistics/academic-center/$' : {
        'name' : 'event.statistics.academic.center'
    },
    
    'home':{
        'name' : 'event.home.view'
    },
}