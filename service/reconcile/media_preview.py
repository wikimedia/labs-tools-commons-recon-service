
import math
from service import app
from service.commons.commons import get_media_preview_data




def convert_size(size_bytes):
    """Convert the size of a file in bytes

    Args:
        size_bytes (int): size of the file in bytes.

    Returns:
        str: The converted size of the file.
    """

    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    size = "%s %s" % (s, size_name[i])
    print(size)

    return "%s %s" % (s, size_name[i])


def build_preview_file_from_type(url, title, preview_width,
                                 preview_height, file_width,
                                 file_height, file_size):
    """Build the actual preview

    Args:
        url (str): Media file url
        title (str): Media file title.
        preview_width (str): Width for image files.
        preview_height (str): Height for media file.
        file_width (str): Image file width.
        file_height (str): Image file height.
        file_size (str): media file size.
    Returns:
        HTML: HTML DOM preview object
    """

    file_extension = url.split(".")[-1].lower()

    # image options
    if file_extension in ["svg", "png", "jpg", "gif", "tiff", "webp", "xcf"]:
        return "<div width='1024' height='100px' style='position: fixed; overflow:hidden; width:400px'> " \
            "<span style='float: left'>" \
            "<img style='padding-right: 5px' src=" + url + " width=" + preview_width + " \
                height=" + preview_height + " style='float: left'>"\
            "</span>" \
            "<span style='float: left; margin-top: -10px'>" \
            "<p style='color: #11c; font-weight: bold; position: fixed; font-size: 10px; font-family: Arial, sans-serif'>" + title + " </p>"\
            "</span>" \
            "<span style='float: left; margin-top:20px'>" \
            "<p style='font-size: 10px;'>" + file_width + " x " + file_height + "; " + convert_size(file_size) + "</p>"\
            "</span></div>"

    # Audio options

    elif file_extension in ["mp3", "midi", "ogg", "webm", "flac", "wav"]:
        
        return "<div width='1024' height='100px' style='position: fixed; overflow:hidden; width:400px'> " \
            "<span style='float: left'>" \
            "<audio style='width: 175px; height:30px' controls><source src=" + url + " type='audio/" + file_extension + "'>"\
            "</span>" \
            "<span style='float: left; margin-top: -5px; margin-left: 5px'>" \
            "<p style=' color: #11c; font-weight: bold; position: fixed; font-size: 10px; font-family: Arial, sans-serif'>" + title + " </p>"\
            "</span>" \
            "<span style='float: left; margin-top:10px; margin-left: 5px'>" \
            "<p style='font-size: 10px;'>" + convert_size(file_size) + "</p>"\
            "</span>" \
            "</div>"

    # Video formats
    elif file_extension in ["webm", "webm", "mpeg", "ogv"]:
        return "<div width='1024' height='100px' style='position: fixed; overflow:hidden; width:400px'> " \
            "<span style='float: left'>" \
            "<video style='width: 200px; height:60px' controls><source src=" + url + " type='video/" + file_extension + "'>" \
            "</span>" \
            "<span style='float: left; margin-top: -5px; margin-left: 10px'>" \
            "<p style=' color: #11c; font-weight: bold; position: fixed; font-size: 10px; font-family: Arial, sans-serif'>" + title + " </p>" \
            "</span>" \
            "<span style='float: left; margin-top:10px; margin-left: 10px'>" \
            "<p style='font-size: 10px;'>" + convert_size(file_size) + "</p>" \
            "</span>" \
            "</div>"
    else:
        return "<strong> <h4>Preview not available</h4>"


def build_preview_content(media_id):
    """Builds HTMl preview for a media given the id

    Args:
        media_id (str): ID of media file

    Returns:
        html_preview (str): HTML preview string for image preview
    """

    preview_info = get_media_preview_data(media_id)
    preview_width = str(app.config["MEDIA_PREV_W"])
    preview_height = str(app.config["MEDIA_PREV_H"])

    if preview_info["url"] is not None and preview_info["title"] is not None:
        return build_preview_file_from_type(preview_info["url"], preview_info["title"], preview_width, preview_height,
                                            preview_info["width"], preview_info["height"], preview_info["size"])
    else:
        return None
