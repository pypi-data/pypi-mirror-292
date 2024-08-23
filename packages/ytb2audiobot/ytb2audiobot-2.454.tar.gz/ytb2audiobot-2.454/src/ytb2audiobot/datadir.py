import pathlib
import tempfile
from ytb2audiobot import config
import hashlib


def get_md5(data, length=999999999):
    md5_hash = hashlib.md5()
    md5_hash.update(data.encode('utf-8'))
    return md5_hash.hexdigest()[:length]


def get_data_dir():
    cwd_md5 = get_md5(pathlib.Path.cwd().as_posix(), length=8)
    print('🏠 Current instance path and its hash : ', pathlib.Path.cwd().as_posix(), cwd_md5)

    temp_dir = pathlib.Path(tempfile.gettempdir())
    if temp_dir.exists():
        data_dir = temp_dir.joinpath(f'{config.DIRNAME_IN_TEMPDIR}-{cwd_md5}')
        data_dir.mkdir(parents=True, exist_ok=True)

        symlink = pathlib.Path(config.DIRNAME_DATA)
        if not symlink.exists():
            symlink.symlink_to(data_dir)

        return symlink
    else:
        data_dir = pathlib.Path(config.DIRNAME_DATA)
        if data_dir.is_symlink():
            try:
                data_dir.unlink()
            except Exception as e:
                print(f'Error symlink unlink: {e}')

        data_dir.mkdir(parents=True, exist_ok=True)

        return data_dir
