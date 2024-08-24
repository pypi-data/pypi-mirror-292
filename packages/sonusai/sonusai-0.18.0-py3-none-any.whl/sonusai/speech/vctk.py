import os
from pathlib import Path
from typing import Optional

from .types import TimeAlignedType


def _get_duration(name: str) -> float:
    import soundfile

    from sonusai import SonusAIError

    try:
        return soundfile.info(name).duration
    except Exception as e:
        raise SonusAIError(f'Error reading {name}: {e}')


def load_text(audio: str | os.PathLike[str]) -> Optional[TimeAlignedType]:
    """Load time-aligned text data given a VCTK audio file.

    :param audio: Path to the VCTK audio file.
    :return: A TimeAlignedType object.
    """
    import string

    file = Path(audio).parents[2] / 'txt' / Path(audio).parent.name / (Path(audio).stem[:-5] + '.txt')
    if not os.path.exists(file):
        return None

    with open(file, mode='r', encoding='utf-8') as f:
        line = f.read()

    start = 0
    end = _get_duration(str(audio))
    text = line.strip().lower().translate(str.maketrans('', '', string.punctuation))

    return TimeAlignedType(start, end, text)


def load_speakers(input_dir: Path) -> dict:
    speakers = {}
    with open(input_dir / 'speaker-info.txt') as file:
        for line in file:
            if not line.startswith('ID'):
                fields = line.strip().split('(', 1)[0].split()
                speaker_id = fields[0]
                age = fields[1]
                gender = fields[2]
                dialect = ' '.join([field for field in fields[3:]])
                speakers[speaker_id] = {'gender': gender, 'dialect': dialect, 'age': age}
    return speakers
