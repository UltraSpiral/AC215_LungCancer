"""Verify an archive and restore only into a new directory; never overwrite."""
from pathlib import Path
import argparse
import hashlib
import shutil
import tarfile
import tempfile


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--destination',type=Path,default=Path('local_data/cpu_bundle'))
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    if digest(args.archive)!=args.sha256:raise ValueError('archive_sha256_mismatch')
    if args.destination.exists():raise ValueError('destination_exists; choose_a_new_directory')
    with tarfile.open(args.archive,'r:gz') as tf:
        members=tf.getmembers()
        for m in members:
            if not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts:
                raise ValueError('unsafe_archive_member')
        if not args.apply:
            print(f'Verified archive and {len(members)} safe file entries; add --apply to restore.')
            return
        args.destination.parent.mkdir(parents=True,exist_ok=True)
        temporary=Path(tempfile.mkdtemp(prefix='.cpu-restore-',dir=args.destination.parent))
        try:
            for member in members:
                target=temporary/member.name;target.parent.mkdir(parents=True,exist_ok=True)
                with tf.extractfile(member) as source,target.open('xb') as dest:
                    shutil.copyfileobj(source,dest)
            temporary.rename(args.destination)
        finally:
            if temporary.exists():shutil.rmtree(temporary)
    print(f'Restored {len(members)} files into {args.destination}')


if __name__=='__main__':main()
