"""Restartable open-access downloads with durable conservative byte reservations."""
from pathlib import Path
import time
import os
from .common import atomic_json, read_json, checksum, persist_file, utcnow, DEFAULT_PERSISTENT
from .gdc import session, API


def download_slide(record,raw_root='/tmp/lungcancer-raw',ledger_path='artifacts/download_ledger.json',budget=10_000_000_000,persist=True):
    if record.get('access')!='open': raise ValueError('only_open_access_downloads_are_supported')
    raw_root=Path(raw_root); raw_root.mkdir(parents=True,exist_ok=True)
    file_id=record['file_id']; size=int(record['file_size']); expected=record['md5sum']
    import uuid
    uuid.UUID(file_id)
    destination=raw_root/f'{file_id}.svs'; partial=destination.with_suffix('.svs.partial')
    ledger_path=Path(ledger_path)
    saved_ledger=DEFAULT_PERSISTENT/'artifacts/download_ledger.json'
    if persist and not ledger_path.exists() and saved_ledger.exists():
        import shutil
        ledger_path.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(saved_ledger,ledger_path)
        if checksum(saved_ledger)!=checksum(ledger_path): raise RuntimeError('restored_download_ledger_checksum_mismatch')
    ledger=read_json(ledger_path) if ledger_path.exists() else {'budget_bytes':budget,'reserved_bytes':0,'transferred_bytes':0,'attempts':[],'verified_files':{}}
    if ledger['budget_bytes']!=budget: raise ValueError('download_budget_change_requires_explicit_review')

    def save():
        atomic_json(ledger_path,ledger)
        if persist: persist_file(ledger_path,'artifacts/download_ledger.json')

    if destination.exists() and destination.stat().st_size==size and checksum(destination,'md5')==expected:
        print(f'Download already verified: {file_id}',flush=True)
        return destination
    if destination.exists(): raise ValueError('existing_raw_file_failed_verification; preserving_for_inspection')
    client=session()
    # Do not let HTTPAdapter retry streamed bodies behind the byte accounting.
    from requests.adapters import HTTPAdapter
    client.mount('https://',HTTPAdapter(max_retries=0))
    for attempt in range(3):
        offset=partial.stat().st_size if partial.exists() else 0
        if offset>size: raise ValueError('partial_file_larger_than_manifest')
        if offset==size:
            if checksum(partial,'md5')==expected:
                os.replace(partial,destination)
                ledger['verified_files'][file_id]={'md5sum':expected,'bytes':size,'verified_at':utcnow()}; save()
                return destination
            partial.unlink(); offset=0
        if ledger['reserved_bytes']+size>budget:
            raise RuntimeError('cumulative_download_budget_exhausted; review_required')
        entry={'file_id':file_id,'started_at':utcnow(),'resume_offset':offset,'reserved_bytes':size,'transferred_bytes':0,'status':'started'}
        ledger['reserved_bytes']+=size; ledger['attempts'].append(entry); save()
        try:
            with client.get(API+'/data/'+file_id,headers={'Range':f'bytes={offset}-'} if offset else {},
                            stream=True,timeout=(20,120)) as response:
                response.raise_for_status()
                if response.status_code==206:
                    if not response.headers.get('Content-Range','').startswith(f'bytes {offset}-'):
                        raise ValueError('unexpected_download_content_range')
                    mode='ab'
                elif response.status_code==200:
                    mode='wb'; offset=0
                else: raise ValueError('unexpected_download_status')
                with partial.open(mode) as stream:
                    for chunk in response.iter_content(chunk_size=1024*1024):
                        if not chunk: continue
                        entry['transferred_bytes']+=len(chunk); ledger['transferred_bytes']+=len(chunk)
                        if entry['transferred_bytes']>size: raise RuntimeError('download_larger_than_manifest')
                        stream.write(chunk)
                    stream.flush(); os.fsync(stream.fileno())
            if partial.stat().st_size!=size or checksum(partial,'md5')!=expected:
                # Only our own temporary download is reset; never user originals.
                entry['status']='checksum_or_size_failure'; save()
                partial.unlink(missing_ok=True)
                raise ValueError('download_checksum_or_size_mismatch')
            os.replace(partial,destination)
            entry['status']='verified'; entry['finished_at']=utcnow()
            ledger['verified_files'][file_id]={'md5sum':expected,'bytes':size,'verified_at':utcnow()}; save()
            print(f'Download verified: {file_id} ({size/1e6:.1f} MB)',flush=True)
            return destination
        except Exception as exc:
            entry['status']='failed'; entry['reason']=str(exc); save()
            print(f'Download attempt {attempt+1} failed: {file_id}: {exc}',flush=True)
            if attempt==2: raise
            time.sleep(2**attempt)


def remove_managed_raw(path,record,verified_receipts,raw_root='/tmp/lungcancer-raw'):
    path=Path(path).resolve(); root=Path(raw_root).resolve()
    if path.parent!=root or path.name!=f'{record["file_id"]}.svs':
        raise ValueError('refusing_cleanup_outside_managed_download_root')
    if not any(x['path'].endswith('/embeddings.npz') for x in verified_receipts):
        raise ValueError('refusing_cleanup_without_persisted_embeddings')
    for receipt in verified_receipts:
        if checksum(receipt['path'])!=receipt['sha256']: raise ValueError('persistent_receipt_verification_failed')
    path.unlink()
