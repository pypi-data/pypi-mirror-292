import argparse
from pathlib import Path
import os
import cv2

supported_file_formats = [".mp4", ".mov", ".mkv", ".m4v"]

def is_valid_dir_path(path) -> Path:
    if os.path.isdir(path):
        return Path(path)
    if os.path.isfile(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid directory.")
    
    
    
def is_valid_file(path) -> Path:
    if os.path.isfile(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"'{path}' is not a file path.")
    
    
    
def ls(ls: Path) -> None :
    directory: Path = ls

    for i in directory.iterdir():
        if i.is_file():
            file_size = i.stat().st_size
            file_size_kb = file_size / 1000
            file_size_mb = file_size_kb / 1000
            
            print(f"{i.name} (FILE | {str(int(file_size_mb)) + ' MB' if file_size_kb > 1000 else str(file_size_kb) + ' KB'})")
        elif i.is_dir():
            print(f"{i.name} (DIR)")
  
  
    
def d_dir(dir: Path, format: list, dest: Path, at: list[float]) -> None :
    directory: Path = dir

    media_file_count = 0
    for i in directory.iterdir():
        if (i.suffix in format) & i.is_file():
            media_file_count += 1

            destination_path = dest / (i.stem + "_THUMBSUP")
            try:
                print(f"Thumbnail generation started for: {i.name}")
                extract_frames(str(i.absolute()), destination_path.resolve(), at)
                print(f"Thumbnail generation completed for: {i.name}")
                print(f"Destination: {destination_path.resolve()}")
            except Exception as err:
                print(f"Something went wrong. file: {i.name}")
                print(err)
                continue

    if not media_file_count:
        print(f"No media files found: --format {format}")
    elif media_file_count > 0:
        print(f"Found {media_file_count} media files: --format {format}")
        


def f_file(file: Path, format: list, dest: Path, at: list[float]):
    if file.is_file():
        destination_path = dest / (file.stem + "_THUMBSUP")
        try:
            print(f"Thumbnail generation started for: {file.name}")
            extract_frames(str(file.absolute()), destination_path.resolve(), at)
            print(f"Thumbnail generation completed for: {file.name}")
            print(f"Destination: {destination_path.resolve()}")
        except Exception as err:
            print(f"Something went wrong. file: {file.name}")
            print(err)
        


def extract_frames(video_path, output_dir, at):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the video file
    video = cv2.VideoCapture(video_path)
    
    # Get the total number of frames
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate frame positions for given, --at, arguments
    frame_positions = []
    for i in at:
        frame_positions.append(int(total_frames * i))

    for i, frame_pos in enumerate(frame_positions):
        # Set the video position
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        
        ret, frame = video.read()
        
        # If frame is read correctly
        if ret:
            # Generate the output filename
            output_filename = f"frame_{i+1}_at_{int(frame_pos / total_frames * 100)}_percent.jpg"
            output_path = os.path.join(output_dir, output_filename)
            
            # Save the frame as an image
            cv2.imwrite(output_path, frame)
            
            print(f"Saved frame at {int(frame_pos / total_frames * 100)}% of video duration")
        else:
            print(f"Failed to read frame at {int(frame_pos / total_frames * 100)}% of video duration")

    video.release()

    print("Frame extraction completed.")


            
parser = argparse.ArgumentParser(description="Thumbnail Generator CLI Tool")

parser.add_argument("-d", "--dir", help="directory to work with", type=is_valid_dir_path)
parser.add_argument("--ls", help="information about the specified path", type=is_valid_dir_path)
parser.add_argument("-F", "--file", help="the file to generate thumbnails from", type=is_valid_file)
parser.add_argument("-D", "--dest", default=".", help="output directory where all the thumbnail folders will be created", type=is_valid_dir_path)
parser.add_argument("-f", "--format", default=[".mp4"], help="to tell the file format(s) you want to capture", choices=supported_file_formats, nargs="+")
parser.add_argument("--at", default=[0.25, 0.5, 0.75], help="capture screenshot at... multiple arguments are supported. ex: 0.25 0.5 0.75", nargs="+", type=float)

args = parser.parse_args()



def main():
    if args.ls:
        ls(args.ls)
    if args.dir:
        d_dir(args.dir, args.format, args.dest, args.at)
    if args.file:
        f_file(args.file, args.format, args.dest, args.at)



if __name__ == "__main__":
    main()
