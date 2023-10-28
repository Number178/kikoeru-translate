import argparse
import os
from pathlib import Path

from transcribe import WhisperModel
from utils import format_timestamp


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcribe audio files with a Whisper model")
    parser.add_argument(
        "--audio-dir",
        type=str,
        required=True,
        help="Path to directory containing audio files to transcribe",
    )
    parser.add_argument(
        "--save-dir",
        type=str,
        default="./",
        help="Path to directory to save transcribed results",
    )
    parser.add_argument(
        "--device",
        default="auto",
        help="Device to use for PyTorch inference",
    )
    parser.add_argument(
        "--model",
        default="./_internal/model",
        help="Name or path to the Whisper model to use",
    )
    return parser


if __name__ == "__main__":
    args = get_parser().parse_args()
    Path(args.save_dir).mkdir(parents=True, exist_ok=True)

    print("正在加载模型...")
    compute_type = "default" if args.device == "cuda" else "int8"
    model = WhisperModel(args.model, device=args.device, compute_type=compute_type)

    print("读取音频...")
    for audio_path in filter(lambda p: not os.path.basename(p).startswith(".") ,Path(args.audio_dir).iterdir()):
        print("正在处理: {} ...".format(audio_path))
        segments, _ = model.transcribe(task="transcribe", audio=str(audio_path), language="zh")
        audio_basename = os.path.basename(audio_path)
        audio_basename = os.path.splitext(audio_basename)[0]
        output_path = os.path.join(args.save_dir, audio_basename + ".lrc")
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(["[{}] {}\n".format(format_timestamp(seg.start)[:-1], seg.text) for seg in segments])
        print("{}的字幕文件已保存到{}".format(audio_path, output_path))
