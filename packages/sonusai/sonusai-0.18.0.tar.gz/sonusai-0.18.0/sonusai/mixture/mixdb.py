from functools import cached_property
from functools import lru_cache
from functools import partial
from sqlite3 import Connection
from sqlite3 import Cursor
from typing import Any
from typing import Callable
from typing import Optional

from sonusai.mixture.datatypes import AudioF
from sonusai.mixture.datatypes import AudioT
from sonusai.mixture.datatypes import AudiosF
from sonusai.mixture.datatypes import AudiosT
from sonusai.mixture.datatypes import ClassCount
from sonusai.mixture.datatypes import Feature
from sonusai.mixture.datatypes import FeatureGeneratorConfig
from sonusai.mixture.datatypes import FeatureGeneratorInfo
from sonusai.mixture.datatypes import GeneralizedIDs
from sonusai.mixture.datatypes import ImpulseResponseFiles
from sonusai.mixture.datatypes import Mixture
from sonusai.mixture.datatypes import Mixtures
from sonusai.mixture.datatypes import NoiseFile
from sonusai.mixture.datatypes import NoiseFiles
from sonusai.mixture.datatypes import Segsnr
from sonusai.mixture.datatypes import SpectralMask
from sonusai.mixture.datatypes import SpectralMasks
from sonusai.mixture.datatypes import SpeechMetadata
from sonusai.mixture.datatypes import TargetFile
from sonusai.mixture.datatypes import TargetFiles
from sonusai.mixture.datatypes import TransformConfig
from sonusai.mixture.datatypes import Truth
from sonusai.mixture.datatypes import UniversalSNR


def db_file(location: str, test: bool = False) -> str:
    from os.path import join

    if test:
        name = 'mixdb_test.db'
    else:
        name = 'mixdb.db'

    return join(location, name)


def db_connection(location: str, create: bool = False, readonly: bool = True, test: bool = False) -> Connection:
    import sqlite3
    from os import remove
    from os.path import exists

    from sonusai import SonusAIError

    name = db_file(location, test)
    if create and exists(name):
        remove(name)

    if not create and not exists(name):
        raise SonusAIError(f'Could not find mixture database in {location}')

    if not create and readonly:
        name += '?mode=ro'

    connection = sqlite3.connect('file:' + name, uri=True)
    # connection.set_trace_callback(print)
    return connection


class SQLiteContextManager:
    def __init__(self, location: str, test: bool = False) -> None:
        self.location = location
        self.test = test

    def __enter__(self) -> Cursor:
        self.con = db_connection(location=self.location, test=self.test)
        self.cur = self.con.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.con.close()


class MixtureDatabase:
    def __init__(self, location: str, test: bool = False) -> None:
        self.location = location
        self.db = partial(SQLiteContextManager, self.location, test)

    @cached_property
    def json(self) -> str:
        from .datatypes import MixtureDatabaseConfig

        config = MixtureDatabaseConfig(
            class_balancing=self.class_balancing,
            class_labels=self.class_labels,
            class_weights_threshold=self.class_weights_thresholds,
            feature=self.feature,
            impulse_response_files=self.impulse_response_files,
            mixtures=self.mixtures,
            noise_mix_mode=self.noise_mix_mode,
            noise_files=self.noise_files,
            num_classes=self.num_classes,
            spectral_masks=self.spectral_masks,
            target_files=self.target_files,
            truth_mutex=self.truth_mutex,
            truth_reduction_function=self.truth_reduction_function
        )
        return config.to_json(indent=2)

    def save(self) -> None:
        """Save the MixtureDatabase as a JSON file
        """
        from os.path import join

        json_name = join(self.location, 'mixdb.json')
        with open(file=json_name, mode='w') as file:
            file.write(self.json)

    @cached_property
    def fg_config(self) -> FeatureGeneratorConfig:
        return FeatureGeneratorConfig(feature_mode=self.feature,
                                      num_classes=self.num_classes,
                                      truth_mutex=self.truth_mutex)

    @cached_property
    def fg_info(self) -> FeatureGeneratorInfo:
        from .helpers import get_feature_generator_info

        return get_feature_generator_info(self.fg_config)

    @cached_property
    def num_classes(self) -> int:
        with self.db() as c:
            return int(c.execute("SELECT top.num_classes from top").fetchone()[0])

    @cached_property
    def truth_mutex(self) -> bool:
        with self.db() as c:
            return bool(c.execute("SELECT top.truth_mutex from top").fetchone()[0])

    @cached_property
    def truth_reduction_function(self) -> str:
        with self.db() as c:
            return str(c.execute("SELECT top.truth_reduction_function from top").fetchone()[0])

    @cached_property
    def noise_mix_mode(self) -> str:
        with self.db() as c:
            return str(c.execute("SELECT top.noise_mix_mode from top").fetchone()[0])

    @cached_property
    def class_balancing(self) -> bool:
        with self.db() as c:
            return bool(c.execute("SELECT top.class_balancing from top").fetchone()[0])

    @cached_property
    def feature(self) -> str:
        with self.db() as c:
            return str(c.execute("SELECT top.feature from top").fetchone()[0])

    @cached_property
    def fg_decimation(self) -> int:
        return self.fg_info.decimation

    @cached_property
    def fg_stride(self) -> int:
        return self.fg_info.stride

    @cached_property
    def fg_step(self) -> int:
        return self.fg_info.step

    @cached_property
    def feature_parameters(self) -> int:
        return self.fg_info.feature_parameters

    @cached_property
    def ft_config(self) -> TransformConfig:
        return self.fg_info.ft_config

    @cached_property
    def eft_config(self) -> TransformConfig:
        return self.fg_info.eft_config

    @cached_property
    def it_config(self) -> TransformConfig:
        return self.fg_info.it_config

    @cached_property
    def transform_frame_ms(self) -> float:
        from .constants import SAMPLE_RATE

        return float(self.ft_config.R) / float(SAMPLE_RATE / 1000)

    @cached_property
    def feature_ms(self) -> float:
        return self.transform_frame_ms * self.fg_decimation * self.fg_stride

    @cached_property
    def feature_samples(self) -> int:
        return self.ft_config.R * self.fg_decimation * self.fg_stride

    @cached_property
    def feature_step_ms(self) -> float:
        return self.transform_frame_ms * self.fg_decimation * self.fg_step

    @cached_property
    def feature_step_samples(self) -> int:
        return self.ft_config.R * self.fg_decimation * self.fg_step

    def total_samples(self, m_ids: GeneralizedIDs = '*') -> int:
        return sum([self.mixture(m_id).samples for m_id in self.mixids_to_list(m_ids)])

    def total_transform_frames(self, m_ids: GeneralizedIDs = '*') -> int:
        return self.total_samples(m_ids) // self.ft_config.R

    def total_feature_frames(self, m_ids: GeneralizedIDs = '*') -> int:
        return self.total_samples(m_ids) // self.feature_step_samples

    def mixture_transform_frames(self, samples: int) -> int:
        return samples // self.ft_config.R

    def mixture_feature_frames(self, samples: int) -> int:
        return samples // self.feature_step_samples

    def mixids_to_list(self, m_ids: Optional[GeneralizedIDs] = None) -> list[int]:
        """Resolve generalized mixture IDs to a list of integers

        :param m_ids: Generalized mixture IDs
        :return: List of mixture ID integers
        """
        from .helpers import generic_ids_to_list

        return generic_ids_to_list(self.num_mixtures, m_ids)

    @cached_property
    def class_labels(self) -> list[str]:
        """Get class labels from db

        :return: Class labels
        """
        with self.db() as c:
            return [str(item[0]) for item in
                    c.execute("SELECT class_label.label FROM class_label ORDER BY class_label.id").fetchall()]

    @cached_property
    def class_weights_thresholds(self) -> list[float]:
        """Get class weights thresholds from db

        :return: Class weights thresholds
        """
        with self.db() as c:
            return [float(item[0]) for item in
                    c.execute("SELECT class_weights_threshold.threshold FROM class_weights_threshold").fetchall()]

    @cached_property
    def random_snrs(self) -> list[float]:
        """Get random snrs from db

        :return: Random SNRs
        """
        with self.db() as c:
            return list(set([float(item[0]) for item in
                             c.execute("SELECT mixture.snr FROM mixture WHERE mixture.random_snr == 1").fetchall()]))

    @cached_property
    def snrs(self) -> list[float]:
        """Get snrs from db

        :return: SNRs
        """
        with self.db() as c:
            return list(set([float(item[0]) for item in
                             c.execute("SELECT mixture.snr FROM mixture WHERE mixture.random_snr == 0").fetchall()]))

    @cached_property
    def all_snrs(self) -> list[UniversalSNR]:
        return sorted(list(set([UniversalSNR(is_random=False, value=snr) for snr in self.snrs] +
                               [UniversalSNR(is_random=True, value=snr) for snr in self.random_snrs])))

    @cached_property
    def spectral_masks(self) -> SpectralMasks:
        """Get spectral masks from db

        :return: Spectral masks
        """
        with self.db() as c:
            results = c.execute(
                "SELECT spectral_mask.f_max_width, f_num, t_max_width, t_num, t_max_percent FROM spectral_mask")
            return [SpectralMask(f_max_width=spectral_mask[0],
                                 f_num=spectral_mask[1],
                                 t_max_width=spectral_mask[2],
                                 t_num=spectral_mask[3],
                                 t_max_percent=spectral_mask[4]) for spectral_mask in results.fetchall()]

    def spectral_mask(self, sm_id: int) -> SpectralMask:
        """Get spectral mask with ID from db

        :param sm_id: Spectral mask ID
        :return: Spectral mask
        """
        return _spectral_mask(self.db, sm_id)

    @cached_property
    def target_files(self) -> TargetFiles:
        """Get target files from db

        :return: Target files
        """
        import json

        from .datatypes import TruthSetting
        from .datatypes import TruthSettings

        with self.db() as c:
            target_files: TargetFiles = []
            for target in c.execute(
                    "SELECT target_file.name, samples, level_type, id, speaker_id FROM target_file").fetchall():
                truth_settings: TruthSettings = []
                for ts in c.execute(
                        "SELECT truth_setting.setting " +
                        "FROM truth_setting, target_file_truth_setting " +
                        "WHERE ? = target_file_truth_setting.target_file_id " +
                        "AND truth_setting.id = target_file_truth_setting.truth_setting_id",
                        (target[3],)).fetchall():
                    entry = json.loads(ts[0])
                    truth_settings.append(TruthSetting(config=entry.get('config', None),
                                                       function=entry.get('function', None),
                                                       index=entry.get('index', None)))
                target_files.append(TargetFile(name=target[0],
                                               samples=target[1],
                                               level_type=target[2],
                                               truth_settings=truth_settings,
                                               speaker_id=target[4]))
            return target_files

    @cached_property
    def target_file_ids(self) -> list[int]:
        """Get target file IDs from db

        :return: List of target file IDs
        """
        with self.db() as c:
            return [int(item[0]) for item in c.execute("SELECT target_file.id FROM target_file").fetchall()]

    def target_file(self, t_id: int) -> TargetFile:
        """Get target file with ID from db

        :param t_id: Target file ID
        :return: Target file
        """
        return _target_file(self.db, t_id)

    @cached_property
    def num_target_files(self) -> int:
        """Get number of target files from db

        :return: Number of target files
        """
        with self.db() as c:
            return int(c.execute("SELECT count(target_file.id) FROM target_file").fetchone()[0])

    @cached_property
    def noise_files(self) -> NoiseFiles:
        """Get noise files from db

        :return: Noise files
        """
        with self.db() as c:
            return [NoiseFile(name=noise[0], samples=noise[1]) for noise in
                    c.execute("SELECT noise_file.name, samples FROM noise_file").fetchall()]

    @cached_property
    def noise_file_ids(self) -> list[int]:
        """Get noise file IDs from db

        :return: List of noise file IDs
        """
        with self.db() as c:
            return [int(item[0]) for item in c.execute("SELECT noise_file.id FROM noise_file").fetchall()]

    def noise_file(self, n_id: int) -> NoiseFile:
        """Get noise file with ID from db

        :param n_id: Noise file ID
        :return: Noise file
        """
        return _noise_file(self.db, n_id)

    @cached_property
    def num_noise_files(self) -> int:
        """Get number of noise files from db

        :return: Number of noise files
        """
        with self.db() as c:
            return int(c.execute("SELECT count(noise_file.id) FROM noise_file").fetchone()[0])

    @cached_property
    def impulse_response_files(self) -> ImpulseResponseFiles:
        """Get impulse response files from db

        :return: Impulse response files
        """
        with self.db() as c:
            return [str(impulse_response[0]) for impulse_response in
                    c.execute("SELECT impulse_response_file.file FROM impulse_response_file").fetchall()]

    @cached_property
    def impulse_response_file_ids(self) -> list[int]:
        """Get impulse response file IDs from db

        :return: List of impulse response file IDs
        """
        with self.db() as c:
            return [int(item[0]) for item in
                    c.execute("SELECT impulse_response_file.id FROM impulse_response_file").fetchall()]

    def impulse_response_file(self, ir_id: int) -> str:
        """Get impulse response file with ID from db

        :param ir_id: Impulse response file ID
        :return: Noise
        """
        return _impulse_response_file(self.db, ir_id)

    @cached_property
    def num_impulse_response_files(self) -> int:
        """Get number of impulse response files from db

        :return: Number of impulse response files
        """
        with self.db() as c:
            return int(c.execute("SELECT count(impulse_response_file.id) FROM impulse_response_file").fetchone()[0])

    @cached_property
    def mixtures(self) -> Mixtures:
        """Get mixtures from db

        :return: Mixtures
        """
        from .helpers import to_mixture
        from .helpers import to_target

        with self.db() as c:
            mixtures: Mixtures = []
            for mixture in c.execute(
                    "SELECT mixture.name, noise_file_id, noise_augmentation, noise_offset, noise_snr_gain, " +
                    "random_snr, snr, samples, spectral_mask_id, spectral_mask_seed, target_snr_gain, id " +
                    "FROM mixture").fetchall():
                targets = [to_target(target) for target in c.execute(
                    "SELECT target.file_id, augmentation, gain " +
                    "FROM target, mixture_target " +
                    "WHERE ? = mixture_target.mixture_id AND target.id = mixture_target.target_id",
                    (mixture[11],)).fetchall()]
                mixtures.append(to_mixture(mixture, targets))
            return mixtures

    @cached_property
    def mixture_ids(self) -> list[int]:
        """Get mixture IDs from db

        :return: List of zero-based mixture IDs
        """
        with self.db() as c:
            return [int(item[0]) - 1 for item in c.execute("SELECT mixture.id FROM mixture").fetchall()]

    def mixture(self, m_id: int) -> Mixture:
        """Get mixture record with ID from db

        :param m_id: Zero-based mixture ID
        :return: Mixture record
        """
        return _mixture(self.db, m_id)

    @cached_property
    def mixid_width(self) -> int:
        with self.db() as c:
            return int(c.execute("SELECT top.mixid_width from top").fetchone()[0])

    def location_filename(self, name: str) -> str:
        """Add the location to the given file name

        :param name: File name
        :return: Location added
        """
        from os.path import join

        return join(self.location, name)

    def mixture_filename(self, m_id: int) -> str:
        """Get the HDF5 file name for the give mixture ID

        :param m_id: Zero-based mixture ID
        :return: File name
        """
        return self.location_filename(self.mixture(m_id).name)

    @cached_property
    def num_mixtures(self) -> int:
        """Get number of mixtures from db

        :return: Number of mixtures
        """
        with self.db() as c:
            return int(c.execute("SELECT count(mixture.id) FROM mixture").fetchone()[0])

    def read_mixture_data(self, m_id: int, items: list[str] | str) -> Any:
        """Read mixture data from a mixture HDF5 file

        :param m_id: Zero-based mixture ID
        :param items: String(s) of dataset(s) to retrieve
        :return: Data (or tuple of data)
        """
        from .helpers import read_mixture_data

        return read_mixture_data(self.location_filename(self.mixture(m_id).name), items)

    def read_target_audio(self, t_id: int) -> AudioT:
        """Read target audio

        :param t_id: Target ID
        :return: Target audio
        """
        from .audio import read_audio

        return read_audio(self.target_file(t_id).name)

    def augmented_noise_audio(self, mixture: Mixture) -> AudioT:
        """Get augmented noise audio

        :param mixture: Mixture
        :return: Augmented noise audio
        """
        from .audio import read_audio
        from .audio import read_ir
        from .augmentation import apply_augmentation
        from .augmentation import apply_impulse_response

        noise = self.noise_file(mixture.noise.file_id)
        audio = read_audio(noise.name)
        audio = apply_augmentation(audio, mixture.noise.augmentation)
        if mixture.noise.augmentation.ir is not None:
            audio = apply_impulse_response(audio, read_ir(self.impulse_response_file(mixture.noise.augmentation.ir)))

        return audio

    def mixture_targets(self, m_id: int, force: bool = False) -> AudiosT:
        """Get the list of augmented target audio data (one per target in the mixup) for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: List of augmented target audio data (one per target in the mixup)
        """
        from sonusai import SonusAIError
        from .augmentation import apply_augmentation
        from .augmentation import apply_gain
        from .augmentation import pad_audio_to_length

        if not force:
            targets_audio = self.read_mixture_data(m_id, 'targets')
            if targets_audio is not None:
                return list(targets_audio)

        mixture = self.mixture(m_id)
        if mixture is None:
            raise SonusAIError(f'Could not find mixture for m_id: {m_id}')

        targets_audio = []
        for target in mixture.targets:
            target_audio = self.read_target_audio(target.file_id)
            target_audio = apply_augmentation(audio=target_audio,
                                              augmentation=target.augmentation,
                                              frame_length=self.feature_step_samples)
            target_audio = apply_gain(audio=target_audio, gain=mixture.target_snr_gain)
            target_audio = pad_audio_to_length(audio=target_audio, length=mixture.samples)
            targets_audio.append(target_audio)

        return targets_audio

    def mixture_targets_f(self,
                          m_id: int,
                          targets: Optional[AudiosT] = None,
                          force: bool = False) -> AudiosF:
        """Get the list of augmented target transform data (one per target in the mixup) for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: List of augmented target transform data (one per target in the mixup)
        """
        from .helpers import forward_transform

        if force or targets is None:
            targets = self.mixture_targets(m_id, force)

        return [forward_transform(target, self.ft_config) for target in targets]

    def mixture_target(self,
                       m_id: int,
                       targets: Optional[AudiosT] = None,
                       force: bool = False) -> AudioT:
        """Get the augmented target audio data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Augmented target audio data
        """
        from .helpers import get_target

        if not force:
            target = self.read_mixture_data(m_id, 'target')
            if target is not None:
                return target

        if force or targets is None:
            targets = self.mixture_targets(m_id, force)

        return get_target(self, self.mixture(m_id), targets)

    def mixture_target_f(self,
                         m_id: int,
                         targets: Optional[AudiosT] = None,
                         target: Optional[AudioT] = None,
                         force: bool = False) -> AudioF:
        """Get the augmented target transform data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param target: Augmented target audio for the given m_id
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Augmented target transform data
        """
        from .helpers import forward_transform

        if force or target is None:
            target = self.mixture_target(m_id, targets, force)

        return forward_transform(target, self.ft_config)

    def mixture_noise(self,
                      m_id: int,
                      force: bool = False) -> AudioT:
        """Get the augmented noise audio data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Augmented noise audio data
        """
        from .audio import get_next_noise
        from .augmentation import apply_gain

        if not force:
            noise = self.read_mixture_data(m_id, 'noise')
            if noise is not None:
                return noise

        mixture = self.mixture(m_id)
        noise = self.augmented_noise_audio(mixture)
        noise = get_next_noise(audio=noise, offset=mixture.noise.offset, length=mixture.samples)
        return apply_gain(audio=noise, gain=mixture.noise_snr_gain)

    def mixture_noise_f(self,
                        m_id: int,
                        noise: Optional[AudioT] = None,
                        force: bool = False) -> AudioF:
        """Get the augmented noise transform for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param noise: Augmented noise audio data
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Augmented noise transform data
        """
        from .helpers import forward_transform

        if force or noise is None:
            noise = self.mixture_noise(m_id, force)

        return forward_transform(noise, self.ft_config)

    def mixture_mixture(self,
                        m_id: int,
                        targets: Optional[AudiosT] = None,
                        target: Optional[AudioT] = None,
                        noise: Optional[AudioT] = None,
                        force: bool = False) -> AudioT:
        """Get the mixture audio data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param target: Augmented target audio data
        :param noise: Augmented noise audio data
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Mixture audio data
        """
        if not force:
            mixture = self.read_mixture_data(m_id, 'mixture')
            if mixture is not None:
                return mixture

        if force or target is None:
            target = self.mixture_target(m_id, targets, force)

        if force or noise is None:
            noise = self.mixture_noise(m_id, force)

        return target + noise

    def mixture_mixture_f(self,
                          m_id: int,
                          targets: Optional[AudiosT] = None,
                          target: Optional[AudioT] = None,
                          noise: Optional[AudioT] = None,
                          mixture: Optional[AudioT] = None,
                          force: bool = False) -> AudioF:
        """Get the mixture transform for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param target: Augmented target audio data
        :param noise: Augmented noise audio data
        :param mixture: Mixture audio data
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Mixture transform data
        """
        from .helpers import forward_transform
        from .spectral_mask import apply_spectral_mask

        if force or mixture is None:
            mixture = self.mixture_mixture(m_id, targets, target, noise, force)

        mixture_f = forward_transform(mixture, self.ft_config)

        m = self.mixture(m_id)
        if m.spectral_mask_id is not None:
            mixture_f = apply_spectral_mask(audio_f=mixture_f,
                                            spectral_mask=self.spectral_mask(int(m.spectral_mask_id)),
                                            seed=m.spectral_mask_seed)

        return mixture_f

    def mixture_truth_t(self,
                        m_id: int,
                        targets: Optional[AudiosT] = None,
                        noise: Optional[AudioT] = None,
                        mixture: Optional[AudioT] = None,
                        force: bool = False) -> Truth:
        """Get the truth_t data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixture ID
        :param noise: Augmented noise audio data for the given mixture ID
        :param mixture: Mixture audio data for the given mixture ID
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: truth_t data
        """
        from .helpers import get_truth_t

        if not force:
            truth_t = self.read_mixture_data(m_id, 'truth_t')
            if truth_t is not None:
                return truth_t

        if force or targets is None:
            targets = self.mixture_targets(m_id, force)

        if force or noise is None:
            noise = self.mixture_noise(m_id, force)

        if force or mixture is None:
            noise = self.mixture_mixture(m_id,
                                         targets=targets,
                                         noise=noise,
                                         force=force)

        return get_truth_t(self, self.mixture(m_id), targets, noise, mixture)

    def mixture_segsnr_t(self,
                         m_id: int,
                         targets: Optional[AudiosT] = None,
                         target: Optional[AudioT] = None,
                         noise: Optional[AudioT] = None,
                         force: bool = False) -> Segsnr:
        """Get the segsnr_t data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param target: Augmented target audio data
        :param noise: Augmented noise audio data
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: segsnr_t data
        """
        from .helpers import get_segsnr_t

        if not force:
            segsnr_t = self.read_mixture_data(m_id, 'segsnr_t')
            if segsnr_t is not None:
                return segsnr_t

        if force or target is None:
            target = self.mixture_target(m_id, targets, force)

        if force or noise is None:
            noise = self.mixture_noise(m_id, force)

        return get_segsnr_t(self, self.mixture(m_id), target, noise)

    def mixture_segsnr(self,
                       m_id: int,
                       segsnr_t: Optional[Segsnr] = None,
                       targets: Optional[AudiosT] = None,
                       target: Optional[AudioT] = None,
                       noise: Optional[AudioT] = None,
                       force: bool = False) -> Segsnr:
        """Get the segsnr data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param segsnr_t: segsnr_t data
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param target: Augmented target audio data
        :param noise: Augmented noise audio data
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: segsnr data
        """
        if not force:
            segsnr = self.read_mixture_data(m_id, 'segsnr')
            if segsnr is not None:
                return segsnr

            segsnr_t = self.read_mixture_data(m_id, 'segsnr_t')
            if segsnr_t is not None:
                return segsnr_t[0::self.ft_config.R]

        if force or segsnr_t is None:
            segsnr_t = self.mixture_segsnr_t(m_id, targets, target, noise, force)

        return segsnr_t[0::self.ft_config.R]

    def mixture_ft(self,
                   m_id: int,
                   targets: Optional[AudiosT] = None,
                   target: Optional[AudioT] = None,
                   noise: Optional[AudioT] = None,
                   mixture_f: Optional[AudioF] = None,
                   mixture: Optional[AudioT] = None,
                   truth_t: Optional[Truth] = None,
                   force: bool = False) -> tuple[Feature, Truth]:
        """Get the feature and truth_f data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param target: Augmented target audio data
        :param noise: Augmented noise audio data
        :param mixture_f: Mixture transform data
        :param mixture: Mixture audio data
        :param truth_t: truth_t
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Tuple of (feature, truth_f) data
        """
        from dataclasses import asdict

        import numpy as np
        from pyaaware import FeatureGenerator

        from .truth import truth_reduction

        if not force:
            feature, truth_f = self.read_mixture_data(m_id, ['feature', 'truth_f'])
            if feature is not None and truth_f is not None:
                return feature, truth_f

        if force or mixture_f is None:
            mixture_f = self.mixture_mixture_f(m_id=m_id,
                                               targets=targets,
                                               target=target,
                                               noise=noise,
                                               mixture=mixture,
                                               force=force)

        if force or truth_t is None:
            truth_t = self.mixture_truth_t(m_id=m_id, targets=targets, noise=noise, force=force)

        m = self.mixture(m_id)
        transform_frames = self.mixture_transform_frames(m.samples)
        feature_frames = self.mixture_feature_frames(m.samples)

        if truth_t is None:
            truth_t = np.zeros((m.samples, self.num_classes), dtype=np.float32)

        feature = np.empty((feature_frames, self.fg_stride, self.feature_parameters), dtype=np.float32)
        truth_f = np.empty((feature_frames, self.num_classes), dtype=np.complex64)

        fg = FeatureGenerator(**asdict(self.fg_config))
        feature_frame = 0
        for transform_frame in range(transform_frames):
            indices = slice(transform_frame * self.ft_config.R, (transform_frame + 1) * self.ft_config.R)
            fg.execute(mixture_f[transform_frame],
                       truth_reduction(truth_t[indices], self.truth_reduction_function))

            if fg.eof():
                feature[feature_frame] = fg.feature()
                truth_f[feature_frame] = fg.truth()
                feature_frame += 1

        if np.isreal(truth_f).all():
            return feature, truth_f.real

        return feature, truth_f

    def mixture_feature(self,
                        m_id: int,
                        targets: Optional[AudiosT] = None,
                        noise: Optional[AudioT] = None,
                        mixture: Optional[AudioT] = None,
                        truth_t: Optional[Truth] = None,
                        force: bool = False) -> Feature:
        """Get the feature data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param noise: Augmented noise audio data
        :param mixture: Mixture audio data
        :param truth_t: truth_t
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Feature data
        """
        feature, _ = self.mixture_ft(m_id=m_id,
                                     targets=targets,
                                     noise=noise,
                                     mixture=mixture,
                                     truth_t=truth_t,
                                     force=force)
        return feature

    def mixture_truth_f(self,
                        m_id: int,
                        targets: Optional[AudiosT] = None,
                        noise: Optional[AudioT] = None,
                        mixture: Optional[AudioT] = None,
                        truth_t: Optional[Truth] = None,
                        force: bool = False) -> Truth:
        """Get the truth_f data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup)
        :param noise: Augmented noise audio data
        :param mixture: Mixture audio data
        :param truth_t: truth_t
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: truth_f data
        """
        _, truth_f = self.mixture_ft(m_id=m_id,
                                     targets=targets,
                                     noise=noise,
                                     mixture=mixture,
                                     truth_t=truth_t,
                                     force=force)
        return truth_f

    def mixture_class_count(self,
                            m_id: int,
                            targets: Optional[AudiosT] = None,
                            noise: Optional[AudioT] = None,
                            truth_t: Optional[Truth] = None) -> ClassCount:
        """Compute the number of samples for which each truth index is active for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param targets: List of augmented target audio (one per target in the mixup)
        :param noise: Augmented noise audio
        :param truth_t: truth_t
        :return: List of class counts
        """
        import numpy as np

        if truth_t is None:
            truth_t = self.mixture_truth_t(m_id, targets, noise)

        class_count = [0] * self.num_classes
        num_classes = self.num_classes
        if self.truth_mutex:
            num_classes -= 1
        for cl in range(num_classes):
            class_count[cl] = int(np.sum(truth_t[:, cl] >= self.class_weights_thresholds[cl]))

        return class_count

    @cached_property
    def speaker_metadata_tiers(self) -> list[str]:
        import json

        with self.db() as c:
            return json.loads(c.execute("SELECT speaker_metadata_tiers FROM top WHERE 1 = id").fetchone()[0])

    @cached_property
    def textgrid_metadata_tiers(self) -> list[str]:
        import json

        with self.db() as c:
            return json.loads(c.execute("SELECT textgrid_metadata_tiers FROM top WHERE 1 = id").fetchone()[0])

    @cached_property
    def speech_metadata_tiers(self) -> list[str]:
        return sorted(set(self.speaker_metadata_tiers + self.textgrid_metadata_tiers))

    def speaker(self, speaker_id: int | None, tier: str) -> Optional[str]:
        if speaker_id is None:
            return None

        with self.db() as c:
            data = c.execute(f'SELECT {tier} FROM speaker WHERE ? = id', (speaker_id,)).fetchone()
            if data is None:
                return None
            if data[0] is None:
                return None
            return data[0]

    def speech_metadata(self, tier: str) -> list[str]:
        from .helpers import get_textgrid_tier_from_target_file

        results: set[str] = set()
        if tier in self.textgrid_metadata_tiers:
            for target_file in self.target_files:
                data = get_textgrid_tier_from_target_file(target_file.name, tier)
                if data is None:
                    continue
                if isinstance(data, list):
                    for item in data:
                        results.add(item.label)
                else:
                    results.add(data)
        elif tier in self.speaker_metadata_tiers:
            for target_file in self.target_files:
                data = self.speaker(target_file.speaker_id, tier)
                if data is not None:
                    results.add(data)

        return sorted(results)

    def mixture_speech_metadata(self, mixid: int, tier: str) -> list[SpeechMetadata]:
        from praatio.utilities.constants import Interval

        from .helpers import get_textgrid_tier_from_target_file

        results: list[SpeechMetadata] = []
        is_textgrid = tier in self.textgrid_metadata_tiers
        if is_textgrid:
            for target in self.mixture(mixid).targets:
                data = get_textgrid_tier_from_target_file(self.target_file(target.file_id).name, tier)
                if data is not None:
                    if isinstance(data, list):
                        # Check for tempo augmentation and adjust Interval start and end data as needed
                        entries = []
                        for entry in data:
                            if target.augmentation.tempo is not None:
                                entries.append(Interval(entry.start / target.augmentation.tempo,
                                                        entry.end / target.augmentation.tempo,
                                                        entry.label))
                            else:
                                entries.append(entry)
                        results.append(entries)
                    else:
                        results.append(data)
        else:
            for target in self.mixture(mixid).targets:
                data = self.speaker(self.target_file(target.file_id).speaker_id, tier)
                if data is not None:
                    results.append(data)

        return sorted(results)

    def mixids_for_speech_metadata(self,
                                   tier: str,
                                   value: str | None,
                                   predicate: Callable[[str], bool] = None) -> list[int]:
        """Get a list of mixture IDs for the given speech metadata tier.

        If 'predicate' is None, then include mixture IDs whose tier values are equal to the given 'value'.
        If 'predicate' is not None, then ignore 'value' and use the given callable to determine which entries
        to include.

        Examples:
        >>> mixdb = MixtureDatabase('/mixdb_location')

        >>> mixids = mixdb.mixids_for_speech_metadata('speaker_id', 'TIMIT_ARC0')
        Get mixutre IDs for mixtures with speakers whose speaker_ids are 'TIMIT_ARC0'.

        >>> mixids = mixdb.mixids_for_speech_metadata('age', '', lambda x: int(x) < 25)
        Get mixture IDs for mixtures with speakers whose ages are less than 25.

        >>> mixids = mixdb.mixids_for_speech_metadata('dialect', '', lambda x: x in ['New York City', 'Northern'])
        Get mixture IDs for mixtures with speakers whose dialects are either 'New York City' or 'Northern'.
        """
        from .helpers import get_textgrid_tier_from_target_file

        if predicate is None:
            def predicate(x: str | None) -> bool:
                return x == value

        # First get list of matching target files
        target_files: list[str] = []
        is_textgrid = tier in self.textgrid_metadata_tiers
        for target_file in self.target_files:
            if is_textgrid:
                metadata = get_textgrid_tier_from_target_file(target_file.name, tier)
            else:
                metadata = self.speaker(target_file.speaker_id, tier)

            if not isinstance(metadata, list) and predicate(metadata):
                target_files.append(target_file.name)

        # Next get list of mixture IDs that contain those target files
        m_ids: list[int] = []
        for m_id in self.mixids_to_list():
            mixid_target_files = [self.target_file(target.file_id).name for target in self.mixture(m_id).targets]
            for mixid_target_file in mixid_target_files:
                if mixid_target_file in target_files:
                    m_ids.append(m_id)

        # Return sorted, unique list of mixture IDs
        return sorted(list(set(m_ids)))

    def mixture_all_speech_metadata(self, m_id: int) -> list[dict[str, SpeechMetadata]]:
        from .helpers import mixture_all_speech_metadata

        return mixture_all_speech_metadata(self, self.mixture(m_id))

    def mixture_metric(self, m_id: int, metric: str, force: bool = False) -> Any:
        """Get metric data for the given mixture ID

        :param m_id: Zero-based mixture ID
        :param metric: Metric data to retrieve
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Metric data
        """
        from sonusai import SonusAIError

        supported_metrics = (
            'MXSNR',
            'MXSSNRAVG',
            'MXSSNRSTD',
            'MXSSNRDAVG',
            'MXSSNRDSTD',
            'MXPESQ',
            'MXWSDR',
            'MXPD',
            'MXSTOI',
            'MXCSIG',
            'MXCBAK',
            'MXCOVL',
            'TDCO',
            'TMIN',
            'TMAX',
            'TPKDB',
            'TLRMS',
            'TPKR',
            'TTR',
            'TCR',
            'TFL',
            'TPKC',
            'NDCO',
            'NMIN',
            'NMAX',
            'NPKDB',
            'NLRMS',
            'NPKR',
            'NTR',
            'NCR',
            'NFL',
            'NPKC',
            'SEDAVG',
            'SEDCNT',
            'SEDTOPN',
        )

        if not (metric in supported_metrics or metric.startswith('MXWER')):
            raise ValueError(f'Unsupported metric: {metric}')

        if not force:
            result = self.read_mixture_data(m_id, metric)
            if result is not None:
                return result

        mixture = self.mixture(m_id)
        if mixture is None:
            raise SonusAIError(f'Could not find mixture for m_id: {m_id}')

        if metric.startswith('MXWER'):
            return None

        if metric == 'MXSNR':
            return self.snrs

        if metric == 'MXSSNRAVG':
            return None

        if metric == 'MXSSNRSTD':
            return None

        if metric == 'MXSSNRDAVG':
            return None

        if metric == 'MXSSNRDSTD':
            return None

        if metric == 'MXPESQ':
            return None

        if metric == 'MXWSDR':
            return None

        if metric == 'MXPD':
            return None

        if metric == 'MXSTOI':
            return None

        if metric == 'MXCSIG':
            return None

        if metric == 'MXCBAK':
            return None

        if metric == 'MXCOVL':
            return None

        if metric == 'TDCO':
            return None

        if metric == 'TMIN':
            return None

        if metric == 'TMAX':
            return None

        if metric == 'TPKDB':
            return None

        if metric == 'TLRMS':
            return None

        if metric == 'TPKR':
            return None

        if metric == 'TTR':
            return None

        if metric == 'TCR':
            return None

        if metric == 'TFL':
            return None

        if metric == 'TPKC':
            return None

        if metric == 'NDCO':
            return None

        if metric == 'NMIN':
            return None

        if metric == 'NMAX':
            return None

        if metric == 'NPKDB':
            return None

        if metric == 'NLRMS':
            return None

        if metric == 'NPKR':
            return None

        if metric == 'NTR':
            return None

        if metric == 'NCR':
            return None

        if metric == 'NFL':
            return None

        if metric == 'NPKC':
            return None

        if metric == 'SEDAVG':
            return None

        if metric == 'SEDCNT':
            return None

        if metric == 'SEDTOPN':
            return None


@lru_cache
def _spectral_mask(db: partial, sm_id: int) -> SpectralMask:
    """Get spectral mask with ID from db

    :param db: Database context
    :param sm_id: Spectral mask ID
    :return: Spectral mask
    """
    with db() as c:
        spectral_mask = c.execute(
            "SELECT spectral_mask.f_max_width, f_num, t_max_width, t_num, t_max_percent " +
            "FROM spectral_mask " +
            "WHERE ? = spectral_mask.id",
            (sm_id,)).fetchone()
        return SpectralMask(f_max_width=spectral_mask[0],
                            f_num=spectral_mask[1],
                            t_max_width=spectral_mask[2],
                            t_num=spectral_mask[3],
                            t_max_percent=spectral_mask[4])


@lru_cache
def _target_file(db: partial, t_id: int) -> TargetFile:
    """Get target file with ID from db

    :param db: Database context
    :param t_id: Target file ID
    :return: Target file
    """
    import json

    from .datatypes import TruthSetting
    from .datatypes import TruthSettings

    with db() as c:
        target = c.execute(
            "SELECT target_file.name, samples, level_type, speaker_id FROM target_file WHERE ? = target_file.id",
            (t_id,)).fetchone()

        truth_settings: TruthSettings = []
        for ts in c.execute(
                "SELECT truth_setting.setting " +
                "FROM truth_setting, target_file_truth_setting " +
                "WHERE ? = target_file_truth_setting.target_file_id " +
                "AND truth_setting.id = target_file_truth_setting.truth_setting_id",
                (t_id,)).fetchall():
            entry = json.loads(ts[0])
            truth_settings.append(TruthSetting(config=entry.get('config', None),
                                               function=entry.get('function', None),
                                               index=entry.get('index', None)))
        return TargetFile(name=target[0],
                          samples=target[1],
                          level_type=target[2],
                          truth_settings=truth_settings,
                          speaker_id=target[3])


@lru_cache
def _noise_file(db: partial, n_id: int) -> NoiseFile:
    """Get noise file with ID from db

    :param db: Database context
    :param n_id: Noise file ID
    :return: Noise file
    """
    with db() as c:
        noise = c.execute("SELECT noise_file.name, samples FROM noise_file WHERE ? = noise_file.id",
                          (n_id,)).fetchone()
        return NoiseFile(name=noise[0], samples=noise[1])


@lru_cache
def _impulse_response_file(db: partial, ir_id: int) -> str:
    """Get impulse response file with ID from db

    :param db: Database context
    :param ir_id: Impulse response file ID
    :return: Noise
    """
    with db() as c:
        return str(c.execute(
            "SELECT impulse_response_file.file FROM impulse_response_file WHERE ? = impulse_response_file.id",
            (ir_id + 1,)).fetchone()[0])


@lru_cache
def _mixture(db: partial, m_id: int) -> Mixture:
    """Get mixture record with ID from db

    :param db: Database context
    :param m_id: Zero-based mixture ID
    :return: Mixture record
    """
    from .helpers import to_mixture
    from .helpers import to_target

    with db() as c:
        mixture = c.execute(
            "SELECT mixture.name, noise_file_id, noise_augmentation, noise_offset, noise_snr_gain, " +
            "random_snr, snr, samples, spectral_mask_id, spectral_mask_seed, target_snr_gain, id " +
            "FROM mixture " +
            "WHERE ? = mixture.id",
            (m_id + 1,)).fetchone()

        targets = [to_target(target) for target in c.execute(
            "SELECT target.file_id, augmentation, gain " +
            "FROM target, mixture_target " +
            "WHERE ? = mixture_target.mixture_id AND target.id = mixture_target.target_id",
            (mixture[11],)).fetchall()]

        return to_mixture(mixture, targets)
