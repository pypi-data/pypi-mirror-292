# Thumbsup 👍

`thumbsup` is a command-line tool for generating thumbnails from video files. It supports various video formats and allows you to capture frames from specified positions within the video. Ideal for quickly creating snapshots from videos for previews or documentation.

## Features

- **List Directory Contents**: Display information about files and directories, including sizes.
- **Generate Thumbnails**: Create thumbnail images from videos in specified formats.
- **Flexible Frame Extraction**: Capture frames at specified percentages of the video's duration.
- **Customizable Output**: Specify the output directory and file formats to process.

## Installation

You can install `thumbsup` via `pip`:

```bash
pip install thumbsup
```

## Usage

### List Directory Contents

```bash
thumbsup --ls /path/to/directory
```

### Generate Thumbnails from a Directory

```bash
thumbsup --dir /path/to/directory --format .mp4 .mov --dest /path/to/output --at 0.25 0.5 0.75
```

### Generate Thumbnails from a File

```bash
thumbsup --file /path/to/video.mp4 --dest /path/to/output --at 0.25 0.5 0.75
```

## Arguments

- `--dir`: Directory to process for video files.
- `--ls`: List information about the specified path.
- `--file`: Single file to process for thumbnails.
- `--dest`: Output directory where thumbnails will be saved.
- `--format`: Video file formats to include (e.g., `.mp4`, `.mov`).
- `--at`: Frame positions to capture (as percentages, e.g., `0.25` for 25%).

## Examples

To list the contents of a directory:

```bash
thumbsup --ls /my/videos
```

To generate thumbnails from all `.mp4` and `.mov` files in a directory:

```bash
thumbsup --dir /my/videos --format .mp4 .mov --dest /my/thumbnails --at 0.25 0.5 0.75
```

## Contributing

If you want to contribute to `thumbsup`, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
