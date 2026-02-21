import yt_dlp


def run_scrubber(url: str, download_dir: str = "/downloads"):
    # Ensure options match your specific needs
    ydl_opts = {
        "format": "bv*+ba/b",
        "format_sort": ["res:2160", "fps", "asr"],
        "outtmpl": f"{download_dir}/%(upload_date)s-%(title)s-%(id)s.%(ext)s",
        # Restrict filenames to ASCII characters, avoiding spaces and special chars
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
        "js_runtimes": {"deno": {"path": "deno"}},  # Use 'deno' from PATH
    }

    # Ensure URL doesn't start with a dash to prevent option injection
    if url.startswith("-"):
        raise ValueError("URL cannot start with a dash")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Return the filename so the frontend knows what to look for
        return ydl.prepare_filename(info)
