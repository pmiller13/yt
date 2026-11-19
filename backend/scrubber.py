import yt_dlp

def run_scrubber(url: str, download_dir: str = "/downloads"):
    ydl_opts = {
        # English audio only: best video-only stream up to 480p + best English track.
        # "language^=?en" = tagged English, or untagged (sites/uploads with no language
        # info). Dubs are always tagged, so a video whose tracks are all tagged as
        # other languages fails rather than downloading one. "bv" (not "bv*"): if the
        # video pick had its own audio, yt-dlp would keep it and drop the English track.
        "format": "bv[height<=480]+ba[language^=?en]/b[height<=480][language^=?en]/b[language^=?en]",

        # Prefer the original English track over English dubs/audio description (lang),
        # then the highest average audio bitrate (abr) and sample rate (asr). "lang"
        # must precede "abr": custom sort keys outrank yt-dlp's built-in ones.
        "format_sort": ["lang", "abr", "asr", "res:480", "fps"],

        "outtmpl": f"{download_dir}/%(upload_date)s-%(title)s-%(id)s.%(ext)s",
        "restrictfilenames": True,
        "writedescription": True,
        "writeinfojson": True,
        "addmetadata": True,
        "postprocessors": [
            {"key": "FFmpegMetadata", "add_chapters": True, "add_metadata": True},
            {"key": "EmbedThumbnail"},
            {"key": "FFmpegEmbedSubtitle"},
            # SponsorBlock
            {
                "key": "SponsorBlock",
                "api": "https://sponsor.ajay.app",
                "when": "after_filter",
                "categories": ["sponsor", "selfpromo", "interaction", "intro", "outro"],
            },
            {
                "key": "ModifyChapters",
                "remove_sponsor_segments": [
                    "sponsor",
                    "selfpromo",
                    "interaction",
                    "intro",
                    "outro",
                ],
            },
        ],
        "writesubtitles": True,
        "subtitleslangs": ["all"],
        "remote_components": ["ejs:github"],
        "sponsorblock_remove": [
            "sponsor",
            "selfpromo",
            "interaction",
            "intro",
            "outro",
        ],
        "merge_output_format": "mp4",
        "ignoreerrors": True,
        "verbose": True,
        "js_runtimes": {"deno": {"path": "deno"}},
    }

    if url.startswith("-"):
        raise ValueError("URL cannot start with a dash")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info is None:  # failed (e.g. no English audio track); yt-dlp already logged why
            return None
        return ydl.prepare_filename(info)
