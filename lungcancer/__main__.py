import argparse
from pathlib import Path
from .common import read_json


def main():
    parser = argparse.ArgumentParser(prog='python -m lungcancer')
    sub = parser.add_subparsers(dest='command', required=True)
    smoke = sub.add_parser('encoder-smoke')
    smoke.add_argument('--output', default='artifacts/encoder_smoke.json')
    smoke.add_argument('--revision')
    backup = sub.add_parser('backup')
    sub.add_parser('restore')
    sub.add_parser('review')
    details=sub.add_parser('pilot-details')
    details.add_argument('--persist',action='store_true')
    profile=sub.add_parser('profile')
    profile.add_argument('--slide',required=True)
    profile.add_argument('--file-id',required=True)
    profile.add_argument('--batch-size',type=int,default=16)
    profile.add_argument('--output')
    discovery = sub.add_parser('discover')
    discovery.add_argument('--output',default='artifacts/discovery')
    audit = sub.add_parser('audit')
    audit.add_argument('--manifest',default='artifacts/discovery/manifest.json')
    audit.add_argument('--refresh-from-raw',action='store_true')
    select = sub.add_parser('select-pilot')
    select.add_argument('--manifest',default='artifacts/discovery/manifest.json')
    select.add_argument('--output',default='artifacts/pilot_selection.json')
    select.add_argument('--per-class',type=int,default=3)
    select.add_argument('--budget',type=int,default=10_000_000_000)
    pilot = sub.add_parser('pilot')
    pilot.add_argument('--selection',default='artifacts/pilot_selection.json')
    pilot.add_argument('--keep-raw',action='store_true')
    pilot.add_argument('--tile-config')
    download = sub.add_parser('download')
    download.add_argument('--selection',default='artifacts/pilot_selection.json')
    download.add_argument('--file-id',required=True)
    preprocessing = sub.add_parser('preprocess')
    preprocessing.add_argument('--slide',required=True)
    preprocessing.add_argument('--output',required=True)
    preprocessing.add_argument('--tile-config')
    embed = sub.add_parser('embed')
    embed.add_argument('--slide',required=True)
    embed.add_argument('--preprocessing',required=True)
    embed.add_argument('--revision')
    split = sub.add_parser('split')
    split.add_argument('--cohort',required=True)
    split.add_argument('--output',required=True)
    split.add_argument('--pilot-selection',default='artifacts/pilot_selection.json')
    split.add_argument('--seed',type=int,default=215)
    training=sub.add_parser('train')
    training.add_argument('--splits',required=True)
    training.add_argument('--artifacts',default='artifacts/slides')
    training.add_argument('--output',required=True)
    evaluation=sub.add_parser('evaluate')
    evaluation.add_argument('--splits',required=True)
    evaluation.add_argument('--artifacts',default='artifacts/slides')
    evaluation.add_argument('--model',required=True)
    evaluation.add_argument('--split',choices=['validation','test'],required=True)
    evaluation.add_argument('--output',required=True)
    prediction=sub.add_parser('predict')
    prediction.add_argument('--slide',required=True)
    prediction.add_argument('--model',required=True)
    prediction.add_argument('--output',required=True)
    if parser.parse_known_args()[0].command == 'encoder-smoke':
        args = parser.parse_args()
        from .encoder import smoke_test
        smoke_test(args.output,args.revision)
    elif parser.parse_known_args()[0].command == 'backup':
        from .common import backup_code, sync_artifacts
        print(backup_code())
        print(f'Persisted {len(sync_artifacts("artifacts"))} artifact files')
    else:
        args=parser.parse_args()
        from . import gdc
        if args.command=='discover': gdc.discover(args.output)
        elif args.command=='audit':
            import json
            report=gdc.refresh_audit(Path(args.manifest).parent) if args.refresh_from_raw else gdc.audit(read_json(args.manifest))
            print(json.dumps(report,indent=2))
        elif args.command=='select-pilot':
            gdc.select_pilot(args.manifest,args.output,args.per_class,args.budget)
        elif args.command=='pilot':
            from .pilot import run_pilot
            from .preprocess import TileConfig
            config=TileConfig(**read_json(args.tile_config)) if args.tile_config else None
            run_pilot(args.selection,config=config,cleanup=not args.keep_raw)
        elif args.command=='download':
            from .download import download_slide
            selection=read_json(args.selection)
            record=next(r for r in selection['slides'] if r['file_id']==args.file_id)
            print(download_slide(record,budget=selection['cumulative_raw_budget_bytes']))
        elif args.command=='preprocess':
            from .preprocess import TileConfig
            from .safety import prepare_checked as prepare_slide
            config=TileConfig(**read_json(args.tile_config)) if args.tile_config else None
            print(prepare_slide(args.slide,args.output,config))
        elif args.command=='embed':
            from .encoder import UNI2Encoder
            from .features import extract_features
            print(extract_features(args.slide,args.preprocessing,UNI2Encoder(args.revision)))
        elif args.command=='split':
            from .modeling import create_splits
            print(create_splits(args.cohort,args.output,args.seed,args.pilot_selection)['counts'])
        elif args.command=='train':
            from .modeling import train
            print(train(args.splits,args.artifacts,args.output)['validation'])
        elif args.command=='evaluate':
            from .modeling import evaluate
            print(evaluate(args.splits,args.artifacts,args.model,args.split,args.output))
        elif args.command=='predict':
            import json
            from .inference import predict
            result=predict(args.slide,args.model,args.output)
            print(json.dumps(result,indent=2))
            if result['status']=='error': raise SystemExit(2)
        elif args.command=='restore':
            from .common import restore_artifacts
            print(f'Restored {restore_artifacts()} missing local artifacts')
        elif args.command=='review':
            from .review import make_review
            print(make_review()['status'])
        elif args.command=='pilot-details':
            from .pilot_details import build_details
            if args.persist:
                from .common import backup_code,persist_file,ROOT
                backup_code()
                for name in ['scripts/show_pilot.py','README.md','STATUS.md']:
                    persist_file(ROOT/name,Path('code')/name)
            report=build_details()
            if args.persist:
                from .common import sync_artifacts
                sync_artifacts(ROOT/'artifacts/pilot_review','artifacts/pilot_review')
            print({k:report[k] for k in ['counts','actual_raw_bytes_downloaded','preservation_methods_as_reported',
                                       'explicit_frozen_confirmations','all_embeddings_finite','latest_source_code_backup']})
        elif args.command=='profile':
            from .profiling import profile_slide
            report=profile_slide(args.slide,args.file_id,args.batch_size,args.output)
            print({k:report[k] for k in ['gpu','batch_size','peak_gpu_allocated_bytes','peak_gpu_reserved_bytes',
                                       'steady_slide_total_seconds','stage_seconds','uni2_forward_cuda_event_seconds']})


if __name__ == '__main__':
    main()
