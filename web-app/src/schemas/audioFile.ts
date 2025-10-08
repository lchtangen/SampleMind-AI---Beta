import { z } from 'zod';

const MAX_FILE_SIZE = 1024 * 1024 * 100; // 100MB
const ACCEPTED_AUDIO_TYPES = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/x-m4a'];

export const AudioFileSchema = z.object({
  audioFile: z
    .any()
    .refine((files) => files?.length === 1, 'Audio file is required.')
    .transform((files) => files?.)
    .refine((file) => file?.size <= MAX_FILE_SIZE, `Max file size is 100MB.`)
    .refine(
      (file) => ACCEPTED_AUDIO_TYPES.includes(file?.type),
      'Only .mp3, .wav, .ogg, and .m4a formats are supported.'
    ),
});

export type AudioFile = z.infer<typeof AudioFileSchema>;
