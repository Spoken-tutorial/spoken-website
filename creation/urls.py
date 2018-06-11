# Third Party Stuff
from django.conf.urls import (
    include,
    patterns,
    url
)

urlpatterns = patterns('',
        # Main pages dispatcher
        url(r'^$', 'creation.views.creationhome', name="creationhome"),

        # Contributor part
        url(r'^upload/$', 'creation.views.upload_index', name="upload_index"),
        url(r'^upload/tutorial/(\d+)/$', 'creation.views.upload_tutorial', name="upload_tutorial"),
        url(r'^upload/outline/(\d+)/$', 'creation.views.upload_outline', name="upload_outline"),
        url(r'^upload/script/(\d+)/$', 'creation.views.upload_script', name="upload_script"),
        url(r'^upload/timed-script/$', 'creation.views.upload_timed_script', name="upload_timed_script"),
        url(r'^upload/timed-script/(\d+)/save/$', 'creation.views.save_timed_script', name="save_timed_script"),
        url(r'^upload/keywords/(\d+)/$', 'creation.views.upload_keywords', name="upload_keywords"),
        url(r'^upload/prerequisite/(\d+)/$', 'creation.views.upload_prerequisite', name="upload_prerequisite"),
        url(r'^upload/component/(\d+)/(\w+)/$', 'creation.views.upload_component', name="upload_component"),
        url(r'^mark/notrequired/(\d+)/(\d+)/(\w+)/$', 'creation.views.mark_notrequired', name="mark_notrequired"),
        url(r'^view/component/(?P<trid>\d+)/(?P<component>\w+)/$', 'creation.views.view_component', name="view_component"),
        url(r'^view/preview_check_avaiable/(?P<trid>\d+)/(?P<component>\w+)/$', 'creation.views.preview_check_avaiable', name="preview_check_avaiable"),
        url(r'^view/component/(?P<trid>\d+)/(?P<component>\w+)/(?P<aud_type>\w+)$', 'creation.views.view_component_audtype', name="view_component_audtype"),
        url(r'^upload/needimprovement/$', 'creation.views.tutorials_needimprovement', name="tutorials_needimprovement"),
        url(r'^upload/contributed/$', 'creation.views.tutorials_contributed', name="tutorials_contributed"),
        url(r'^upload/pending-tutorials/$', 'creation.views.tutorials_pending', name="tutorials_pending"),
        url(r'^upload-publish-outline/$', 'creation.views.upload_publish_outline', name="upload_publish_outline"),
        url(r'^list-missing-script/$', 'creation.script.list_missing_script', name="list_missing_script"),
        url(r'^ajax-upload-foss/$', 'creation.views.ajax_upload_foss', name="ajax_upload_foss"),
        url(r'^ajax-upload-prerequisite/$', 'creation.views.ajax_upload_prerequisite', name="ajax_upload_prerequisite"),
        url(r'^ajax-upload-timed-script/$', 'creation.views.ajax_upload_timed_script', name="ajax_upload_timed_script"),
        url(r'^ajax-get-keywords/$', 'creation.views.ajax_get_keywords', name="ajax_get_keywords"),
        url(r'^view_brochure/$', 'creation.views.view_brochure', name="view_brochure"),

        # Admin Reviewer part
        url(r'^admin-review/$', 'creation.views.admin_review_index', name="admin_review_index"),
        url(r'^admin-review/reviewed/$', 'creation.views.admin_reviewed_video', name="admin_reviewed_video"),
        url(r'^admin-review/video/(\d+)/$', 'creation.views.admin_review_video', name="admin_review_video"),

        # Domain Reviewer part
        url(r'^domain-review/$', 'creation.views.domain_review_index', name="domain_review_index"),
        url(r'^domain-review/reviewed/$', 'creation.views.domain_reviewed_tutorials', name="domain_reviewed_tutorials"),
        url(r'^domain-review/tutorial/(\d+)/$', 'creation.views.domain_review_tutorial', name="domain_review_tutorial"),
        url(r'^domain-review/component/(\d+)/(\w+)/$', 'creation.views.domain_review_component', name="domain_review_component"),

        # Quality Reviewer part
        url(r'^quality-review/$', 'creation.views.quality_review_index', name="quality_review_index"),
        url(r'^quality-review/(\d+)/$', 'creation.views.quality_review_index', name="quality_review_index"),
        url(r'^quality-review/reviewed/$', 'creation.views.quality_reviewed_tutorials', name="quality_reviewed_tutorials"),
        url(r'^quality-review/tutorial/(\d+)/$', 'creation.views.quality_review_tutorial', name="quality_review_tutorial"),
        url(r'^quality-review/tutorial/publish/index/$', 'creation.views.publish_tutorial_index', name="publish_tutorial_index"),
        url(r'^quality-review/tutorial/publish/(\d+)/$', 'creation.views.publish_tutorial', name="publish_tutorial"),
        url(r'^quality-review/component/(\d+)/(\w+)/$', 'creation.views.quality_review_component', name="quality_review_component"),
        url(r'^public-review/tutorial/index/$', 'creation.views.public_review_tutorial_index', name="public_review_tutorial_index"),
        url(r'^public-review/tutorial/(\d+)/$', 'creation.views.public_review_tutorial', name="public_review_tutorial"),
        url(r'^public-review/publish/(\d+)/$', 'creation.views.public_review_publish', name="public_review_publish"),
        url(r'^public-review/mark-as-pending/(\d+)/$', 'creation.views.public_review_mark_as_pending', name="public_review_mark_as_pending"),
        url(r'^public-review/list/$', 'creation.views.public_review_list', name="public_review_list"),

        # Administrator part
        url(r'^role/requests/$', 'creation.views.creation_list_role_requests', name="creation_list_role_requests"),
        url(r'^update-prerequisite/$', 'creation.views.update_prerequisite', name="update_prerequisite"),
        url(r'^update-keywords/$', 'creation.views.update_keywords', name="update_keywords"),
        url(r'^update-manual/(\w+)/$', 'creation.views.update_sheet', name="update_sheet"),
        url(r'^update-assignment/$', 'creation.views.update_assignment', name="update_assignment"),
        url(r'^role/requests/([a-zA-Z-]+)/$', 'creation.views.creation_list_role_requests', name="creation_list_role_requests"),
        url(r'^role/accept/(\d+)/$', 'creation.views.creation_accept_role_request', name="creation_accept_role_request"),
        url(r'^role/reject/(\d+)/$', 'creation.views.creation_reject_role_request', name="creation_reject_role_request"),
        url(r'^role/revoke/([a-zA-Z-]+)/$', 'creation.views.creation_revoke_role_request', name="creation_revoke_role_request"),
        url(r'^admin/tutorial/status/pending/$', 'creation.views.creation_change_published_to_pending', name="creation_change_published_to_pending"),
        url(r'^admin/tutorial/component/status/$', 'creation.views.creation_change_component_status', name="creation_change_component_status"),
        url(r'^ajax-publish-to-pending/$', 'creation.views.ajax_publish_to_pending', name="ajax_publish_to_pending"),
        url(r'^ajax-change-component-status/$', 'creation.views.ajax_change_component_status', name="ajax_change_component_status"),
        url(r'^ajax-manual-language/$', 'creation.views.ajax_manual_language', name="ajax_manual_language"),
        url(r'^ajax-get-tutorials/$', 'creation.views.ajax_get_tutorials', name="ajax_get_tutorials"),

        # Common to Domain & Admin reviewer parts
        url(r'^accept-all/(\w+)/(\d+)/$', 'creation.views.accept_all', name="accept_all"),
        url(r'^delete-notification/(\w+)/(\d+)/$', 'creation.views.delete_creation_notification', name="delete_creation_notification"),
        url(r'^clear-notifications/(\w+)/$', 'creation.views.clear_creation_notification', name="clear_creation_notification"),
        url(r'^tutorial/view/([0-9a-zA-Z-+%\(\).]+)/([0-9a-zA-Z-+%\(\)]+)/([a-zA-Z-]+)/$', 'creation.views.creation_view_tutorial', name="creation_view_tutorial"),
        url(r'^init/$', 'creation.views.init_creation_app', name="init_creation_app"),
        url(r'^role/add/([a-zA-Z-]+)/$', 'creation.views.creation_add_role', name="creation_add_role"),
        url(r'^collaborate/$', 'creation.views.collaborate', name="collaborate"),
        url(r'^suggest-a-topic/$', 'creation.views.suggest_topic', name="suggest_topic"),
        url(r'^suggest-an-example/$', 'creation.views.suggest_example', name="suggest_example"),
        url(r'^report-missing-component/(\d+)/$', 'creation.views.report_missing_component', name="report_missing_component"),
        url(r'^report-missing-component/reply/(\d+)/$', 'creation.views.report_missing_component_reply', name="report_missing_component_reply"),
        url(r'^report-missing-component/list/$', 'creation.views.report_missing_component_list', name="report_missing_component_list"),
        )
