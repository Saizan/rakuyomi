#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple
import json
import sys 
import subprocess

@dataclass
class Location:
    line: int
    character: int

    @staticmethod
    def from_json(json: Dict[Any, Any]) -> 'Location':
        return Location(
            line=json['line'],
            character=json['character'],
        )

@dataclass
class Diagnostic:
    code: str
    message: str
    range: Tuple[Location, Location]

    def from_json(json: Dict[Any, Any]) -> 'Diagnostic':
        range_start = Location.from_json(json['range']['start'])
        range_end = Location.from_json(json['range']['end'])

        return Diagnostic(
            code=json['code'],
            message=json['message'],
            range=(range_start, range_end),
        )

def main(project_path: Path) -> None: 
    file_diagnostics = collect_diagnostics(project_path)

    if len(file_diagnostics) > 0:
        print(f'❌ Found problems in {len(file_diagnostics)} files:')
    else:
        print('✔️ No problems found!')

    for file, diagnostics in file_diagnostics.items():
        relative_path = file.relative_to(project_path.absolute())
        print(f'📄 {str(relative_path)}:')

        for diagnostic in diagnostics:
            print(
                f'- {diagnostic.range[0].line}:{diagnostic.range[0].character}'
                '-'
                f'{diagnostic.range[1].line}:{diagnostic.range[1].character}'
                ': '
                f'{diagnostic.message} ({diagnostic.code})'
            )
        
        print()
    
    exit_code = 2 if len(file_diagnostics) > 0 else 0
    sys.exit(exit_code)

def collect_diagnostics(project_path: Path) -> Dict[Path, List[Diagnostic]]:
    with TemporaryDirectory() as temporary_dir:
        log_path_folder = Path(temporary_dir)
        log_path = log_path_folder / 'check.json'

        subprocess.check_call([
            'lua-language-server',
            '--check', project_path,
            '--logpath', str(log_path_folder)
        ], stdout=subprocess.DEVNULL)

        # No diagnostics found, everything is OK.
        if not log_path.exists():
            return {}

        with open(log_path) as log:
            json_file_diagnostics: Dict[str, Dict[Any, Any]] = json.load(log)

            return {
                Path(source_path.removeprefix('file://')): [Diagnostic.from_json(json_diagnostic) for json_diagnostic in json_diagnostics]
                for source_path, json_diagnostics in json_file_diagnostics.items()
            }

def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('project_path', type=Path)

    return parser

if __name__ == '__main__':
    parser = create_argument_parser()
    args = parser.parse_args()

    main(**vars(args))
