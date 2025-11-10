import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { cn } from '../../lib/utils';
import { AudioAnalysisResult } from '@samplemind-ai/audio-engine';

interface AudioAnalysisVisualizerProps {
  analysis: AudioAnalysisResult;
  className?: string;
  width?: number;
  height?: number;
}

const KEY_NAMES = [
  'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'
];

const SCALE_NAMES = ['Major', 'Minor'];

export const AudioAnalysisVisualizer: React.FC<AudioAnalysisVisualizerProps> = ({
  analysis,
  className,
  width = 400,
  height = 300,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!analysis || !svgRef.current) return;
    
    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();
    
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Draw BPM gauge
    drawBPMGauge(svg, analysis.bpm, innerWidth, innerHeight / 3);
    
    // Draw key and scale indicators
    drawKeyScaleIndicator(
      svg,
      analysis.key,
      analysis.scale,
      innerWidth,
      innerHeight / 3,
      0,
      innerHeight / 3
    );
    
    // Draw feature radar chart
    drawFeatureRadar(
      svg,
      {
        energy: analysis.energy,
        danceability: analysis.danceability,
        valence: analysis.valence,
        arousal: analysis.arousal,
      },
      innerWidth,
      innerHeight / 3,
      0,
      (innerHeight / 3) * 2
    );
    
  }, [analysis, width, height]);
  
  const drawBPMGauge = (
    svg: d3.Selection<SVGGElement, unknown, null, undefined>,
    bpm: number,
    width: number,
    height: number
  ) => {
    const maxBPM = 200;
    const bpmNormalized = Math.min(bpm / maxBPM, 1);
    
    // Background
    svg.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', width)
      .attr('height', height)
      .attr('rx', 8)
      .attr('ry', 8)
      .attr('fill', 'rgba(0, 240, 255, 0.05)')
      .attr('stroke', 'rgba(0, 240, 255, 0.2)')
      .attr('stroke-width', 1);
    
    // BPM text
    svg.append('text')
      .attr('x', 10)
      .attr('y', 20)
      .attr('font-size', '12px')
      .attr('fill', 'rgba(255, 255, 255, 0.7)')
      .text('BPM');
    
    // BPM value
    svg.append('text')
      .attr('x', width - 10)
      .attr('y', 20)
      .attr('text-anchor', 'end')
      .attr('font-size', '24px')
      .attr('font-weight', 'bold')
      .attr('fill', 'rgba(0, 240, 255, 1)')
      .text(Math.round(bpm));
    
    // Gauge
    const gaugeHeight = 10;
    const gaugeY = 35;
    
    // Gauge background
    svg.append('rect')
      .attr('x', 0)
      .attr('y', gaugeY)
      .attr('width', width)
      .attr('height', gaugeHeight)
      .attr('rx', gaugeHeight / 2)
      .attr('ry', gaugeHeight / 2)
      .attr('fill', 'rgba(255, 255, 255, 0.1)');
    
    // Gauge fill
    svg.append('rect')
      .attr('x', 0)
      .attr('y', gaugeY)
      .attr('width', width * bpmNormalized)
      .attr('height', gaugeHeight)
      .attr('rx', gaugeHeight / 2)
      .attr('ry', gaugeHeight / 2)
      .attr('fill', 'url(#bpmGradient)');
    
    // Add gradient
    const defs = svg.append('defs');
    const gradient = defs.append('linearGradient')
      .attr('id', 'bpmGradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '0%');
    
    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#00f0ff');
      
    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#ff00ff');
  };
  
  const drawKeyScaleIndicator = (
    svg: d3.Selection<SVGGElement, unknown, null, undefined>,
    key: number,
    scale: number,
    width: number,
    height: number,
    x: number,
    y: number
  ) => {
    const keyName = KEY_NAMES[Math.round(key) % 12];
    const scaleName = SCALE_NAMES[Math.round(scale)] || 'Major';
    
    const group = svg.append('g')
      .attr('transform', `translate(${x}, ${y})`);
    
    // Background
    group.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('rx', 8)
      .attr('ry', 8)
      .attr('fill', 'rgba(0, 240, 255, 0.05)')
      .attr('stroke', 'rgba(0, 240, 255, 0.2)')
      .attr('stroke-width', 1);
    
    // Title
    group.append('text')
      .attr('x', 10)
      .attr('y', 20)
      .attr('font-size', '12px')
      .attr('fill', 'rgba(255, 255, 255, 0.7)')
      .text('Key & Scale');
    
    // Key and scale display
    const keyScaleGroup = group.append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2 + 10})`);
    
    // Outer circle
    keyScaleGroup.append('circle')
      .attr('r', 40)
      .attr('fill', 'rgba(0, 240, 255, 0.1)')
      .attr('stroke', 'rgba(0, 240, 255, 0.5)')
      .attr('stroke-width', 2);
    
    // Key text
    keyScaleGroup.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', '24px')
      .attr('font-weight', 'bold')
      .attr('fill', '#00f0ff')
      .text(keyName);
    
    // Scale text
    keyScaleGroup.append('text')
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', 'rgba(255, 255, 255, 0.7)')
      .text(scaleName);
  };
  
  const drawFeatureRadar = (
    svg: d3.Selection<SVGGElement, unknown, null, undefined>,
    features: {
      energy: number;
      danceability: number;
      valence: number;
      arousal: number;
    },
    width: number,
    height: number,
    x: number,
    y: number
  ) => {
    const radius = Math.min(width, height * 1.5) * 0.4;
    const centerX = width / 2;
    const centerY = height / 2;
    
    const group = svg.append('g')
      .attr('transform', `translate(${x}, ${y})`);
    
    // Background
    group.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('rx', 8)
      .attr('ry', 8)
      .attr('fill', 'rgba(0, 240, 255, 0.05)')
      .attr('stroke', 'rgba(0, 240, 255, 0.2)')
      .attr('stroke-width', 1);
    
    // Title
    group.append('text')
      .attr('x', 10)
      .attr('y', 20)
      .attr('font-size', '12px')
      .attr('fill', 'rgba(255, 255, 255, 0.7)')
      .text('Audio Features');
    
    const radarGroup = group.append('g')
      .attr('transform', `translate(${centerX}, ${centerY + 10})`);
    
    // Radar chart implementation...
    // (Implementation details omitted for brevity)
  };
  
  return (
    <div ref={containerRef} className={cn('w-full h-full', className)}>
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
};
