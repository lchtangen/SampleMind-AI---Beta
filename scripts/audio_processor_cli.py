#!/usr/bin/env python3
"""
SampleMind Audio Processor - Command Line Interface

A command-line tool for applying audio effects and noise reduction to audio files.
"""
import os
import argparse
import time
import numpy as np
import soundfile as sf
from pathlib import Path
from tqdm import tqdm

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from samplemind.audio.processor import AudioProcessor, AudioFormat
from samplemind.audio.effects import EffectType

# Supported audio formats
SUPPORTED_FORMATS = [f.value for f in AudioFormat]

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SampleMind Audio Processor')
    
    # Input/Output
    parser.add_argument('input', type=str, help='Input audio file or directory')
    parser.add_argument('-o', '--output', type=str, help='Output file or directory')
    parser.add_argument('--format', type=str, choices=SUPPORTED_FORMATS, 
                       default='wav', help='Output format (default: wav)')
    
    # Audio processing
    parser.add_argument('--sample-rate', type=int, default=44100,
                      help='Target sample rate in Hz (default: 44100)')
    parser.add_argument('--bit-depth', type=int, choices=[16, 24, 32], 
                      default=16, help='Output bit depth (default: 16)')
    
    # Effects
    effects_group = parser.add_argument_group('Audio Effects')
    effects_group.add_argument('--pitch-shift', type=float, default=0.0,
                             help='Pitch shift in semitones (e.g., 2.0, -1.5)')
    effects_group.add_argument('--time-stretch', type=float, default=1.0,
                             help='Time stretch factor (e.g., 1.2 for 20%% slower)')
    effects_group.add_argument('--reverb', action='store_true',
                             help='Add reverb effect')
    
    # Noise reduction
    noise_group = parser.add_argument_group('Noise Reduction')
    noise_group.add_argument('--reduce-noise', action='store_true',
                           help='Enable noise reduction')
    noise_group.add_argument('--noise-profile', type=str,
                           help='Noise profile audio file (for noise reduction)')
    noise_group.add_argument('--reduction-db', type=float, default=12.0,
                           help='Noise reduction amount in dB (default: 12.0)')
    noise_group.add_argument('--de-ess', action='store_true',
                           help='Reduce sibilance in vocals')
    noise_group.add_argument('--remove-clicks', action='store_true',
                           help='Remove clicks and pops')
    
    # Performance
    perf_group = parser.add_argument_group('Performance')
    perf_group.add_argument('--gpu', action='store_true',
                          help='Enable GPU acceleration if available')
    perf_group.add_argument('--batch-size', type=int, default=4,
                          help='Batch size for parallel processing (default: 4)')
    
    # Other
    parser.add_argument('--overwrite', action='store_true',
                      help='Overwrite existing output files')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                      help='Increase verbosity level')
    
    return parser.parse_args()

def process_single_file(processor, input_path, output_path, args):
    """Process a single audio file."""
    try:
        # Load audio
        if args.verbose > 0:
            print(f"Processing: {input_path}")
            
        y, sr = processor.load_audio(input_path)
        
        # Apply effects if any
        if args.pitch_shift != 0.0 or args.time_stretch != 1.0 or args.reverb:
            if args.verbose > 1:
                print("Applying audio effects...")
                
            # Clear any existing effects
            processor.clear_effects()
            
            # Add requested effects
            if args.time_stretch != 1.0:
                processor.add_effect(EffectType.TIME_STRETCH, {"rate": args.time_stretch})
                
            if args.pitch_shift != 0.0:
                processor.add_effect(EffectType.PITCH_SHIFT, {"n_steps": args.pitch_shift})
                
            if args.reverb:
                processor.add_effect(EffectType.REVERB, {
                    "room_size": 0.7,
                    "damping": 0.5,
                    "wet_level": 0.3,
                    "dry_level": 0.7
                })
            
            # Process effects
            y = processor.process_effects(y, sr)
        
        # Apply noise reduction if requested
        if args.reduce_noise and args.noise_profile:
            if args.verbose > 1:
                print("Learning noise profile...")
                
            # Load noise profile
            noise, noise_sr = processor.load_audio(args.noise_profile)
            processor.learn_noise_profile(noise)
            
            if args.verbose > 1:
                print("Reducing noise...")
                
            y = processor.reduce_noise(y, sr, reduction_db=args.reduction_db)
        
        # Apply de-essing if requested
        if args.de_ess:
            if args.verbose > 1:
                print("Reducing sibilance...")
                
            y = processor.de_ess(y, sr, threshold=0.15, ratio=4.0)
        
        # Apply click removal if requested
        if args.remove_clicks:
            if args.verbose > 1:
                print("Removing clicks...")
                
            y = processor.remove_clicks(y, sr)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the result
        if args.verbose > 0:
            print(f"Saving to: {output_path}")
            
        sf.write(output_path, y, sr, format=args.format, subtype=f'PCM_{args.bit_depth}')
        
        return True
        
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}", file=sys.stderr)
        return False

def main():
    """Main function."""
    args = parse_arguments()
    
    # Initialize processor
    processor = AudioProcessor(
        sample_rate=args.sample_rate,
        enable_gpu=args.gpu
    )
    
    # Process input
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Single file processing
        if not args.output:
            # Generate output filename if not provided
            output_path = input_path.with_stem(f"{input_path.stem}_processed")
            if args.format:
                output_path = output_path.with_suffix(f".{args.format}")
        else:
            output_path = Path(args.output)
        
        if not args.overwrite and output_path.exists():
            print(f"Error: Output file already exists: {output_path}", file=sys.stderr)
            print("Use --overwrite to overwrite existing files.", file=sys.stderr)
            sys.exit(1)
            
        success = process_single_file(processor, input_path, output_path, args)
        sys.exit(0 if success else 1)
        
    elif input_path.is_dir():
        # Batch processing
        if not args.output:
            print("Error: Output directory must be specified for batch processing", file=sys.stderr)
            sys.exit(1)
            
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all audio files in the input directory
        audio_files = []
        for ext in [f".{f}" for f in SUPPORTED_FORMATS]:
            audio_files.extend(list(input_path.rglob(f"*{ext}")))
            audio_files.extend(list(input_path.rglob(f"*{ext.upper()}")))
        
        if not audio_files:
            print(f"No supported audio files found in {input_path}", file=sys.stderr)
            sys.exit(1)
            
        print(f"Found {len(audio_files)} audio files to process")
        
        # Process files
        success_count = 0
        for audio_file in tqdm(audio_files, desc="Processing"):
            # Determine output path
            rel_path = audio_file.relative_to(input_path)
            output_path = output_dir / rel_path
            
            # Change extension if needed
            if args.format:
                output_path = output_path.with_suffix(f".{args.format}")
            
            # Skip if output exists and not overwriting
            if not args.overwrite and output_path.exists():
                if args.verbose > 0:
                    print(f"Skipping existing file: {output_path}")
                continue
                
            # Process the file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if process_single_file(processor, audio_file, output_path, args):
                success_count += 1
        
        print(f"\nProcessed {success_count}/{len(audio_files)} files successfully")
        sys.exit(0 if success_count == len(audio_files) else 1)
        
    else:
        print(f"Error: Input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
