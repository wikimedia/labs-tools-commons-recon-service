
from service import app
from service.commons.commons import get_media_preview_url


def build_preview_content(media_id):
    """Builds HTMl preview for a media given the id

    Args:
        media_id (str): ID of media file

    Returns:
        html_preview (str): HTML preview string for image preview
    """

    media_url, media_title = get_media_preview_url(media_id)
    preview_width = str(app.config["MEDIA_PREV_W"])
    preview_height = str(app.config["MEDIA_PREV_H"])
    if media_url is not None and media_title is not None:
        return "<html><head><meta charset='utf-8' /></head>" \
            "<body> <img src=" + media_url + " width=" + preview_width + "\
            height=" + preview_height + " style='float: left'>"\
            "<p>" + media_title + " </p> </body>"\
            "</html>"
    else:
        return None
