import yt_dlp

def run_scrubber(url: str, download_dir: str = "/downloads"):
    ydl_opts = {
        # Select best video up to 480p + the absolute best audio stream available
        "format": "bv*[height<=480]+ba/b[height<=480]/b",

        # Prioritize average audio bitrate (abr) and audio sample rate (asr)
        "format_sort": ["abr", "asr", "res:480", "fps"],

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
        "merge_output_format": "mkv",
        "ignoreerrors": True,
        "verbose": True,
        "js_runtimes": {"deno": {"path": "deno"}},
    }

    if url.startswith("-"):
        raise ValueError("URL cannot start with a dash")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
