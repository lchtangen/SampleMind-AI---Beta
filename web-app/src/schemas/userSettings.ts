import { z } from 'zod';

export const UserSettingsSchema = z.object({
  theme: z.enum(['light', 'dark', 'system']),
  notifications: z.object({
    email: z.boolean(),
    push: z.boolean(),
  }),
  language: z.string().default('en'),
});

export type UserSettings = z.infer<typeof UserSettingsSchema>;
