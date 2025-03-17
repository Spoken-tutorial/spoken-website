# Third Party Stuff
from django.urls import path, re_path
from creation.views import *
from creation.script import *
from django.contrib.sitemaps.views import sitemap
from creation.sitemaps import TutorialSitemap

app_name = 'creation'

tutorial_sitemaps = {
    'tutorial': TutorialSitemap
}

urlpatterns = [
    # Main pages dispatcher
    path(r'',  creationhome, name="creationhome"),

    # Contributor part
    re_path(r'^upload/$',  upload_index, name="upload_index"),
    re_path(r'^upload/tutorial/(\d+)/$',  upload_tutorial, name="upload_tutorial"),
    re_path(r'^upload/outline/(\d+)/$',  upload_outline, name="upload_outline"),
    re_path(r'^upload/script/(\d+)/$',  upload_script, name="upload_script"),
    re_path(r'^upload/timed-script/$',  upload_timed_script, name="upload_timed_script"),
    re_path(r'^upload/timed-script/(\d+)/save/$',  save_timed_script, name="save_timed_script"),
    re_path(r'^upload/keywords/(\d+)/$',  upload_keywords, name="upload_keywords"),
    re_path(r'^upload/prerequisite/(\d+)/$',  upload_prerequisite, name="upload_prerequisite"),
    re_path(r'^upload/component/(\d+)/(\w+)/$',  upload_component, name="upload_component"),
    re_path(r'^mark/notrequired/(\d+)/(\d+)/(\w+)/$',  mark_notrequired, name="mark_notrequired"),
    re_path(r'^view/component/(\d+)/(\w+)/$',  view_component, name="view_component"),
    re_path(r'^upload/needimprovement/$',  tutorials_needimprovement, name="tutorials_needimprovement"),
    re_path(r'^upload/contributed/$',  tutorials_contributed, name="tutorials_contributed"),
    re_path(r'^upload/pending-tutorials/$',  tutorials_pending, name="tutorials_pending"),
    re_path(r'^upload-publish-outline/$',  upload_publish_outline, name="upload_publish_outline"),
    re_path(r'^list-missing-script/$', list_missing_script, name="list_missing_script"),
    re_path(r'^ajax-upload-foss/$',  ajax_upload_foss, name="ajax_upload_foss"),
    re_path(r'^ajax-upload-prerequisite/$',  ajax_upload_prerequisite, name="ajax_upload_prerequisite"),
    re_path(r'^ajax-upload-timed-script/$',  ajax_upload_timed_script, name="ajax_upload_timed_script"),
    re_path(r'^ajax-get-keywords/$',  ajax_get_keywords, name="ajax_get_keywords"),
    re_path(r'^view_brochure/$',  view_brochure, name="view_brochure"),

    # Admin Reviewer part
    re_path(r'^admin-review/$',  admin_review_index, name="admin_review_index"),
    re_path(r'^admin-review/reviewed/$',  admin_reviewed_video, name="admin_reviewed_video"),
    re_path(r'^admin-review/video/(\d+)/$',  admin_review_video, name="admin_review_video"),

    # Domain Reviewer part
    re_path(r'^domain-review/$',  domain_review_index, name="domain_review_index"),
    re_path(r'^domain-review/reviewed/$',  domain_reviewed_tutorials, name="domain_reviewed_tutorials"),
    re_path(r'^domain-review/tutorial/(\d+)/$',  domain_review_tutorial, name="domain_review_tutorial"),
    re_path(r'^domain-review/component/(\d+)/(\w+)/$',  domain_review_component, name="domain_review_component"),

    # Quality Reviewer part
    re_path(r'^quality-review/$',  quality_review_index, name="quality_review_index"),
    re_path(r'^quality-review/(\d+)/$',  quality_review_index, name="quality_review_index"),
    re_path(r'^quality-review/reviewed/$',  quality_reviewed_tutorials, name="quality_reviewed_tutorials"),
    re_path(r'^quality-review/tutorial/(\d+)/$',  quality_review_tutorial, name="quality_review_tutorial"),
    re_path(r'^quality-review/tutorial/publish/index/$',  publish_tutorial_index, name="publish_tutorial_index"),
    re_path(r'^quality-review/tutorial/publish/(\d+)/$',  publish_tutorial, name="publish_tutorial"),
    re_path(r'^quality-review/component/(\d+)/(\w+)/$',  quality_review_component, name="quality_review_component"),
    re_path(r'^public-review/tutorial/index/$',  public_review_tutorial_index, name="public_review_tutorial_index"),
    re_path(r'^public-review/tutorial/(\d+)/$',  public_review_tutorial, name="public_review_tutorial"),
    re_path(r'^public-review/publish/(\d+)/$',  public_review_publish, name="public_review_publish"),
    re_path(r'^public-review/mark-as-pending/(\d+)/$',  public_review_mark_as_pending, name="public_review_mark_as_pending"),
    re_path(r'^public-review/list/$',  public_review_list, name="public_review_list"),

    # Administrator part
    re_path(r'^role/requests/$',  creation_list_role_requests, name="creation_list_role_requests"),
    re_path(r'^role/lang_requests/$',  creation_lang_list_role_requests, name="creation_lang_list_role_requests"),
    re_path(r'^update-prerequisite/$',  update_prerequisite, name="update_prerequisite"),
    re_path(r'^update-keywords/$',  update_keywords, name="update_keywords"),
    re_path(r'^update-manual/(\w+)/$',  update_sheet, name="update_sheet"),
    re_path(r'^update-assignment/$',  update_assignment, name="update_assignment"),
    re_path(r'^update-thumbnail/$',  update_thumbnail, name="update_thumbnail"),
    re_path(r'^update-codefiles/$',  update_codefiles, name="update_codefiles"),
    re_path(r'^role/requests/([a-zA-Z-]+)/$',  creation_list_role_requests, name="creation_list_role_requests"),
    re_path(r'^role/lang_requests/([a-zA-Z-]+)/$',  creation_lang_list_role_requests, name="creation_lang_list_role_requests"),
    re_path(r'^role/accept/(?P<recid>\d+)/(?P<user_type>\w+)/$',  creation_accept_role_request, name="creation_accept_role_request"),
    re_path(r'^role/reject/(?P<recid>\d+)/(?P<user_type>\w+)/$',  creation_reject_role_request, name="creation_reject_role_request"),
    re_path(r'^role/revoke/([a-zA-Z-]+)/([0-9/]+)/$',  creation_revoke_role_request, name="creation_revoke_role_request"),
    re_path(r'^admin/tutorial/status/pending/$',  creation_change_published_to_pending, name="creation_change_published_to_pending"),
    re_path(r'^admin/tutorial/component/status/$',  creation_change_component_status, name="creation_change_component_status"),
    re_path(r'^ajax-publish-to-pending/$',  ajax_publish_to_pending, name="ajax_publish_to_pending"),
    re_path(r'^ajax-change-component-status/$',  ajax_change_component_status, name="ajax_change_component_status"),
    re_path(r'^ajax-manual-language/$',  ajax_manual_language, name="ajax_manual_language"),
    re_path(r'^ajax-get-tutorials/$',  ajax_get_tutorials, name="ajax_get_tutorials"),
    re_path(r'^update-common-component/$', update_common_component, name="update_common_component"),
    re_path(r'^update_tutorials/$',  update_tutorials, name="update_tutorials"),
    re_path(r'^grant_role/$',  grant_role, name="grant_role"),

    # Common to Domain & Admin reviewer parts    
    re_path(r'^accept-all/(\w+)/(\d+)/$',  accept_all, name="accept_all"),
    re_path(r'^delete-notification/(\w+)/(\d+)/$',  delete_creation_notification, name="delete_creation_notification"),
    re_path(r'^clear-notifications/(\w+)/$',  clear_creation_notification, name="clear_creation_notification"),
    re_path(r'^tutorial/view/([0-9a-zA-Z-+%\(\).,\']+)/([0-9a-zA-Z-+%\(\).,\']+)/([a-zA-Z-]+)/$',  creation_view_tutorial, name="creation_view_tutorial"),
    re_path(r'^init/$',  init_creation_app, name="init_creation_app"),
    re_path(r'^role/add/([a-zA-Z-]+)/([0-9/]+)/$',  creation_add_role, name="creation_add_role"),
    re_path(r'^collaborate/$',  collaborate, name="collaborate"),
    re_path(r'^suggest-a-topic/$',  suggest_topic, name="suggest_topic"),
    re_path(r'^suggest-an-example/$',  suggest_example, name="suggest_example"),
    re_path(r'^report-missing-component/(\d+)/$',  report_missing_component, name="report_missing_component"),
    re_path(r'^report-missing-component/reply/(\d+)/$',  report_missing_component_reply, name="report_missing_component_reply"),
    re_path(r'^report-missing-component/list/$',  report_missing_component_list, name="report_missing_component_list"),
    

    # Additional Views Created for Payment Module
    re_path(r'payment/tutorials/$',  list_all_published_tutorials, name="list_all_published_tutorials"),
    re_path(r'payment/ajax/languages/$',  load_languages, name="load_languages"),
    re_path(r'payment/ajax/fosses/$',  load_fosses, name="load_fosses"),
    re_path(r'payment/due/$',  list_all_due_tutorials, name="payment_due_tutorials"),
    re_path(r'payment/honorarium/$',  list_payment_honorarium, name="payment_honorarium_list"),
    re_path(r'payment/honorarium/detail/(\d+)/$',  detail_payment_honorarium, name="payment_honorarium_detail"),
    re_path(r'hono_agreement/(?P<hono_id>\d+)/',honorarium_agreement,name='honorarium_agreement'),
    re_path(r'honorarium/(?P<hono_id>\d+)/',honorarium,name='honorarium'),
    re_path(r'hono_receipt/(?P<hono_id>\d+)/',honorarium_receipt,name='honorarium_receipt'),
    re_path(r'add_details/',add_details,name='add_details'),
    re_path(r'save_details/',save_details,name='save_details'),
    re_path(r'file_checker/(?P<username>[\w]+)/(?P<file_name>[-\w]+)',file_checker,name='file_checker'),



    #Bidding Module
    re_path(r'^rate_contributors/$',rate_contributors,name = "rate_contributors"),
    re_path(r'^add_contributorrating',add_contributorrating,name  = "add_contributorrating"),
    re_path(r'^allocate_tutorial/(?P<sel_status>\w+)/(?P<role>\w+)/$', allocate_tutorial, name="allocate_tutorial"),
    re_path(r'^allocate_tutorial_manager/(?P<sel_status>\w+)/(?P<role>\w+)/$', allocate_tutorial, name="allocate_tutorial_manager"),
    #re_path(r'^refresh_tutorials/$',refresh_tutorials,name = "refresh_tutorials"),
    #re_path(r'^revoke_allocated_tutorial/(?P<uid>\w+)/(?P<lid>\w+)/(?P<tdid>\w+)/(?P<taid>\w+)/(?P<reason>\w+)/$', revoke_allocated_tutorial, name="revoke_allocated_tutorial"),
    re_path(r'^revoke_allocated_tutorial/$', revoke_allocated_tutorial, name="revoke_allocated_tutorial"),
    re_path(r'^extend_submission_date/$', extend_submission_date, name="extend_submission_date"),
    re_path(r'^allocate/(?P<tdid>\d+)/(?P<lid>\d+)/(?P<uid>\d+)/(?P<days>\d+)/$', allocate, name="allocate"),
    re_path(r'^allocate_foss/(?P<fid>\d+)/(?P<lang>\w+)/(?P<uid>\d+)/(?P<level>\w+)/(?P<days>\d+)/$', allocate_foss, name="allocate_foss"),
    re_path(r'^get_languages/(?P<uid>\w+)$', get_languages, name="get_languages"),
    re_path(r'^get_tutorials/(?P<fid>\w+)/(?P<lang>\w+)$', get_tutorials, name="get_tutorials"),
    re_path(r'^get_other_languages/(?P<uid>\w+)$', get_other_languages, name="get_other_languages"),
    re_path(r'^get_domain_languages/(?P<uid>\w+)$', get_domain_languages, name="get_domain_languages"),
    re_path(r'^get_quality_languages/(?P<uid>\w+)$', get_quality_languages, name="get_quality_languages"),
    re_path(r'^refresh_roles/$', refresh_roles, name="refresh_roles"),
    re_path(r'^get_rated_contributors/$', get_rated_contributors, name="get_rated_contributors"),
    re_path(r'^update_contributors/$', update_contributors, name="update_contributors"),

    #creation sitemaps
    re_path(r'^sitemap\.xml/$', sitemap, {'sitemaps' : tutorial_sitemaps } , name='tutorial_sitemap'),
]
