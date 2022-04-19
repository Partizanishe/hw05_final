import tempfile
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

GROUP_TITLE = "Тестовая группа - 1"
GROUP_SLUG = "test-slug_1"
GROUP_DESCRIPTION = "Тестовое описание группы 1"
GROUP_TITLE_NEW = "Тестовая группа- 2"
GROUP_SLUG_NEW = "test-slug_2"
GROUP_DESCRIPTION_NEW = "Тестовое описание группы 2"
POST_TEXT = "Test Test Test Test Test Text"
COMMENT_TEXT = "Test Comment Text"
USERNAME = "HasNoName"
USERNAME_ALTER = "HasSomeName"
USERNAME_ALTER2 = "HasAnotherName"


INDEX_URL = reverse("posts:index")
FOLLOW_INDEX_URL = reverse("posts:follow_index")
GROUP_LIST_URL = reverse("posts:group_posts", args=[GROUP_SLUG])
PROFILE_URL = reverse("posts:profile", args=[USERNAME])
GROUP_LIST_URL_2 = reverse("posts:group_posts", args=[GROUP_SLUG_NEW])
POST_CREATE_URL = reverse("posts:post_create")
LOGIN_URL = reverse("users:login")
OTHER_PAGES = 4
NEXT_PAGE = "?page=2"
NEXT = "?next="

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x02\x00"
    b"\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
    b"\x00\x00\x00\x2C\x00\x00\x00\x00"
    b"\x02\x00\x01\x00\x00\x02\x02\x0C"
    b"\x0A\x00\x3B"
)
UPLOADED = SimpleUploadedFile(
    name="small.gif", content=SMALL_GIF, content_type="image/gif"
)
