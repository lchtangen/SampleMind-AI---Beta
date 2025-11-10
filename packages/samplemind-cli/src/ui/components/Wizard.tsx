import React from 'react';
import { Box, Text } from 'ink';

interface WizardStep {
  title: string;
  description: string;
}

interface WizardProps {
  title: string;
  steps: WizardStep[];
  activeStep: number;
  footer?: string;
}

export const Wizard: React.FC<WizardProps> = ({ title, steps, activeStep, footer }) => (
  <Box flexDirection="column" borderStyle="round" borderColor="#22d3ee" padding={1} width={60}>
    <Text color="#22d3ee" bold>
      {title}
    </Text>
    {steps.map((step, index) => (
      <Box key={step.title} flexDirection="column" marginTop={1}>
        <Text color={index === activeStep ? '#38bdf8' : '#475569'}>
          {index === activeStep ? '➤' : '•'} {step.title}
        </Text>
        {index === activeStep && (
          <Text color="#94a3b8">{step.description}</Text>
        )}
      </Box>
    ))}
    {footer && (
      <Box marginTop={1}>
        <Text color="#475569">{footer}</Text>
      </Box>
    )}
  </Box>
);
