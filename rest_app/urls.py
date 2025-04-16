from django.urls import path
from rest_app.views import (
    home_view, login_view, register_view, user_home_view, logout_view,
    upload_file_view, delete_file_view, list_folder_files_view,
    conversation_list_view, conversation_detail_view, send_prompt_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    # path('user-home/', user_home_view, name='user_home'),
    path('logout/', logout_view, name='logout'),
    # path('upload-file/', upload_file_view, name='upload_file'),
    # path('delete-file/<int:file_id>/', delete_file_view, name='delete_file'),
    # path('list-folder-files/', list_folder_files_view, name='list_folder_files'),
    path("main/", conversation_list_view, name="conversation_list"),
    path("main/conversation/<int:conversation_id>/", conversation_detail_view, name="conversation_detail"),
    path("main/send-prompt/", send_prompt_view, name="send_prompt"),
] 