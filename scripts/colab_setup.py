"""Run once from a Colab notebook with %run; never stores a secret in the repo."""

from pathlib import Path
import os


def main():
    from IPython import get_ipython

    shell = get_ipython()
    if shell is None or not hasattr(shell, 'kernel'):
        raise SystemExit(
            'Run this in a Colab notebook code cell: '
            '%run /content/LungCancer/scripts/colab_setup.py'
        )

    from google.colab import drive, userdata
    from huggingface_hub import login, constants

    drive.mount('/content/drive')
    project = Path('/content/drive/MyDrive/LungCancer_AC215')
    (project / 'artifacts').mkdir(parents=True, exist_ok=True)

    previous_umask = os.umask(0o077)
    try:
        login(token=userdata.get('HF_HARV'), add_to_git_credential=False)
    finally:
        os.umask(previous_umask)
        for credential_path in (
            constants.HF_TOKEN_PATH,
            constants.HF_STORED_TOKENS_PATH,
        ):
            path = Path(credential_path)
            if path.exists():
                path.chmod(0o600)

    print('Drive and Hugging Face setup complete.')


if __name__ == '__main__':
    main()
