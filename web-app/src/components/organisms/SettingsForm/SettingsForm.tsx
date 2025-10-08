import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { UserSettingsSchema, UserSettings } from '../../../schemas/userSettings';
import { CyberpunkInput } from '../../atoms/CyberpunkInput/CyberpunkInput';
import { NeonButton } from '../../atoms/NeonButton';

export const SettingsForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UserSettings>({
    resolver: zodResolver(UserSettingsSchema),
  });

  const onSubmit = (data: UserSettings) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <CyberpunkInput
        label="Theme"
        {...register('theme')}
        error={errors.theme?.message}
      />
      <CyberpunkInput
        label="Enable Animations"
        type="checkbox"
        {...register('enableAnimations')}
        error={errors.enableAnimations?.message}
      />
      <CyberpunkInput
        label="Audio Quality"
        {...register('audioQuality')}
        error={errors.audioQuality?.message}
      />
      <CyberpunkInput
        label="Auto Play"
        type="checkbox"
        {...register('autoPlay')}
        error={errors.autoPlay?.message}
      />
      <NeonButton type="submit">Save Settings</NeonButton>
    </form>
  );
};
